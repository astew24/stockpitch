"""
dcf_model.py — Discounted cash flow valuation engine for StockPitch.

Fetches live financial statements from yfinance, projects free cash flows
over a configurable horizon, and discounts them at WACC to arrive at an
intrinsic value per share. Also computes a WACC / terminal-growth sensitivity
heatmap and renders a multi-page PDF pitch brief via matplotlib.

Key functions:
    fetch_company_snapshot    — pull revenue, net income, FCF, shares, net debt
    run_dcf                   — project FCFs and compute intrinsic value per share
    build_sensitivity_heatmap — WACC × terminal-growth upside/downside grid
    create_pitch_pdf_bytes    — render cover, projection, and sensitivity pages to PDF
"""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
import math
from typing import Iterable

import matplotlib

matplotlib.use("Agg")

from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd
import yfinance as yf

from generate_pitches import GOLD, GREEN, LGRAY, MGRAY, NAVY, RED, WHITE


DEFAULT_WACC = 0.10
DEFAULT_TERMINAL_GROWTH = 0.025
DEFAULT_PROJECTION_YEARS = 5
# Terminal growth should stay below the long-run GDP growth assumption —
# anything above ~3.5% implies the company eventually grows faster than the economy.
_TERMINAL_GROWTH_CAP = 0.035


@dataclass(frozen=True)
class CompanyFinancialSnapshot:
    ticker: str
    company_name: str
    currency: str
    current_price: float
    shares_outstanding: float
    net_debt: float
    revenue_history: pd.Series
    net_income_history: pd.Series
    free_cash_flow_history: pd.Series

    @property
    def latest_revenue(self) -> float:
        return float(self.revenue_history.iloc[-1])

    @property
    def latest_net_income(self) -> float:
        return float(self.net_income_history.iloc[-1])

    @property
    def latest_free_cash_flow(self) -> float:
        return float(self.free_cash_flow_history.iloc[-1])


@dataclass(frozen=True)
class DCFInputs:
    revenue_growth_rate: float
    wacc: float
    terminal_growth_rate: float
    projection_years: int


@dataclass(frozen=True)
class DCFResult:
    inputs: DCFInputs
    fcf_margin: float
    projection_table: pd.DataFrame
    terminal_value: float
    present_value_of_terminal: float
    enterprise_value: float
    equity_value: float
    intrinsic_value_per_share: float
    upside_pct: float


def _normalize_history(series: pd.Series) -> pd.Series:
    cleaned = pd.to_numeric(series, errors="coerce").dropna()
    if cleaned.empty:
        raise ValueError("Required financial statement row is empty.")
    if not isinstance(cleaned.index, pd.DatetimeIndex):
        cleaned.index = pd.to_datetime(cleaned.index)
    return cleaned.sort_index()


def _extract_statement_series(statement: pd.DataFrame, labels: Iterable[str]) -> pd.Series:
    if statement is None or statement.empty:
        raise ValueError("Missing financial statement data from yfinance.")

    for label in labels:
        if label in statement.index:
            return _normalize_history(statement.loc[label])

    available = ", ".join(str(index) for index in statement.index[:12])
    raise ValueError(f"Could not find statement row. Tried {list(labels)}. Available rows: {available}")


def _latest_statement_value(statement: pd.DataFrame, labels: Iterable[str]) -> float | None:
    for label in labels:
        if label in statement.index:
            values = pd.to_numeric(statement.loc[label], errors="coerce").dropna()
            if not values.empty:
                return float(values.iloc[0])
    return None


def _coerce_positive_years(value: int) -> int:
    if value < 1:
        raise ValueError("Projection years must be at least 1.")
    return int(value)


def _latest_close_price(ticker: yf.Ticker) -> float:
    history = ticker.history(period="5d", auto_adjust=False)
    closes = history.get("Close")
    if closes is None or closes.dropna().empty:
        raise ValueError("No recent market price returned by yfinance.")
    return float(closes.dropna().iloc[-1])


def calculate_cagr(series: pd.Series) -> float:
    normalized = _normalize_history(series)
    if len(normalized) < 2:
        return math.nan

    start = float(normalized.iloc[0])
    end = float(normalized.iloc[-1])
    periods = len(normalized) - 1
    if start <= 0 or end <= 0:
        return math.nan
    return (end / start) ** (1 / periods) - 1


def compute_trailing_fcf_margin(snapshot: CompanyFinancialSnapshot, window: int = 3) -> float:
    aligned = pd.concat(
        [snapshot.revenue_history.rename("revenue"), snapshot.free_cash_flow_history.rename("fcf")],
        axis=1,
        join="inner",
    ).dropna()
    if aligned.empty:
        raise ValueError("Unable to compute free cash flow margin from yfinance data.")

    trailing = aligned.tail(window)
    margins = trailing["fcf"] / trailing["revenue"]
    margin = float(margins.mean())
    if not math.isfinite(margin):
        raise ValueError("Computed free cash flow margin is not finite.")
    return margin


def build_default_inputs(snapshot: CompanyFinancialSnapshot) -> DCFInputs:
    historical_growth = calculate_cagr(snapshot.revenue_history)
    if not math.isfinite(historical_growth):
        historical_growth = 0.08
    default_growth = min(0.20, max(-0.05, historical_growth))
    return DCFInputs(
        revenue_growth_rate=default_growth,
        wacc=DEFAULT_WACC,
        terminal_growth_rate=DEFAULT_TERMINAL_GROWTH,
        projection_years=DEFAULT_PROJECTION_YEARS,
    )


def fetch_company_snapshot(ticker_symbol: str) -> CompanyFinancialSnapshot:
    cleaned_ticker = ticker_symbol.strip().upper()
    if not cleaned_ticker:
        raise ValueError("Enter a stock ticker.")

    ticker = yf.Ticker(cleaned_ticker)
    try:
        financials = ticker.financials
        cashflow = ticker.cashflow
        balance_sheet = ticker.balance_sheet
        info = ticker.info or {}
    except Exception as exc:
        raise ValueError(f"Unable to fetch financial statements for {cleaned_ticker}.") from exc

    revenue_history = _extract_statement_series(financials, ["Total Revenue", "Operating Revenue"])
    net_income_history = _extract_statement_series(
        financials,
        [
            "Net Income",
            "Net Income Common Stockholders",
            "Net Income From Continuing Operation Net Minority Interest",
        ],
    )
    free_cash_flow_history = _extract_statement_series(cashflow, ["Free Cash Flow"])

    shares_outstanding = _latest_statement_value(
        balance_sheet, ["Ordinary Shares Number", "Share Issued"]
    )
    if shares_outstanding is None:
        shares_outstanding = info.get("sharesOutstanding")
    if shares_outstanding is None or shares_outstanding <= 0:
        raise ValueError(f"Unable to determine shares outstanding for {cleaned_ticker}.")

    net_debt = _latest_statement_value(balance_sheet, ["Net Debt"])
    if net_debt is None:
        total_debt = _latest_statement_value(balance_sheet, ["Total Debt"])
        cash = _latest_statement_value(
            balance_sheet,
            ["Cash Cash Equivalents And Short Term Investments", "Cash And Cash Equivalents"],
        )
        net_debt = float(total_debt or 0.0) - float(cash or 0.0)

    company_name = (
        info.get("longName")
        or info.get("shortName")
        or cleaned_ticker
    )
    currency = info.get("currency") or ticker.fast_info.get("currency") or "USD"

    return CompanyFinancialSnapshot(
        ticker=cleaned_ticker,
        company_name=company_name,
        currency=currency,
        current_price=_latest_close_price(ticker),
        shares_outstanding=float(shares_outstanding),
        net_debt=float(net_debt),
        revenue_history=revenue_history,
        net_income_history=net_income_history,
        free_cash_flow_history=free_cash_flow_history,
    )


def run_dcf(snapshot: CompanyFinancialSnapshot, inputs: DCFInputs) -> DCFResult:
    projection_years = _coerce_positive_years(inputs.projection_years)
    if inputs.wacc <= inputs.terminal_growth_rate:
        raise ValueError("WACC must be greater than terminal growth rate.")

    fcf_margin = compute_trailing_fcf_margin(snapshot)
    base_year = int(snapshot.revenue_history.index[-1].year)
    projected_rows = []

    for year_number in range(1, projection_years + 1):
        projected_revenue = snapshot.latest_revenue * ((1 + inputs.revenue_growth_rate) ** year_number)
        projected_fcf = projected_revenue * fcf_margin
        discount_factor = 1 / ((1 + inputs.wacc) ** year_number)
        present_value = projected_fcf * discount_factor
        projected_rows.append(
            {
                "label": f"FY{base_year + year_number}",
                "year_number": year_number,
                "projected_revenue": projected_revenue,
                "projected_fcf": projected_fcf,
                "discount_factor": discount_factor,
                "present_value_of_fcf": present_value,
            }
        )

    projection_table = pd.DataFrame(projected_rows)
    terminal_cash_flow = float(projection_table.iloc[-1]["projected_fcf"]) * (
        1 + inputs.terminal_growth_rate
    )
    terminal_value = terminal_cash_flow / (inputs.wacc - inputs.terminal_growth_rate)
    present_value_of_terminal = terminal_value * float(projection_table.iloc[-1]["discount_factor"])
    enterprise_value = float(projection_table["present_value_of_fcf"].sum()) + present_value_of_terminal
    equity_value = enterprise_value - snapshot.net_debt
    intrinsic_value_per_share = equity_value / snapshot.shares_outstanding
    upside_pct = ((intrinsic_value_per_share - snapshot.current_price) / snapshot.current_price) * 100

    return DCFResult(
        inputs=inputs,
        fcf_margin=fcf_margin,
        projection_table=projection_table,
        terminal_value=terminal_value,
        present_value_of_terminal=present_value_of_terminal,
        enterprise_value=enterprise_value,
        equity_value=equity_value,
        intrinsic_value_per_share=intrinsic_value_per_share,
        upside_pct=upside_pct,
    )


def build_sensitivity_heatmap(
    snapshot: CompanyFinancialSnapshot,
    base_inputs: DCFInputs,
    wacc_values: Iterable[float],
    terminal_growth_values: Iterable[float],
) -> pd.DataFrame:
    matrix = {}
    for wacc in wacc_values:
        row = {}
        for terminal_growth in terminal_growth_values:
            if terminal_growth >= wacc:
                row[terminal_growth] = np.nan
                continue
            result = run_dcf(
                snapshot,
                DCFInputs(
                    revenue_growth_rate=base_inputs.revenue_growth_rate,
                    wacc=wacc,
                    terminal_growth_rate=terminal_growth,
                    projection_years=base_inputs.projection_years,
                ),
            )
            row[terminal_growth] = result.upside_pct
        matrix[wacc] = row
    return pd.DataFrame.from_dict(matrix, orient="index").sort_index()


def build_summary_table(snapshot: CompanyFinancialSnapshot, result: DCFResult) -> pd.DataFrame:
    rows = [
        ("Latest revenue", snapshot.latest_revenue),
        ("Latest net income", snapshot.latest_net_income),
        ("Latest free cash flow", snapshot.latest_free_cash_flow),
        ("Trailing FCF margin", result.fcf_margin),
        ("Shares outstanding", snapshot.shares_outstanding),
        ("Net debt", snapshot.net_debt),
        ("Revenue growth", result.inputs.revenue_growth_rate),
        ("WACC", result.inputs.wacc),
        ("Terminal growth", result.inputs.terminal_growth_rate),
        ("Projection years", float(result.inputs.projection_years)),
        ("Enterprise value", result.enterprise_value),
        ("Equity value", result.equity_value),
        ("Intrinsic value / share", result.intrinsic_value_per_share),
        ("Current price", snapshot.current_price),
        ("Upside / downside", result.upside_pct),
    ]
    return pd.DataFrame(rows, columns=["Metric", "Value"])


def format_money(value: float, currency: str = "USD") -> str:
    absolute = abs(value)
    if absolute >= 1_000_000_000:
        amount = f"{absolute / 1_000_000_000:,.2f}B"
    elif absolute >= 1_000_000:
        amount = f"{absolute / 1_000_000:,.2f}M"
    else:
        amount = f"{absolute:,.2f}"

    prefix = "-" if value < 0 else ""

    if currency == "USD":
        return f"{prefix}${amount}"
    return f"{prefix}{amount} {currency}"


def create_pitch_pdf_bytes(
    snapshot: CompanyFinancialSnapshot,
    result: DCFResult,
    sensitivity: pd.DataFrame,
) -> bytes:
    buffer = BytesIO()
    with PdfPages(buffer) as pdf:
        _build_cover_page(pdf, snapshot, result)
        _build_projection_page(pdf, snapshot, result)
        _build_sensitivity_page(pdf, snapshot, result, sensitivity)
    buffer.seek(0)
    return buffer.read()


def _new_pdf_figure():
    figure = plt.figure(figsize=(13.33, 7.5))
    figure.patch.set_facecolor(WHITE)
    return figure


def _header(ax, title: str, subtitle: str, tag: str, tag_color: str) -> None:
    ax.set_facecolor(NAVY)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.04, 0.62, title, color=WHITE, fontsize=24, fontweight="bold", ha="left")
    ax.text(0.04, 0.24, subtitle, color=GOLD, fontsize=11, ha="left")
    ax.add_patch(plt.Rectangle((0.80, 0.20), 0.14, 0.56, color=tag_color))
    ax.text(0.87, 0.48, tag, color=WHITE, fontsize=12, fontweight="bold", ha="center")
    ax.axhline(0.02, color=GOLD, linewidth=2)


def _footer(ax, ticker: str) -> None:
    from datetime import date
    ax.set_facecolor(NAVY)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.03, 0.5, ticker, color=MGRAY, fontsize=8, ha="left")
    ax.text(0.97, 0.5, f"Generated from live yfinance data · {date.today().isoformat()}", color=MGRAY, fontsize=8, ha="right")


def _build_cover_page(pdf: PdfPages, snapshot: CompanyFinancialSnapshot, result: DCFResult) -> None:
    figure = _new_pdf_figure()
    header_ax = figure.add_axes([0, 0.82, 1, 0.18])
    tag_color = GREEN if result.upside_pct >= 0 else RED
    _header(
        header_ax,
        f"{snapshot.company_name} ({snapshot.ticker})",
        "Streamlit DCF pitch generated from live financial statements",
        "DCF",
        tag_color,
    )

    body_ax = figure.add_axes([0.05, 0.12, 0.90, 0.64])
    body_ax.axis("off")

    body_ax.text(
        0.00,
        0.92,
        "Intrinsic value per share",
        fontsize=11,
        color=MGRAY,
        ha="left",
    )
    body_ax.text(
        0.00,
        0.76,
        format_money(result.intrinsic_value_per_share, snapshot.currency),
        fontsize=30,
        color=tag_color,
        fontweight="bold",
        ha="left",
    )
    body_ax.text(
        0.00,
        0.57,
        f"Current price: {format_money(snapshot.current_price, snapshot.currency)}",
        fontsize=12,
        color=NAVY,
        ha="left",
    )
    body_ax.text(
        0.00,
        0.47,
        f"Valuation gap: {result.upside_pct:+.1f}%",
        fontsize=14,
        color=tag_color,
        fontweight="bold",
        ha="left",
    )

    summary_lines = [
        f"Latest revenue: {format_money(snapshot.latest_revenue, snapshot.currency)}",
        f"Latest net income: {format_money(snapshot.latest_net_income, snapshot.currency)}",
        f"Latest free cash flow: {format_money(snapshot.latest_free_cash_flow, snapshot.currency)}",
        f"Trailing FCF margin: {result.fcf_margin * 100:.2f}%",
        f"WACC: {result.inputs.wacc * 100:.2f}%",
        f"Terminal growth: {result.inputs.terminal_growth_rate * 100:.2f}%",
        f"Projection years: {result.inputs.projection_years}",
    ]
    for index, line in enumerate(summary_lines):
        body_ax.text(0.50, 0.84 - index * 0.10, line, fontsize=11, color=NAVY, ha="left")

    footer_ax = figure.add_axes([0, 0, 1, 0.05])
    _footer(footer_ax, snapshot.ticker)
    pdf.savefig(figure, bbox_inches="tight")
    plt.close(figure)


def _build_projection_page(pdf: PdfPages, snapshot: CompanyFinancialSnapshot, result: DCFResult) -> None:
    figure = _new_pdf_figure()
    header_ax = figure.add_axes([0, 0.82, 1, 0.18])
    _header(header_ax, "DCF Projection", "Revenue growth, free cash flow, and discounted value", "MODEL", NAVY)

    table_ax = figure.add_axes([0.04, 0.14, 0.92, 0.60])
    table_ax.axis("off")

    table_frame = result.projection_table.copy()
    table_frame["Revenue"] = table_frame["projected_revenue"].map(
        lambda value: format_money(value, snapshot.currency)
    )
    table_frame["Free Cash Flow"] = table_frame["projected_fcf"].map(
        lambda value: format_money(value, snapshot.currency)
    )
    table_frame["Discount Factor"] = table_frame["discount_factor"].map(lambda value: f"{value:.3f}")
    table_frame["PV of FCF"] = table_frame["present_value_of_fcf"].map(
        lambda value: format_money(value, snapshot.currency)
    )

    rendered = table_frame[["label", "Revenue", "Free Cash Flow", "Discount Factor", "PV of FCF"]]
    rendered.columns = ["Year", "Revenue", "Free Cash Flow", "Discount Factor", "PV of FCF"]
    table = table_ax.table(
        cellText=rendered.values,
        colLabels=rendered.columns,
        cellLoc="center",
        loc="upper center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor(NAVY)
            cell.set_text_props(color=WHITE, weight="bold")
        else:
            cell.set_facecolor(LGRAY if row % 2 else WHITE)
            cell.set_edgecolor("#D9DFE8")

    notes_ax = figure.add_axes([0.06, 0.05, 0.88, 0.08])
    notes_ax.axis("off")
    notes_ax.text(
        0.00,
        0.70,
        f"Enterprise value: {format_money(result.enterprise_value, snapshot.currency)}",
        fontsize=10,
        color=NAVY,
        fontweight="bold",
    )
    notes_ax.text(
        0.35,
        0.70,
        f"Net debt: {format_money(snapshot.net_debt, snapshot.currency)}",
        fontsize=10,
        color=NAVY,
        fontweight="bold",
    )
    notes_ax.text(
        0.63,
        0.70,
        f"Equity value: {format_money(result.equity_value, snapshot.currency)}",
        fontsize=10,
        color=NAVY,
        fontweight="bold",
    )
    notes_ax.text(
        0.00,
        0.15,
        f"PV of terminal value: {format_money(result.present_value_of_terminal, snapshot.currency)}",
        fontsize=9,
        color=MGRAY,
    )
    notes_ax.text(
        0.45,
        0.15,
        f"Terminal value: {format_money(result.terminal_value, snapshot.currency)}",
        fontsize=9,
        color=MGRAY,
    )

    footer_ax = figure.add_axes([0, 0, 1, 0.05])
    _footer(footer_ax, snapshot.ticker)
    pdf.savefig(figure, bbox_inches="tight")
    plt.close(figure)


def _build_sensitivity_page(
    pdf: PdfPages,
    snapshot: CompanyFinancialSnapshot,
    result: DCFResult,
    sensitivity: pd.DataFrame,
) -> None:
    figure = _new_pdf_figure()
    header_ax = figure.add_axes([0, 0.82, 1, 0.18])
    _header(
        header_ax,
        "WACC / Terminal Growth Sensitivity",
        "Green implies upside to the current price, red implies downside",
        "SENS",
        GOLD,
    )

    heatmap_ax = figure.add_axes([0.08, 0.15, 0.62, 0.58])
    image = heatmap_ax.imshow(sensitivity.values, cmap="RdYlGn", aspect="auto")
    heatmap_ax.set_xticks(range(len(sensitivity.columns)))
    heatmap_ax.set_xticklabels([f"{value * 100:.1f}%" for value in sensitivity.columns])
    heatmap_ax.set_yticks(range(len(sensitivity.index)))
    heatmap_ax.set_yticklabels([f"{value * 100:.1f}%" for value in sensitivity.index])
    heatmap_ax.set_xlabel("Terminal growth rate")
    heatmap_ax.set_ylabel("WACC")
    heatmap_ax.set_title("Upside / downside vs. current price")

    for row_index in range(sensitivity.shape[0]):
        for col_index in range(sensitivity.shape[1]):
            value = sensitivity.iat[row_index, col_index]
            label = "n/a" if pd.isna(value) else f"{value:+.0f}%"
            heatmap_ax.text(col_index, row_index, label, ha="center", va="center", fontsize=9)

    colorbar_ax = figure.add_axes([0.72, 0.15, 0.02, 0.58])
    figure.colorbar(image, cax=colorbar_ax)

    notes_ax = figure.add_axes([0.78, 0.15, 0.18, 0.58])
    notes_ax.axis("off")
    notes_ax.text(0.0, 0.90, "Base case", fontsize=12, color=NAVY, fontweight="bold")
    notes_ax.text(0.0, 0.78, f"Revenue growth: {result.inputs.revenue_growth_rate * 100:.2f}%", fontsize=10, color=NAVY)
    notes_ax.text(0.0, 0.68, f"WACC: {result.inputs.wacc * 100:.2f}%", fontsize=10, color=NAVY)
    notes_ax.text(0.0, 0.58, f"Terminal growth: {result.inputs.terminal_growth_rate * 100:.2f}%", fontsize=10, color=NAVY)
    notes_ax.text(0.0, 0.48, f"Projection years: {result.inputs.projection_years}", fontsize=10, color=NAVY)
    notes_ax.text(0.0, 0.30, "Data policy", fontsize=12, color=NAVY, fontweight="bold")
    notes_ax.text(
        0.0,
        0.12,
        "Public yfinance data only.\nNo API keys.\nNo saved user inputs.",
        fontsize=10,
        color=MGRAY,
        linespacing=1.5,
    )

    footer_ax = figure.add_axes([0, 0, 1, 0.05])
    _footer(footer_ax, snapshot.ticker)
    pdf.savefig(figure, bbox_inches="tight")
    plt.close(figure)

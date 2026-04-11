from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from dcf_model import (
    CompanyFinancialSnapshot,
    DCFInputs,
    build_default_inputs,
    build_sensitivity_heatmap,
    build_summary_table,
    create_pitch_pdf_bytes,
    fetch_company_snapshot,
    format_money,
    run_dcf,
)
from generate_pitches import GOLD, GREEN, LGRAY, NAVY, RED, WHITE


st.set_page_config(
    page_title="StockPitch Live DCF Demo",
    page_icon="SP",
    layout="wide",
)


def inject_styles() -> None:
    st.markdown(
        f"""
        <style>
        :root {{
            --navy: {NAVY};
            --gold: {GOLD};
            --green: {GREEN};
            --red: {RED};
            --paper: {WHITE};
            --mist: {LGRAY};
        }}
        .stApp {{
            background:
                radial-gradient(circle at top left, rgba(201,168,76,0.18), transparent 35%),
                linear-gradient(180deg, #f8f5ee 0%, #eef3f8 100%);
        }}
        .hero {{
            padding: 2rem 2.2rem;
            border-radius: 24px;
            background: linear-gradient(135deg, #08182d 0%, #143459 65%, #27516a 100%);
            color: white;
            box-shadow: 0 18px 45px rgba(11, 31, 58, 0.16);
            margin-bottom: 1.25rem;
        }}
        .hero h1 {{
            margin: 0;
            font-size: 2.4rem;
            font-family: "Avenir Next", "Segoe UI", sans-serif;
            letter-spacing: -0.04em;
        }}
        .hero p {{
            margin: 0.85rem 0 0;
            max-width: 60rem;
            color: rgba(255, 255, 255, 0.82);
            font-size: 1.02rem;
            line-height: 1.6;
        }}
        .badge-row {{
            display: flex;
            gap: 0.65rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }}
        .pill {{
            display: inline-flex;
            align-items: center;
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}
        .pill-demo {{
            color: #08182d;
            background: #f4e1a1;
        }}
        .pill-safe {{
            color: white;
            background: rgba(255,255,255,0.16);
            border: 1px solid rgba(255,255,255,0.18);
        }}
        .section-label {{
            margin-top: 0.25rem;
            color: #526170;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=900, show_spinner=False)
def load_snapshot(ticker: str) -> CompanyFinancialSnapshot:
    return fetch_company_snapshot(ticker)


def initialize_sidebar_defaults(snapshot: CompanyFinancialSnapshot) -> None:
    defaults = build_default_inputs(snapshot)
    if st.session_state.get("_defaults_for_ticker") == snapshot.ticker:
        return

    st.session_state["_defaults_for_ticker"] = snapshot.ticker
    st.session_state["growth_input"] = round(defaults.revenue_growth_rate * 100, 2)
    st.session_state["wacc_input"] = round(defaults.wacc * 100, 2)
    st.session_state["terminal_growth_input"] = round(defaults.terminal_growth_rate * 100, 2)
    st.session_state["projection_years_input"] = defaults.projection_years


def reset_sidebar_defaults(snapshot: CompanyFinancialSnapshot) -> None:
    defaults = build_default_inputs(snapshot)
    st.session_state["growth_input"] = round(defaults.revenue_growth_rate * 100, 2)
    st.session_state["wacc_input"] = round(defaults.wacc * 100, 2)
    st.session_state["terminal_growth_input"] = round(defaults.terminal_growth_rate * 100, 2)
    st.session_state["projection_years_input"] = defaults.projection_years


def build_sensitivity_axes(base_inputs: DCFInputs) -> tuple[np.ndarray, np.ndarray]:
    wacc_values = np.array(
        sorted(
            {
                round(max(0.03, base_inputs.wacc + delta), 4)
                for delta in (-0.02, -0.01, 0.0, 0.01, 0.02)
            }
        )
    )

    tgr_candidates = sorted(
        {
            round(base_inputs.terminal_growth_rate + delta, 4)
            for delta in (-0.01, -0.005, 0.0, 0.005, 0.01)
            if base_inputs.terminal_growth_rate + delta < base_inputs.wacc - 0.0025
        }
    )
    if len(tgr_candidates) < 3:
        floor = max(-0.02, base_inputs.terminal_growth_rate - 0.01)
        ceiling = base_inputs.wacc - 0.005
        tgr_candidates = list(np.round(np.linspace(floor, ceiling, 3), 4))
    terminal_growth_values = np.array(sorted(set(tgr_candidates)))
    return wacc_values, terminal_growth_values


def format_summary_for_display(summary_table: pd.DataFrame, snapshot: CompanyFinancialSnapshot) -> pd.DataFrame:
    formatted_rows = []
    money_metrics = {
        "Latest revenue",
        "Latest net income",
        "Latest free cash flow",
        "Net debt",
        "Enterprise value",
        "Equity value",
        "Intrinsic value / share",
        "Current price",
    }
    decimal_percent_metrics = {
        "Trailing FCF margin",
        "Revenue growth",
        "WACC",
        "Terminal growth",
    }

    for _, row in summary_table.iterrows():
        metric = row["Metric"]
        value = row["Value"]
        if metric in money_metrics:
            display_value = format_money(float(value), snapshot.currency)
        elif metric in decimal_percent_metrics:
            display_value = f"{float(value) * 100:,.2f}%"
        elif metric == "Upside / downside":
            display_value = f"{float(value):,.2f}%"
        elif metric == "Shares outstanding":
            display_value = f"{float(value):,.0f}"
        elif metric == "Projection years":
            display_value = f"{int(round(float(value)))}"
        else:
            display_value = f"{value}"
        formatted_rows.append({"Metric": metric, "Value": display_value})

    return pd.DataFrame(formatted_rows)


def render_heatmap(sensitivity: pd.DataFrame) -> plt.Figure:
    figure, axis = plt.subplots(figsize=(8.6, 4.8))
    image = axis.imshow(sensitivity.values, cmap="RdYlGn", aspect="auto")
    axis.set_xticks(range(len(sensitivity.columns)))
    axis.set_xticklabels([f"{value * 100:.1f}%" for value in sensitivity.columns])
    axis.set_yticks(range(len(sensitivity.index)))
    axis.set_yticklabels([f"{value * 100:.1f}%" for value in sensitivity.index])
    axis.set_xlabel("Terminal growth rate")
    axis.set_ylabel("WACC")
    axis.set_title("Upside / downside versus current price")

    for row_index in range(sensitivity.shape[0]):
        for column_index in range(sensitivity.shape[1]):
            cell_value = sensitivity.iat[row_index, column_index]
            label = "n/a" if pd.isna(cell_value) else f"{cell_value:+.0f}%"
            axis.text(column_index, row_index, label, ha="center", va="center", fontsize=9)

    figure.colorbar(image, ax=axis, fraction=0.046, pad=0.04)
    figure.tight_layout()
    return figure


def render_history_chart(snapshot: CompanyFinancialSnapshot) -> plt.Figure:
    history_frame = pd.concat(
        [
            snapshot.revenue_history.rename("Revenue"),
            snapshot.net_income_history.rename("Net income"),
            snapshot.free_cash_flow_history.rename("Free cash flow"),
        ],
        axis=1,
        join="inner",
    )
    history_frame.index = history_frame.index.year.astype(str)
    history_frame = history_frame / 1_000_000_000

    figure, axis = plt.subplots(figsize=(8.6, 4.6))
    history_frame.plot(kind="bar", ax=axis, color=[NAVY, GOLD, GREEN], width=0.68)
    axis.set_ylabel(f"Billions ({snapshot.currency})")
    axis.set_xlabel("Fiscal year")
    axis.set_title("Historical revenue, earnings, and free cash flow")
    axis.grid(axis="y", alpha=0.2)
    axis.legend(frameon=False)
    figure.tight_layout()
    return figure


def render_app() -> None:
    inject_styles()
    st.markdown(
        """
        <div class="hero">
          <div class="badge-row">
            <span class="pill pill-demo">Live Demo</span>
            <span class="pill pill-safe">Read-only and stateless</span>
            <span class="pill pill-safe">No API keys</span>
          </div>
          <h1>StockPitch Live DCF Demo</h1>
          <p>
            This app keeps the repo's PDF-first research feel, but swaps the hardcoded deck numbers
            for live public financial statements from yfinance. Enter a ticker, adjust the core DCF
            assumptions, review the valuation gap, inspect the WACC / terminal growth sensitivity,
            and export a clean PDF brief without storing any user data.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("## Inputs")
    ticker = st.sidebar.text_input("Ticker", value="MSFT", help="Public equity ticker symbol.").strip().upper()

    if not ticker:
        st.info("Enter a ticker in the sidebar to load live financial statements.")
        return

    try:
        with st.spinner(f"Loading live statements for {ticker}..."):
            snapshot = load_snapshot(ticker)
    except ValueError as exc:
        st.error(str(exc))
        return

    initialize_sidebar_defaults(snapshot)
    if st.sidebar.button("Reset to live defaults", use_container_width=True):
        reset_sidebar_defaults(snapshot)

    growth_input = st.sidebar.number_input(
        "Revenue growth rate (%)",
        min_value=-20.0,
        max_value=40.0,
        step=0.5,
        key="growth_input",
    )
    wacc_input = st.sidebar.number_input(
        "WACC (%)",
        min_value=3.0,
        max_value=25.0,
        step=0.25,
        key="wacc_input",
    )
    terminal_growth_input = st.sidebar.number_input(
        "Terminal growth rate (%)",
        min_value=-2.0,
        max_value=8.0,
        step=0.25,
        key="terminal_growth_input",
    )
    projection_years_input = st.sidebar.slider(
        "Projection years",
        min_value=3,
        max_value=10,
        key="projection_years_input",
    )

    inputs = DCFInputs(
        revenue_growth_rate=growth_input / 100.0,
        wacc=wacc_input / 100.0,
        terminal_growth_rate=terminal_growth_input / 100.0,
        projection_years=projection_years_input,
    )

    if inputs.wacc <= inputs.terminal_growth_rate:
        st.error("WACC must be greater than the terminal growth rate.")
        return

    try:
        result = run_dcf(snapshot, inputs)
    except ValueError as exc:
        st.error(str(exc))
        return

    wacc_values, terminal_growth_values = build_sensitivity_axes(inputs)
    sensitivity = build_sensitivity_heatmap(snapshot, inputs, wacc_values, terminal_growth_values)
    summary_table = build_summary_table(snapshot, result)
    summary_display = format_summary_for_display(summary_table, snapshot)
    pdf_bytes = create_pitch_pdf_bytes(snapshot, result, sensitivity)

    metric_columns = st.columns(4)
    metric_columns[0].metric("Current Price", format_money(snapshot.current_price, snapshot.currency))
    metric_columns[1].metric("Intrinsic Value", format_money(result.intrinsic_value_per_share, snapshot.currency))
    metric_columns[2].metric("Valuation Gap", f"{result.upside_pct:+.1f}%")
    metric_columns[3].metric("Trailing FCF Margin", f"{result.fcf_margin * 100:.2f}%")

    st.markdown('<div class="section-label">Valuation Summary</div>', unsafe_allow_html=True)
    summary_column, history_column = st.columns([0.95, 1.05])
    with summary_column:
        st.dataframe(summary_display, use_container_width=True, hide_index=True)
    with history_column:
        history_figure = render_history_chart(snapshot)
        st.pyplot(history_figure, use_container_width=True)
        plt.close(history_figure)

    detail_column, projection_column = st.columns([1.15, 1.0])
    with detail_column:
        st.markdown('<div class="section-label">Sensitivity</div>', unsafe_allow_html=True)
        heatmap_figure = render_heatmap(sensitivity)
        st.pyplot(heatmap_figure, use_container_width=True)
        plt.close(heatmap_figure)
    with projection_column:
        st.markdown('<div class="section-label">Projected Cash Flows</div>', unsafe_allow_html=True)
        projection_display = result.projection_table.copy()
        projection_display["projected_revenue"] = projection_display["projected_revenue"].map(
            lambda value: format_money(value, snapshot.currency)
        )
        projection_display["projected_fcf"] = projection_display["projected_fcf"].map(
            lambda value: format_money(value, snapshot.currency)
        )
        projection_display["discount_factor"] = projection_display["discount_factor"].map(
            lambda value: f"{value:.3f}"
        )
        projection_display["present_value_of_fcf"] = projection_display["present_value_of_fcf"].map(
            lambda value: format_money(value, snapshot.currency)
        )
        projection_display = projection_display.rename(
            columns={
                "label": "Year",
                "projected_revenue": "Revenue",
                "projected_fcf": "Free Cash Flow",
                "discount_factor": "Discount Factor",
                "present_value_of_fcf": "PV of FCF",
            }
        )
        st.dataframe(
            projection_display[["Year", "Revenue", "Free Cash Flow", "Discount Factor", "PV of FCF"]],
            use_container_width=True,
            hide_index=True,
        )

    if snapshot.latest_free_cash_flow < 0:
        st.warning(
            "The latest reported free cash flow is negative. The DCF output is still based on real yfinance data,"
            " but you should pressure-test the margin and terminal assumptions before relying on the result."
        )

    st.download_button(
        label="Download pitch PDF",
        data=pdf_bytes,
        file_name=f"{snapshot.ticker}_dcf_pitch.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
    st.caption(
        "Public yfinance data only. No API keys, no user uploads, and no saved user state beyond the current session."
    )


render_app()

"""
Stock Pitch Deck Generator
3 differentiated pitches across sectors for AM interviews
Uses matplotlib PdfPages — no extra dependencies needed
"""

import argparse
import csv
from dataclasses import dataclass
import json
import os
from typing import Dict, List

plt = None
mpatches = None
np = None
PdfPages = None
FancyBboxPatch = None

# ─── DESIGN SYSTEM ────────────────────────────────────────────────────────────

NAVY   = "#0B1F3A"
GOLD   = "#C9A84C"
WHITE  = "#FFFFFF"
LGRAY  = "#F4F5F7"
MGRAY  = "#8C97A8"
RED    = "#C0392B"
GREEN  = "#1A7A4A"
ORANGE = "#E67E22"
BLUE   = "#1A5276"

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
DECK_DATE_LABEL = "April 2026"
DEFAULT_AUDIENCE_LABEL = "For Interview Use Only"
DEFAULT_DESK_NAME = "Confidential Research"
DEFAULT_ANALYST = "Analyst Team"


@dataclass
class RenderProfile:
    deck_date: str = DECK_DATE_LABEL
    audience_label: str = DEFAULT_AUDIENCE_LABEL
    desk_name: str = DEFAULT_DESK_NAME
    analyst_name: str = DEFAULT_ANALYST


RENDER_PROFILE = RenderProfile()


@dataclass(frozen=True)
class PitchProfile:
    ticker: str
    pdf_basename: str
    name: str
    sector: str
    recommendation: str
    current_price: float
    target_price: float
    thesis: str
    playbook: str
    confidence: float
    catalyst_score: int
    downside_risk: int


# Scoring weights used for the quant signal layer:
#   confidence × catalyst_score / (1 + downside_risk) → expected payoff proxy
# These are rough approximations — not meant to be precise, just directional.
PITCH_PROFILES: Dict[str, PitchProfile] = {
    "PLTR": PitchProfile(
        ticker="PLTR",
        pdf_basename="PLTR_Short_Palantir",
        name="Palantir Technologies",
        sector="Technology",
        recommendation="SHORT",
        current_price=80.0,
        target_price=28.0,
        thesis=(
            "Valuation bubble (115x P/E), plateauing government growth, and"
            " weak commercial quality drive a likely de-rating."
        ),
        playbook="Valuation Compression",
        confidence=0.72,
        catalyst_score=8,
        downside_risk=7,
    ),
    "MEDP": PitchProfile(
        ticker="MEDP",
        pdf_basename="MEDP_Long_Medpace",
        name="Medpace Holdings",
        sector="Healthcare / CRO",
        recommendation="LONG",
        current_price=293.0,
        target_price=410.0,
        thesis=(
            "Founder-led CRO with high FCF conversion and margin leadership"
            " trading below slower peers."
        ),
        playbook="Quality Compounder Re-Rating",
        confidence=0.77,
        catalyst_score=7,
        downside_risk=5,
    ),
    "DDS": PitchProfile(
        ticker="DDS",
        pdf_basename="DDS_Long_Dillards",
        name="Dillard's Inc.",
        sector="Consumer / Real Estate",
        recommendation="LONG",
        current_price=333.0,
        target_price=450.0,
        thesis=(
            "Aggressive buybacks, owned real-estate optionality, and underfollowed"
            " fundamentals create durable upside."
        ),
        playbook="Capital Allocation + Asset Value",
        confidence=0.74,
        catalyst_score=8,
        downside_risk=6,
    ),
}


def ensure_plotting_dependencies() -> None:
    global plt, mpatches, np, PdfPages, FancyBboxPatch
    if plt is not None:
        return

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.patches as matplotlib_patches
        import matplotlib.pyplot as pyplot
        import numpy as numpy
        from matplotlib.backends.backend_pdf import PdfPages as pdf_pages_class
        from matplotlib.patches import FancyBboxPatch as fancy_bbox_patch
    except ModuleNotFoundError as exc:
        missing = str(exc).split("'")[1] if "'" in str(exc) else str(exc)
        raise SystemExit(
            "Missing plotting dependency "
            f"`{missing}`. Install with `pip install -r requirements.txt`."
        ) from exc

    plt = pyplot
    mpatches = matplotlib_patches
    np = numpy
    PdfPages = pdf_pages_class
    FancyBboxPatch = fancy_bbox_patch


def set_render_profile(args) -> None:
    global RENDER_PROFILE
    RENDER_PROFILE = RenderProfile(
        deck_date=args.deck_date.strip() or DECK_DATE_LABEL,
        audience_label=args.audience_label.strip() or DEFAULT_AUDIENCE_LABEL,
        desk_name=args.desk_name.strip() or DEFAULT_DESK_NAME,
        analyst_name=args.analyst_name.strip() or DEFAULT_ANALYST,
    )


def cover_stamp_text() -> str:
    return (
        f"{RENDER_PROFILE.desk_name}  ·  {RENDER_PROFILE.deck_date}  ·  "
        f"{RENDER_PROFILE.audience_label}"
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate stock pitch PDFs and a quant-ranked combined deck."
    )
    parser.add_argument(
        "--tickers",
        default=",".join(PITCH_PROFILES.keys()),
        help="Comma-separated tickers to include (default: all).",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where PDFs/CSV are written.",
    )
    parser.add_argument(
        "--combined-name",
        default="StockPitches_Combined.pdf",
        help="Filename for the combined PDF deck.",
    )
    parser.add_argument(
        "--combined-only",
        action="store_true",
        help="Only produce the combined deck (skip individual pitch PDFs).",
    )
    parser.add_argument(
        "--export-csv",
        action="store_true",
        help="Export a CSV with the generated signal metrics.",
    )
    parser.add_argument(
        "--export-json",
        action="store_true",
        help="Export a JSON file with the generated signal metrics.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only compute and print ranked metrics (skip PDF rendering).",
    )
    parser.add_argument(
        "--deck-date",
        default=DECK_DATE_LABEL,
        help="Deck date label shown on covers and summary slide.",
    )
    parser.add_argument(
        "--audience-label",
        default=DEFAULT_AUDIENCE_LABEL,
        help="Audience label appended on covers (example: For IC Review Only).",
    )
    parser.add_argument(
        "--desk-name",
        default=DEFAULT_DESK_NAME,
        help="Desk or organization name shown in footer and cover stamps.",
    )
    parser.add_argument(
        "--analyst-name",
        default=DEFAULT_ANALYST,
        help="Analyst name shown in footer and exported memo.",
    )
    parser.add_argument(
        "--export-memo",
        action="store_true",
        help="Export a PM-style markdown investment memo.",
    )
    return parser.parse_args()


def normalize_tickers(raw_tickers: str) -> List[str]:
    tickers = [ticker.strip().upper() for ticker in raw_tickers.split(",") if ticker.strip()]
    if not tickers:
        raise ValueError("No tickers provided. Use --tickers PLTR,MEDP,DDS.")

    invalid = sorted(set(tickers) - set(PITCH_PROFILES))
    if invalid:
        valid = ", ".join(sorted(PITCH_PROFILES))
        raise ValueError(
            f"Unsupported ticker(s): {', '.join(invalid)}. Valid options: {valid}"
        )

    deduped = []
    seen = set()
    for ticker in tickers:
        if ticker not in seen:
            deduped.append(ticker)
            seen.add(ticker)
    return deduped


def format_currency(value: float) -> str:
    return f"${value:,.0f}"


def target_move_pct(profile: PitchProfile) -> float:
    if profile.recommendation == "SHORT":
        return ((profile.current_price - profile.target_price) / profile.current_price) * 100
    return ((profile.target_price - profile.current_price) / profile.current_price) * 100


def build_pitch_metrics(profile: PitchProfile) -> Dict[str, float]:
    expected_return_pct = target_move_pct(profile)
    confidence_pct = profile.confidence * 100
    asymmetry_ratio = expected_return_pct / max(10.0, profile.downside_risk * 4.0)
    conviction_score = (
        expected_return_pct * 0.45
        + confidence_pct * 0.30
        + profile.catalyst_score * 10 * 0.15
        + (11 - profile.downside_risk) * 10 * 0.10
    )
    conviction_score = max(0.0, min(100.0, conviction_score))
    return {
        "ticker": profile.ticker,
        "name": profile.name,
        "sector": profile.sector,
        "recommendation": profile.recommendation,
        "price": profile.current_price,
        "target": profile.target_price,
        "expected_return_pct": expected_return_pct,
        "thesis": profile.thesis,
        "playbook": profile.playbook,
        "confidence_pct": confidence_pct,
        "catalyst_score": float(profile.catalyst_score),
        "downside_risk": float(profile.downside_risk),
        "asymmetry_ratio": asymmetry_ratio,
        "conviction_score": conviction_score,
    }


def build_portfolio_metrics(selected_tickers: List[str]) -> List[Dict[str, float]]:
    metrics = [build_pitch_metrics(PITCH_PROFILES[ticker]) for ticker in selected_tickers]
    metrics.sort(key=lambda metric: metric["conviction_score"], reverse=True)
    for rank, metric in enumerate(metrics, start=1):
        metric["rank"] = float(rank)
    return metrics


def recommendation_color(recommendation: str) -> str:
    return GREEN if recommendation == "LONG" else RED


def portfolio_construction_note(metrics: List[Dict[str, float]]) -> str:
    if not metrics:
        return "No ideas selected."

    gross_expected = sum(metric["expected_return_pct"] for metric in metrics) / len(metrics)
    short_count = sum(metric["recommendation"] == "SHORT" for metric in metrics)
    long_count = len(metrics) - short_count
    short_carry_drag = short_count * 2.0
    net_expected = gross_expected - short_carry_drag
    avg_confidence = sum(metric["confidence_pct"] for metric in metrics) / len(metrics)
    top_idea = max(metrics, key=lambda metric: metric["conviction_score"])

    return (
        f"Equal-weighted {long_count} long / {short_count} short basket with "
        f"{gross_expected:.1f}% average gross target move and ~{net_expected:.1f}% "
        f"net after short-carry haircut. Average confidence {avg_confidence:.0f}%. "
        f"Top-ranked signal: {top_idea['ticker']} ({top_idea['playbook']})."
    )


def export_metrics_csv(metrics: List[Dict[str, float]], output_dir: str) -> str:
    csv_path = os.path.join(output_dir, "PitchSignalMetrics.csv")
    fieldnames = [
        "rank",
        "ticker",
        "recommendation",
        "name",
        "sector",
        "price",
        "target",
        "expected_return_pct",
        "confidence_pct",
        "asymmetry_ratio",
        "conviction_score",
        "catalyst_score",
        "downside_risk",
        "playbook",
        "thesis",
    ]
    with open(csv_path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for metric in metrics:
            writer.writerow(metric)
    return csv_path


def export_metrics_json(metrics: List[Dict[str, float]], output_dir: str) -> str:
    json_path = os.path.join(output_dir, "PitchSignalMetrics.json")
    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(metrics, json_file, indent=2)
    return json_path


def print_ranked_metrics(metrics: List[Dict[str, float]]) -> None:
    print("\nRanked signal view:")
    for metric in metrics:
        print(
            f"  #{int(metric['rank'])} {metric['ticker']:4s} "
            f"{metric['recommendation']:5s} | "
            f"payoff {metric['expected_return_pct']:>5.1f}% | "
            f"conviction {metric['conviction_score']:>5.1f} | "
            f"confidence {metric['confidence_pct']:>5.1f}%"
        )

    print(f"\n{portfolio_construction_note(metrics)}")


def suggested_weights(metrics: List[Dict[str, float]]) -> List[Dict[str, float]]:
    weighted_metrics = []
    score_sum = sum(
        metric["conviction_score"] * (metric["confidence_pct"] / 100.0)
        for metric in metrics
    )
    if score_sum <= 0:
        score_sum = len(metrics)

    for metric in metrics:
        raw = metric["conviction_score"] * (metric["confidence_pct"] / 100.0)
        weight = (raw / score_sum) * 100.0
        weighted_metric = dict(metric)
        weighted_metric["suggested_weight_pct"] = weight
        weighted_metric["entry_range"] = (
            f"{format_currency(metric['price'] * 0.97)} - {format_currency(metric['price'] * 1.03)}"
        )
        weighted_metric["stop_rule"] = (
            "Cover +12% above entry" if metric["recommendation"] == "SHORT"
            else "Cut -12% below entry"
        )
        weighted_metrics.append(weighted_metric)

    return weighted_metrics


def portfolio_action_brief(metrics: List[Dict[str, float]]) -> List[str]:
    weighted = suggested_weights(metrics)
    strongest = max(weighted, key=lambda metric: metric["conviction_score"])
    median_confidence = sorted(metric["confidence_pct"] for metric in weighted)[len(weighted) // 2]
    short_count = sum(metric["recommendation"] == "SHORT" for metric in weighted)
    long_count = len(weighted) - short_count

    lines = [
        f"Lead with {strongest['ticker']} as the anchor idea "
        f"({strongest['conviction_score']:.0f} conviction score).",
        f"Portfolio posture: {long_count} long / {short_count} short with median "
        f"{median_confidence:.0f}% confidence across ideas.",
        "Enter in tiers over 3 sessions; keep first tranche at half size until"
        " the first catalyst confirms direction.",
    ]
    return lines


def export_memo_markdown(metrics: List[Dict[str, float]], output_dir: str) -> str:
    memo_path = os.path.join(output_dir, "PortfolioManagerMemo.md")
    weighted = suggested_weights(metrics)
    brief_lines = portfolio_action_brief(metrics)
    gross_target_move = sum(metric["expected_return_pct"] for metric in metrics) / len(metrics)

    lines = [
        "# Portfolio Manager Brief",
        "",
        f"- Prepared by: {RENDER_PROFILE.analyst_name}",
        f"- Desk: {RENDER_PROFILE.desk_name}",
        f"- Date: {RENDER_PROFILE.deck_date}",
        "",
        "## Why this basket",
        (
            f"This slate mixes valuation compression and quality compounders with an "
            f"average target move of {gross_target_move:.1f}%. Ideas are ranked by a"
            " blended conviction model (payoff, catalysts, confidence, and risk)."
        ),
        "",
        "## Action brief",
    ]
    for line in brief_lines:
        lines.append(f"- {line}")

    lines.extend(["", "## Position plan"])
    for metric in weighted:
        lines.extend(
            [
                f"### {metric['ticker']} ({metric['recommendation']})",
                f"- Suggested weight: {metric['suggested_weight_pct']:.1f}%",
                f"- Entry range: {metric['entry_range']}",
                f"- Stop rule: {metric['stop_rule']}",
                f"- Thesis: {metric['thesis']}",
                "",
            ]
        )

    with open(memo_path, "w", encoding="utf-8") as memo_file:
        memo_file.write("\n".join(lines))
    return memo_path


def new_fig():
    fig = plt.figure(figsize=(13.33, 7.5))  # 16:9 widescreen
    fig.patch.set_facecolor(WHITE)
    return fig

def navy_header(fig, title, subtitle="", tag="", tag_color=RED):
    """Full-width navy header bar."""
    ax = fig.add_axes([0, 0.82, 1, 0.18])
    ax.set_facecolor(NAVY)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis('off')
    ax.text(0.04, 0.62, title, color=WHITE, fontsize=22, fontweight='bold',
            va='center', ha='left', fontfamily='DejaVu Sans')
    if subtitle:
        ax.text(0.04, 0.22, subtitle, color=GOLD, fontsize=11,
                va='center', ha='left')
    if tag:
        ax.add_patch(FancyBboxPatch((0.78, 0.25), 0.18, 0.50,
                                    boxstyle="round,pad=0.02",
                                    fc=tag_color, ec='none'))
        ax.text(0.87, 0.50, tag, color=WHITE, fontsize=14, fontweight='bold',
                va='center', ha='center')
    # gold rule
    ax.axhline(0, color=GOLD, linewidth=2.5)

def footer(fig, ticker, page):
    ax = fig.add_axes([0, 0, 1, 0.04])
    ax.set_facecolor(NAVY)
    ax.axis('off')
    ax.text(0.04, 0.5, f"{ticker} — {RENDER_PROFILE.desk_name}", color=MGRAY,
            fontsize=7, va='center')
    ax.text(0.50, 0.5, f"Prepared by {RENDER_PROFILE.analyst_name}", color=MGRAY,
            fontsize=7, va='center', ha='center')
    ax.text(0.96, 0.5, f"Page {page}", color=MGRAY, fontsize=7,
            va='center', ha='right')

def kpi_box(ax, x, y, w, h, label, value, sub="", color=NAVY):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.015",
                                fc=color, ec='none'))
    ax.text(x + w/2, y + h*0.72, value, color=WHITE,
            fontsize=16, fontweight='bold', ha='center', va='center')
    ax.text(x + w/2, y + h*0.35, label, color=GOLD,
            fontsize=8, ha='center', va='center')
    if sub:
        ax.text(x + w/2, y + h*0.12, sub, color=MGRAY,
                fontsize=7, ha='center', va='center')

def bullet_section(ax, x, y, title, bullets, title_color=NAVY, bullet_color="#2C3E50", spacing=0.072):
    ax.text(x, y, title, fontsize=11, fontweight='bold', color=title_color,
            transform=ax.transAxes)
    for i, b in enumerate(bullets):
        ax.text(x + 0.015, y - spacing*(i+1), f"▸  {b}",
                fontsize=9, color=bullet_color, transform=ax.transAxes,
                wrap=True)

# ─── PITCH 1: SHORT PALANTIR ──────────────────────────────────────────────────

def pitch_pltr(pdf):

    # --- SLIDE 1: COVER ---
    fig = new_fig()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(NAVY); ax.axis('off')
    ax.text(0.5, 0.80, "PALANTIR TECHNOLOGIES", color=WHITE,
            fontsize=30, fontweight='bold', ha='center', va='center')
    ax.text(0.5, 0.68, "PLTR  |  NYSE  |  Technology / AI Software", color=GOLD,
            fontsize=14, ha='center', va='center')

    ax.add_patch(FancyBboxPatch((0.32, 0.50), 0.36, 0.10,
                                boxstyle="round,pad=0.02", fc=RED, ec='none'))
    ax.text(0.50, 0.555, "SHORT  ·  TARGET: $28  ·  ~65% DOWNSIDE",
            color=WHITE, fontsize=13, fontweight='bold', ha='center', va='center')

    ax.text(0.5, 0.36, "Thesis: A momentum-driven valuation bubble disconnected from\n"
            "fundamental economics in a commoditizing AI market.",
            color=LGRAY, fontsize=11, ha='center', va='center', linespacing=1.6)

    ax.text(0.5, 0.10, cover_stamp_text(), color=MGRAY, fontsize=9, ha='center')
    pdf.savefig(fig, bbox_inches='tight'); plt.close()

    # --- SLIDE 2: SNAPSHOT & THESIS ---
    fig = new_fig()
    navy_header(fig, "Investment Snapshot", "PLTR — Short Thesis Overview", "SHORT", RED)
    footer(fig, "PLTR", 2)

    ax = fig.add_axes([0.03, 0.10, 0.94, 0.68])
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')

    # KPI row
    kpis = [
        ("Current Price",  "~$80",    "Apr 2026"),
        ("Price Target",   "$28",     "12-month"),
        ("Upside / (Down)","-65%",    "to target"),
        ("NTM P/E",        "115x",    "vs. SaaS @ 30x"),
        ("NTM EV/Rev",     "42x",     "vs. SaaS @ 8x"),
        ("Insider Sales",  "$2.1B+",  "TTM, CEO & founders"),
    ]
    for i, (lbl, val, sub) in enumerate(kpis):
        col = RED if "Down" in lbl or "115" in val or "42x" in val or "2.1" in val else NAVY
        kpi_box(ax, 0.01 + i*0.165, 0.72, 0.15, 0.24, lbl, val, sub, col)

    # Thesis pillars
    pillars = [
        ("① VALUATION ABSURDITY",
         ["115x NTM P/E and 42x EV/Rev are > 3x premium to best-in-class SaaS peers",
          "At consensus long-term growth (20%), PLTR needs 50%+ EBIT margins to justify price",
          "Current GAAP margins are ~14%; even Palantir's own targets imply < $2.50 EPS by FY28"]),
        ("② GOVERNMENT REVENUE IS ZERO-SUM",
         ["US Gov revenue +3% YoY in 2025 — defense budgets are fixed pools, not expanding TAM",
          "Large contracts (TDA, TITAN) are multi-year; incremental ACV growth is decelerating",
          "Legacy C2/analytical tools face DoD modernization pressure from AWS GovCloud, Snowflake"]),
        ("③ COMMERCIAL GROWTH IS MISLEADING",
         ["'AIP Boot Camps' inflate US commercial customer count with non-revenue-bearing pilots",
          "Net Dollar Retention drifted from 131% (2022) to ~108% (2025) — expansion is slowing",
          "International commercial revenue flat for 6 consecutive quarters"]),
        ("④ STRUCTURAL DILUTION",
         ["SBC is ~27% of revenue; GAAP EPS depressed far below adjusted figures",
          "Founders retain super-voting shares; no credible capital return framework",
          "Float expansion via ongoing employee equity awards will pressure price over time"]),
    ]
    xs = [0.0, 0.50, 0.0, 0.50]
    ys = [0.58, 0.58, 0.12, 0.12]
    for (ttl, buls), x, y in zip(pillars, xs, ys):
        ax.add_patch(FancyBboxPatch((x+0.01, y), 0.46, 0.40,
                                    boxstyle="round,pad=0.015", fc=LGRAY, ec=NAVY, lw=0.5))
        bullet_section(ax, x+0.03, y+0.37, ttl, buls,
                       title_color=RED, bullet_color="#2C3E50", spacing=0.095)
    pdf.savefig(fig, bbox_inches='tight'); plt.close()

    # --- SLIDE 3: CATALYSTS & RISKS ---
    fig = new_fig()
    navy_header(fig, "Catalysts & Key Risks", "PLTR — Path to Thesis Realization", "SHORT", RED)
    footer(fig, "PLTR", 3)

    ax = fig.add_axes([0.03, 0.10, 0.94, 0.68])
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')

    # Catalysts
    ax.add_patch(FancyBboxPatch((0.01, 0.01), 0.46, 0.94,
                                boxstyle="round,pad=0.015", fc="#FEF9F0", ec=RED, lw=1))
    ax.text(0.24, 0.92, "NEAR-TERM CATALYSTS (0–12 mo)", fontsize=10,
            fontweight='bold', color=RED, ha='center', transform=ax.transAxes)

    cats = [
        ("Q2/Q3 2026 Earnings",  "Boot-camp customer churn becomes visible; NRR continues slide"),
        ("DoD Budget Reconciliation", "CR-constrained Pentagon delays incremental PLTR awards"),
        ("AI Commoditization",   "Open-source LLMs (Llama 4, Mistral) erode PLTR's AI wedge pitch"),
        ("Insider Lockup Lapses","Karp & Thiel have unloaded $2B+ via 10b5-1; more to come"),
        ("S&P 500 Rebalancing",  "Any weight reduction triggers passive selling pressure"),
    ]
    for i, (c_title, c_body) in enumerate(cats):
        y = 0.80 - i*0.155
        ax.add_patch(FancyBboxPatch((0.03, y-0.04), 0.42, 0.125,
                                    boxstyle="round,pad=0.01", fc=WHITE, ec=RED, lw=0.4))
        ax.text(0.05, y+0.045, c_title, fontsize=9, fontweight='bold',
                color=RED, transform=ax.transAxes)
        ax.text(0.05, y-0.01, c_body, fontsize=8, color="#2C3E50",
                transform=ax.transAxes, wrap=True)

    # Risks to thesis (right)
    ax.add_patch(FancyBboxPatch((0.53, 0.01), 0.46, 0.94,
                                boxstyle="round,pad=0.015", fc="#F0F4F8", ec=NAVY, lw=1))
    ax.text(0.76, 0.92, "RISKS TO SHORT THESIS", fontsize=10,
            fontweight='bold', color=NAVY, ha='center', transform=ax.transAxes)

    risks = [
        ("AI Supercycle Narrative", "MEDIUM",
         "Continued hype cycle could keep multiple elevated; sentiment matters more than fundamentals short-term"),
        ("Large Government Win",    "MEDIUM",
         "TITAN expansion or new DoD AI program could reaccelerate gov revenue growth"),
        ("Acquisition Premium",     "LOW",
         "Strategic buyer (defense prime, Big Tech) could pay 50–60x EV/Rev; low probability but non-zero"),
        ("Short Squeeze",           "HIGH",
         "35%+ short interest; any positive catalyst could trigger violent squeeze — size accordingly"),
    ]
    risk_colors = {
        "HIGH": RED, "MEDIUM": ORANGE, "LOW": GREEN
    }
    for i, (r_title, severity, r_body) in enumerate(risks):
        y = 0.80 - i*0.185
        rc = risk_colors[severity]
        ax.add_patch(FancyBboxPatch((0.55, y-0.055), 0.42, 0.145,
                                    boxstyle="round,pad=0.01", fc=WHITE, ec=rc, lw=0.8))
        ax.text(0.57, y+0.055, r_title, fontsize=9, fontweight='bold',
                color=NAVY, transform=ax.transAxes)
        ax.add_patch(FancyBboxPatch((0.79, y+0.03), 0.08, 0.055,
                                    boxstyle="round,pad=0.01", fc=rc, ec='none'))
        ax.text(0.83, y+0.057, severity, fontsize=7, fontweight='bold',
                color=WHITE, ha='center', transform=ax.transAxes)
        ax.text(0.57, y-0.025, r_body, fontsize=7.5, color="#4A4A4A",
                transform=ax.transAxes, wrap=True)

    pdf.savefig(fig, bbox_inches='tight'); plt.close()

    # --- SLIDE 4: DCF MODEL ---
    fig = new_fig()
    navy_header(fig, "Valuation — DCF & Scenario Analysis", "PLTR — Bear Case Drives $28 Target", "SHORT", RED)
    footer(fig, "PLTR", 4)

    ax = fig.add_axes([0.03, 0.08, 0.94, 0.70])
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')

    # DCF table
    years = ["FY25A", "FY26E", "FY27E", "FY28E", "FY29E", "FY30E", "Terminal"]
    rows = {
        "Revenue ($M)":       ["3,465", "4,020", "4,740", "5,450", "6,100", "6,710", "—"],
        "Rev Growth":         ["29%",   "16%",   "18%",   "15%",   "12%",   "10%",   "—"],
        "EBIT Margin (GAAP)": ["14%",   "16%",   "18%",   "20%",   "22%",   "24%",   "—"],
        "EBIT ($M)":          ["485",   "643",   "853",   "1,090", "1,342", "1,610", "—"],
        "NOPAT ($M)":         ["364",   "483",   "640",   "818",   "1,007", "1,208", "—"],
        "FCF ($M)":           ["320",   "430",   "580",   "750",   "940",   "1,150", "—"],
        "Discount Factor":    ["—",     "0.92",  "0.84",  "0.77",  "0.71",  "0.65",  "—"],
        "PV of FCF ($M)":     ["—",     "396",   "487",   "578",   "667",   "748",   "—"],
    }

    col_w = 0.118
    col_xs = [0.01 + i*col_w for i in range(7)]

    # Header row
    for j, yr in enumerate(years):
        color = GOLD if yr == "Terminal" else (NAVY if "A" not in yr else BLUE)
        ax.add_patch(FancyBboxPatch((col_xs[j], 0.87), col_w-0.005, 0.07,
                                    boxstyle="square,pad=0", fc=NAVY, ec='none'))
        ax.text(col_xs[j] + (col_w-0.005)/2, 0.905, yr, fontsize=8.5,
                fontweight='bold', color=GOLD if yr == "FY25A" else WHITE,
                ha='center', transform=ax.transAxes)

    row_ys = np.linspace(0.79, 0.14, len(rows))
    for ri, (rname, vals) in enumerate(rows.items()):
        y = row_ys[ri]
        bg = LGRAY if ri % 2 == 0 else WHITE
        ax.add_patch(FancyBboxPatch((-0.01, y-0.01), 1.02, 0.075,
                                    boxstyle="square,pad=0", fc=bg, ec='none'))
        for j, v in enumerate(vals):
            ax.text(col_xs[j] + (col_w-0.005)/2, y+0.025, v, fontsize=8,
                    ha='center', color=NAVY if v != "—" else MGRAY,
                    transform=ax.transAxes)
        # row label (leftmost)
        ax.text(-0.005, y+0.025, rname, fontsize=7.5, color=NAVY,
                fontweight='bold', transform=ax.transAxes)

    # Scenario summary boxes
    scenarios = [
        ("BEAR CASE",  "$28",  "10% rev CAGR, 20% EBIT margin,\nWACC 12%, TGR 2%",   RED),
        ("BASE CASE",  "$52",  "15% rev CAGR, 25% EBIT margin,\nWACC 11%, TGR 2.5%", ORANGE),
        ("BULL CASE",  "$85",  "20% rev CAGR, 30% EBIT margin,\nWACC 10%, TGR 3%",   GREEN),
    ]
    for i, (sc, pt, assum, col) in enumerate(scenarios):
        x = 0.01 + i*0.34
        ax.add_patch(FancyBboxPatch((x, -0.02), 0.30, 0.115,
                                    boxstyle="round,pad=0.015", fc=col, ec='none'))
        ax.text(x+0.15, 0.075, sc, fontsize=9, fontweight='bold', color=WHITE,
                ha='center', transform=ax.transAxes)
        ax.text(x+0.15, 0.040, pt, fontsize=14, fontweight='bold', color=WHITE,
                ha='center', transform=ax.transAxes)
        ax.text(x+0.15, 0.005, assum, fontsize=7, color=WHITE,
                ha='center', transform=ax.transAxes, linespacing=1.4)

    # assumptions box
    ax.text(0.70, 0.06, "Key DCF Assumptions\n"
            "• WACC: 11%  • TGR: 2.5%  • Tax Rate: 25%\n"
            "• Shares: 2.17B  • Net Cash: $4.2B\n"
            "• SBC excluded from FCF (GAAP basis)",
            fontsize=7.5, color=NAVY, transform=ax.transAxes,
            bbox=dict(fc=LGRAY, ec=NAVY, lw=0.5, boxstyle='round,pad=0.5'),
            linespacing=1.5)

    pdf.savefig(fig, bbox_inches='tight'); plt.close()


# ─── PITCH 2: LONG MEDPACE HOLDINGS ──────────────────────────────────────────

def pitch_medp(pdf):

    # --- SLIDE 1: COVER ---
    fig = new_fig()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(NAVY); ax.axis('off')
    ax.text(0.5, 0.80, "MEDPACE HOLDINGS", color=WHITE,
            fontsize=30, fontweight='bold', ha='center')
    ax.text(0.5, 0.68, "MEDP  |  NASDAQ  |  Healthcare — Contract Research Organization",
            color=GOLD, fontsize=14, ha='center')
    ax.add_patch(FancyBboxPatch((0.32, 0.50), 0.36, 0.10,
                                boxstyle="round,pad=0.02", fc=GREEN, ec='none'))
    ax.text(0.50, 0.555, "LONG  ·  TARGET: $410  ·  ~40% UPSIDE",
            color=WHITE, fontsize=13, fontweight='bold', ha='center', va='center')
    ax.text(0.5, 0.36,
            "Thesis: A founder-led, best-in-class CRO compounding FCF at 20%+\n"
            "with a durable competitive moat, trading at an unwarranted discount to peers.",
            color=LGRAY, fontsize=11, ha='center', linespacing=1.6)
    ax.text(0.5, 0.10, cover_stamp_text(), color=MGRAY, fontsize=9, ha='center')
    pdf.savefig(fig, bbox_inches='tight'); plt.close()

    # --- SLIDE 2: SNAPSHOT & THESIS ---
    fig = new_fig()
    navy_header(fig, "Investment Snapshot", "MEDP — Long Thesis Overview", "LONG", GREEN)
    footer(fig, "MEDP", 2)

    ax = fig.add_axes([0.03, 0.10, 0.94, 0.68])
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')

    kpis = [
        ("Current Price",  "~$293",   "Apr 2026"),
        ("Price Target",   "$410",    "12-month"),
        ("Upside",         "+40%",    "to target"),
        ("NTM P/E",        "21x",     "IQVIA @ 28x"),
        ("FCF Yield",      "4.8%",    "vs. peer avg 2.1%"),
        ("Revenue CAGR",   "20%",     "3-yr trailing"),
    ]
    for i, (lbl, val, sub) in enumerate(kpis):
        col = GREEN if "410" in val or "+40" in val or "4.8" in val else NAVY
        kpi_box(ax, 0.01 + i*0.165, 0.72, 0.15, 0.24, lbl, val, sub, col)

    pillars = [
        ("① FOUNDER-ALIGNED, NICHE FOCUSED",
         ["CEO August Troendle founded MEDP in 1992; owns 40%+ of shares outstanding",
          "Pure-play on small/mid biotech CRO — deliberately avoided large pharma (lower margin)",
          "Therapeutic depth in oncology, cardio-metabolic, CNS drives repeat client relationships"]),
        ("② BIOTECH OUTSOURCING TAILWIND",
         ["Biotech funding recovering post-2022 trough; NIH grants + VC back to 2021 levels",
          "Small biotech outsources 80%+ of Phase I–III work; MEDP is top-3 preferred provider",
          "FDA PDUFA dates and IND approvals create visible near-term revenue catalysts"]),
        ("③ SUPERIOR UNIT ECONOMICS",
         ["EBITDA margins ~25% vs. IQVIA/Syneos ~18% — integrated model eliminates middlemen",
          "Asset-light: CapEx < 1.5% of revenue; converts ~90% of EBITDA to FCF",
          "Backlog $9.2B (3.5x TTM revenue), providing 18-month forward revenue visibility"]),
        ("④ VALUATION DISCOUNT UNWARRANTED",
         ["Trades at 21x NTM P/E vs. IQVIA 28x, Charles River 26x — 25–30% discount to peers",
          "Superior margins and growth profile should command premium, not discount",
          "No debt, $800M+ cash; management telegraphed buyback acceleration"]),
    ]
    xs = [0.0, 0.50, 0.0, 0.50]
    ys = [0.58, 0.58, 0.12, 0.12]
    for (ttl, buls), x, y in zip(pillars, xs, ys):
        ax.add_patch(FancyBboxPatch((x+0.01, y), 0.46, 0.40,
                                    boxstyle="round,pad=0.015", fc=LGRAY, ec=NAVY, lw=0.5))
        bullet_section(ax, x+0.03, y+0.37, ttl, buls,
                       title_color=GREEN, bullet_color="#2C3E50", spacing=0.095)
    pdf.savefig(fig, bbox_inches='tight'); plt.close()

    # --- SLIDE 3: CATALYSTS & RISKS ---
    fig = new_fig()
    navy_header(fig, "Catalysts & Key Risks", "MEDP — Path to Thesis Realization", "LONG", GREEN)
    footer(fig, "MEDP", 3)

    ax = fig.add_axes([0.03, 0.10, 0.94, 0.68])
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')

    ax.add_patch(FancyBboxPatch((0.01, 0.01), 0.46, 0.94,
                                boxstyle="round,pad=0.015", fc="#F0FAF4", ec=GREEN, lw=1))
    ax.text(0.24, 0.92, "NEAR-TERM CATALYSTS (0–18 mo)", fontsize=10,
            fontweight='bold', color=GREEN, ha='center', transform=ax.transAxes)

    cats = [
        ("Biotech Funding Recovery",  "VC/crossover funding back to $15B+ quarterly run rate; IND pipeline deepens"),
        ("Q2 2026 Earnings",          "Backlog growth should re-accelerate to 15%+ YoY after Q4 lull"),
        ("Share Buyback Announcement","Balance sheet has $800M+ dry powder; CEO hinted at accelerated repurchase"),
        ("Large Pharma Outsourcing",  "Eli Lilly, AZ GLP-1 wave driving Phase II/III overflow to CROs like MEDP"),
        ("Re-Rating to Peer Multiples","Close discount vs. IQVIA/CRL — 25x P/E alone = $360/share"),
    ]
    for i, (c_title, c_body) in enumerate(cats):
        y = 0.80 - i*0.155
        ax.add_patch(FancyBboxPatch((0.03, y-0.04), 0.42, 0.125,
                                    boxstyle="round,pad=0.01", fc=WHITE, ec=GREEN, lw=0.4))
        ax.text(0.05, y+0.045, c_title, fontsize=9, fontweight='bold',
                color=GREEN, transform=ax.transAxes)
        ax.text(0.05, y-0.01, c_body, fontsize=8, color="#2C3E50",
                transform=ax.transAxes)

    ax.add_patch(FancyBboxPatch((0.53, 0.01), 0.46, 0.94,
                                boxstyle="round,pad=0.015", fc="#F0F4F8", ec=NAVY, lw=1))
    ax.text(0.76, 0.92, "RISKS TO LONG THESIS", fontsize=10,
            fontweight='bold', color=NAVY, ha='center', transform=ax.transAxes)

    risks = [
        ("Client Concentration",    "MEDIUM",
         "Top 10 clients = ~50% revenue; loss of one large biotech sponsor impactful"),
        ("Biotech Funding Reversal", "MEDIUM",
         "Rising rates or risk-off environment could freeze small biotech budgets again"),
        ("Regulatory / FDA Delays",  "LOW",
         "Clinical hold or IND rejection on key client programs pushes out backlog conversion"),
        ("Competitive Pricing",      "LOW",
         "IQVIA/PPD winning bids at lower margin to gain market share in small biotech segment"),
    ]
    risk_colors = {"HIGH": RED, "MEDIUM": ORANGE, "LOW": GREEN}
    for i, (r_title, severity, r_body) in enumerate(risks):
        y = 0.80 - i*0.185
        rc = risk_colors[severity]
        ax.add_patch(FancyBboxPatch((0.55, y-0.055), 0.42, 0.145,
                                    boxstyle="round,pad=0.01", fc=WHITE, ec=rc, lw=0.8))
        ax.text(0.57, y+0.055, r_title, fontsize=9, fontweight='bold',
                color=NAVY, transform=ax.transAxes)
        ax.add_patch(FancyBboxPatch((0.79, y+0.03), 0.08, 0.055,
                                    boxstyle="round,pad=0.01", fc=rc, ec='none'))
        ax.text(0.83, y+0.057, severity, fontsize=7, fontweight='bold',
                color=WHITE, ha='center', transform=ax.transAxes)
        ax.text(0.57, y-0.025, r_body, fontsize=7.5, color="#4A4A4A",
                transform=ax.transAxes, wrap=True)

    pdf.savefig(fig, bbox_inches='tight'); plt.close()

    # --- SLIDE 4: DCF ---
    fig = new_fig()
    navy_header(fig, "Valuation — DCF & Comps", "MEDP — $410 Target, 40% Upside", "LONG", GREEN)
    footer(fig, "MEDP", 4)

    ax = fig.add_axes([0.03, 0.08, 0.94, 0.70])
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')

    years = ["FY25A", "FY26E", "FY27E", "FY28E", "FY29E", "FY30E", "Terminal"]
    rows = {
        "Revenue ($M)":        ["2,210", "2,650", "3,180", "3,720", "4,220", "4,640", "—"],
        "Rev Growth":          ["22%",   "20%",   "20%",   "17%",   "13%",   "10%",   "—"],
        "EBITDA Margin":       ["25%",   "26%",   "27%",   "28%",   "28%",   "29%",   "—"],
        "EBITDA ($M)":         ["553",   "689",   "859",   "1,042", "1,182", "1,346", "—"],
        "FCF ($M)":            ["490",   "610",   "765",   "930",   "1,055", "1,200", "—"],
        "Discount Factor":     ["—",     "0.93",  "0.86",  "0.80",  "0.74",  "0.69",  "—"],
        "PV of FCF ($M)":      ["—",     "567",   "658",   "744",   "781",   "828",   "—"],
    }

    col_w = 0.118
    col_xs = [0.01 + i*col_w for i in range(7)]
    for j, yr in enumerate(years):
        ax.add_patch(FancyBboxPatch((col_xs[j], 0.87), col_w-0.005, 0.07,
                                    boxstyle="square,pad=0", fc=NAVY, ec='none'))
        ax.text(col_xs[j] + (col_w-0.005)/2, 0.905, yr, fontsize=8.5,
                fontweight='bold', color=GOLD if yr == "FY25A" else WHITE,
                ha='center', transform=ax.transAxes)

    row_ys = np.linspace(0.79, 0.14, len(rows))
    for ri, (rname, vals) in enumerate(rows.items()):
        y = row_ys[ri]
        bg = LGRAY if ri % 2 == 0 else WHITE
        ax.add_patch(FancyBboxPatch((-0.01, y-0.01), 1.02, 0.075,
                                    boxstyle="square,pad=0", fc=bg, ec='none'))
        for j, v in enumerate(vals):
            ax.text(col_xs[j] + (col_w-0.005)/2, y+0.025, v, fontsize=8,
                    ha='center', color=NAVY if v != "—" else MGRAY,
                    transform=ax.transAxes)
        ax.text(-0.005, y+0.025, rname, fontsize=7.5, color=NAVY,
                fontweight='bold', transform=ax.transAxes)

    scenarios = [
        ("BEAR CASE",  "$280",  "15% CAGR, 24% EBITDA\nWACC 10%, TGR 2%",   RED),
        ("BASE CASE",  "$410",  "20% CAGR, 27% EBITDA\nWACC 9%,  TGR 2.5%", GREEN),
        ("BULL CASE",  "$520",  "22% CAGR, 29% EBITDA\nWACC 8.5%, TGR 3%",  BLUE),
    ]
    for i, (sc, pt, assum, col) in enumerate(scenarios):
        x = 0.01 + i*0.34
        ax.add_patch(FancyBboxPatch((x, -0.02), 0.30, 0.115,
                                    boxstyle="round,pad=0.015", fc=col, ec='none'))
        ax.text(x+0.15, 0.075, sc, fontsize=9, fontweight='bold', color=WHITE,
                ha='center', transform=ax.transAxes)
        ax.text(x+0.15, 0.040, pt, fontsize=14, fontweight='bold', color=WHITE,
                ha='center', transform=ax.transAxes)
        ax.text(x+0.15, 0.005, assum, fontsize=7, color=WHITE,
                ha='center', transform=ax.transAxes, linespacing=1.4)

    ax.text(0.70, 0.06, "Key DCF Assumptions\n"
            "• WACC: 9%  • TGR: 2.5%  • Tax Rate: 24%\n"
            "• Shares: 23.4M  • Net Cash: $820M\n"
            "• CapEx < 1.5% revenue (asset-light)",
            fontsize=7.5, color=NAVY, transform=ax.transAxes,
            bbox=dict(fc=LGRAY, ec=NAVY, lw=0.5, boxstyle='round,pad=0.5'),
            linespacing=1.5)

    pdf.savefig(fig, bbox_inches='tight'); plt.close()


# ─── PITCH 3: LONG DILLARD'S ─────────────────────────────────────────────────

def pitch_dds(pdf):

    # --- SLIDE 1: COVER ---
    fig = new_fig()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(NAVY); ax.axis('off')
    ax.text(0.5, 0.80, "DILLARD'S, INC.", color=WHITE,
            fontsize=30, fontweight='bold', ha='center')
    ax.text(0.5, 0.68, "DDS  |  NYSE  |  Consumer — Department Store / Real Estate",
            color=GOLD, fontsize=14, ha='center')
    ax.add_patch(FancyBboxPatch((0.32, 0.50), 0.36, 0.10,
                                boxstyle="round,pad=0.02", fc=GREEN, ec='none'))
    ax.text(0.50, 0.555, "LONG  ·  TARGET: $450  ·  ~35% UPSIDE",
            color=WHITE, fontsize=13, fontweight='bold', ha='center', va='center')
    ax.text(0.5, 0.36,
            "Thesis: The most aggressive capital allocator in retail, hiding in plain sight.\n"
            "Owns its real estate, has retired 85%+ of shares, and trades at 6x FCF.",
            color=LGRAY, fontsize=11, ha='center', linespacing=1.6)
    ax.text(0.5, 0.10, cover_stamp_text(), color=MGRAY, fontsize=9, ha='center')
    pdf.savefig(fig, bbox_inches='tight'); plt.close()

    # --- SLIDE 2: SNAPSHOT & THESIS ---
    fig = new_fig()
    navy_header(fig, "Investment Snapshot", "DDS — Long Thesis Overview", "LONG", GREEN)
    footer(fig, "DDS", 2)

    ax = fig.add_axes([0.03, 0.10, 0.94, 0.68])
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')

    kpis = [
        ("Current Price",  "~$333",   "Apr 2026"),
        ("Price Target",   "$450",    "12-month"),
        ("Upside",         "+35%",    "to target"),
        ("NTM P/E",        "8x",      "vs. TJX 24x"),
        ("FCF Yield",      "15%+",    "best in retail"),
        ("Shares Retired", "~85%",    "vs. 2012 peak"),
    ]
    for i, (lbl, val, sub) in enumerate(kpis):
        col = GREEN if "450" in val or "+35" in val or "15%" in val else NAVY
        kpi_box(ax, 0.01 + i*0.165, 0.72, 0.15, 0.24, lbl, val, sub, col)

    pillars = [
        ("① EXTRAORDINARY CAPITAL ALLOCATION",
         ["Share count reduced from ~58M (2012) to ~8M today — ~85% buyback; EPS explodes",
          "Annual buyback ~$500M–$700M on $2.7B market cap = > 20% of float retired per year",
          "At current pace, share count approaches zero within 4–5 years — terminal case study"]),
        ("② REAL ESTATE IS HIDDEN ASSET",
         ["Owns 90%+ of its 250 stores (fee-simple); estimated NAV $3–4B vs. $2.7B market cap",
          "Real estate value alone exceeds market cap — retail operation is effectively free",
          "Real estate monetization (sale-leaseback, REIT spin) = major unlocking event"]),
        ("③ MOAT IN UNDERSERVED MARKETS",
         ["Operates in Southeast/Southwest secondary cities with limited luxury competition",
          "Not competing with Amazon on commodity goods; curated private label + exclusive brands",
          "Loyalty program with 30M+ members drives 60%+ repeat purchase rate"]),
        ("④ MISUNDERSTOOD AS 'DYING RETAIL'",
         ["DDS has grown EPS from $4 (2019) to $30+ (2025) — up 7.5x in 6 years",
          "Inventory discipline keeps gross margins above 40% — higher than Nordstrom/Macy's",
          "Sell-side ignores; <5 analysts cover; institutional ownership low → re-rating opportunity"]),
    ]
    xs = [0.0, 0.50, 0.0, 0.50]
    ys = [0.58, 0.58, 0.12, 0.12]
    for (ttl, buls), x, y in zip(pillars, xs, ys):
        ax.add_patch(FancyBboxPatch((x+0.01, y), 0.46, 0.40,
                                    boxstyle="round,pad=0.015", fc=LGRAY, ec=NAVY, lw=0.5))
        bullet_section(ax, x+0.03, y+0.37, ttl, buls,
                       title_color=GREEN, bullet_color="#2C3E50", spacing=0.095)
    pdf.savefig(fig, bbox_inches='tight'); plt.close()

    # --- SLIDE 3: CATALYSTS & RISKS ---
    fig = new_fig()
    navy_header(fig, "Catalysts & Key Risks", "DDS — Path to Thesis Realization", "LONG", GREEN)
    footer(fig, "DDS", 3)

    ax = fig.add_axes([0.03, 0.10, 0.94, 0.68])
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')

    ax.add_patch(FancyBboxPatch((0.01, 0.01), 0.46, 0.94,
                                boxstyle="round,pad=0.015", fc="#F0FAF4", ec=GREEN, lw=1))
    ax.text(0.24, 0.92, "NEAR-TERM CATALYSTS (0–18 mo)", fontsize=10,
            fontweight='bold', color=GREEN, ha='center', transform=ax.transAxes)

    cats = [
        ("Share Count Milestone",     "< 8M shares remaining; each quarter buyback = > 5% float reduction"),
        ("Real Estate Monetization",  "Management exploring REIT conversion or sale-leaseback of prime locations"),
        ("Earnings Surprise",         "Street models assume SSS decline; any flat-to-positive SSS = EPS upside"),
        ("Activist / Institutional",  "Low analyst coverage creates re-rating catalyst if large fund discloses stake"),
        ("Special Dividend",          "Free cash builds on balance sheet; special dividend announcement likely"),
    ]
    for i, (c_title, c_body) in enumerate(cats):
        y = 0.80 - i*0.155
        ax.add_patch(FancyBboxPatch((0.03, y-0.04), 0.42, 0.125,
                                    boxstyle="round,pad=0.01", fc=WHITE, ec=GREEN, lw=0.4))
        ax.text(0.05, y+0.045, c_title, fontsize=9, fontweight='bold',
                color=GREEN, transform=ax.transAxes)
        ax.text(0.05, y-0.01, c_body, fontsize=8, color="#2C3E50",
                transform=ax.transAxes)

    ax.add_patch(FancyBboxPatch((0.53, 0.01), 0.46, 0.94,
                                boxstyle="round,pad=0.015", fc="#F0F4F8", ec=NAVY, lw=1))
    ax.text(0.76, 0.92, "RISKS TO LONG THESIS", fontsize=10,
            fontweight='bold', color=NAVY, ha='center', transform=ax.transAxes)

    risks = [
        ("Consumer Spending Slowdown","HIGH",
         "DDS targets middle-to-upper income consumer; recession sensitivity is real, see 2008/2020"),
        ("Secular Retail Decline",    "MEDIUM",
         "Long-term traffic trends in department stores remain challenged despite strong execution"),
        ("Real Estate Market Decline","LOW",
         "Commercial real estate downturn could impair NAV-based valuation thesis"),
        ("No Float Left to Buy",      "LOW",
         "With ~8M shares, buyback program mathematically must slow — EPS accretion engine decelerates"),
    ]
    risk_colors = {"HIGH": RED, "MEDIUM": ORANGE, "LOW": GREEN}
    for i, (r_title, severity, r_body) in enumerate(risks):
        y = 0.80 - i*0.185
        rc = risk_colors[severity]
        ax.add_patch(FancyBboxPatch((0.55, y-0.055), 0.42, 0.145,
                                    boxstyle="round,pad=0.01", fc=WHITE, ec=rc, lw=0.8))
        ax.text(0.57, y+0.055, r_title, fontsize=9, fontweight='bold',
                color=NAVY, transform=ax.transAxes)
        ax.add_patch(FancyBboxPatch((0.79, y+0.03), 0.08, 0.055,
                                    boxstyle="round,pad=0.01", fc=rc, ec='none'))
        ax.text(0.83, y+0.057, severity, fontsize=7, fontweight='bold',
                color=WHITE, ha='center', transform=ax.transAxes)
        ax.text(0.57, y-0.025, r_body, fontsize=7.5, color="#4A4A4A",
                transform=ax.transAxes, wrap=True)

    pdf.savefig(fig, bbox_inches='tight'); plt.close()

    # --- SLIDE 4: DCF + SUM OF PARTS ---
    fig = new_fig()
    navy_header(fig, "Valuation — DCF & Sum-of-Parts", "DDS — $450 Target, 35% Upside", "LONG", GREEN)
    footer(fig, "DDS", 4)

    ax = fig.add_axes([0.03, 0.08, 0.94, 0.70])
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')

    years = ["FY25A", "FY26E", "FY27E", "FY28E", "FY29E", "FY30E", "Terminal"]
    rows = {
        "Revenue ($M)":       ["6,470", "6,350", "6,200", "6,100", "6,050", "6,050", "—"],
        "Rev Growth":         ["-2%",   "-2%",   "-2%",   "-2%",   "-1%",   "0%",    "—"],
        "EBIT Margin":        ["12%",   "13%",   "14%",   "14%",   "15%",   "15%",   "—"],
        "EBIT ($M)":          ["776",   "826",   "868",   "854",   "908",   "908",   "—"],
        "FCF ($M)":           ["720",   "760",   "790",   "775",   "820",   "820",   "—"],
        "Buyback ($M)":       ["(590)", "(600)", "(610)", "(620)", "(620)", "(—)",   "—"],
        "Discount Factor":    ["—",     "0.93",  "0.87",  "0.81",  "0.75",  "0.70",  "—"],
        "PV of FCF ($M)":     ["—",     "707",   "687",   "628",   "615",   "574",   "—"],
    }

    col_w = 0.118
    col_xs = [0.01 + i*col_w for i in range(7)]
    for j, yr in enumerate(years):
        ax.add_patch(FancyBboxPatch((col_xs[j], 0.87), col_w-0.005, 0.07,
                                    boxstyle="square,pad=0", fc=NAVY, ec='none'))
        ax.text(col_xs[j] + (col_w-0.005)/2, 0.905, yr, fontsize=8.5,
                fontweight='bold', color=GOLD if yr == "FY25A" else WHITE,
                ha='center', transform=ax.transAxes)

    row_ys = np.linspace(0.79, 0.14, len(rows))
    for ri, (rname, vals) in enumerate(rows.items()):
        y = row_ys[ri]
        bg = LGRAY if ri % 2 == 0 else WHITE
        ax.add_patch(FancyBboxPatch((-0.01, y-0.01), 1.02, 0.075,
                                    boxstyle="square,pad=0", fc=bg, ec='none'))
        for j, v in enumerate(vals):
            ax.text(col_xs[j] + (col_w-0.005)/2, y+0.025, v, fontsize=8,
                    ha='center', color=NAVY if v != "—" else MGRAY,
                    transform=ax.transAxes)
        ax.text(-0.005, y+0.025, rname, fontsize=7.5, color=NAVY,
                fontweight='bold', transform=ax.transAxes)

    # Sum-of-parts box + DCF scenarios
    ax.add_patch(FancyBboxPatch((0.01, -0.03), 0.42, 0.14,
                                boxstyle="round,pad=0.015", fc=LGRAY, ec=NAVY, lw=0.8))
    ax.text(0.22, 0.085, "SUM-OF-PARTS SANITY CHECK", fontsize=9,
            fontweight='bold', color=NAVY, ha='center', transform=ax.transAxes)
    sop = [
        ("Real Estate NAV (owned stores @ $12M/store)",  "$3.0B", "$375/sh"),
        ("Retail Operations (6x EV/EBITDA)",             "$1.3B", "$163/sh"),
        ("Less: Net Debt / Pensions",                    "($0.6B)", "($75/sh)"),
        ("SOP Equity Value",                             "$3.7B",  "$463/sh"),
    ]
    for i, (item, val, per_sh) in enumerate(sop):
        y = 0.065 - i*0.022
        col = GREEN if "SOP" in item else NAVY
        ax.text(0.03, y, item, fontsize=7.5, color=col, fontweight='bold' if "SOP" in item else 'normal',
                transform=ax.transAxes)
        ax.text(0.31, y, val, fontsize=7.5, color=col, ha='center',
                transform=ax.transAxes)
        ax.text(0.41, y, per_sh, fontsize=7.5, color=GREEN if "SOP" in item else NAVY,
                ha='right', transform=ax.transAxes)

    scenarios = [
        ("BEAR CASE",  "$300",  "FCF yield 16%, 7x P/E\nConsumer slowdown",   RED),
        ("BASE CASE",  "$450",  "DCF + SOP blend\nWACC 8%, TGR 1%",          GREEN),
        ("BULL CASE",  "$600",  "Real estate realization\nBuyback completion", BLUE),
    ]
    for i, (sc, pt, assum, col) in enumerate(scenarios):
        x = 0.46 + i*0.18
        ax.add_patch(FancyBboxPatch((x+0.01, -0.03), 0.15, 0.14,
                                    boxstyle="round,pad=0.015", fc=col, ec='none'))
        ax.text(x+0.085, 0.083, sc, fontsize=8, fontweight='bold', color=WHITE,
                ha='center', transform=ax.transAxes)
        ax.text(x+0.085, 0.048, pt, fontsize=13, fontweight='bold', color=WHITE,
                ha='center', transform=ax.transAxes)
        ax.text(x+0.085, 0.008, assum, fontsize=6.5, color=WHITE,
                ha='center', transform=ax.transAxes, linespacing=1.4)

    pdf.savefig(fig, bbox_inches='tight'); plt.close()


# ─── PORTFOLIO-LEVEL SLIDES ───────────────────────────────────────────────────

def quant_signal_slide(pdf, metrics):
    fig = new_fig()
    navy_header(
        fig,
        "Quant Signal Dashboard",
        "Systematic ranking of payoff, confidence, and downside asymmetry",
        "AUTO",
        BLUE,
    )
    footer(fig, "PORTFOLIO", 1)

    # Left: payoff bar chart
    bar_ax = fig.add_axes([0.06, 0.18, 0.38, 0.52])
    bar_ax.set_facecolor("#F8FAFD")
    y_positions = np.arange(len(metrics))
    payoffs = [metric["expected_return_pct"] for metric in metrics]
    bar_colors = [recommendation_color(metric["recommendation"]) for metric in metrics]
    max_payoff = max(payoffs) if payoffs else 1.0

    bar_ax.barh(y_positions, payoffs, color=bar_colors, alpha=0.92, height=0.55)
    bar_ax.set_yticks(y_positions)
    bar_ax.set_yticklabels(
        [metric["ticker"] for metric in metrics],
        fontsize=10,
        color=NAVY,
        fontweight="bold",
    )
    bar_ax.invert_yaxis()
    bar_ax.set_xlim(0, max_payoff * 1.32)
    bar_ax.tick_params(axis='x', labelsize=8, colors=NAVY)
    bar_ax.tick_params(axis='y', labelsize=10, colors=NAVY)
    bar_ax.xaxis.grid(alpha=0.25, color=MGRAY)
    bar_ax.set_axisbelow(True)
    bar_ax.set_title("Target Move to Price Target", fontsize=10, color=NAVY, fontweight='bold')
    bar_ax.set_xlabel("Expected payoff (%)", fontsize=8, color=NAVY)
    for idx, payoff in enumerate(payoffs):
        bar_ax.text(
            payoff + max_payoff * 0.03,
            idx,
            f"{payoff:.0f}%",
            va='center',
            fontsize=9,
            color=NAVY,
            fontweight='bold',
        )

    # Right: confidence vs asymmetry bubble plot
    bubble_ax = fig.add_axes([0.53, 0.18, 0.41, 0.52])
    bubble_ax.set_facecolor("#F8FAFD")
    asymmetry_values = [metric["asymmetry_ratio"] for metric in metrics]
    confidence_values = [metric["confidence_pct"] for metric in metrics]
    avg_asymmetry = sum(asymmetry_values) / len(asymmetry_values)
    avg_confidence = sum(confidence_values) / len(confidence_values)

    for metric in metrics:
        bubble_size = 80 + metric["conviction_score"] * 4
        bubble_ax.scatter(
            metric["asymmetry_ratio"],
            metric["confidence_pct"],
            s=bubble_size,
            color=recommendation_color(metric["recommendation"]),
            alpha=0.65,
            edgecolor=NAVY,
            linewidth=0.8,
        )
        bubble_ax.text(
            metric["asymmetry_ratio"] + 0.03,
            metric["confidence_pct"] + 0.6,
            metric["ticker"],
            fontsize=9,
            color=NAVY,
            fontweight='bold',
        )

    bubble_ax.axvline(avg_asymmetry, color=MGRAY, linewidth=0.9, linestyle='--')
    bubble_ax.axhline(avg_confidence, color=MGRAY, linewidth=0.9, linestyle='--')
    bubble_ax.set_xlim(0.9, max(2.0, max(asymmetry_values) * 1.35))
    bubble_ax.set_ylim(max(50, min(confidence_values) - 5), min(95, max(confidence_values) + 6))
    bubble_ax.set_title("Asymmetry vs Confidence", fontsize=10, color=NAVY, fontweight='bold')
    bubble_ax.set_xlabel("Reward-to-risk ratio", fontsize=8, color=NAVY)
    bubble_ax.set_ylabel("Confidence (%)", fontsize=8, color=NAVY)
    bubble_ax.tick_params(axis='both', labelsize=8, colors=NAVY)
    bubble_ax.grid(alpha=0.25, color=MGRAY)

    # Bottom: ranked signal cards
    cards_ax = fig.add_axes([0.06, 0.06, 0.88, 0.09])
    cards_ax.set_xlim(0, 1)
    cards_ax.set_ylim(0, 1)
    cards_ax.axis('off')
    card_width = (0.98 / len(metrics)) - 0.01
    for idx, metric in enumerate(metrics):
        x0 = 0.01 + idx * (0.98 / len(metrics))
        border = recommendation_color(metric["recommendation"])
        cards_ax.add_patch(
            FancyBboxPatch(
                (x0, 0.08),
                card_width,
                0.84,
                boxstyle="round,pad=0.01",
                fc=WHITE,
                ec=border,
                lw=1.1,
            )
        )
        cards_ax.text(
            x0 + 0.01,
            0.66,
            f"#{int(metric['rank'])} {metric['ticker']}  |  {metric['playbook']}",
            fontsize=7.3,
            color=NAVY,
            fontweight='bold',
            va='center',
        )
        cards_ax.text(
            x0 + 0.01,
            0.33,
            f"Conviction {metric['conviction_score']:.0f}  |  Catalysts {metric['catalyst_score']:.0f}/10  |  Risk {metric['downside_risk']:.0f}/10",
            fontsize=7.1,
            color=MGRAY,
            va='center',
        )

    pdf.savefig(fig, bbox_inches='tight'); plt.close()


def portfolio_manager_brief_slide(pdf, metrics):
    weighted = suggested_weights(metrics)
    brief_lines = portfolio_action_brief(metrics)
    fig = new_fig()
    navy_header(
        fig,
        "Portfolio Manager Brief",
        f"{RENDER_PROFILE.desk_name}  ·  {RENDER_PROFILE.deck_date}",
        "PM",
        GOLD,
    )
    footer(fig, "PORTFOLIO", 2)

    ax = fig.add_axes([0.03, 0.08, 0.94, 0.70])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Left panel: decision memo
    ax.add_patch(FancyBboxPatch((0.00, 0.02), 0.46, 0.94,
                                boxstyle="round,pad=0.015", fc=LGRAY, ec=NAVY, lw=0.8))
    ax.text(0.03, 0.91, "Desk Notes", fontsize=11, fontweight='bold',
            color=NAVY, transform=ax.transAxes)
    ax.text(0.03, 0.85, f"Prepared by: {RENDER_PROFILE.analyst_name}",
            fontsize=8.5, color=MGRAY, transform=ax.transAxes)

    for idx, line in enumerate(brief_lines):
        y = 0.74 - idx * 0.19
        ax.add_patch(FancyBboxPatch((0.03, y - 0.08), 0.40, 0.14,
                                    boxstyle="round,pad=0.01", fc=WHITE, ec="#D5DCE5", lw=0.8))
        ax.text(0.05, y + 0.01, f"0{idx + 1}", fontsize=8, color=GOLD,
                fontweight='bold', transform=ax.transAxes)
        ax.text(0.09, y + 0.01, line, fontsize=8.3, color=NAVY,
                transform=ax.transAxes, wrap=True)

    ax.text(0.03, 0.08,
            "Execution principle: size ideas by conviction and confidence,"
            " not by headline payoff alone.",
            fontsize=8, color=MGRAY, transform=ax.transAxes, wrap=True)

    # Right panel: position sizing table
    ax.add_patch(FancyBboxPatch((0.50, 0.02), 0.49, 0.94,
                                boxstyle="round,pad=0.015", fc="#F8FAFD", ec=NAVY, lw=0.8))
    ax.text(0.74, 0.91, "Suggested Position Plan", fontsize=11, fontweight='bold',
            color=NAVY, ha='center', transform=ax.transAxes)

    headers = ["Ticker", "Side", "Weight", "Entry", "Stop Rule"]
    xs = [0.52, 0.61, 0.69, 0.78, 0.89]
    for idx, header in enumerate(headers):
        ax.text(xs[idx], 0.83, header, fontsize=8.2, color=MGRAY, fontweight='bold',
                ha='center', transform=ax.transAxes)

    for row_idx, metric in enumerate(weighted):
        y = 0.73 - row_idx * 0.21
        side_color = recommendation_color(metric["recommendation"])
        ax.add_patch(FancyBboxPatch((0.515, y - 0.07), 0.46, 0.15,
                                    boxstyle="round,pad=0.01", fc=WHITE, ec="#DDE4EE", lw=0.8))
        ax.text(xs[0], y, metric["ticker"], fontsize=10, fontweight='bold',
                color=NAVY, ha='center', transform=ax.transAxes)
        ax.add_patch(FancyBboxPatch((xs[1] - 0.026, y - 0.03), 0.052, 0.06,
                                    boxstyle="round,pad=0.01", fc=side_color, ec='none'))
        ax.text(xs[1], y, metric["recommendation"], fontsize=7.5, color=WHITE,
                fontweight='bold', ha='center', va='center', transform=ax.transAxes)
        ax.text(xs[2], y, f"{metric['suggested_weight_pct']:.1f}%", fontsize=9,
                color=NAVY, fontweight='bold', ha='center', transform=ax.transAxes)
        ax.text(xs[3], y, metric["entry_range"], fontsize=7.2,
                color=NAVY, ha='center', transform=ax.transAxes)
        ax.text(xs[4], y, metric["stop_rule"], fontsize=7.2,
                color=MGRAY, ha='center', transform=ax.transAxes)

    pdf.savefig(fig, bbox_inches='tight'); plt.close()


def summary_slide(pdf, metrics):
    fig = new_fig()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(NAVY); ax.axis('off')
    footer(fig, "PORTFOLIO", 3)

    idea_label = "Idea" if len(metrics) == 1 else "Ideas"
    ax.text(0.5, 0.91, "EQUITY RESEARCH — PORTFOLIO SUMMARY", color=GOLD,
            fontsize=14, fontweight='bold', ha='center')
    ax.text(0.5, 0.85, f"{len(metrics)} Differentiated {idea_label} Across Sectors  ·  {RENDER_PROFILE.deck_date}",
            color=WHITE, fontsize=10, ha='center')

    headers = ["Ticker", "Name", "Sector", "Rec.", "Price", "Target", "Payoff", "Core Thesis"]
    col_xs = [0.02, 0.09, 0.19, 0.31, 0.38, 0.45, 0.53, 0.63]
    col_ws = [0.07, 0.10, 0.12, 0.07, 0.07, 0.07, 0.10, 0.36]

    y_hdr = 0.78
    for hdr, cx, cw in zip(headers, col_xs, col_ws):
        ax.add_patch(mpatches.FancyBboxPatch((cx, y_hdr), cw-0.005, 0.05,
                                             boxstyle="square,pad=0",
                                             fc=GOLD, ec='none',
                                             transform=ax.transAxes))
        ax.text(cx + (cw-0.005)/2, y_hdr+0.025, hdr, fontsize=9,
                fontweight='bold', color=NAVY, ha='center', va='center',
                transform=ax.transAxes)

    for ri, metric in enumerate(metrics):
        y = 0.63 - ri*0.175
        bg = "#0D2540" if ri % 2 == 0 else "#0F2A48"
        ax.add_patch(mpatches.FancyBboxPatch((0.02, y), 0.96, 0.155,
                                             boxstyle="square,pad=0", fc=bg, ec='none',
                                             transform=ax.transAxes))

        vals = [
            metric["ticker"],
            metric["name"],
            metric["sector"],
            metric["recommendation"],
            format_currency(metric["price"]),
            format_currency(metric["target"]),
            f"{metric['expected_return_pct']:.0f}%",
            metric["thesis"],
        ]

        for col_i, (val, cx, cw) in enumerate(zip(vals, col_xs, col_ws)):
            if col_i == 3:  # recommendation badge + conviction score
                badge_color = recommendation_color(metric["recommendation"])
                ax.add_patch(mpatches.FancyBboxPatch((cx+0.005, y+0.045), cw-0.015, 0.065,
                                                     boxstyle="round,pad=0.01",
                                                     fc=badge_color, ec='none', transform=ax.transAxes))
                ax.text(cx+(cw-0.005)/2, y+0.086, val, fontsize=8,
                        fontweight='bold', color=WHITE, ha='center', va='center',
                        transform=ax.transAxes)
                ax.text(cx+(cw-0.005)/2, y+0.057, f"CV {metric['conviction_score']:.0f}",
                        fontsize=6.5, color=GOLD, ha='center', va='center',
                        transform=ax.transAxes, fontweight='bold')
            elif col_i == 6:  # payoff
                payoff_color = recommendation_color(metric["recommendation"])
                ax.text(cx+(cw-0.005)/2, y+0.078, val, fontsize=11,
                        fontweight='bold', color=payoff_color, ha='center', va='center',
                        transform=ax.transAxes)
            elif col_i == 7:  # thesis
                ax.text(cx+0.01, y+0.078, val, fontsize=7.3, color=LGRAY,
                        va='center', transform=ax.transAxes, wrap=True)
            elif col_i == 0:  # ticker
                ax.text(cx+(cw-0.005)/2, y+0.078, val, fontsize=10,
                        fontweight='bold', color=GOLD, ha='center', va='center',
                        transform=ax.transAxes)
            else:
                ax.text(cx+(cw-0.005)/2, y+0.078, val, fontsize=8.5,
                        color=WHITE, ha='center', va='center',
                        transform=ax.transAxes)

    ax.add_patch(mpatches.FancyBboxPatch((0.02, 0.06), 0.96, 0.10,
                                         boxstyle="round,pad=0.015",
                                         fc=GOLD, ec='none', transform=ax.transAxes))
    ax.text(0.5, 0.13, "Portfolio Construction Note", fontsize=9,
            fontweight='bold', color=NAVY, ha='center', transform=ax.transAxes)
    ax.text(0.5, 0.09, portfolio_construction_note(metrics),
            fontsize=8, color=NAVY, ha='center', transform=ax.transAxes)

    ax.text(0.5, 0.025, "Disclaimer: For illustrative/interview purposes only. Not investment advice.",
            color=MGRAY, fontsize=7, ha='center', transform=ax.transAxes)

    pdf.savefig(fig, bbox_inches='tight'); plt.close()


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()
    set_render_profile(args)
    try:
        selected_tickers = normalize_tickers(args.tickers)
    except ValueError as exc:
        raise SystemExit(str(exc))

    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    combined_name = args.combined_name
    if not combined_name.lower().endswith(".pdf"):
        combined_name = f"{combined_name}.pdf"

    pitch_renderers = {
        "PLTR": pitch_pltr,
        "MEDP": pitch_medp,
        "DDS": pitch_dds,
    }
    portfolio_metrics = build_portfolio_metrics(selected_tickers)
    metrics_by_ticker = {
        metric["ticker"]: metric for metric in portfolio_metrics
    }

    if args.dry_run:
        print_ranked_metrics(portfolio_metrics)

    if args.export_csv:
        csv_path = export_metrics_csv(portfolio_metrics, output_dir)
        print(f"  ✓  {csv_path}")

    if args.export_json:
        json_path = export_metrics_json(portfolio_metrics, output_dir)
        print(f"  ✓  {json_path}")

    if args.export_memo:
        memo_path = export_memo_markdown(portfolio_metrics, output_dir)
        print(f"  ✓  {memo_path}")

    if args.dry_run:
        print("\nDry run completed. No PDFs were generated.")
        return

    ensure_plotting_dependencies()

    if not args.combined_only:
        for ticker in selected_tickers:
            profile = PITCH_PROFILES[ticker]
            path = os.path.join(output_dir, f"{profile.pdf_basename}.pdf")
            with PdfPages(path) as pdf:
                pitch_renderers[ticker](pdf)
            metric = metrics_by_ticker[ticker]
            print(
                f"  ✓  {path}  |  payoff {metric['expected_return_pct']:.0f}%"
                f", conviction {metric['conviction_score']:.0f}"
            )

    combined_path = os.path.join(output_dir, combined_name)
    with PdfPages(combined_path) as pdf:
        quant_signal_slide(pdf, portfolio_metrics)
        portfolio_manager_brief_slide(pdf, portfolio_metrics)
        summary_slide(pdf, portfolio_metrics)
        for ticker in selected_tickers:
            pitch_renderers[ticker](pdf)

    print(f"  ✓  {combined_path}")
    print("\nAll PDFs generated successfully.")

if __name__ == "__main__":
    main()

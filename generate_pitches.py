"""
Stock Pitch Deck Generator
3 differentiated pitches across sectors for AM interviews
Uses matplotlib PdfPages — no extra dependencies needed
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch
import numpy as np
import os

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
    ax.text(0.04, 0.5, f"{ticker} — Confidential Research", color=MGRAY,
            fontsize=7, va='center')
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

    ax.text(0.5, 0.10, "Equity Research  ·  April 2026  ·  For Interview Use Only",
            color=MGRAY, fontsize=9, ha='center')
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
    ax.text(0.5, 0.10, "Equity Research  ·  April 2026  ·  For Interview Use Only",
            color=MGRAY, fontsize=9, ha='center')
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
    ax.text(0.5, 0.10, "Equity Research  ·  April 2026  ·  For Interview Use Only",
            color=MGRAY, fontsize=9, ha='center')
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


# ─── COMBINED SUMMARY DECK ────────────────────────────────────────────────────

def summary_slide(pdf):
    fig = new_fig()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(NAVY); ax.axis('off')

    ax.text(0.5, 0.91, "EQUITY RESEARCH — PORTFOLIO SUMMARY", color=GOLD,
            fontsize=14, fontweight='bold', ha='center')
    ax.text(0.5, 0.85, "Three Differentiated Ideas Across Sectors  ·  April 2026",
            color=WHITE, fontsize=10, ha='center')

    headers = ["Ticker", "Name", "Sector", "Rec.", "Price", "Target", "Upside", "Core Thesis"]
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

    pitches = [
        ("PLTR",  "Palantir Technologies", "Technology",      "SHORT", "~$80", "$28",  "-65%",
         "Valuation bubble (115x P/E); govt revenue plateauing; commercial growth misleading; massive insider selling"),
        ("MEDP",  "Medpace Holdings",      "Healthcare / CRO","LONG",  "~$293","$410", "+40%",
         "Founder-led best-in-class CRO; biotech outsourcing tailwind; superior margins at peer discount; $820M cash"),
        ("DDS",   "Dillard's Inc.",        "Consumer / RE",   "LONG",  "~$333","$450", "+35%",
         "85%+ float retired via buybacks; real estate NAV > market cap; 15%+ FCF yield; ignored by sell-side"),
    ]
    rec_colors = {"SHORT": RED, "LONG": GREEN}
    up_colors  = {"-65%": RED, "+40%": GREEN, "+35%": GREEN}

    for ri, (ticker, name, sector, rec, px, tgt, upside, thesis) in enumerate(pitches):
        y = 0.63 - ri*0.175
        bg = "#0D2540" if ri % 2 == 0 else "#0F2A48"
        ax.add_patch(mpatches.FancyBboxPatch((0.02, y), 0.96, 0.155,
                                             boxstyle="square,pad=0", fc=bg, ec='none',
                                             transform=ax.transAxes))
        vals = [ticker, name, sector, rec, px, tgt, upside, thesis]
        for col_i, (val, cx, cw) in enumerate(zip(vals, col_xs, col_ws)):
            if col_i == 3:  # rec badge
                c = rec_colors[val]
                ax.add_patch(mpatches.FancyBboxPatch((cx+0.005, y+0.045), cw-0.015, 0.065,
                                                     boxstyle="round,pad=0.01",
                                                     fc=c, ec='none', transform=ax.transAxes))
                ax.text(cx+(cw-0.005)/2, y+0.078, val, fontsize=9,
                        fontweight='bold', color=WHITE, ha='center', va='center',
                        transform=ax.transAxes)
            elif col_i == 6:  # upside
                c = up_colors.get(val, WHITE)
                ax.text(cx+(cw-0.005)/2, y+0.078, val, fontsize=11,
                        fontweight='bold', color=c, ha='center', va='center',
                        transform=ax.transAxes)
            elif col_i == 7:  # thesis
                ax.text(cx+0.01, y+0.078, thesis, fontsize=7.5, color=LGRAY,
                        va='center', transform=ax.transAxes, wrap=True)
            elif col_i == 0:  # ticker
                ax.text(cx+(cw-0.005)/2, y+0.078, val, fontsize=10,
                        fontweight='bold', color=GOLD, ha='center', va='center',
                        transform=ax.transAxes)
            else:
                ax.text(cx+(cw-0.005)/2, y+0.078, val, fontsize=8.5,
                        color=WHITE, ha='center', va='center',
                        transform=ax.transAxes)

    # Portfolio expected return
    ax.add_patch(mpatches.FancyBboxPatch((0.02, 0.06), 0.96, 0.10,
                                         boxstyle="round,pad=0.015",
                                         fc=GOLD, ec='none', transform=ax.transAxes))
    ax.text(0.5, 0.13, "Portfolio Construction Note", fontsize=9,
            fontweight='bold', color=NAVY, ha='center', transform=ax.transAxes)
    ax.text(0.5, 0.09,
            "Equal-weighted long/short portfolio: MEDP (long) + DDS (long) + PLTR (short)  ·  "
            "Blended expected return: ~47% gross, ~23% net of short carry  ·  "
            "Low macro beta: MEDP/DDS uncorrelated to PLTR; idiosyncratic drivers dominate",
            fontsize=8, color=NAVY, ha='center', transform=ax.transAxes)

    ax.text(0.5, 0.025, "Disclaimer: For illustrative/interview purposes only. Not investment advice.",
            color=MGRAY, fontsize=7, ha='center', transform=ax.transAxes)

    pdf.savefig(fig, bbox_inches='tight'); plt.close()


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    os.makedirs("/Users/andrewstewart/stockpitch/output", exist_ok=True)

    # Individual pitch PDFs
    for name, func, ticker in [
        ("PLTR_Short_Palantir",       pitch_pltr, "PLTR"),
        ("MEDP_Long_Medpace",         pitch_medp, "MEDP"),
        ("DDS_Long_Dillards",         pitch_dds,  "DDS"),
    ]:
        path = f"/Users/andrewstewart/stockpitch/output/{name}.pdf"
        with PdfPages(path) as pdf:
            globals()[f"pitch_{ticker.lower()}"](pdf)
        print(f"  ✓  {path}")

    # Combined deck
    combined = "/Users/andrewstewart/stockpitch/output/StockPitches_Combined.pdf"
    with PdfPages(combined) as pdf:
        summary_slide(pdf)
        pitch_pltr(pdf)
        pitch_medp(pdf)
        pitch_dds(pdf)
    print(f"  ✓  {combined}")
    print("\nAll PDFs generated successfully.")

if __name__ == "__main__":
    main()

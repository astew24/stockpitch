# StockPitch: Portfolio Manager Support & Research Automation

An automated equity research workflow designed to accelerate the creation of decision-useful investment decks and systematic signal tracking. This system automates the "last mile" of reporting, allowing analysts to focus on research rather than document formatting.

## Project Overview
StockPitch provides a dual-surface approach to equity research:
1.  **Dynamic Analysis:** A live Streamlit app that pulls real-time financials, runs DCF models, and generates sensitivity heatmaps for instant valuation.
2.  **Systematic Production:** A CLI tool that ranks multiple investment ideas using a custom "Quant Signal Engine" and generates professional 16-slide PDF pitch decks.

## Key Capabilities
- **Automated Valuation:** Pulls revenue, FCF, and balance sheet data via `yfinance` to build dynamic DCF and Comparable Company models.
- **Quant Signal Engine:** Scores investments based on expected payoff, confidence, catalysts, and downside risk to generate a "Portfolio Manager Brief."
- **Institutional-Grade Export:** Generates structured PDF briefs and combined pitch decks with automated sizing, entry ranges, and stop-loss rules.
- **Sensitivity Heatmaps:** Visualizes how intrinsic value changes across different WACC and terminal growth assumptions.

## Tech Stack
- **Languages:** Python (Pandas, NumPy)
- **Frameworks:** Streamlit, ReportLab (for PDF generation)
- **Data:** yfinance API
- **Testing:** Python `unittest` for scoring and ranking logic

## How to Run Locally

### 1. Environment Setup
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Interactive Analysis (Streamlit)
```bash
streamlit run streamlit_app.py
```

### 3. Bulk Production (CLI)
```bash
# Generate decks for specific tickers with CSV/JSON metrics
python3 generate_pitches.py --tickers AAPL,MSFT --export-csv --export-json
```

## What I Learned
- **Workflow Optimization:** I learned how to translate a manual, spreadsheet-heavy process into a code-driven workflow that reduces reporting time by 90%.
- **Decision Support Logic:** Building the Quant Signal Engine taught me how to quantify qualitative conviction and translate it into actionable portfolio sizing suggestions.
- **Data Integration:** Handling live financial data required building robust validation layers to ensure model integrity across different company reporting structures.

## Future Improvements
- **Multi-Ticker Benchmarking:** Expand the Streamlit interface to allow side-by-side DCF comparisons for peer groups.
- **Integrated Research Feed:** Pull in real-time news and analyst estimates to dynamically update catalyst maps.
- **LLM Pitch Generation:** Use LLMs to draft the qualitative thesis slides based on the automated financial outputs.

---
*Public Demo: [Hosted Demo Desk](https://astew24.github.io/stockpitch/)*

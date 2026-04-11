# StockPitch

[![Live Demo](https://img.shields.io/badge/Live_Demo-Streamlit_DCF-FF4B4B?logo=streamlit&logoColor=white)](#streamlit-demo)

Human-readable equity pitch deck generator with a systematic ranking layer.

The repo now has two surfaces:
- `generate_pitches.py` keeps the original PDF deck generator for the built-in interview ideas.
- `streamlit_app.py` adds a read-only live DCF demo that pulls real public financials with `yfinance`, values a user-entered ticker, renders a WACC / terminal growth sensitivity heatmap, and exports a PDF brief on demand.

## What This Version Adds
- Dynamic CLI (`--tickers`, `--output-dir`, `--combined-only`, `--combined-name`).
- Quant signal engine that scores each idea by expected payoff, confidence, catalysts, and downside risk.
- Auto-generated `Quant Signal Dashboard` slide in the combined deck.
- Auto-generated `Portfolio Manager Brief` slide with suggested weights, entry ranges, and stop rules.
- Dynamic summary slide driven by model output (not hardcoded rows).
- Optional CSV and JSON exports (`PitchSignalMetrics.csv`, `PitchSignalMetrics.json`) for analysis and tracking.
- Optional markdown PM memo export (`PortfolioManagerMemo.md`) for interview packet prep.
- `--dry-run` mode for ranking/exports without requiring PDF dependencies.
- Runtime branding controls (`--deck-date`, `--desk-name`, `--analyst-name`, `--audience-label`).
- Unit tests for scoring, ranking, sizing, and runtime profile behavior.

## Setup
```bash
python3 -m pip install -r requirements.txt
```

## Streamlit Demo
```bash
streamlit run streamlit_app.py
```

The app:
- pulls live public revenue, net income, free cash flow, balance-sheet, and market-price data with `yfinance`
- projects revenue and free cash flow using user-supplied DCF assumptions
- computes intrinsic value per share, equity value, and a WACC / terminal growth sensitivity grid
- generates a downloadable PDF brief from the current live analysis without storing user input

## Usage
```bash
python3 generate_pitches.py
```

```bash
python3 generate_pitches.py --tickers MEDP,DDS --combined-only --export-csv
```

```bash
python3 generate_pitches.py --output-dir ./output --combined-name InterviewDeck.pdf --export-json
```

```bash
python3 generate_pitches.py --tickers PLTR,MEDP --dry-run --export-csv --export-json --export-memo
```

```bash
python3 generate_pitches.py --deck-date "Spring 2026" --desk-name "Blue River Capital" --analyst-name "Jane Doe"
```

## Tests
```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

## Deployment
Local run:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Streamlit Community Cloud:
1. Push this repo to GitHub.
2. In Streamlit Community Cloud, create a new app from the repo.
3. Set the app entrypoint to `streamlit_app.py`.
4. Leave secrets empty; the demo uses public `yfinance` data only.

## Output
- Individual PDFs (unless `--combined-only` or `--dry-run` is used)
- Combined deck with:
  1. Quant Signal Dashboard
  2. Portfolio Manager Brief
  3. Portfolio Summary
  4. Full pitch sections for selected tickers
- Optional `PitchSignalMetrics.csv`, `PitchSignalMetrics.json`, and `PortfolioManagerMemo.md`

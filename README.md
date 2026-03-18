# StockPitch

**[Live Demo →](https://astew24.github.io/stockpitch/)**

Equity pitch deck generator with a DCF valuation layer and quant signal scoring. Generates PDF pitch decks from a set of ideas, scores each by expected payoff and confidence, and exports a combined deck with a portfolio brief and sensitivity heatmap.

The repo has two surfaces:
- `generate_pitches.py` — CLI for generating PDF decks from the built-in idea set
- `streamlit_app.py` — live DCF demo that pulls public financials with `yfinance`, values any ticker, and exports a PDF brief on demand

## Setup

```bash
python3 -m pip install -r requirements.txt
```

## Usage

```bash
# Generate deck for default ideas
python3 generate_pitches.py

# Custom tickers
python3 generate_pitches.py --tickers MEDP,DDS --combined-only --export-csv

# Full options
python3 generate_pitches.py --output-dir ./output --combined-name InterviewDeck.pdf --export-json

# Dry run (scoring + exports, no PDF dependencies needed)
python3 generate_pitches.py --tickers PLTR,MEDP --dry-run --export-csv --export-json --export-memo

# Custom branding
python3 generate_pitches.py --deck-date "Spring 2026" --desk-name "Blue River Capital" --analyst-name "Jane Doe"
```

## Streamlit App

```bash
streamlit run streamlit_app.py
```

Pulls live revenue, FCF, and balance sheet data from `yfinance`, runs a DCF with user-supplied assumptions, and generates a downloadable PDF brief. No stored data — everything is computed from the live yfinance feed.

## Tests

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

## Output

Running `generate_pitches.py` produces:
- Individual PDFs per ticker (unless `--combined-only`)
- Combined deck with quant signal dashboard, portfolio brief, and full pitch sections
- Optional `PitchSignalMetrics.csv`, `PitchSignalMetrics.json`, `PortfolioManagerMemo.md`

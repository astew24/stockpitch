# StockPitch

[Live demo](https://astew24.github.io/stockpitch/)

Two related things:

- `generate_pitches.py` renders three hand-written stock pitches (PLTR
  short, MEDP long, DDS long) into PDF decks plus a combined deck with a
  signal-ranked cover slide and a PM brief.
- `streamlit_app.py` is a live DCF demo that pulls public financials via
  `yfinance` for any ticker, runs the valuation with your assumptions,
  and exports a PDF brief on demand.

## Setup

```bash
python3 -m pip install -r requirements.txt
```

## Generating pitch PDFs

```bash
# Default set
python3 generate_pitches.py

# Subset + exports
python3 generate_pitches.py --tickers MEDP,DDS --combined-only --export-csv

# All exports + custom output
python3 generate_pitches.py --output-dir ./output --combined-name InterviewDeck.pdf --export-json

# Dry run (ranking + exports only; no matplotlib needed)
python3 generate_pitches.py --tickers PLTR,MEDP --dry-run --export-csv --export-json --export-memo

# Branding
python3 generate_pitches.py --deck-date "Spring 2026" --desk-name "Blue River Capital" --analyst-name "Jane Doe"
```

## Streamlit app

```bash
streamlit run streamlit_app.py
```

Pulls revenue, FCF, and balance-sheet data from `yfinance`, runs a DCF
with user-supplied assumptions, and offers a downloadable PDF brief.
Nothing is stored; every run re-reads the yfinance feed.

## Tests

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

## What `generate_pitches.py` produces

- Individual per-ticker PDFs (unless `--combined-only`)
- A combined deck with the quant signal dashboard, PM brief, and each
  pitch in full
- Optionally `PitchSignalMetrics.csv`, `PitchSignalMetrics.json`,
  `PortfolioManagerMemo.md`

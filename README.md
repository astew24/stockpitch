# StockPitch

Human-readable equity pitch deck generator with a systematic ranking layer.

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

## Output
- Individual PDFs (unless `--combined-only` or `--dry-run` is used)
- Combined deck with:
  1. Quant Signal Dashboard
  2. Portfolio Manager Brief
  3. Portfolio Summary
  4. Full pitch sections for selected tickers
- Optional `PitchSignalMetrics.csv`, `PitchSignalMetrics.json`, and `PortfolioManagerMemo.md`

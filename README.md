# StockPitch

Human-readable equity pitch deck generator with a systematic ranking layer.

## What This Version Adds
- Dynamic CLI (`--tickers`, `--output-dir`, `--combined-only`, `--combined-name`).
- Quant signal engine that scores each idea by expected payoff, confidence, catalysts, and downside risk.
- Auto-generated `Quant Signal Dashboard` slide in the combined deck.
- Dynamic summary slide driven by model output (not hardcoded rows).
- Optional CSV export (`PitchSignalMetrics.csv`) for analysis and tracking.

## Usage
```bash
python3 generate_pitches.py
```

```bash
python3 generate_pitches.py --tickers MEDP,DDS --combined-only --export-csv
```

```bash
python3 generate_pitches.py --output-dir ./output --combined-name InterviewDeck.pdf
```

## Output
- Individual PDFs (unless `--combined-only` is used)
- Combined deck with:
  1. Quant Signal Dashboard
  2. Portfolio Summary
  3. Full pitch sections for selected tickers
- Optional `PitchSignalMetrics.csv` with rank and signal inputs

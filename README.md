# Sovereign Debt Spiral Monitor

A sovereign debt sustainability monitor built around one analytical model (`docs/MODEL.md`):
a sovereign that borrows in its own currency can always pay nominally, so the questions are
whether the trajectory is sustainable on the *forward* effective rate, and, if not, who pays
and through which channel. Captivity of the holder base decides whether an unsustainable path
resolves as a decades-long repression grind or a crisis within a cycle; the currency, not the
yield, is the pressure gauge; union members cannot print, so for them the gauge is the spread.

It collects fiscal and monetary data for 11 core markets and 7 backtest-only countries,
computes ~40 quarterly indicators with full history, backtests them against 28 labelled
crises, builds a self-contained HTML dashboard, has Claude write a quarterly narrative, and
emails it through Gmail. Plain files, no database. Everything is versioned in this repo.

## Re-run from a clean clone

```
make setup                 # venv, package, dev + report extras, .env from template (~2 min)
make test                  # 49 unit tests, no network
make indicators            # quarterly panel + indicator table from the committed data (~1 min)
make backtest              # reports/backtest/BACKTEST.md
make dashboard             # reports/dashboard/latest.html (open it in a browser)
make report                # Claude narrative -> reports/quarterly/YYYY-Qn.md (needs ANTHROPIC_API_KEY)
make email DRY=1           # writes the full email to reports/outbox/*.eml
make update                # refresh every data source (needs outbound HTTPS; FRED key optional)
```

Data refreshes normally run on GitHub Actions (`.github/workflows/update.yml`), which commit
the new data back. The monthly and quarterly workflows do the same plus the email.

## Layout

| Path | What |
|---|---|
| `config/universe.yaml` | tiers, monetary regimes, regime history, anchors, inflation targets |
| `config/indicators.yaml` | captivity weights and scales, quadrant thresholds, indicator thresholds, source priority, resample rules |
| `config/stages.yaml` | stage 0–6 rules with union-member and peg overrides, in a readable grammar |
| `config/report.yaml` | narrative model, cadence, email settings |
| `docs/` | `MODEL.md` (framework), `INDICATORS.md` (generated table), `DATA_SOURCES.md`, `DATA_GAPS.md`, `DECISIONS.md`, `SETUP.md` |
| `data/raw/` | latest raw response per series; `data/raw/_probe/` is the recorded API discovery |
| `data/clean/` | long-format CSV per source with vintages; `panel.csv` (quarterly concepts), `indicators.csv`, `indicators_latest.csv`, `transitions.csv` |
| `data/manual/` | hand-maintained series with citations and a confidence flag |
| `data/catalog.csv` | one row per series: source, URL, frequency, units, first/last obs, vintage, errors |
| `data/events.csv` | the labelled crisis set for the backtest |
| `src/sdm/collect/` | one collector per source (`sources/`), common base, concept vocabulary |
| `src/sdm/indicators/` | panel builder, indicator functions (docstrings feed the dashboard), stage engine, compute |
| `src/sdm/backtest/` | lead times, quadrant hit rates, forward real returns, forward-r accuracy, `BACKTEST.md` |
| `src/sdm/report/` | dashboard, narrative (Claude), Gmail email, monthly alert, docs generator |
| `prompts/report_instructions.md` | the report brief Claude follows |
| `reports/` | `backtest/`, `dashboard/`, `quarterly/`, `outbox/` |
| `.github/workflows/` | `update.yml` (data), `monthly.yml`, `quarterly.yml`, `probe.yml` |

## How a number gets from a source to the report

1. A collector fetches a series, caches the raw response under `data/raw/<source>/` and
   appends new or revised observations (with a download timestamp) to `data/clean/<source>.csv`.
2. `sdm indicators` builds the quarterly panel: per country and concept the highest-priority
   source wins, lower ones fill gaps after being spliced to its level; stocks and rates take
   the quarter's last observation, flows sum, annual values cover their four quarters, and
   nothing is forward-filled beyond one quarter. `panel_sources.csv` records every cell's source.
3. Each indicator is a pure function of the panel (`src/sdm/indicators/blocks.py`); the stage
   engine evaluates `config/stages.yaml`; quadrant and transitions follow.
4. The dashboard, the backtest and the narrative all read `indicators.csv`; stale or failed
   series are listed in every email under "Data issues" rather than silently reused.

## Status and known weaknesses

Read `reports/backtest/BACKTEST.md` and `docs/DATA_GAPS.md` first. In short: holder shares
before 2004 and after 2016, and average maturities outside the UK, are hand-maintained
approximations; forward r currently under-predicts realised r in the backtest; trend nominal
growth over ten years still carries the 2021–23 inflation burst.

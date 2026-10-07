# Sovereign Debt Spiral Monitor

A sovereign debt sustainability monitor. It collects fiscal and monetary data for a set of
countries, computes indicators derived from one analytical model (`docs/MODEL.md`), backtests
that model against historical crises, and each quarter has Claude write a narrative report
and build an HTML dashboard that are emailed to the owner.

Plain files, no database: raw API responses in `data/raw/`, tidy Parquet in `data/clean/`,
one catalog row per series in `data/catalog.csv`.

## Status

Phase 1 of 8 (scaffold, config, model doc). See `docs/DATA_SOURCES.md` for the data plan and
`docs/DECISIONS.md` for every judgement call so far.

## Quick start

```
make setup                 # venv + install + .env from template
# edit .env: FRED_API_KEY, ANTHROPIC_API_KEY
make test                  # unit tests
.venv/bin/sdm check        # validate config
make update                # refresh data            (phase 2)
make indicators            # quarterly indicator table (phase 3)
make backtest              # reports/backtest/BACKTEST.md (phase 4)
make dashboard             # reports/dashboard/latest.html (phase 5)
make report                # Claude-written quarterly  (phase 6)
make email DRY=1           # writes the email to reports/outbox/ (phase 7)
```

## Layout

```
config/     universe.yaml (tiers, monetary regimes), indicators.yaml (weights, thresholds),
            stages.yaml (stage rules), report.yaml (model, cadence, email)
docs/       MODEL.md (the framework), INDICATORS.md, DATA_SOURCES.md, DATA_GAPS.md,
            DECISIONS.md, SETUP.md
data/       raw/ clean/ manual/ catalog.csv events.csv
src/sdm/    collect/ indicators/ backtest/ report/ cli.py config.py
prompts/    report_instructions.md
reports/    backtest/ dashboard/ quarterly/ outbox/
tests/
```

## The model in one paragraph

A sovereign that borrows in its own currency can always pay nominally, so the question is not
"will they default" but "is the trajectory sustainable, and if not, who pays and how".
Trajectory is `Δ(debt/GDP) ≈ (r − g)·debt/GDP − primary balance`, read on the *forward*
effective rate rather than today's lagging average coupon. Captivity of the holder base decides
whether an unsustainable path resolves as a decades-long repression grind (Japan, US, UK,
Italy, France) or a crisis within a cycle (Argentina, Turkey, Russia 1998, Greece). The
indicators watch for stage transitions; the currency, not the yield, is the pressure gauge.
Union members cannot print, so for them the gauge is the spread to the Bund and the political
captivity of the ECB.

"""Write reports/backtest/BACKTEST.md from the backtest result, honestly."""

from __future__ import annotations

from datetime import date

import pandas as pd

from sdm.paths import REPORTS

OUT = REPORTS / "backtest" / "BACKTEST.md"


def _md(df: pd.DataFrame, floatfmt: str = ".2f", max_rows: int = 60) -> str:
    if df is None or len(df) == 0:
        return "_no data_"
    d = df.head(max_rows).copy()
    for c in d.columns:
        if d[c].dtype.kind == "f":
            d[c] = d[c].map(lambda v: "" if pd.isna(v) else format(v, floatfmt))
    cols = list(d.columns)
    lines = ["| " + " | ".join(str(c) for c in cols) + " |", "|" + "---|" * len(cols)]
    for _, r in d.iterrows():
        lines.append("| " + " | ".join("" if pd.isna(v) else str(v) for v in r.values) + " |")
    if len(df) > max_rows:
        lines.append(f"\n_{len(df) - max_rows} more rows in the CSV_")
    return "\n".join(lines)


def write_backtest_md(res: object, events: pd.DataFrame) -> None:
    r = res  # BacktestResult
    cov = r.coverage
    n_events = len(events)
    n_with_quadrant = int(cov["quadrant"].sum()) if len(cov) else 0
    n_with_fiscal = (
        int((cov["debt_gdp"] & cov["primary_balance_gdp"] & cov["r_effective"]).sum()) if len(cov) else 0
    )

    qb = r.quadrant_before
    crisis_types = {"currency", "default", "inflation", "IMF-program", "bond-market"}
    qb_crisis = qb[qb["type"].isin(crisis_types)] if len(qb) else qb
    fp = r.false_positives
    n_fp = int(fp["false_positive"].sum()) if len(fp) else 0
    n_runs = len(fp)

    fr = r.forward_r
    fwd_better = f"{int(fr['forward_better'].sum())}/{len(fr)}" if len(fr) else "n/a"

    n_crisis = len(qb_crisis)
    n_modal_free = int((qb_crisis["modal_quadrant"] == "unsustainable_free").sum()) if n_crisis else 0
    n_half_unsus = int((qb_crisis["share_unsustainable"] > 0.5).sum()) if n_crisis else 0
    reg = r.regression
    reg_show = reg[~reg["term"].str.startswith("mean:")] if len(reg) else reg
    means_show = reg[reg["term"].str.startswith("mean:")] if len(reg) else reg

    text = f"""# Backtest

Generated {date.today().isoformat()} from `data/events.csv` ({n_events} labelled episodes) and
`data/clean/indicators.csv`. Everything here is reproducible with `make backtest`. This
document is written to say where the model is weak, not to sell it.

## 0. Coverage: what could actually be tested

Of {n_events} events, {n_with_fiscal} have the three trajectory inputs (debt/GDP, primary
balance, effective rate) in the eight quarters before the event and {n_with_quadrant} have a
quadrant classification. The rest are limited by data, not by the model: holder shares before
2004 are hand-coded single points, average maturity is a manual annual series, and the
pre-1995 fiscal history comes from annual IMF and JST tables spread over quarters.

{_md(cov)}

## 1. Lead times: how far ahead did each indicator cross its threshold?

For each event and each thresholded indicator: did the indicator sit on its warning side at
any point in the 20 quarters before the event, and how many quarters before the event did
it first cross? `warned_share` is the fraction of events (with data) that were warned;
`mean_share_on_warning_side` is how much of the window was spent on the warning side (a high
number with a high warned share means the indicator is on all the time, which is not a
signal).

{_md(r.lead_summary.reset_index())}

Per-event detail is in `lead_times.csv`. Read the summary with two cautions. First, the
sample of crisis events is tiny and dominated by emerging-market pegs, where the trajectory
block had the least data. Second, several thresholds (debt/GDP 90, bill share 25) are
context lines, not predictors, and the lead-time table shows exactly that: they warn in most
cases because they are on most of the time.

## 2. Did the quadrant put the crisis countries in the crisis cell?

Modal quadrant in the eight quarters before each event, the share of those quarters spent
in `unsustainable_free`, the highest stage estimate, and the captivity score at the time.

{_md(qb)}

Crisis-type events only (currency, default, inflation, IMF program, bond market):
{n_crisis} events, of which {n_modal_free} had `unsustainable_free` as the modal quadrant and
{n_half_unsus} spent more than half the window in either unsustainable cell.

**False positives.** Every run of `unsustainable_free` in the full history, whether an event
followed within the run or the following two years, and whether the run exceeded three years
with no event: {n_fp} false-positive runs out of {n_runs} runs.

{_md(fp)}

## 3. Does unsustainable-captive predict negative real bond returns and currency erosion?

Forward real returns on rolling 10-year local bonds (duration approximation from quarterly
yields; see DECISIONS.md) and on gold in local currency, annualised over the next 5 and 10
years, for every country-quarter with a quadrant. Means by quadrant, then an OLS of the
return on quadrant dummies (base: `sustainable_captive`). The windows overlap, so the standard
errors are scaled by the number of non-overlapping windows; treat the t-statistics as rough.

Means by quadrant:

{_md(means_show[["horizon_years", "return", "term", "coef", "n"]] if len(means_show) else means_show)}

Regression:

{_md(reg_show)}

## 4. Does forward r beat current r as a forecast of r five years later?

RMSE of `forward_r_5y` against the realised effective rate 20 quarters later, versus the
naive forecast that r stays where it is. Forward r is better in {fwd_better} countries with
enough history.

{_md(fr)}

## 5. What does not work (yet)

- **Captivity before 2004 is a single hand-coded point per event.** The quadrant test for
  the 1970s–90s events therefore tests the manual table as much as the model. Replacing it
  with Arslanalp–Tsuda's full dataset or national flow-of-funds tables is the first fix.
- **Average maturity is approximate for every country but the UK snapshot**, and forward r
  is built on it. The forward-r RMSE test above is only as good as that table.
- **Few developed-market spirals.** The brief anticipated this; the calibration leans on EM
  pegs, where the mechanism (reserve loss) differs from the floater mechanism (currency and
  repression). The regime overrides in `config/stages.yaml` exist for that reason, but the
  peg stage-5 rule needs reserves data that only the World Bank annual series provides.
- **Bond returns are approximated from yields**, not measured. JST annual bond returns
  exist for 11 countries and are in the clean store (`bond_total_return`) for a cross-check
  that is not yet automated.
- **Trend g.** A 10-year trailing mean of nominal growth still carries the 2021–23 inflation
  burst, which flatters forward r − g for every core country in 2026. That is a modelling
  choice the backtest cannot settle; it is one line in `config/indicators.yaml`.
- **Stage 6 by rule only catches consolidations.** Repression grinds and defaults are
  labelled by hand in `events.csv`.
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")

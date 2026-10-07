# Backtest

Generated 2026-10-07 from `data/events.csv` (28 labelled episodes) and
`data/clean/indicators.csv`. Everything here is reproducible with `make backtest`. This
document is written to say where the model is weak, not to sell it.

## 0. Coverage: what could actually be tested

Of 28 events, 26 have the three trajectory inputs (debt/GDP, primary
balance, effective rate) in the eight quarters before the event and 4 have a
quadrant classification. The rest are limited by data, not by the model: holder shares before
2004 are hand-coded single points, average maturity is a manual annual series, and the
pre-1995 fiscal history comes from annual IMF and JST tables spread over quarters.

| event_id | debt_gdp | primary_balance_gdp | r_effective | g_nominal | captivity_score | forward_r_minus_g_5y | quadrant |
|---|---|---|---|---|---|---|---|
| GB-1976 | True | True | True | True | True | False | False |
| IT-1992 | True | True | True | True | True | False | False |
| SE-1992 | True | True | True | True | True | False | False |
| SE-1994 | True | True | True | True | False | False | False |
| MX-1994 | True | True | True | True | True | False | False |
| CA-1994 | True | True | True | True | True | False | False |
| RU-1998 | True | True | True | True | True | False | False |
| AR-2001 | True | True | True | True | True | False | False |
| GR-2010 | True | True | True | True | True | False | False |
| GR-2012 | True | True | True | True | True | False | False |
| GR-2015 | True | True | True | True | True | False | False |
| BR-2015 | True | True | True | True | True | False | False |
| TR-2018 | True | True | True | True | True | False | False |
| TR-2021 | True | True | True | True | True | False | False |
| GB-2022 | True | True | True | True | True | True | True |
| AR-2018 | True | True | True | True | True | False | False |
| AR-2019 | True | True | True | True | True | False | False |
| AR-2023 | True | True | True | True | False | False | False |
| JP-2022 | True | True | True | True | True | True | True |
| RU-2014 | True | True | True | True | True | False | False |
| MX-1982 | False | True | False | True | False | False | False |
| GB-1992 | True | True | True | True | False | False | False |
| BR-1999 | False | True | False | True | False | False | False |
| TR-2001 | True | True | True | True | False | False | False |
| IT-2011 | True | True | True | True | True | False | False |
| EA-2012 | True | True | True | True | True | False | False |
| IT-2018 | True | True | True | True | True | True | True |
| FR-2024 | True | True | True | True | True | True | True |

## 1. Lead times: how far ahead did each indicator cross its threshold?

For each event and each thresholded indicator: did the indicator sit on its warning side at
any point in the 20 quarters before the event, and how many quarters before the event did
it first cross? `warned_share` is the fraction of events (with data) that were warned;
`mean_share_on_warning_side` is how much of the window was spent on the warning side (a high
number with a high warned share means the indicator is on all the time, which is not a
signal).

| indicator | events_with_data | warned_share | median_lead_quarters | mean_share_on_warning_side |
|---|---|---|---|---|
| breakeven_10y | 2 | 1.0 | 20.00 | 1.00 |
| cb_holdings_change_4q | 8 | 0.875 | 19.00 | 0.46 |
| policy_rate_minus_inflation | 24 | 0.8333333333333334 | 20.00 | 0.42 |
| avg_coupon_gap | 16 | 0.8125 | 19.00 | 0.41 |
| primary_balance_gdp | 28 | 0.75 | 20.00 | 0.52 |
| term_premium_proxy | 16 | 0.75 | 12.00 | 0.35 |
| fx_vs_usd_12m | 28 | 0.7142857142857143 | 18.50 | 0.30 |
| spread_to_anchor_bp | 7 | 0.7142857142857143 | 20.00 | 0.42 |
| r_minus_g | 26 | 0.6923076923076923 | 19.50 | 0.48 |
| target2_balance_gdp | 6 | 0.6666666666666666 | 8.00 | 0.35 |
| captivity_score | 23 | 0.6521739130434783 | 6.00 | 0.56 |
| issuance_shortening | 8 | 0.625 | 11.00 | 0.19 |
| forward_r_minus_g_5y | 4 | 0.5 | 13.50 | 0.34 |
| debt_gdp | 26 | 0.46153846153846156 | 20.00 | 0.39 |
| fx_broad_reer_12m | 20 | 0.45 | 18.00 | 0.11 |
| bill_share | 9 | 0.2222222222222222 | 7.50 | 0.22 |
| foreign_share | 23 | 0.13043478260869565 | 3.00 | 0.13 |

Per-event detail is in `lead_times.csv`. Read the summary with two cautions. First, the
sample of crisis events is tiny and dominated by emerging-market pegs, where the trajectory
block had the least data. Second, several thresholds (debt/GDP 90, bill share 25) are
context lines, not predictors, and the lead-time table shows exactly that: they warn in most
cases because they are on most of the time.

## 2. Did the quadrant put the crisis countries in the crisis cell?

Modal quadrant in the eight quarters before each event, the share of those quarters spent
in `unsustainable_free`, the highest stage estimate, and the captivity score at the time.

| event_id | country | type | quarters_with_quadrant | share_unsustainable_free | share_unsustainable | modal_quadrant | max_stage | captivity_score |
|---|---|---|---|---|---|---|---|---|
| GB-1976 | GB | IMF-program | 0 |  |  |  | 0.00 | 61.78 |
| IT-1992 | IT | currency | 0 |  |  |  | 0.00 | 60.04 |
| SE-1992 | SE | currency | 0 |  |  |  | 0.00 | 43.94 |
| SE-1994 | SE | successful-consolidation | 0 |  |  |  | 0.00 |  |
| MX-1994 | MX | currency | 0 |  |  |  | 0.00 | 13.23 |
| CA-1994 | CA | successful-consolidation | 0 |  |  |  | 0.00 | 46.34 |
| RU-1998 | RU | default | 0 |  |  |  |  | 56.92 |
| AR-2001 | AR | default | 0 |  |  |  | 0.00 | 15.45 |
| GR-2010 | GR | IMF-program | 0 |  |  |  | 0.00 | 67.89 |
| GR-2012 | GR | default | 0 |  |  |  | 0.00 | 66.71 |
| GR-2015 | GR | default | 0 |  |  |  | 0.00 | 60.90 |
| BR-2015 | BR | currency | 0 |  |  |  | 0.00 | 63.08 |
| TR-2018 | TR | currency | 0 |  |  |  | 0.00 | 47.75 |
| TR-2021 | TR | currency | 0 |  |  |  | 0.00 | 66.40 |
| GB-2022 | GB | bond-market | 4 | 0.00 | 0.00 | sustainable_captive | 0.00 | 75.69 |
| AR-2018 | AR | currency | 0 |  |  |  | 0.00 | 44.31 |
| AR-2019 | AR | default | 0 |  |  |  | 0.00 | 44.31 |
| AR-2023 | AR | inflation | 0 |  |  |  | 0.00 |  |
| JP-2022 | JP | currency | 4 | 0.00 | 0.00 | sustainable_captive | 0.00 | 64.69 |
| RU-2014 | RU | currency | 0 |  |  |  | 0.00 | 42.34 |
| MX-1982 | MX | default | 0 |  |  |  | 0.00 |  |
| GB-1992 | GB | currency | 0 |  |  |  | 0.00 |  |
| BR-1999 | BR | currency | 0 |  |  |  | 0.00 |  |
| TR-2001 | TR | currency | 0 |  |  |  | 0.00 |  |
| IT-2011 | IT | bond-market | 0 |  |  |  | 0.00 | 65.28 |
| EA-2012 | EA | bond-market | 0 |  |  |  | 0.00 | 64.14 |
| IT-2018 | IT | bond-market | 1 | 0.00 | 0.00 | sustainable_free | 0.00 | 51.80 |
| FR-2024 | FR | bond-market | 1 | 0.00 | 0.00 | sustainable_free | 0.00 | 29.27 |

Crisis-type events only (currency, default, inflation, IMF program, bond market):
26 events, of which 0 had `unsustainable_free` as the modal quadrant and
0 spent more than half the window in either unsustainable cell.

**False positives.** Every run of `unsustainable_free` in the full history, whether an event
followed within the run or the following two years, and whether the run exceeded three years
with no event: 0 false-positive runs out of 2 runs.

| country | start | end | quarters | event_followed | event_id | false_positive |
|---|---|---|---|---|---|---|
| IT | 2024-03-31 | 2024-09-30 | 3 | False |  | False |
| JP | 2015-03-31 | 2015-12-31 | 4 | False |  | False |

## 3. Does unsustainable-captive predict negative real bond returns and currency erosion?

Forward real returns on rolling 10-year local bonds (duration approximation from quarterly
yields; see DECISIONS.md) and on gold in local currency, annualised over the next 5 and 10
years, for every country-quarter with a quadrant. Means by quadrant, then an OLS of the
return on quadrant dummies (base: `sustainable_captive`). The windows overlap, so the standard
errors are scaled by the number of non-overlapping windows; treat the t-statistics as rough.

Means by quadrant:

| horizon_years | return | term | coef | n |
|---|---|---|---|---|
| 5 | real_bond_return_ann | mean:sustainable_captive | -2.47 | 13 |
| 5 | real_bond_return_ann | mean:sustainable_free | -0.71 | 32 |
| 5 | real_bond_return_ann | mean:unsustainable_captive | 17.38 | 2 |
| 5 | real_bond_return_ann | mean:unsustainable_free | 0.23 | 4 |

Regression:

| horizon_years | return | term | coef | se_overlap_adj | t | n | effective_n |
|---|---|---|---|---|---|---|---|
| 5 | real_bond_return_ann | const | -2.47 | 3.14 | -0.79 | 51 | 5.00 |
| 5 | real_bond_return_ann | sustainable_free | 1.77 | 3.72 | 0.47 | 51 | 5.00 |
| 5 | real_bond_return_ann | unsustainable_captive | 19.86 | 8.59 | 2.31 | 51 | 5.00 |
| 5 | real_bond_return_ann | unsustainable_free | 2.71 | 6.46 | 0.42 | 51 | 5.00 |

## 4. Does forward r beat current r as a forecast of r five years later?

RMSE of `forward_r_5y` against the realised effective rate 20 quarters later, versus the
naive forecast that r stays where it is. Forward r is better in 1/8 countries with
enough history.

| country | n | rmse_forward_r | rmse_current_r | bias_forward_r | bias_current_r | forward_better |
|---|---|---|---|---|---|---|
| DE | 8 | 1.18 | 0.73 | -0.92 | 0.11 | False |
| FR | 8 | 1.07 | 0.70 | -0.81 | 0.10 | False |
| GB | 11 | 2.78 | 2.45 | -2.04 | -1.52 | False |
| GR | 8 | 2.08 | 0.61 | 1.03 | -0.06 | False |
| IT | 8 | 1.00 | 0.57 | -0.83 | 0.01 | False |
| JP | 8 | 0.18 | 0.26 | -0.17 | 0.25 | True |
| NL | 8 | 0.94 | 0.57 | -0.78 | 0.26 | False |
| US | 15 | 1.28 | 0.90 | -0.97 | -0.66 | False |

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

# Backtest

Generated 2026-10-08 from `data/events.csv` (28 labelled episodes) and
`data/clean/indicators.csv`. Everything here is reproducible with `make backtest`. This
document is written to say where the model is weak, not to sell it.

## 0. Coverage: what could actually be tested

Of 28 events, 25 have the three trajectory inputs (debt/GDP, primary
balance, effective rate) in the eight quarters before the event and 4 have a
quadrant classification. The rest are limited by data, not by the model: holder shares before
2004 are hand-coded single points, average maturity is a manual annual series, and the
pre-1995 fiscal history comes from annual IMF and JST tables spread over quarters.

| event_id | debt_gdp | primary_balance_gdp | r_effective | g_nominal | captivity_score | forward_r_minus_g_5y | quadrant |
|---|---|---|---|---|---|---|---|
| GB-1976 | True | True | True | True | False | False | False |
| IT-1992 | True | True | True | True | False | False | False |
| SE-1992 | True | True | True | True | False | False | False |
| SE-1994 | True | True | True | True | False | False | False |
| MX-1994 | True | True | True | True | False | False | False |
| CA-1994 | True | True | True | True | False | False | False |
| RU-1998 | True | True | False | True | False | False | False |
| AR-2001 | True | True | True | True | False | False | False |
| GR-2010 | True | True | True | True | False | False | False |
| GR-2012 | True | True | True | True | False | False | False |
| GR-2015 | True | True | True | True | False | False | False |
| BR-2015 | True | True | True | True | False | False | False |
| TR-2018 | True | True | True | True | False | False | False |
| TR-2021 | True | True | True | True | False | False | False |
| GB-2022 | True | True | True | True | True | True | True |
| AR-2018 | True | True | True | True | False | False | False |
| AR-2019 | True | True | True | True | False | False | False |
| AR-2023 | True | True | True | True | False | False | False |
| JP-2022 | True | True | True | True | True | True | True |
| RU-2014 | True | True | True | True | False | False | False |
| MX-1982 | False | True | False | True | False | False | False |
| GB-1992 | True | True | True | True | False | False | False |
| BR-1999 | False | True | False | True | False | False | False |
| TR-2001 | True | True | True | True | False | False | False |
| IT-2011 | True | True | True | True | False | False | False |
| EA-2012 | True | True | True | True | False | False | False |
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
| policy_rate_minus_inflation | 24 | 0.8333333333333334 | 20.00 | 0.42 |
| gold_local_ccy_12m | 28 | 0.8214285714285714 | 19.00 | 0.34 |
| avg_coupon_gap | 16 | 0.8125 | 19.00 | 0.40 |
| primary_balance_gdp | 28 | 0.75 | 20.00 | 0.54 |
| forward_r_minus_g_5y | 4 | 0.75 | 9.00 | 0.31 |
| r_minus_g | 25 | 0.72 | 20.00 | 0.49 |
| spread_to_anchor_bp | 7 | 0.7142857142857143 | 20.00 | 0.42 |
| fx_vs_usd_12m | 28 | 0.7142857142857143 | 18.50 | 0.30 |
| cb_holdings_change_4q | 17 | 0.7058823529411765 | 20.00 | 0.48 |
| term_premium_proxy | 16 | 0.6875 | 11.00 | 0.35 |
| target2_balance_gdp | 6 | 0.6666666666666666 | 8.00 | 0.35 |
| issuance_shortening | 8 | 0.625 | 11.00 | 0.17 |
| captivity_score | 4 | 0.5 | 14.50 | 0.50 |
| debt_gdp | 26 | 0.46153846153846156 | 20.00 | 0.39 |
| fx_broad_reer_12m | 20 | 0.45 | 18.00 | 0.11 |
| foreign_share | 25 | 0.12 | 3.00 | 0.12 |
| bill_share | 9 | 0.1111111111111111 | 11.00 | 0.11 |

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
| GB-1976 | GB | IMF-program | 0 |  |  |  | 0.00 |  |
| IT-1992 | IT | currency | 0 |  |  |  | 0.00 |  |
| SE-1992 | SE | currency | 0 |  |  |  | 0.00 |  |
| SE-1994 | SE | successful-consolidation | 0 |  |  |  | 0.00 |  |
| MX-1994 | MX | currency | 0 |  |  |  | 0.00 |  |
| CA-1994 | CA | successful-consolidation | 0 |  |  |  | 0.00 |  |
| RU-1998 | RU | default | 0 |  |  |  |  |  |
| AR-2001 | AR | default | 0 |  |  |  | 0.00 |  |
| GR-2010 | GR | IMF-program | 0 |  |  |  | 0.00 |  |
| GR-2012 | GR | default | 0 |  |  |  | 0.00 |  |
| GR-2015 | GR | default | 0 |  |  |  | 0.00 |  |
| BR-2015 | BR | currency | 0 |  |  |  | 0.00 |  |
| TR-2018 | TR | currency | 0 |  |  |  | 0.00 |  |
| TR-2021 | TR | currency | 0 |  |  |  | 0.00 |  |
| GB-2022 | GB | bond-market | 8 | 0.00 | 0.00 | sustainable_captive | 0.00 | 73.75 |
| AR-2018 | AR | currency | 0 |  |  |  | 0.00 |  |
| AR-2019 | AR | default | 0 |  |  |  | 0.00 |  |
| AR-2023 | AR | inflation | 0 |  |  |  | 0.00 |  |
| JP-2022 | JP | currency | 8 | 0.00 | 0.00 | sustainable_captive | 0.00 | 78.19 |
| RU-2014 | RU | currency | 0 |  |  |  | 0.00 |  |
| MX-1982 | MX | default | 0 |  |  |  | 0.00 |  |
| GB-1992 | GB | currency | 0 |  |  |  | 0.00 |  |
| BR-1999 | BR | currency | 0 |  |  |  | 0.00 |  |
| TR-2001 | TR | currency | 0 |  |  |  | 0.00 |  |
| IT-2011 | IT | bond-market | 0 |  |  |  | 0.00 |  |
| EA-2012 | EA | bond-market | 0 |  |  |  | 0.00 |  |
| IT-2018 | IT | bond-market | 8 | 0.00 | 0.00 | sustainable_free | 0.00 | 48.55 |
| FR-2024 | FR | bond-market | 8 | 0.12 | 0.12 | sustainable_free | 3.00 | 38.95 |

Crisis-type events only (currency, default, inflation, IMF program, bond market):
26 events, of which 0 had `unsustainable_free` as the modal quadrant and
0 spent more than half the window in either unsustainable cell.

**False positives.** Every run of `unsustainable_free` in the full history, whether an event
followed within the run or the following two years, and whether the run exceeded three years
with no event: 1 false-positive runs out of 3 runs.

| country | start | end | quarters | event_followed | event_id | false_positive |
|---|---|---|---|---|---|---|
| FR | 2023-03-31 | 2023-03-31 | 1 | True | FR-2024 | False |
| IT | 2020-06-30 | 2024-09-30 | 18 | False |  | True |
| JP | 2015-03-31 | 2016-06-30 | 6 | False |  | False |

## 3. Does unsustainable-captive predict negative real bond returns and currency erosion?

Forward real returns on rolling 10-year local bonds (duration approximation from quarterly
yields; see DECISIONS.md) and on gold in local currency, annualised over the next 5 and 10
years, for every country-quarter with a quadrant. Means by quadrant, then an OLS of the
return on quadrant dummies (base: `sustainable_captive`). The windows overlap, so the standard
errors are scaled by the number of non-overlapping windows; treat the t-statistics as rough.

Means by quadrant:

| horizon_years | return | term | coef | n |
|---|---|---|---|---|
| 5 | real_bond_return_ann | mean:sustainable_captive | -3.10 | 57 |
| 5 | real_bond_return_ann | mean:sustainable_free | -2.44 | 261 |
| 5 | real_bond_return_ann | mean:unsustainable_captive | 2.61 | 10 |
| 5 | real_bond_return_ann | mean:unsustainable_free | -2.60 | 12 |
| 5 | real_gold_return_ann | mean:sustainable_captive | 11.46 | 57 |
| 5 | real_gold_return_ann | mean:sustainable_free | 8.25 | 261 |
| 5 | real_gold_return_ann | mean:unsustainable_captive | 9.43 | 10 |
| 5 | real_gold_return_ann | mean:unsustainable_free | 10.46 | 12 |
| 5 | gold_minus_bond_ann | mean:sustainable_captive | 15.08 | 60 |
| 5 | gold_minus_bond_ann | mean:sustainable_free | 10.77 | 263 |
| 5 | gold_minus_bond_ann | mean:unsustainable_captive | 6.82 | 10 |
| 5 | gold_minus_bond_ann | mean:unsustainable_free | 13.05 | 12 |
| 10 | real_bond_return_ann | mean:sustainable_captive | -2.49 | 14 |
| 10 | real_bond_return_ann | mean:sustainable_free | -0.04 | 91 |
| 10 | real_bond_return_ann | mean:unsustainable_captive | 2.38 | 3 |
| 10 | real_bond_return_ann | mean:unsustainable_free | -2.46 | 6 |
| 10 | real_gold_return_ann | mean:sustainable_captive | 10.18 | 14 |
| 10 | real_gold_return_ann | mean:sustainable_free | 7.55 | 91 |
| 10 | real_gold_return_ann | mean:unsustainable_captive | 12.71 | 3 |
| 10 | real_gold_return_ann | mean:unsustainable_free | 14.41 | 6 |
| 10 | gold_minus_bond_ann | mean:sustainable_captive | 12.75 | 15 |
| 10 | gold_minus_bond_ann | mean:sustainable_free | 7.77 | 94 |
| 10 | gold_minus_bond_ann | mean:unsustainable_captive | 12.56 | 4 |
| 10 | gold_minus_bond_ann | mean:unsustainable_free | 16.86 | 6 |

Regression:

| horizon_years | return | term | coef | se_overlap_adj | t | n | effective_n |
|---|---|---|---|---|---|---|---|
| 5 | real_bond_return_ann | const | -3.10 | 2.48 | -1.25 | 340 | 17.00 |
| 5 | real_bond_return_ann | sustainable_free | 0.65 | 2.74 | 0.24 | 340 | 17.00 |
| 5 | real_bond_return_ann | unsustainable_captive | 5.70 | 6.42 | 0.89 | 340 | 17.00 |
| 5 | real_bond_return_ann | unsustainable_free | 0.50 | 5.95 | 0.08 | 340 | 17.00 |
| 5 | real_gold_return_ann | const | 11.46 | 3.40 | 3.37 | 340 | 17.00 |
| 5 | real_gold_return_ann | sustainable_free | -3.22 | 3.75 | -0.86 | 340 | 17.00 |
| 5 | real_gold_return_ann | unsustainable_captive | -2.04 | 8.79 | -0.23 | 340 | 17.00 |
| 5 | real_gold_return_ann | unsustainable_free | -1.00 | 8.15 | -0.12 | 340 | 17.00 |
| 5 | gold_minus_bond_ann | const | 15.08 | 4.44 | 3.40 | 345 | 17.20 |
| 5 | gold_minus_bond_ann | sustainable_free | -4.31 | 4.92 | -0.88 | 345 | 17.20 |
| 5 | gold_minus_bond_ann | unsustainable_captive | -8.26 | 11.74 | -0.70 | 345 | 17.20 |
| 5 | gold_minus_bond_ann | unsustainable_free | -2.02 | 10.87 | -0.19 | 345 | 17.20 |
| 10 | real_bond_return_ann | const | -2.49 | 3.47 | -0.72 | 114 | 5.00 |
| 10 | real_bond_return_ann | sustainable_free | 2.45 | 3.73 | 0.66 | 114 | 5.00 |
| 10 | real_bond_return_ann | unsustainable_captive | 4.87 | 8.26 | 0.59 | 114 | 5.00 |
| 10 | real_bond_return_ann | unsustainable_free | 0.03 | 6.34 | 0.00 | 114 | 5.00 |
| 10 | real_gold_return_ann | const | 10.18 | 6.07 | 1.68 | 114 | 5.00 |
| 10 | real_gold_return_ann | sustainable_free | -2.64 | 6.52 | -0.40 | 114 | 5.00 |
| 10 | real_gold_return_ann | unsustainable_captive | 2.53 | 14.44 | 0.17 | 114 | 5.00 |
| 10 | real_gold_return_ann | unsustainable_free | 4.22 | 11.08 | 0.38 | 114 | 5.00 |
| 10 | gold_minus_bond_ann | const | 12.75 | 7.10 | 1.80 | 119 | 5.00 |
| 10 | gold_minus_bond_ann | sustainable_free | -4.99 | 7.65 | -0.65 | 119 | 5.00 |
| 10 | gold_minus_bond_ann | unsustainable_captive | -0.19 | 15.48 | -0.01 | 119 | 5.00 |
| 10 | gold_minus_bond_ann | unsustainable_free | 4.11 | 13.28 | 0.31 | 119 | 5.00 |

## 4. Does forward r beat current r as a forecast of r five years later?

RMSE of `forward_r_5y` against the realised effective rate 20 quarters later, versus the
naive forecast that r stays where it is. Forward r is better in 1/13 countries with
enough history.

| country | n | rmse_forward_r | rmse_current_r | bias_forward_r | bias_current_r | forward_better |
|---|---|---|---|---|---|---|
| AU | 24 | 1.21 | 1.09 | -0.49 | 0.65 | False |
| CA | 24 | 1.47 | 0.54 | -1.31 | 0.09 | False |
| CH | 20 | 0.94 | 0.33 | -0.92 | -0.16 | False |
| DE | 21 | 1.01 | 0.58 | -0.79 | 0.12 | False |
| EA | 21 | 1.23 | 0.58 | -1.07 | -0.05 | False |
| FR | 21 | 0.93 | 0.50 | -0.75 | 0.03 | False |
| GB | 27 | 2.74 | 2.31 | -2.06 | -1.42 | False |
| GR | 21 | 1.59 | 0.51 | 0.79 | -0.06 | False |
| IT | 21 | 0.85 | 0.42 | -0.64 | -0.08 | False |
| JP | 24 | 0.30 | 0.22 | -0.29 | 0.18 | False |
| NL | 21 | 0.81 | 0.48 | -0.64 | 0.26 | False |
| SE | 20 | 1.34 | 0.92 | -1.05 | -0.60 | False |
| US | 83 | 1.49 | 2.03 | -0.34 | 1.01 | True |

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

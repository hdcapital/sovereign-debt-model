# SYSTEM

# The model

This document is the analytical framework behind every indicator, threshold and report in
this repository. It is also the system prompt for the quarterly narrative. Nothing in the
code should contradict it; if the two drift, this document wins and the code is wrong.

## 1. The question is not "will they pay"

A government that issues its own currency and borrows in that currency cannot be forced into a
nominal default. The central bank can always create the money and absorb the debt. It does
not even need to buy at auction: primary dealers buy, the central bank buys from dealers, and
if dealers run out of balance sheet the central bank repo-finances them or the law is changed.
Nominal payment is therefore never in doubt for such a sovereign, and any analysis that starts
from "can they pay?" is answering the wrong question.

The right questions are:

1. **Is the debt trajectory sustainable?**
2. **If not, who pays, and through which channel?**

There are only three exits from an unsustainable trajectory:

- **(a) Real fiscal correction.** Primary surpluses large enough, for long enough, to bend the
  path. Politically rare without outside help (a falling currency, an easing central bank, a
  booming trading partner).
- **(b) Financial repression and inflation.** Holders are made to accept returns below
  inflation, so the real value of the stock is eroded. The transfer runs from bondholders and
  savers to the state.
- **(c) Currency collapse, hyperinflation, or formal default.** The disorderly version of (b),
  or the only version available to a state that cannot print what it owes.

Developed sovereigns with their own currency almost always end in (b). The model's job is to
say which countries are on that path, how far along they are, and when the regime is shifting.

## 2. The arithmetic

The change in the debt ratio is mechanical:

```
Δ(debt/GDP) ≈ (r − g) × (debt/GDP) − primary_balance
```

- `r` is the **average effective interest rate on the outstanding stock**: interest paid in the
  year divided by the debt stock at the start of the year. It is not the market yield.
- `g` is **nominal** GDP growth. Inflation counts fully, which is why exit (b) works.
- `primary_balance` is the budget balance excluding interest, surplus positive.

If `r > g` and the primary balance is in deficit, the debt ratio rises with no further decisions
required. Stock-flow adjustments (bank bailouts, valuation effects, below-the-line financing)
make the actual change differ from the identity, and the gap is itself a diagnostic: a country
whose debt rises faster than the identity predicts is hiding something off budget.

## 3. The lag: average versus marginal

Most sovereign debt is fixed-coupon. The average rate `r` therefore moves slowly, converging
towards the marginal market yield only as the stock rolls over. Roughly `1 / average_maturity`
of the stock reprices each year, plus all new issuance to fund the deficit.

The gap between the current average rate and the marginal yield is **interest cost already
committed**. It will show up in the budget whether or not anything else changes. So the
informative quantity is not today's `r` but **forward r**: the average rate the stock will
carry in N years if yields stay where they are and issuance continues on its current pattern.
Forward `r − g` is the model's main trajectory variable.

A country can look fine on current `r − g` and be on an unsustainable path on forward `r − g`.
The reverse also happens: a country that locked in long cheap debt can run a primary deficit
for years while the market yield is well above its average coupon.

## 4. The sorting variable: captivity

Debt/GDP on its own is almost useless as a crisis predictor. Russia defaulted at about 55% of
GDP, Argentina at about 50%, Turkey had a currency crisis at about 30%. Japan has sat above
200% for a generation without one, and the UK carried 180% through the 1920s.

What separates these cases is whether the holders of the debt can leave. **Captivity** is the
degree to which the holder base has no practical exit:

- share held by residents versus non-residents;
- share held by the central bank (the ultimate captive buyer);
- average maturity: short debt means holders are effectively free, since they are repaid soon
  and choose whether to come back;
- regulatory captivity: banks, pensions and insurers compelled by liquidity, solvency and
  collateral rules to hold government paper;
- capital controls;
- reserve-currency status: for the United States the rest of the world is the captive holder;
- the size of the domestic savings pool relative to the debt.

Captivity does not make debt sustainable. It determines **how** an unsustainable path resolves:
slowly through repression, or quickly through flight.

## 5. The quadrants

Cross the trajectory question with the captivity question:

|                                                         | Holders captive                                                                                   | Holders free                                                                                   |
|---------------------------------------------------------|---------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| **Sustainable** (forward r ≤ g, or primary surplus)     | Nothing to see. Germany, Switzerland.                                                             | Fine until the trajectory turns. Australia, Canada.                                            |
| **Unsustainable** (forward r > g with primary deficit)  | **Japan equilibrium.** Slow grind: repression, negative real rates, currency erosion, for decades. Japan, US, UK, Italy, France. | **Crisis within a cycle.** Currency collapse or default; the threshold can be 30–50% of GDP. Argentina, Turkey, Russia 1998, Greece. |

The two unsustainable cells have opposite time signatures. The captive cell is a decades-long
transfer that is easy to predict in direction and nearly impossible to time. The free cell
resolves within a business cycle. The indicators exist to catch movement between cells and
along the stage sequence below.

## 6. The stages of a spiral

Each stage has observable tells. The code's `stage_estimate` is a rule-based reading of these
tells (rules in `config/stages.yaml`).

0. **Fuel.** A persistent primary deficit that does not close in expansions.
1. **Trigger.** `r` rises above `g`. Usually because the central bank hikes against inflation,
   not because buyers vanish. Tell: marginal yield above the average coupon, so the interest
   bill is rising on autopilot.
2. **Pricing.** The market starts charging for the risk: term premium rises, breakevens rise,
   auction tails widen.
3. **Choice.** The central bank is forced to choose between the currency and the bond market.
   Tells: hikes pause with inflation still above target; purchases justified as "market
   functioning" rather than policy.
4. **Fiscal dominance.** The bank chooses the bond market. Policy rate below inflation; the
   central bank's share of the stock rising; balance sheet growing faster than nominal GDP;
   the treasury shortening issuance into bills.
5. **Flight.** The currency falls without further easing; gold at record highs in local terms;
   capital controls and repression intensify.
6. **Resolution.** One of three: a real fiscal correction (which has historically needed a
   falling currency, an easing central bank and a booming trading partner, as in Canada 1994–95
   and Sweden 1992–94); a repression grind (UK and US after 1945, Japan now); or hyperinflation
   and default.

Stages are not strictly sequential and countries can sit in one for years. The tells are
there to catch transitions, which is what the model can actually predict.

## 7. What the model predicts, and how confidently

- **Direction, long run: high confidence.** For unsustainable-captive sovereigns: negative real
  returns on nominal bonds, currency erosion against hard assets, intensifying repression, and
  central banks that tolerate above-target inflation at every forced choice.
- **Timing: low confidence.** Captive systems persist for decades. Nothing here is a timing
  signal on its own.
- **Regime transitions: moderate confidence.** Movement between quadrants and along stages is
  observable in the tells, with lead times that the backtest measures rather than assumes.

Portfolio implications follow directly. Long nominal bonds of unsustainable-captive sovereigns
are the asset that gets taxed. Real assets, equities with pricing power and gold are on the
other side of the transfer. The currency, not the bond yield, is the pressure gauge: a yield
can be pinned, a currency cannot be pinned without reserves. Expect the central bank to
surprise dovish whenever it is forced to choose.

## 8. Monetary regime changes the analysis

Every country in `config/universe.yaml` carries a `monetary_regime`:
`sovereign_float`, `currency_union_member`, `pegged`, or `dollarised`. The claim in section 1
("can always pay nominally") holds **only for `sovereign_float`**. The other regimes change the
analysis in four ways.

**Union members cannot print.** Germany, France, Italy, the Netherlands and Greece borrow in a
currency they do not individually issue. They can miss a coupon (Greece 2012), so genuine
default is a live resolution branch for them. They also cannot inflate away their own debt;
the repression exit exists only at bloc level, through the ECB, and the bloc's inflation is
shared with members who did not need it.

**Captivity for a union member is political, not structural.** The decisive captive holder is
the ECB, and the ECB stays captive only as long as the other members tolerate purchases skewed
towards the stressed member (PEPP reinvestment flexibility, the Transmission Protection
Instrument). The captivity score therefore includes a `central_bank_control` term: a country
with its own central bank gets full credit for central-bank holdings, a union member gets
partial credit, a dollarised country gets none. The weights are configuration.

**The pressure gauge swaps.** For floaters the gauge is the currency and gold in local terms.
For union members and pegs it is the **spread to the anchor** (BTP–Bund, OAT–Bund) and, inside
the euro area, TARGET2 balances. The euro's own exchange rate tells you about the bloc, not
about the member. The code computes both the bloc-level identity (the ECB's constraint: can the
euro area as a whole print its way out) and the member-level identity (who gets squeezed within
the bloc).

**Stage rules differ.** A union member at stage 3 does not show a falling currency. It shows a
widening spread and a central bank announcing a backstop. Stage 5 for a member is a spread
blow-out with TARGET2 flight, not a currency collapse. For a peg, stage 5 is reserve loss and
a parallel-rate premium. `config/stages.yaml` carries these as `regime_overrides`.

Historical regimes matter for the backtest. Italy in 1992 was a peg (ERM), not a union member;
Argentina 1991–2001 was a currency board; Sweden 1992 was an ECU peg. The universe file records
`regime_history` so each event is read under the regime in force at the time.

## 9. How the code maps to this document

| Model concept                      | Indicator block (see `docs/INDICATORS.md`)                                  |
|-----------------------------------|------------------------------------------------------------------------------|
| Arithmetic, lag, forward r         | Trajectory block: `r_effective`, `g_nominal`, `avg_coupon_gap`, `forward_r_5y`, `debt_gdp_projection_10y` |
| Captivity                          | Captivity block: holder shares, maturity, bill/linker share, `captivity_score` |
| Stage tells                        | Pressure block: real policy rate, central-bank share change, issuance shortening, currency and gold, spread to anchor |
| Quadrants and transitions          | `trajectory_unsustainable`, `holders_captive`, `quadrant`, transition flags |
| Confidence claims                  | Backtest: lead times, false positives, forward real returns by quadrant, forward-r accuracy |


# USER

# Quarterly report instructions

You are writing the quarterly Sovereign Debt Monitor for one reader. They allocate across
AUD, USD, GBP, EUR, JPY and CHF and decide whether to hold duration anywhere. The framework
is the system prompt (the model document). Relative position across the core markets matters
more than absolute prediction: the decision this feeds is which currency to be in and
whether any long nominal bond is worth owning.

## Inputs you receive

1. The latest indicator table for the core markets (CSV), with the quarter each value refers
   to and how stale it is.
2. The eight-quarter history of every indicator for every core market (CSV).
3. The transitions log (quadrant and stage changes).
4. Backtest calibration statistics: how far ahead each indicator warned before past events,
   and how well forward r forecast realised r.
5. The previous quarter's report, if one exists.
6. A list of data issues: stale or failed series.

Every number you quote must come from these inputs. Name the quarter a number refers to when
it is older than the report quarter. Do not invent data; where an input is blank, say it is
blank and reason around it.

## Structure, in this order

1. **TL;DR**: exactly five bullets, each one sentence, each with a position in it (a market,
   a direction, a reason).
2. **Cross-sectional ranking**. Two ranked lists of the core markets (the euro area counts
   once, with its members discussed inside it), worst to best positioned: (i) the currency
   over the next one to three years, (ii) long-duration nominal bonds. One compact table with
   the two ranks and a one-line reason each, then the reasoning in prose. Say what separates
   adjacent ranks. Disagree with the mechanical quadrant where the data behind it is thin
   (the table says which inputs are approximate) and say why.
3. **What changed this quarter and what it means**. Transitions first, then the largest
   moves. Map every observation to a stage, a quadrant, or an exit. The gauge is the currency
   and gold in local terms for floaters, the spread to Bunds and TARGET2 for euro members.
4. **Euro area members** through the union-member lens: they cannot print, default is a live
   branch, captivity is political (the ECB's willingness), the backstop status, spreads.
5. **Portfolio implications**, framed as which assets are on the wrong side of the transfer
   in each market: long nominals of unsustainable-captive sovereigns are taxed; real assets,
   pricing power and gold are on the other side. Be specific about which currency pairs and
   which curves.
6. **What would change my mind**: the three to five observations that would move a market
   between quadrants or stages, with the indicator and the level.
7. **Scorecard on last quarter's report**: what it got right, what it got wrong, in two or
   three sentences each. Skip if there is no previous report, and say so.
8. **Data issues**: list the stale or failed series verbatim from the input, one line each,
   and say which conclusions above they weaken.

## Tone and length

1,500 to 2,500 words after the TL;DR. Plain declarative sentences. No hedging filler, no
"it is important to note", no restating the framework; the reader wrote it. Numbers in the
text, not adjectives: "r − g at +0.4pp with a 2.9% primary deficit", not "a worrying
trajectory". Use the indicator names from the table when precision matters. Markdown with
`##` headings for the sections above; the TL;DR goes under a `## TL;DR` heading at the top.
No preamble before the TL;DR and no sign-off after the data issues.


---

# Inputs for 2026-Q3

Report quarter: 2026-Q3. Today: 2026-10-07.

## 1. Latest indicator table (core markets)

```csv
country,indicator,quarter,value,chg_1y,chg_5y,stale_quarters
US,auction_tail,2026-09-30,-0.06,-0.189,0.095,0.0
US,avg_coupon_gap,2026-09-30,1.6,1.101,2.425,0.0
US,avg_maturity_years,2025-12-31,6.0,,,3.0
US,bill_share,2026-09-30,22.373,0.832,5.385,0.0
US,breakeven_10y,2026-12-31,2.36,0.11,-0.2,0.0
US,captivity_score,2026-03-31,57.349,5.63,2.76,2.0
US,cb_balance_sheet_gdp,2026-06-30,21.196,-0.956,-14.728,1.0
US,cb_balance_sheet_growth_minus_g,2026-06-30,-4.56,8.323,-13.246,1.0
US,cb_holdings_change_4q,2026-03-31,-0.826,1.554,-4.71,2.0
US,central_bank_share,2026-03-31,14.922,-0.826,-9.622,2.0
US,debt_dynamics,2026-06-30,-0.109,-1.681,-8.393,1.0
US,debt_dynamics_residual,2026-03-31,2.702,1.346,6.323,2.0
US,debt_gdp,2026-03-31,110.8,3.1,-14.6,2.0
US,debt_gdp_projection_10y,2025-12-31,118.891,,,3.0
US,domestic_private_share,2026-03-31,55.337,2.371,11.864,2.0
US,foreign_share,2026-03-31,29.741,-1.545,-2.241,2.0
US,forward_r_5y,2025-12-31,3.766,,,3.0
US,forward_r_minus_g_5y,2025-12-31,-1.573,,,3.0
US,fx_broad_reer_12m,2026-09-30,-0.735,0.004,-0.161,0.0
US,g_nominal,2026-06-30,5.663,0.647,0.282,1.0
US,g_trend,2026-12-31,5.605,0.266,1.625,0.0
US,gold_local_ccy_12m,,,,,
US,gold_local_record,,,,,
US,holders_captive,2025-12-31,0.0,,,3.0
US,household_savings_to_debt,2026-03-31,4.311,0.056,-0.373,2.0
US,interest_to_revenue,2026-06-30,17.738,0.111,12.505,1.0
US,issuance_shortening,2026-09-30,0.706,-0.399,-1.724,0.0
US,linker_share,2026-09-30,6.827,-0.202,-0.732,0.0
US,marginal_yield,2026-12-31,5.122,1.226,3.918,0.0
US,net_foreign_asset_position_gdp,2026-06-30,-70.553,0.659,-12.384,1.0
US,policy_rate_minus_inflation,2026-09-30,0.491,-0.622,5.756,0.0
US,primary_balance_gdp,2026-06-30,-2.05,1.151,10.689,1.0
US,quadrant,2025-12-31,,,,3.0
US,r_effective,2026-09-30,3.526,0.089,1.677,0.0
US,r_minus_g,2026-06-30,-2.031,-0.458,1.53,1.0
US,stage_estimate,2026-06-30,0.0,0.0,0.0,1.0
US,term_premium_proxy,2026-12-31,1.085,0.514,1.144,0.0
US,trajectory_unsustainable,2025-12-31,0.0,,,3.0
GB,avg_coupon_gap,2026-09-30,0.039,0.866,0.937,0.0
GB,avg_maturity_years,2026-12-31,13.279,,-1.721,0.0
GB,bill_share,2026-12-31,4.946,,,0.0
GB,breakeven_10y,2026-12-31,3.247,0.04,-0.553,0.0
GB,captivity_score,2024-12-31,55.877,,,7.0
GB,cb_balance_sheet_gdp,2026-06-30,25.753,-2.047,-18.515,1.0
GB,cb_balance_sheet_growth_minus_g,2026-06-30,-7.661,7.681,-28.259,1.0
GB,cb_holdings_change_4q,2025-12-31,-4.0,0.0,,3.0
GB,central_bank_share,2025-12-31,22.0,-4.0,-11.0,3.0
GB,debt_dynamics,2026-06-30,0.797,0.081,-8.541,1.0
GB,debt_dynamics_residual,2026-06-30,0.053,2.269,8.591,1.0
GB,debt_gdp,2026-09-30,86.65,0.35,-42.95,0.0
GB,debt_gdp_projection_10y,2026-06-30,88.043,,-101.929,1.0
GB,domestic_private_share,2024-12-31,42.0,,,7.0
GB,foreign_share,2024-12-31,32.0,,,7.0
GB,forward_r_5y,2026-06-30,4.731,,3.606,1.0
GB,forward_r_minus_g_5y,2026-06-30,-0.026,,1.765,1.0
GB,fx_broad_reer_12m,2026-09-30,0.134,-0.648,-4.268,0.0
GB,fx_vs_usd_12m,2026-12-31,-1.584,-8.98,-0.398,0.0
GB,g_nominal,2026-06-30,4.057,-1.532,2.998,1.0
GB,g_trend,2026-12-31,4.811,0.131,1.721,0.0
GB,gold_local_ccy_12m,,,,,
GB,gold_local_record,,,,,
GB,holders_captive,2021-12-31,1.0,,,19.0
GB,household_savings_to_debt,,,,,
GB,interest_to_revenue,2026-09-30,11.829,-0.676,5.867,0.0
GB,issuance_shortening,,,,,
GB,linker_share,2026-12-31,24.157,,,0.0
GB,marginal_yield,2026-12-31,5.19,0.939,4.274,0.0
GB,net_foreign_asset_position_gdp,,,,,
GB,policy_rate_minus_inflation,2026-09-30,0.663,0.463,3.588,0.0
GB,primary_balance_gdp,2026-06-30,-0.081,0.92,8.492,1.0
GB,quadrant,2021-12-31,,,,19.0
GB,r_effective,2026-09-30,5.153,-0.103,3.384,0.0
GB,r_minus_g,2026-06-30,0.826,1.151,0.245,1.0
GB,stage_estimate,2026-06-30,0.0,0.0,0.0,1.0
GB,term_premium_proxy,2026-12-31,1.613,0.897,0.85,0.0
GB,trajectory_unsustainable,2021-12-31,0.0,,,19.0
JP,avg_coupon_gap,2024-12-31,0.169,0.461,1.038,7.0
JP,avg_maturity_years,2024-12-31,9.4,,,7.0
JP,bill_share,2026-06-30,46.553,0.475,,1.0
JP,breakeven_10y,,,,,
JP,captivity_score,2025-12-31,71.493,,,3.0
JP,cb_balance_sheet_gdp,2026-06-30,98.272,-16.181,-32.373,1.0
JP,cb_balance_sheet_growth_minus_g,2026-06-30,-14.677,-5.348,-24.461,1.0
JP,cb_holdings_change_4q,2025-12-31,-2.0,-3.0,,3.0
JP,central_bank_share,2025-12-31,46.0,-2.0,,3.0
JP,debt_dynamics,2024-12-31,-4.827,5.25,-7.352,7.0
JP,debt_dynamics_residual,2024-12-31,-8.073,-10.15,-9.348,7.0
JP,debt_gdp,2026-03-31,175.6,-15.4,-53.3,2.0
JP,debt_gdp_projection_10y,2024-12-31,183.336,,,7.0
JP,domestic_private_share,2025-12-31,41.0,,,3.0
JP,foreign_share,2025-12-31,13.0,,,3.0
JP,forward_r_5y,2024-12-31,0.814,,,7.0
JP,forward_r_minus_g_5y,2024-12-31,-0.787,,,7.0
JP,fx_broad_reer_12m,2026-09-30,-8.076,-5.235,0.596,0.0
JP,fx_vs_usd_12m,2026-12-31,-0.64,-1.004,9.762,0.0
JP,g_nominal,2026-06-30,3.814,-0.715,3.126,1.0
JP,g_trend,2026-12-31,1.82,0.074,0.902,0.0
JP,gold_local_ccy_12m,,,,,
JP,gold_local_record,,,,,
JP,holders_captive,2021-12-31,1.0,,,19.0
JP,household_savings_to_debt,,,,,
JP,interest_to_revenue,2024-12-31,3.976,0.091,-0.907,7.0
JP,issuance_shortening,2026-06-30,-3.328,5.333,,1.0
JP,linker_share,,,,,
JP,marginal_yield,2026-12-31,2.634,0.927,2.618,0.0
JP,net_foreign_asset_position_gdp,,,,,
JP,policy_rate_minus_inflation,2026-09-30,-0.898,1.48,-0.574,0.0
JP,primary_balance_gdp,2024-12-31,-0.206,0.76,1.122,7.0
JP,quadrant,2021-12-31,,,,19.0
JP,r_effective,2024-12-31,0.738,0.038,-0.069,7.0
JP,r_minus_g,2024-12-31,-2.409,2.682,-2.986,7.0
JP,stage_estimate,2024-12-31,0.0,0.0,0.0,7.0
JP,term_premium_proxy,2026-12-31,1.173,0.274,0.989,0.0
JP,trajectory_unsustainable,2021-12-31,0.0,,,19.0
AU,avg_coupon_gap,2023-09-30,0.34,-0.167,1.462,12.0
AU,avg_maturity_years,2024-12-31,7.0,,-0.2,7.0
AU,bill_share,,,,,
AU,breakeven_10y,2026-06-30,2.365,0.24,0.21,1.0
AU,captivity_score,2024-12-31,43.473,,,7.0
AU,cb_balance_sheet_gdp,2023-09-30,20.615,-4.993,10.985,12.0
AU,cb_balance_sheet_growth_minus_g,2023-09-30,-20.932,-12.52,-21.441,12.0
AU,cb_holdings_change_4q,2025-12-31,-4.0,,,3.0
AU,central_bank_share,2025-12-31,24.0,-4.0,14.0,3.0
AU,debt_dynamics,2023-09-30,-2.067,1.692,-1.681,12.0
AU,debt_dynamics_residual,2023-09-30,-0.733,3.408,-1.519,12.0
AU,debt_gdp,2026-03-31,51.1,0.1,-8.1,2.0
AU,debt_gdp_projection_10y,2022-12-31,50.792,,,15.0
AU,domestic_private_share,2024-12-31,27.0,,,7.0
AU,foreign_share,2024-12-31,45.0,,,7.0
AU,forward_r_5y,2022-12-31,3.26,,,15.0
AU,forward_r_minus_g_5y,2022-12-31,-1.476,,,15.0
AU,fx_broad_reer_12m,2026-09-30,8.15,9.555,8.342,0.0
AU,fx_vs_usd_12m,2026-12-31,3.861,-3.795,9.652,0.0
AU,g_nominal,2023-09-30,7.346,-4.952,2.725,12.0
AU,g_trend,2026-12-31,6.506,0.525,2.516,0.0
AU,gold_local_ccy_12m,,,,,
AU,gold_local_record,,,,,
AU,holders_captive,2022-12-31,0.0,,,15.0
AU,household_savings_to_debt,,,,,
AU,interest_to_revenue,2023-09-30,4.145,0.456,0.366,12.0
AU,issuance_shortening,,,,,
AU,linker_share,,,,,
AU,marginal_yield,2026-09-30,5.136,1.276,4.127,0.0
AU,net_foreign_asset_position_gdp,,,,,
AU,policy_rate_minus_inflation,2026-06-30,0.408,-1.347,4.122,1.0
AU,primary_balance_gdp,2024-12-31,-0.524,-0.76,2.594,7.0
AU,quadrant,2022-12-31,,,,15.0
AU,r_effective,2023-09-30,3.204,0.692,-0.316,12.0
AU,r_minus_g,2023-09-30,-4.142,5.644,-3.041,12.0
AU,stage_estimate,2024-12-31,0.0,0.0,0.0,7.0
AU,term_premium_proxy,2026-09-30,0.786,-0.185,-0.804,0.0
AU,trajectory_unsustainable,2022-12-31,0.0,,,15.0
CA,avg_coupon_gap,2023-09-30,0.536,-0.054,1.799,12.0
CA,avg_maturity_years,2024-12-31,6.8,,0.8,7.0
CA,bill_share,,,,,
CA,breakeven_10y,2026-12-31,1.96,0.41,0.4,0.0
CA,captivity_score,2024-12-31,53.538,,,7.0
CA,cb_balance_sheet_gdp,2023-09-30,11.315,-4.314,6.144,12.0
CA,cb_balance_sheet_growth_minus_g,2023-09-30,-28.57,-2.281,-27.886,12.0
CA,cb_holdings_change_4q,2021-12-31,4.0,,,19.0
CA,central_bank_share,2025-12-31,22.0,,-16.0,3.0
CA,debt_dynamics,2023-09-30,-2.956,10.62,1.676,12.0
CA,debt_dynamics_residual,2023-09-30,-0.544,6.08,-3.376,12.0
CA,debt_gdp,2026-03-31,97.1,1.6,-13.8,2.0
CA,debt_gdp_projection_10y,2022-12-31,47.416,,,15.0
CA,domestic_private_share,2021-12-31,36.0,,,19.0
CA,foreign_share,2024-12-31,28.0,,,7.0
CA,forward_r_5y,2022-12-31,3.297,,,15.0
CA,forward_r_minus_g_5y,2022-12-31,-0.912,,,15.0
CA,fx_broad_reer_12m,2026-09-30,-1.089,1.833,-4.406,0.0
CA,fx_vs_usd_12m,2026-12-31,-3.796,-8.813,-3.608,0.0
CA,g_nominal,2023-09-30,3.509,-9.729,-1.737,12.0
CA,g_trend,2026-12-31,5.399,0.634,2.065,0.0
CA,gold_local_ccy_12m,,,,,
CA,gold_local_record,,,,,
CA,holders_captive,2015-12-31,0.0,,,43.0
CA,household_savings_to_debt,,,,,
CA,interest_to_revenue,2023-09-30,7.678,1.162,0.508,12.0
CA,issuance_shortening,,,,,
CA,linker_share,,,,,
CA,marginal_yield,2026-12-31,3.68,0.596,2.448,0.0
CA,net_foreign_asset_position_gdp,,,,,
CA,policy_rate_minus_inflation,2026-09-30,-0.721,-0.863,3.411,0.0
CA,primary_balance_gdp,2024-12-31,1.519,-1.791,-1.439,7.0
CA,quadrant,2015-12-31,,,,43.0
CA,r_effective,2023-09-30,3.83,1.008,0.231,12.0
CA,r_minus_g,2023-09-30,0.321,10.737,1.968,12.0
CA,stage_estimate,2024-12-31,0.0,0.0,0.0,7.0
CA,term_premium_proxy,2026-12-31,0.7,-0.14,0.23,0.0
CA,trajectory_unsustainable,2015-12-31,0.0,,,43.0
CH,avg_coupon_gap,2023-09-30,-0.461,-0.091,0.817,12.0
CH,avg_maturity_years,2024-12-31,11.0,,,7.0
CH,bill_share,,,,,
CH,breakeven_10y,,,,,
CH,captivity_score,2024-12-31,56.044,,,7.0
CH,cb_balance_sheet_gdp,2023-09-30,103.686,-11.181,-11.637,12.0
CH,cb_balance_sheet_growth_minus_g,2023-09-30,-9.963,11.379,-6.353,12.0
CH,cb_holdings_change_4q,2017-06-30,-0.005,-0.005,-0.005,37.0
CH,central_bank_share,2024-12-31,0.0,,,7.0
CH,debt_dynamics,2023-09-30,-0.907,1.553,1.404,12.0
CH,debt_dynamics_residual,2023-09-30,2.007,4.147,2.396,12.0
CH,debt_gdp,2026-03-31,26.5,1.0,-3.7,2.0
CH,debt_gdp_projection_10y,2020-12-31,52.044,,,23.0
CH,domestic_private_share,2024-12-31,85.0,,,7.0
CH,foreign_share,2024-12-31,15.0,,,7.0
CH,forward_r_5y,2020-12-31,0.015,,,23.0
CH,forward_r_minus_g_5y,2020-12-31,-1.325,,,23.0
CH,fx_broad_reer_12m,2026-09-30,-3.011,-3.912,1.387,0.0
CH,fx_vs_usd_12m,2026-12-31,-4.305,-18.569,-0.97,0.0
CH,g_nominal,2023-09-30,2.357,-3.696,-1.171,12.0
CH,g_trend,2026-12-31,2.388,0.184,1.043,0.0
CH,gold_local_ccy_12m,,,,,
CH,gold_local_record,,,,,
CH,holders_captive,2016-06-30,1.0,,,41.0
CH,household_savings_to_debt,,,,,
CH,interest_to_revenue,2023-09-30,1.148,0.061,0.172,12.0
CH,issuance_shortening,,,,,
CH,linker_share,,,,,
CH,marginal_yield,2026-09-30,0.514,0.321,0.899,0.0
CH,net_foreign_asset_position_gdp,,,,,
CH,policy_rate_minus_inflation,2026-09-30,-1.029,-0.805,0.663,0.0
CH,primary_balance_gdp,2024-12-31,0.936,0.443,-0.658,7.0
CH,quadrant,2016-06-30,,,,41.0
CH,r_effective,2023-09-30,1.578,0.259,0.48,12.0
CH,r_minus_g,2023-09-30,-0.778,3.954,1.651,12.0
CH,stage_estimate,2024-12-31,0.0,0.0,0.0,7.0
CH,term_premium_proxy,2026-09-30,0.514,0.053,-0.032,0.0
CH,trajectory_unsustainable,2016-06-30,0.0,,,41.0
EA,avg_coupon_gap,2026-03-31,0.714,0.309,2.477,2.0
EA,avg_maturity_years,2024-12-31,7.634,,,7.0
EA,bill_share,2022-03-31,7.495,-1.51,0.892,18.0
EA,breakeven_10y,,,,,
EA,captivity_score,2024-12-31,43.188,,,7.0
EA,cb_balance_sheet_gdp,2026-03-31,39.299,-1.898,-24.981,2.0
EA,cb_balance_sheet_growth_minus_g,2026-03-31,-4.765,3.21,-52.714,2.0
EA,cb_holdings_change_4q,2026-03-31,-2.385,0.34,-2.353,2.0
EA,central_bank_share,2026-03-31,12.402,-2.385,-7.413,2.0
EA,debt_dynamics,2026-03-31,0.231,0.335,-11.564,2.0
EA,debt_dynamics_residual,2026-03-31,0.669,0.765,-2.536,2.0
EA,debt_gdp,2026-03-31,85.6,0.9,-26.8,2.0
EA,debt_gdp_projection_10y,,,,,
EA,domestic_private_share,2024-12-31,40.582,,,7.0
EA,ecb_backstop_active,2026-12-31,1.0,0.0,0.0,0.0
EA,foreign_share,2024-12-31,43.854,,,7.0
EA,forward_r_5y,,,,,
EA,forward_r_minus_g_5y,,,,,
EA,fx_broad_reer_12m,2026-09-30,-1.195,-4.311,0.953,0.0
EA,fx_vs_usd_12m,2026-12-31,-4.064,-17.445,3.393,0.0
EA,g_nominal,2026-03-31,3.428,-0.294,7.255,2.0
EA,g_trend,2026-12-31,4.16,0.093,1.98,0.0
EA,gold_local_ccy_12m,,,,,
EA,gold_local_record,,,,,
EA,holders_captive,,,,,
EA,household_savings_to_debt,,,,,
EA,interest_to_revenue,,,,,
EA,issuance_shortening,2022-03-31,1.21,-2.053,2.313,18.0
EA,linker_share,,,,,
EA,marginal_yield,2026-09-30,3.425,0.738,3.674,0.0
EA,net_foreign_asset_position_gdp,,,,,
EA,policy_rate_minus_inflation,2026-09-30,-0.902,-0.673,2.461,0.0
EA,primary_balance_gdp,2026-03-31,-1.164,-0.093,5.452,2.0
EA,quadrant,,,,,
EA,r_effective,2026-03-31,2.326,-0.012,0.836,2.0
EA,r_minus_g,2026-03-31,-1.102,0.282,-6.419,2.0
EA,stage_estimate,2026-03-31,0.0,0.0,0.0,2.0
EA,term_premium_proxy,2026-09-30,0.443,-0.717,-0.342,0.0
EA,trajectory_unsustainable,,,,,
DE,avg_coupon_gap,2026-03-31,1.059,0.099,2.474,2.0
DE,avg_maturity_years,2024-12-31,7.0,,,7.0
DE,bill_share,2022-03-31,8.516,-1.468,4.713,18.0
DE,breakeven_10y,,,,,
DE,captivity_score,2024-12-31,31.899,,,7.0
DE,cb_balance_sheet_gdp,,,,,
DE,cb_balance_sheet_growth_minus_g,,,,,
DE,cb_holdings_change_4q,2026-03-31,-3.194,0.115,-3.001,2.0
DE,central_bank_share,2026-03-31,16.067,-3.194,-8.887,2.0
DE,debt_dynamics,2026-03-31,1.104,0.442,-6.201,2.0
DE,debt_dynamics_residual,2026-03-31,0.496,1.858,-1.799,2.0
DE,debt_gdp,2026-03-31,58.7,1.6,-17.3,2.0
DE,debt_gdp_projection_10y,2024-12-31,62.919,,,7.0
DE,domestic_private_share,2024-12-31,32.891,,,7.0
DE,ecb_backstop_active,2026-09-30,1.0,0.0,0.0,0.0
DE,foreign_share,2024-12-31,47.0,,,7.0
DE,forward_r_5y,2024-12-31,2.017,,,7.0
DE,forward_r_minus_g_5y,2024-12-31,-1.964,,,7.0
DE,fx_broad_reer_12m,2026-09-30,-1.403,-3.132,-0.918,0.0
DE,g_nominal,2026-06-30,3.532,0.542,1.273,1.0
DE,g_trend,2026-09-30,3.949,0.011,1.052,0.0
DE,gold_local_ccy_12m,,,,,
DE,gold_local_record,,,,,
DE,holders_captive,2024-12-31,0.0,,,7.0
DE,household_savings_to_debt,,,,,
DE,interest_to_revenue,2024-12-31,2.233,0.336,0.553,7.0
DE,issuance_shortening,2022-03-31,3.246,-2.711,4.093,18.0
DE,linker_share,,,,,
DE,marginal_yield,2026-09-30,3.185,0.492,3.548,0.0
DE,net_foreign_asset_position_gdp,,,,,
DE,policy_rate_minus_inflation,2026-09-30,-0.36,0.063,3.752,0.0
DE,primary_balance_gdp,2026-03-31,-2.01,-0.671,2.896,2.0
DE,quadrant,2024-12-31,,,,7.0
DE,r_effective,2026-03-31,1.851,0.07,0.8,2.0
DE,r_minus_g,2026-03-31,-1.586,-0.415,-5.199,2.0
DE,spread_to_anchor_bp,,,,,
DE,stage_estimate,2026-03-31,0.0,0.0,0.0,2.0
DE,target2_balance_gdp,2026-06-30,22.591,-0.978,-8.199,1.0
DE,term_premium_proxy,2026-09-30,0.935,0.242,1.298,0.0
DE,trajectory_unsustainable,2024-12-31,0.0,,,7.0
FR,avg_coupon_gap,2026-03-31,1.671,0.226,3.007,2.0
FR,avg_maturity_years,2024-12-31,8.5,,,7.0
FR,bill_share,2022-03-31,9.401,-1.735,-0.917,18.0
FR,breakeven_10y,,,,,
FR,captivity_score,2024-12-31,28.793,,,7.0
FR,cb_balance_sheet_gdp,,,,,
FR,cb_balance_sheet_growth_minus_g,,,,,
FR,cb_holdings_change_4q,2026-03-31,-2.176,0.3,-2.026,2.0
FR,central_bank_share,2026-03-31,10.867,-2.176,-7.11,2.0
FR,debt_dynamics,2026-03-31,3.021,0.155,-11.043,2.0
FR,debt_dynamics_residual,2026-03-31,-0.421,0.945,-4.357,2.0
FR,debt_gdp,2026-03-31,109.4,2.6,-23.5,2.0
FR,debt_gdp_projection_10y,2024-12-31,137.555,,,7.0
FR,domestic_private_share,2024-12-31,32.148,,,7.0
FR,ecb_backstop_active,2026-09-30,1.0,0.0,0.0,0.0
FR,foreign_share,2024-12-31,54.0,,,7.0
FR,forward_r_5y,2024-12-31,2.576,,,7.0
FR,forward_r_minus_g_5y,2024-12-31,-0.567,,,7.0
FR,fx_broad_reer_12m,2026-09-30,-0.323,-0.459,1.623,0.0
FR,g_nominal,2026-06-30,1.857,-0.603,-1.504,1.0
FR,g_trend,2026-09-30,3.209,0.03,1.524,0.0
FR,gold_local_ccy_12m,,,,,
FR,gold_local_record,,,,,
FR,holders_captive,2024-12-31,0.0,,,7.0
FR,household_savings_to_debt,,,,,
FR,interest_to_revenue,2024-12-31,3.983,0.321,1.124,7.0
FR,issuance_shortening,2022-03-31,2.074,-2.021,3.981,18.0
FR,linker_share,,,,,
FR,marginal_yield,2026-09-30,4.0,0.49,3.96,0.0
FR,net_foreign_asset_position_gdp,,,,,
FR,policy_rate_minus_inflation,2026-09-30,-1.11,-1.957,1.053,0.0
FR,primary_balance_gdp,2026-03-31,-2.96,0.635,5.697,2.0
FR,quadrant,2024-12-31,,,,7.0
FR,r_effective,2026-03-31,1.969,-0.016,0.703,2.0
FR,r_minus_g,2026-03-31,0.057,0.75,-4.649,2.0
FR,spread_to_anchor_bp,2026-09-30,81.5,-0.2,41.2,0.0
FR,stage_estimate,2026-03-31,0.0,0.0,0.0,2.0
FR,target2_balance_gdp,2026-06-30,-6.512,0.041,-5.685,1.0
FR,term_premium_proxy,2026-09-30,1.75,0.24,1.71,0.0
FR,trajectory_unsustainable,2024-12-31,0.0,,,7.0
IT,avg_coupon_gap,2026-03-31,0.891,0.016,2.578,2.0
IT,avg_maturity_years,2024-12-31,7.1,,,7.0
IT,bill_share,2022-03-31,4.835,-0.783,-1.138,18.0
IT,breakeven_10y,,,,,
IT,captivity_score,2024-12-31,41.028,,,7.0
IT,cb_balance_sheet_gdp,,,,,
IT,cb_balance_sheet_growth_minus_g,,,,,
IT,cb_holdings_change_4q,2026-03-31,-1.82,0.615,-2.01,2.0
IT,central_bank_share,2026-03-31,9.524,-1.82,-6.341,2.0
IT,debt_dynamics,2026-03-31,-0.545,-0.811,-19.768,2.0
IT,debt_dynamics_residual,2026-03-31,1.545,-2.189,-6.932,2.0
IT,debt_gdp,2026-03-31,137.3,1.0,-38.9,2.0
IT,debt_gdp_projection_10y,2024-12-31,132.366,,,7.0
IT,domestic_private_share,2024-12-31,57.941,,,7.0
IT,ecb_backstop_active,2026-09-30,1.0,0.0,0.0,0.0
IT,foreign_share,2024-12-31,30.0,,,7.0
IT,forward_r_5y,2024-12-31,3.183,,,7.0
IT,forward_r_minus_g_5y,2024-12-31,0.114,,,7.0
IT,fx_broad_reer_12m,2026-09-30,-0.31,-0.904,1.329,0.0
IT,g_nominal,2026-06-30,2.671,0.222,0.02,1.0
IT,g_trend,2026-09-30,3.263,0.085,2.716,0.0
IT,gold_local_ccy_12m,,,,,
IT,gold_local_record,,,,,
IT,holders_captive,2024-12-31,0.0,,,7.0
IT,household_savings_to_debt,,,,,
IT,interest_to_revenue,2024-12-31,8.218,0.449,1.1,7.0
IT,issuance_shortening,2022-03-31,-1.025,-0.846,0.064,18.0
IT,linker_share,,,,,
IT,marginal_yield,2026-09-30,3.986,0.427,3.209,0.0
IT,net_foreign_asset_position_gdp,,,,,
IT,policy_rate_minus_inflation,2026-09-30,-1.257,-1.688,1.285,0.0
IT,primary_balance_gdp,2026-03-31,0.699,0.314,7.828,2.0
IT,quadrant,2024-12-31,,,,7.0
IT,r_effective,2026-03-31,2.842,-0.17,0.451,2.0
IT,r_minus_g,2026-03-31,0.114,-0.379,-8.031,2.0
IT,spread_to_anchor_bp,2026-09-30,80.1,-6.5,-33.9,0.0
IT,stage_estimate,2026-03-31,0.0,0.0,0.0,2.0
IT,target2_balance_gdp,2026-06-30,-14.635,3.012,15.131,1.0
IT,term_premium_proxy,2026-09-30,1.736,0.177,0.959,0.0
IT,trajectory_unsustainable,2024-12-31,0.0,,,7.0
NL,avg_coupon_gap,2026-03-31,1.236,-0.025,2.932,2.0
NL,avg_maturity_years,2024-12-31,8.5,,,7.0
NL,bill_share,2022-03-31,5.811,-5.026,1.235,18.0
NL,breakeven_10y,,,,,
NL,captivity_score,2024-12-31,39.416,,,7.0
NL,cb_balance_sheet_gdp,,,,,
NL,cb_balance_sheet_growth_minus_g,,,,,
NL,cb_holdings_change_4q,2026-03-31,-3.443,-1.3,-3.186,2.0
NL,central_bank_share,2026-03-31,19.909,-3.443,-7.492,2.0
NL,debt_dynamics,2026-03-31,-0.242,1.176,-6.242,2.0
NL,debt_dynamics_residual,2026-03-31,0.442,1.024,1.842,2.0
NL,debt_gdp,2026-03-31,40.7,0.2,-19.9,2.0
NL,debt_gdp_projection_10y,2024-12-31,31.688,,,7.0
NL,domestic_private_share,2024-12-31,34.661,,,7.0
NL,ecb_backstop_active,2026-09-30,1.0,0.0,0.0,0.0
NL,foreign_share,2024-12-31,42.0,,,7.0
NL,forward_r_5y,2024-12-31,2.051,,,7.0
NL,forward_r_minus_g_5y,2024-12-31,-2.93,,,7.0
NL,fx_broad_reer_12m,2026-09-30,-0.559,-3.799,1.271,0.0
NL,g_nominal,2026-06-30,4.782,-0.896,1.328,1.0
NL,g_trend,2026-09-30,5.412,0.181,2.801,0.0
NL,gold_local_ccy_12m,,,,,
NL,gold_local_record,,,,,
NL,holders_captive,2024-12-31,0.0,,,7.0
NL,household_savings_to_debt,,,,,
NL,interest_to_revenue,2024-12-31,1.626,0.071,-0.142,7.0
NL,issuance_shortening,2022-03-31,-2.064,-6.169,-1.795,18.0
NL,linker_share,,,,,
NL,marginal_yield,2026-09-30,3.285,0.402,3.624,0.0
NL,net_foreign_asset_position_gdp,,,,,
NL,policy_rate_minus_inflation,2026-09-30,-0.81,0.368,1.895,0.0
NL,primary_balance_gdp,2026-03-31,-0.954,-0.562,3.264,2.0
NL,quadrant,2024-12-31,,,,7.0
NL,r_effective,2026-03-31,1.791,0.116,0.426,2.0
NL,r_minus_g,2026-03-31,-2.953,1.304,-6.135,2.0
NL,spread_to_anchor_bp,2026-09-30,10.0,-9.0,7.6,0.0
NL,stage_estimate,2026-03-31,0.0,0.0,0.0,2.0
NL,target2_balance_gdp,2026-06-30,4.14,-3.338,2.511,1.0
NL,term_premium_proxy,2026-09-30,1.035,0.152,1.374,0.0
NL,trajectory_unsustainable,2024-12-31,0.0,,,7.0

```

## 2. Eight-quarter history

```csv
quarter,country,debt_gdp,primary_balance_gdp,r_effective,g_nominal,r_minus_g,debt_dynamics,debt_dynamics_residual,marginal_yield,avg_coupon_gap,forward_r_5y,g_trend,forward_r_minus_g_5y,debt_gdp_projection_10y,foreign_share,central_bank_share,domestic_private_share,avg_maturity_years,bill_share,linker_share,household_savings_to_debt,net_foreign_asset_position_gdp,captivity_score,term_premium_proxy,breakeven_10y,policy_rate_minus_inflation,cb_balance_sheet_gdp,cb_balance_sheet_growth_minus_g,cb_holdings_change_4q,issuance_shortening,fx_vs_usd_12m,fx_broad_reer_12m,gold_local_ccy_12m,gold_local_record,auction_tail,spread_to_anchor_bp,target2_balance_gdp,ecb_backstop_active,fx_reserves_12m,interest_to_revenue,stage_estimate,quadrant,trajectory_unsustainable,holders_captive
2025-03-31,US,107.7,-3.256,3.445,5.358,-1.913,1.245,1.355,4.094,0.649,3.905,5.281,-1.375,125.011,31.286,15.748,52.966,6.0,21.546,7.125,4.255,-70.482,51.72,0.499,2.38,1.984,22.675,-15.305,-2.38,4.85,,4.085,,,0.006,,,,,18.03,0.0,sustainable_free,0.0,0.0
2025-06-30,US,106.3,-3.201,3.442,5.015,-1.573,1.573,1.227,4.032,0.59,3.86,5.29,-1.43,122.728,31.383,15.643,52.974,6.0,20.195,7.264,4.431,-71.212,51.996,0.46,2.29,1.706,22.152,-12.884,-1.777,2.237,,-2.323,,,-0.095,,,,,17.627,0.0,sustainable_free,0.0,0.0
2025-09-30,US,109.7,-2.887,3.437,5.044,-1.606,1.157,0.843,3.936,0.499,3.788,5.31,-1.522,121.791,30.489,14.884,54.628,6.0,21.541,7.029,4.415,-72.318,51.772,0.503,2.36,1.112,21.682,-11.705,-1.758,1.105,,-0.739,,,0.129,,,,,17.535,0.0,sustainable_free,0.0,0.0
2025-12-31,US,110.9,-2.519,3.467,5.038,-1.572,0.85,3.85,3.896,0.429,3.766,5.339,-1.573,118.891,30.027,14.669,55.304,6.0,21.641,7.052,4.403,-70.877,51.863,0.571,2.25,0.948,21.518,-8.601,-1.372,0.107,,-5.441,,,0.046,,,,,17.547,0.0,sustainable_free,0.0,0.0
2026-03-31,US,110.8,-2.351,3.466,5.279,-1.813,0.398,2.702,4.096,0.63,,5.389,,,29.741,14.922,55.337,,22.122,6.779,4.311,-67.964,57.349,0.654,2.3,0.369,21.272,-6.512,-0.826,-0.385,,-4.423,,,0.065,,,,,17.192,0.0,,,
2026-06-30,US,,-2.05,3.632,5.663,-2.031,-0.109,,4.32,0.688,,5.46,,,,,,,21.536,6.967,,-70.553,,0.697,2.24,0.094,21.196,-4.56,,0.209,,-0.194,,,0.044,,,,,17.738,0.0,,,
2026-09-30,US,,,3.526,,,,,5.126,1.6,,5.533,,,,,,,22.373,6.827,,,,1.077,2.36,0.491,,,,0.706,,-0.735,,,-0.06,,,,,,,,,
2026-12-31,US,,,,,,,,5.122,,,5.605,,,,,,,,,,,,1.085,2.36,,,,,,,,,,,,,,,,,,,
2025-03-31,GB,85.1,-0.838,5.07,5.452,-0.382,0.502,-3.702,4.453,-0.617,,4.538,,,,22.0,,,,,,,,0.153,3.298,1.868,28.846,-13.35,-4.0,,2.05,2.229,,,,,,,,12.051,0.0,,,
2025-06-30,GB,86.6,-1.001,5.265,5.589,-0.324,0.716,-2.216,4.194,-1.071,,4.575,,,,22.0,,,,,,,,0.191,3.25,0.671,27.8,-15.342,-4.0,,8.56,3.21,,,,,,,,12.457,0.0,,,
2025-09-30,GB,86.3,-0.959,5.256,5.389,-0.132,0.842,-3.742,4.429,-0.827,,4.629,,,,22.0,,,,,,,,0.691,3.224,0.2,26.873,-14.986,-4.0,,0.328,0.782,,,,,,,,12.505,0.0,,,
2025-12-31,GB,88.9,-0.666,5.256,4.807,0.449,1.052,2.048,4.251,-1.005,,4.68,,,,22.0,,,,,,,,0.716,3.207,0.431,25.982,-10.533,-4.0,,7.396,-0.437,,,,,,,,11.997,0.0,,,
2026-03-31,GB,86.5,-0.201,5.11,4.367,0.743,0.833,0.567,4.692,-0.417,4.911,4.724,0.187,90.083,,,,13.279,4.946,24.157,,,,1.112,3.301,0.453,25.947,-10.487,,,2.233,-0.867,,,,,,,,11.402,0.0,,,
2026-06-30,GB,87.45,-0.081,4.884,4.057,0.826,0.797,0.053,4.556,-0.327,4.731,4.756,-0.026,88.043,,,,13.279,4.946,24.157,,,,0.992,3.106,1.158,25.753,-7.661,,,-3.374,-2.681,,,,,,,,11.072,0.0,,,
2026-09-30,GB,86.65,,5.153,,,,,5.192,0.039,,4.79,,,,,,13.279,4.946,24.157,,,,1.621,3.242,0.663,,,,,-1.309,0.134,,,,,,,,11.829,,,,
2026-12-31,GB,,,,,,,,5.19,,,4.811,,,,,,13.279,4.946,24.157,,,,1.613,3.247,,,,,,-1.584,,,,,,,,,,,,,
2025-03-31,JP,191.0,,,3.763,,,,1.24,,,1.642,,,13.0,46.0,41.0,,46.504,,,,70.395,0.643,,-3.049,117.905,-7.287,-2.0,-18.252,0.881,3.312,,,,,,,,,,,,
2025-06-30,JP,188.7,,,4.529,,,,1.176,,,1.69,,,13.0,46.0,41.0,,46.078,,,,70.591,0.716,,-2.916,114.453,-9.329,-2.0,-8.661,11.59,7.406,,,,,,,,,,,,
2025-09-30,JP,183.2,,,4.676,,,,1.38,,,1.723,,,13.0,46.0,41.0,,43.391,,,,71.831,0.704,,-2.378,109.867,-12.312,-2.0,-1.007,-3.19,-2.841,,,,,,,,,,,,
2025-12-31,JP,177.7,,,4.654,,,,1.706,,,1.746,,,13.0,46.0,41.0,,44.124,,,,71.493,0.899,,-1.272,105.998,-14.041,-2.0,-7.867,0.364,-5.497,,,,,,,,,,,,
2026-03-31,JP,175.6,,,4.276,,,,1.97,,,1.77,,,,,,,48.393,,,,,0.991,,-0.661,102.729,-13.422,,-5.201,-5.771,-10.388,,,,,,,,,,,,
2026-06-30,JP,,,,3.814,,,,2.167,,,1.801,,,,,,,46.553,,,,,1.308,,-0.702,98.272,-14.677,,-3.328,-11.34,-11.631,,,,,,,,,,,,
2026-09-30,JP,,,,,,,,2.615,,,1.803,,,,,,,,,,,,1.105,,-0.898,,,,,-5.901,-8.076,,,,,,,,,,,,
2026-12-31,JP,,,,,,,,2.634,,,1.82,,,,,,,,,,,,1.173,,,,,,,-0.64,,,,,,,,,,,,,
2025-03-31,AU,51.0,,,,,,,4.542,,,5.587,,,,24.0,,,,,,,,0.442,,1.7,,,-4.0,,-3.858,-2.783,,,,,,,,,,,,
2025-06-30,AU,50.2,,,,,,,3.861,,,5.712,,,,24.0,,,,,,,,0.971,2.125,1.755,,,-4.0,,-1.117,-4.985,,,,,,,,,,,,
2025-09-30,AU,51.4,,,,,,,3.861,,,5.844,,,,24.0,,,,,,,,0.971,2.125,0.381,,,-4.0,,-4.761,-1.405,,,,,,,,,,,,
2025-12-31,AU,50.6,,,,,,,4.84,,,5.981,,,,24.0,,,,,,,,1.24,,-0.026,,,-4.0,,7.656,2.535,,,,,,,,,,,,
2026-03-31,AU,51.1,,,,,,,5.047,,,6.124,,,,,,,,,,,,0.947,,0.006,,,,,8.997,10.153,,,,,,,,,,,,
2026-06-30,AU,,,,,,,,4.711,,,6.262,,,,,,,,,,,,0.318,2.365,0.408,,,,,4.87,8.958,,,,,,,,,,,,
2026-09-30,AU,,,,,,,,5.136,,,6.401,,,,,,,,,,,,0.786,,,,,,,5.68,8.15,,,,,,,,,,,,
2026-12-31,AU,,,,,,,,,,,6.506,,,,,,,,,,,,,,,,,,,3.861,,,,,,,,,,,,,
2025-03-31,CA,95.5,,,,,,,2.766,,,4.446,,,,22.0,,,,,,,,0.51,1.6,0.435,,,,,-5.835,-4.373,,,,,,,,,,,,
2025-06-30,CA,95.2,,,,,,,3.004,,,4.503,,,,22.0,,,,,,,,0.69,1.63,0.891,,,,,0.47,-1.716,,,,,,,,,,,,
2025-09-30,CA,96.1,,,,,,,2.89,,,4.61,,,,22.0,,,,,,,,0.7,1.51,0.141,,,,,-2.987,-2.922,,,,,,,,,,,,
2025-12-31,CA,96.1,,,,,,,3.084,,,4.766,,,,22.0,,,,,,,,0.84,1.55,-0.107,,,,,5.018,0.432,,,,,,,,,,,,
2026-03-31,CA,97.1,,,,,,,3.204,,,4.935,,,,,,,,,,,,0.64,1.63,-0.135,,,,,3.053,1.891,,,,,,,,,,,,
2026-06-30,CA,,,,,,,,3.124,,,5.107,,,,,,,,,,,,0.64,1.67,-0.548,,,,,-4.118,-3.431,,,,,,,,,,,,
2026-09-30,CA,,,,,,,,3.742,,,5.269,,,,,,,,,,,,0.62,2.01,-0.721,,,,,-1.992,-1.089,,,,,,,,,,,,
2026-12-31,CA,,,,,,,,3.68,,,5.399,,,,,,,,,,,,0.7,1.96,,,,,,-3.796,,,,,,,,,,,,,
2025-03-31,CH,25.5,,,,,,,0.35,,,2.066,,,,,,,,,,,,0.411,,-0.092,,,,,1.945,-1.146,,,,,,,,,,,,
2025-06-30,CH,25.7,,,,,,,0.222,,,2.099,,,,,,,,,,,,0.471,,-0.078,,,,,13.278,2.158,,,,,,,,,,,,
2025-09-30,CH,25.8,,,,,,,0.194,,,2.145,,,,,,,,,,,,0.461,,-0.224,,,,,6.001,0.902,,,,,,,,,,,,
2025-12-31,CH,26.2,,,,,,,0.374,,,2.204,,,,,,,,,,,,0.374,,-0.063,,,,,14.264,1.487,,,,,,,,,,,,
2026-03-31,CH,26.5,,,,,,,0.444,,,2.265,,,,,,,,,,,,0.444,,-0.315,,,,,10.166,4.616,,,,,,,,,,,,
2026-06-30,CH,,,,,,,,0.354,,,2.316,,,,,,,,,,,,0.354,,-0.451,,,,,-1.782,-0.983,,,,,,,,,,,,
2026-09-30,CH,,,,,,,,0.514,,,2.355,,,,,,,,,,,,0.514,,-1.029,,,,,-4.576,-3.011,,,,,,,,,,,,
2026-12-31,CH,,,,,,,,,,,2.388,,,,,,,,,,,,,,,,,,,-4.305,,,,,,,,,,,,,
2025-03-31,EA,84.7,-1.071,2.338,3.722,-1.384,-0.104,-0.096,2.743,0.405,,4.026,,,,14.787,,,,,,,,1.247,,0.322,41.197,-7.975,-2.725,,0.046,-0.983,,,,,,1.0,,,0.0,,,
2025-06-30,EA,85.7,-1.015,2.353,3.771,-1.418,-0.178,1.778,2.542,0.188,,4.049,,,,14.135,,,,,,,,1.161,,0.013,39.548,-9.608,-2.632,,9.887,2.063,,,,,,1.0,,,0.0,,,
2025-09-30,EA,85.7,-1.104,2.294,3.699,-1.405,-0.105,-0.195,2.687,0.393,,4.061,,,,13.647,,,,,,,,1.16,,-0.229,39.642,-7.264,-2.474,,5.294,3.115,,,,,,1.0,,,0.0,,,
2025-12-31,EA,85.0,-1.063,2.325,3.687,-1.362,-0.096,-0.004,2.771,0.446,,4.067,,,,13.128,,,,,,,,1.104,,0.036,40.001,-5.106,-2.436,,13.38,4.536,,,,,,1.0,,,0.0,,,
2026-03-31,EA,85.6,-1.164,2.326,3.428,-1.102,0.231,0.669,3.04,0.714,,4.067,,,,12.402,,,,,,,,0.751,,-0.553,39.299,-4.765,-2.385,,6.688,2.404,,,,,,1.0,,,0.0,,,
2026-06-30,EA,,,,,,,,3.011,,,4.09,,,,,,,,,,,,0.891,,-0.499,,,,,-2.999,-1.136,,,,,,1.0,,,,,,
2026-09-30,EA,,,,,,,,3.425,,,4.122,,,,,,,,,,,,0.443,,-0.902,,,,,-3.323,-1.195,,,,,,1.0,,,,,,
2026-12-31,EA,,,,,,,,,,,4.16,,,,,,,,,,,,,,,,,,,-4.064,,,,,,,1.0,,,,,,
2024-12-31,DE,58.2,-1.614,1.742,3.134,-1.392,0.795,-1.495,2.178,0.436,2.017,3.982,-1.964,62.919,47.0,20.109,32.891,7.0,,,,,31.899,-0.822,,0.359,,,-3.23,,,-0.423,,,,,23.837,1.0,,2.233,0.0,sustainable_free,0.0,0.0
2025-03-31,DE,57.1,-1.339,1.781,2.953,-1.171,0.662,-1.362,2.741,0.96,,3.964,,,,19.261,,,,,,,,0.241,,0.308,,,-3.308,,,-0.662,,,,,24.171,1.0,,,0.0,,,
2025-06-30,DE,57.6,-1.161,1.799,2.99,-1.191,0.484,0.316,2.52,0.721,,3.949,,,,18.468,,,,,,,,0.52,,-0.01,,,-3.15,,,0.994,,,,,23.569,1.0,,,0.0,,,
2025-09-30,DE,57.9,-1.173,1.799,3.169,-1.369,0.372,-0.972,2.693,0.894,,3.939,,,,17.642,,,,,,,,0.693,,-0.423,,,-3.152,,,1.729,,,,,23.334,1.0,,,0.0,,,
2025-12-31,DE,58.2,-1.652,1.829,3.368,-1.539,0.756,-0.756,2.813,0.984,,3.941,,,,16.982,,,,,,,,0.813,,0.174,,,-3.126,,,2.013,,,,,22.557,1.0,,,0.0,,,
2026-03-31,DE,58.7,-2.01,1.851,3.437,-1.586,1.104,0.496,2.91,1.059,,3.937,,,,16.067,,,,,,,,0.91,,-0.723,,,-3.194,,,1.394,,,,,22.529,1.0,,,0.0,,,
2026-06-30,DE,,,,3.532,,,,2.964,,,3.937,,,,,,,,,,,,0.714,,-0.049,,,,,,-1.382,,,,,22.591,1.0,,,,,,
2026-09-30,DE,,,,,,,,3.185,,,3.949,,,,,,,,,,,,0.935,,-0.36,,,,,,-1.403,,,,,,1.0,,,,,,
2024-12-31,FR,106.7,-3.747,1.938,3.494,-1.556,2.101,-1.201,3.01,1.072,2.576,3.144,-0.567,137.555,54.0,13.852,32.148,8.5,,,,,28.793,0.01,,1.682,,,-2.395,,,-1.842,,,,83.2,-3.682,1.0,,3.983,0.0,sustainable_free,0.0,0.0
2025-03-31,FR,106.8,-3.595,1.984,2.677,-0.693,2.866,-1.366,3.43,1.446,,3.168,,,,13.042,,,,,,,,0.93,,1.731,,,-2.475,,,-1.882,,,,68.9,-5.883,1.0,,,0.0,,,
2025-06-30,FR,108.7,-3.501,1.956,2.46,-0.504,2.975,1.325,3.24,1.284,,3.179,,,,12.366,,,,,,,,1.24,,1.034,,,-2.438,,,-0.218,,,,72.0,-6.553,1.0,,,0.0,,,
2025-09-30,FR,109.6,-3.33,1.947,1.962,-0.015,3.315,-1.715,3.51,1.563,,3.179,,,,12.122,,,,,,,,1.51,,0.847,,,-2.171,,,0.136,,,,81.7,-6.764,1.0,,,0.0,,,
2025-12-31,FR,107.7,-2.956,1.988,1.988,0.0,2.956,-1.956,3.56,1.572,,3.175,,,,11.592,,,,,,,,1.56,,1.213,,,-2.259,,,0.706,,,,74.7,-5.297,1.0,,,0.0,,,
2026-03-31,FR,109.4,-2.96,1.969,1.911,0.057,3.021,-0.421,3.64,1.671,,3.17,,,,10.867,,,,,,,,1.64,,0.312,,,-2.176,,,0.169,,,,73.0,-5.037,1.0,,,0.0,,,
2026-06-30,FR,,,,1.857,,,,3.68,,,3.169,,,,,,,,,,,,1.43,,0.486,,,,,,-1.401,,,,71.6,-6.512,1.0,,,,,,
2026-09-30,FR,,,,,,,,4.0,,,3.209,,,,,,,,,,,,1.75,,-1.11,,,,,,-0.323,,,,81.5,,1.0,,,,,,
2024-12-31,IT,135.0,0.403,2.979,3.022,-0.043,-0.461,3.261,3.321,0.342,3.183,3.069,0.114,132.366,30.0,12.059,57.941,7.1,,,,,41.028,0.321,,1.75,,,-2.345,,,-1.991,,,,114.3,-18.838,1.0,,8.218,6.0,sustainable_free,0.0,0.0
2025-03-31,IT,136.3,0.385,3.012,2.519,0.493,0.267,3.733,3.887,0.875,,3.111,,,,11.344,,,,,,,,1.387,,0.592,,,-2.435,,,-0.824,,,,114.6,-18.403,1.0,,,0.0,,,
2025-06-30,IT,138.9,0.597,2.957,2.449,0.508,0.076,6.424,3.501,0.544,,3.149,,,,10.816,,,,,,,,1.501,,0.344,,,-2.385,,,0.545,,,,98.1,-17.647,1.0,,,0.0,,,
2025-09-30,IT,137.6,0.448,2.935,2.508,0.426,0.13,1.87,3.559,0.624,,3.178,,,,10.469,,,,,,,,1.559,,0.432,,,-2.152,,,0.594,,,,86.6,-17.018,1.0,,,0.0,,,
2025-12-31,IT,137.6,0.626,2.937,2.579,0.358,-0.142,2.742,3.552,0.615,,3.204,,,,10.084,,,,,,,,1.552,,0.847,,,-1.974,,,1.123,,,,73.9,-15.823,1.0,,,0.0,,,
2026-03-31,IT,137.3,0.699,2.842,2.728,0.114,-0.545,1.545,3.733,0.891,,3.224,,,,9.524,,,,,,,,1.733,,0.288,,,-1.82,,,0.172,,,,82.3,-15.64,1.0,,,0.0,,,
2026-06-30,IT,,,,2.671,,,,3.734,,,3.238,,,,,,,,,,,,1.484,,-0.798,,,,,,-0.271,,,,77.0,-14.635,1.0,,,,,,
2026-09-30,IT,,,,,,,,3.986,,,3.263,,,,,,,,,,,,1.736,,-1.257,,,,,,-0.31,,,,80.1,,1.0,,,,,,
2024-12-31,NL,42.2,0.011,1.637,6.201,-4.565,-2.047,-0.353,2.447,0.81,2.051,4.981,-2.93,31.688,42.0,23.339,34.661,8.5,,,,,39.416,-0.553,,-1.094,,,-3.05,,,0.699,,,,26.9,5.967,1.0,,1.626,0.0,sustainable_free,0.0,0.0
2025-03-31,NL,40.5,-0.392,1.675,5.932,-4.257,-1.418,-0.582,2.936,1.261,,5.085,,,,23.353,,,,,,,,0.436,,-1.14,,,-2.144,,,1.103,,,,19.5,8.648,1.0,,,0.0,,,
2025-06-30,NL,40.6,-0.699,1.708,5.678,-3.97,-0.941,0.241,2.757,1.049,,5.17,,,,23.084,,,,,,,,0.757,,-0.992,,,-2.312,,,2.508,,,,23.7,7.478,1.0,,,0.0,,,
2025-09-30,NL,40.1,-0.802,1.759,5.404,-3.645,-0.692,-0.208,2.883,1.124,,5.231,,,,21.672,,,,,,,,0.883,,-1.178,,,-2.786,,,3.24,,,,19.0,6.802,1.0,,,0.0,,,
2025-12-31,NL,42.1,-0.87,1.729,4.964,-3.234,-0.495,0.395,2.968,1.239,,5.28,,,,20.389,,,,,,,,0.968,,-0.912,,,-2.95,,,4.361,,,,15.5,3.576,1.0,,,0.0,,,
2026-03-31,NL,40.7,-0.954,1.791,4.744,-2.953,-0.242,0.442,3.027,1.236,,5.312,,,,19.909,,,,,,,,1.027,,-0.684,,,-3.443,,,1.979,,,,11.7,6.087,1.0,,,0.0,,,
2026-06-30,NL,,,,4.782,,,,3.077,,,5.348,,,,,,,,,,,,0.827,,-0.665,,,,,,-0.161,,,,11.3,4.14,1.0,,,,,,
2026-09-30,NL,,,,,,,,3.285,,,5.412,,,,,,,,,,,,1.035,,-0.81,,,,,,-0.559,,,,10.0,,1.0,,,,,,

```

## 3. Transitions (last eight quarters)

```
country,quarter,kind,from,to
IT,2024-12-31,quadrant,unsustainable_free,sustainable_free
IT,2024-12-31,stage,3.0,6.0
IT,2025-03-31,stage,6.0,0.0

```

## 4. Backtest calibration

### lead_summary
indicator,events_with_data,warned_share,median_lead_quarters,mean_share_on_warning_side
breakeven_10y,2,1.0,20.0,1.0
cb_holdings_change_4q,8,0.875,19.0,0.45625
policy_rate_minus_inflation,24,0.8333333333333334,20.0,0.4166666666666667
avg_coupon_gap,16,0.8125,19.0,0.409375
primary_balance_gdp,28,0.75,20.0,0.5214285714285715
term_premium_proxy,16,0.75,12.0,0.35
fx_vs_usd_12m,28,0.7142857142857143,18.5,0.3
spread_to_anchor_bp,7,0.7142857142857143,20.0,0.42142857142857143
r_minus_g,26,0.6923076923076923,19.5,0.4836538461538461
target2_balance_gdp,6,0.6666666666666666,8.0,0.35000000000000003
captivity_score,23,0.6521739130434783,6.0,0.5624467178175617
issuance_shortening,8,0.625,11.0,0.1875
forward_r_minus_g_5y,4,0.5,13.5,0.34375
debt_gdp,26,0.46153846153846156,20.0,0.39166666666666666
fx_broad_reer_12m,20,0.45,18.0,0.10500000000000001
bill_share,9,0.2222222222222222,7.5,0.2222222222222222
foreign_share,23,0.13043478260869565,3.0,0.13043478260869565

### forward_r
country,n,rmse_forward_r,rmse_current_r,bias_forward_r,bias_current_r,forward_better
DE,8,1.183360332978418,0.7338907789551266,-0.9212704530538964,0.1115795822777042,False
FR,8,1.0663796517871162,0.6986257141009418,-0.8072102187448843,0.10148822380035355,False
GB,11,2.7789800734571477,2.4480286320401126,-2.043240488240063,-1.5173168914046924,False
GR,8,2.082481650457524,0.6058404787367676,1.0292790108616612,-0.055661032885413575,False
IT,8,0.9967053172410777,0.5680287880544431,-0.8252009951307036,0.008931121209822535,False
JP,8,0.20108759464438497,0.23826010963098496,-0.19604363435243494,0.2316595164611805,True
NL,8,0.943795361435629,0.5670140290928485,-0.7767471907252975,0.2570791427156535,False
US,15,1.2769965894242592,0.8968586371826173,-0.9728767406573238,-0.6642990987723653,False

## 5. Previous report (2026-Q2)

(no previous report)

## 6. Data issues

US gold_local_ccy_12m: no data
US gold_local_record: no data
GB foreign_share: last value 2024-12-31, 7 quarters stale
GB domestic_private_share: last value 2024-12-31, 7 quarters stale
GB household_savings_to_debt: no data
GB net_foreign_asset_position_gdp: no data
GB captivity_score: last value 2024-12-31, 7 quarters stale
GB issuance_shortening: no data
GB gold_local_ccy_12m: no data
GB gold_local_record: no data
GB quadrant: last value 2021-12-31, 19 quarters stale
GB trajectory_unsustainable: last value 2021-12-31, 19 quarters stale
GB holders_captive: last value 2021-12-31, 19 quarters stale
JP primary_balance_gdp: last value 2024-12-31, 7 quarters stale
JP r_effective: last value 2024-12-31, 7 quarters stale
JP r_minus_g: last value 2024-12-31, 7 quarters stale
JP debt_dynamics: last value 2024-12-31, 7 quarters stale
JP debt_dynamics_residual: last value 2024-12-31, 7 quarters stale
JP avg_coupon_gap: last value 2024-12-31, 7 quarters stale
JP forward_r_5y: last value 2024-12-31, 7 quarters stale
JP forward_r_minus_g_5y: last value 2024-12-31, 7 quarters stale
JP debt_gdp_projection_10y: last value 2024-12-31, 7 quarters stale
JP avg_maturity_years: last value 2024-12-31, 7 quarters stale
JP linker_share: no data
JP household_savings_to_debt: no data
JP net_foreign_asset_position_gdp: no data
JP breakeven_10y: no data
JP gold_local_ccy_12m: no data
JP gold_local_record: no data
JP interest_to_revenue: last value 2024-12-31, 7 quarters stale
JP stage_estimate: last value 2024-12-31, 7 quarters stale
JP quadrant: last value 2021-12-31, 19 quarters stale
JP trajectory_unsustainable: last value 2021-12-31, 19 quarters stale
JP holders_captive: last value 2021-12-31, 19 quarters stale
AU primary_balance_gdp: last value 2024-12-31, 7 quarters stale
AU r_effective: last value 2023-09-30, 12 quarters stale
AU g_nominal: last value 2023-09-30, 12 quarters stale
AU r_minus_g: last value 2023-09-30, 12 quarters stale
AU debt_dynamics: last value 2023-09-30, 12 quarters stale
AU debt_dynamics_residual: last value 2023-09-30, 12 quarters stale
AU avg_coupon_gap: last value 2023-09-30, 12 quarters stale
AU forward_r_5y: last value 2022-12-31, 15 quarters stale
AU forward_r_minus_g_5y: last value 2022-12-31, 15 quarters stale
AU debt_gdp_projection_10y: last value 2022-12-31, 15 quarters stale
AU foreign_share: last value 2024-12-31, 7 quarters stale
AU domestic_private_share: last value 2024-12-31, 7 quarters stale
AU avg_maturity_years: last value 2024-12-31, 7 quarters stale
AU bill_share: no data
AU linker_share: no data
AU household_savings_to_debt: no data
AU net_foreign_asset_position_gdp: no data
AU captivity_score: last value 2024-12-31, 7 quarters stale
AU cb_balance_sheet_gdp: last value 2023-09-30, 12 quarters stale
AU cb_balance_sheet_growth_minus_g: last value 2023-09-30, 12 quarters stale
AU issuance_shortening: no data
AU gold_local_ccy_12m: no data
AU gold_local_record: no data
AU interest_to_revenue: last value 2023-09-30, 12 quarters stale
AU stage_estimate: last value 2024-12-31, 7 quarters stale
AU quadrant: last value 2022-12-31, 15 quarters stale
AU trajectory_unsustainable: last value 2022-12-31, 15 quarters stale
AU holders_captive: last value 2022-12-31, 15 quarters stale
CA primary_balance_gdp: last value 2024-12-31, 7 quarters stale
CA r_effective: last value 2023-09-30, 12 quarters stale
CA g_nominal: last value 2023-09-30, 12 quarters stale
CA r_minus_g: last value 2023-09-30, 12 quarters stale
CA debt_dynamics: last value 2023-09-30, 12 quarters stale
CA debt_dynamics_residual: last value 2023-09-30, 12 quarters stale
CA avg_coupon_gap: last value 2023-09-30, 12 quarters stale
CA forward_r_5y: last value 2022-12-31, 15 quarters stale
CA forward_r_minus_g_5y: last value 2022-12-31, 15 quarters stale
CA debt_gdp_projection_10y: last value 2022-12-31, 15 quarters stale
CA foreign_share: last value 2024-12-31, 7 quarters stale
CA domestic_private_share: last value 2021-12-31, 19 quarters stale
CA avg_maturity_years: last value 2024-12-31, 7 quarters stale
CA bill_share: no data
CA linker_share: no data
CA household_savings_to_debt: no data
CA net_foreign_asset_position_gdp: no data
CA captivity_score: last value 2024-12-31, 7 quarters stale
CA cb_balance_sheet_gdp: last value 2023-09-30, 12 quarters stale
CA cb_balance_sheet_growth_minus_g: last value 2023-09-30, 12 quarters stale
CA cb_holdings_change_4q: last value 2021-12-31, 19 quarters stale
CA issuance_shortening: no data
CA gold_local_ccy_12m: no data
CA gold_local_record: no data
CA interest_to_revenue: last value 2023-09-30, 12 quarters stale
CA stage_estimate: last value 2024-12-31, 7 quarters stale
CA quadrant: last value 2015-12-31, 43 quarters stale
CA trajectory_unsustainable: last value 2015-12-31, 43 quarters stale
CA holders_captive: last value 2015-12-31, 43 quarters stale
CH primary_balance_gdp: last value 2024-12-31, 7 quarters stale
CH r_effective: last value 2023-09-30, 12 quarters stale
CH g_nominal: last value 2023-09-30, 12 quarters stale
CH r_minus_g: last value 2023-09-30, 12 quarters stale
CH debt_dynamics: last value 2023-09-30, 12 quarters stale
CH debt_dynamics_residual: last value 2023-09-30, 12 quarters stale
CH avg_coupon_gap: last value 2023-09-30, 12 quarters stale
CH forward_r_5y: last value 2020-12-31, 23 quarters stale
CH forward_r_minus_g_5y: last value 2020-12-31, 23 quarters stale
CH debt_gdp_projection_10y: last value 2020-12-31, 23 quarters stale
CH foreign_share: last value 2024-12-31, 7 quarters stale
CH central_bank_share: last value 2024-12-31, 7 quarters stale
CH domestic_private_share: last value 2024-12-31, 7 quarters stale
CH avg_maturity_years: last value 2024-12-31, 7 quarters stale
CH bill_share: no data
CH linker_share: no data
CH household_savings_to_debt: no data
CH net_foreign_asset_position_gdp: no data
CH captivity_score: last value 2024-12-31, 7 quarters stale
CH breakeven_10y: no data
CH cb_balance_sheet_gdp: last value 2023-09-30, 12 quarters stale
CH cb_balance_sheet_growth_minus_g: last value 2023-09-30, 12 quarters stale
CH cb_holdings_change_4q: last value 2017-06-30, 37 quarters stale
CH issuance_shortening: no data
CH gold_local_ccy_12m: no data
CH gold_local_record: no data
CH interest_to_revenue: last value 2023-09-30, 12 quarters stale
CH stage_estimate: last value 2024-12-31, 7 quarters stale
CH quadrant: last value 2016-06-30, 41 quarters stale
CH trajectory_unsustainable: last value 2016-06-30, 41 quarters stale
CH holders_captive: last value 2016-06-30, 41 quarters stale
EA forward_r_5y: no data
EA forward_r_minus_g_5y: no data
EA debt_gdp_projection_10y: no data
EA foreign_share: last value 2024-12-31, 7 quarters stale
EA domestic_private_share: last value 2024-12-31, 7 quarters stale
EA avg_maturity_years: last value 2024-12-31, 7 quarters stale
EA bill_share: last value 2022-03-31, 18 quarters stale
EA linker_share: no data
EA household_savings_to_debt: no data
EA net_foreign_asset_position_gdp: no data
EA captivity_score: last value 2024-12-31, 7 quarters stale
EA breakeven_10y: no data
EA issuance_shortening: last value 2022-03-31, 18 quarters stale
EA gold_local_ccy_12m: no data
EA gold_local_record: no data
EA interest_to_revenue: no data
EA trajectory_unsustainable: no data
EA holders_captive: no data
DE forward_r_5y: last value 2024-12-31, 7 quarters stale
DE forward_r_minus_g_5y: last value 2024-12-31, 7 quarters stale
DE debt_gdp_projection_10y: last value 2024-12-31, 7 quarters stale
DE foreign_share: last value 2024-12-31, 7 quarters stale
DE domestic_private_share: last value 2024-12-31, 7 quarters stale
DE avg_maturity_years: last value 2024-12-31, 7 quarters stale
DE bill_share: last value 2022-03-31, 18 quarters stale
DE linker_share: no data
DE household_savings_to_debt: no data
DE net_foreign_asset_position_gdp: no data
DE captivity_score: last value 2024-12-31, 7 quarters stale
DE breakeven_10y: no data
DE cb_balance_sheet_gdp: no data
DE cb_balance_sheet_growth_minus_g: no data
DE issuance_shortening: last value 2022-03-31, 18 quarters stale
DE gold_local_ccy_12m: no data
DE gold_local_record: no data
DE spread_to_anchor_bp: no data
DE interest_to_revenue: last value 2024-12-31, 7 quarters stale
DE quadrant: last value 2024-12-31, 7 quarters stale
DE trajectory_unsustainable: last value 2024-12-31, 7 quarters stale
DE holders_captive: last value 2024-12-31, 7 quarters stale
FR forward_r_5y: last value 2024-12-31, 7 quarters stale
FR forward_r_minus_g_5y: last value 2024-12-31, 7 quarters stale
FR debt_gdp_projection_10y: last value 2024-12-31, 7 quarters stale
FR foreign_share: last value 2024-12-31, 7 quarters stale
FR domestic_private_share: last value 2024-12-31, 7 quarters stale
FR avg_maturity_years: last value 2024-12-31, 7 quarters stale
FR bill_share: last value 2022-03-31, 18 quarters stale
FR linker_share: no data
FR household_savings_to_debt: no data
FR net_foreign_asset_position_gdp: no data
FR captivity_score: last value 2024-12-31, 7 quarters stale
FR breakeven_10y: no data
FR cb_balance_sheet_gdp: no data
FR cb_balance_sheet_growth_minus_g: no data
FR issuance_shortening: last value 2022-03-31, 18 quarters stale
FR gold_local_ccy_12m: no data
FR gold_local_record: no data
FR interest_to_revenue: last value 2024-12-31, 7 quarters stale
FR quadrant: last value 2024-12-31, 7 quarters stale
FR trajectory_unsustainable: last value 2024-12-31, 7 quarters stale
FR holders_captive: last value 2024-12-31, 7 quarters stale
IT forward_r_5y: last value 2024-12-31, 7 quarters stale
IT forward_r_minus_g_5y: last value 2024-12-31, 7 quarters stale
IT debt_gdp_projection_10y: last value 2024-12-31, 7 quarters stale
IT foreign_share: last value 2024-12-31, 7 quarters stale
IT domestic_private_share: last value 2024-12-31, 7 quarters stale
IT avg_maturity_years: last value 2024-12-31, 7 quarters stale
IT bill_share: last value 2022-03-31, 18 quarters stale
IT linker_share: no data
IT household_savings_to_debt: no data
IT net_foreign_asset_position_gdp: no data
IT captivity_score: last value 2024-12-31, 7 quarters stale
IT breakeven_10y: no data
IT cb_balance_sheet_gdp: no data
IT cb_balance_sheet_growth_minus_g: no data
IT issuance_shortening: last value 2022-03-31, 18 quarters stale
IT gold_local_ccy_12m: no data
IT gold_local_record: no data
IT interest_to_revenue: last value 2024-12-31, 7 quarters stale
IT quadrant: last value 2024-12-31, 7 quarters stale
IT trajectory_unsustainable: last value 2024-12-31, 7 quarters stale
IT holders_captive: last value 2024-12-31, 7 quarters stale
NL forward_r_5y: last value 2024-12-31, 7 quarters stale
NL forward_r_minus_g_5y: last value 2024-12-31, 7 quarters stale
NL debt_gdp_projection_10y: last value 2024-12-31, 7 quarters stale
NL foreign_share: last value 2024-12-31, 7 quarters stale
NL domestic_private_share: last value 2024-12-31, 7 quarters stale
NL avg_maturity_years: last value 2024-12-31, 7 quarters stale
NL bill_share: last value 2022-03-31, 18 quarters stale
NL linker_share: no data
NL household_savings_to_debt: no data
NL net_foreign_asset_position_gdp: no data
NL captivity_score: last value 2024-12-31, 7 quarters stale
NL breakeven_10y: no data
NL cb_balance_sheet_gdp: no data
NL cb_balance_sheet_growth_minus_g: no data
NL issuance_shortening: last value 2022-03-31, 18 quarters stale
NL gold_local_ccy_12m: no data
NL gold_local_record: no data
NL interest_to_revenue: last value 2024-12-31, 7 quarters stale
NL quadrant: last value 2024-12-31, 7 quarters stale
NL trajectory_unsustainable: last value 2024-12-31, 7 quarters stale
NL holders_captive: last value 2024-12-31, 7 quarters stale
AR.gg_debt_gdp.BIS: failed to update (HttpError: HTTP 404 for https://stats.bis.org/api/v2/data/dataflow/BIS/WS_TC/2.0/Q.AR.G.A.M.770.A?fo)
AR.gg_debt_gdp.WORLDBANK: failed to update (ValueError: no observations parsed)
BR.gg_debt_gdp.BIS: failed to update (HttpError: HTTP 404 for https://stats.bis.org/api/v2/data/dataflow/BIS/WS_TC/2.0/Q.BR.G.A.M.770.A?fo)
CA.bond_total_return.JST: failed to update (ValueError: no observations parsed)
CA.breakeven_10y.BOC: failed to update (HttpError: HTTP 404 for https://www.bankofcanada.ca/valet/observations/BD.CDN.BEI.DQ.YLD/json?start_)
CA.equity_total_return.JST: failed to update (ValueError: no observations parsed)
EA.gg_interest_gdp.IMF_WEO: failed to update (ValueError: no values for ie/EURO: keys=['USA', 'GBR', 'AUT', 'BEL', 'DNK'])
EA.gg_primary_balance_gdp.IMF_WEO: failed to update (ValueError: no values for GGXONLB_NGDP/EURO: keys=[])
EA.gg_revenue_gdp.IMF_WEO: failed to update (ValueError: no values for GGR_NGDP/EURO: keys=[])
GR.cb_gov_holdings_lcu.ECB_PSPP: failed to update (ValueError: Greece not in PSPP table: ['Austria', 'Belgium', 'Cyprus', 'Germany', 'Estonia', 'Spain')
GR.gg_debt_gdp.WORLDBANK: failed to update (ValueError: no observations parsed)
MX.gg_debt_gdp.BIS: failed to update (HttpError: HTTP 404 for https://stats.bis.org/api/v2/data/dataflow/BIS/WS_TC/2.0/Q.MX.G.A.M.770.A?fo)
RU.cb_total_assets_lcu.BIS: failed to update (HttpError: HTTP 404 for https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CBTA/1.0/M.RU?format=csv: )
RU.gg_debt_gdp.BIS: failed to update (HttpError: HTTP 404 for https://stats.bis.org/api/v2/data/dataflow/BIS/WS_TC/2.0/Q.RU.G.A.M.770.A?fo)
SE.gg_debt_gdp.WORLDBANK: failed to update (ValueError: no observations parsed)

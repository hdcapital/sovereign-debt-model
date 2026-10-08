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

Report quarter: 2026-Q3. Today: 2026-10-08.

## 1. Latest indicator table (core markets)

```csv
country,indicator,quarter,value,chg_1y,chg_5y,stale_quarters
US,auction_tail,2026-09-30,-0.06,-0.189,0.095,0.0
US,avg_coupon_gap,2026-09-30,1.6,1.101,2.425,0.0
US,avg_maturity_years,2026-09-30,5.876,-0.124,-0.024,0.0
US,bill_share,2026-09-30,22.373,0.832,5.385,0.0
US,breakeven_10y,2026-09-30,2.36,0.0,-0.01,0.0
US,captivity_score,2026-03-31,51.895,0.176,-2.694,2.0
US,cb_balance_sheet_gdp,2026-06-30,21.196,-0.956,-14.728,1.0
US,cb_balance_sheet_growth_minus_g,2026-06-30,-4.56,8.323,-13.246,1.0
US,cb_holdings_change_4q,2026-03-31,-0.826,1.554,-4.71,2.0
US,central_bank_share,2026-03-31,14.922,-0.826,-9.622,2.0
US,debt_dynamics,2026-06-30,-0.109,-1.681,-8.393,1.0
US,debt_dynamics_residual,2026-03-31,2.702,1.346,6.323,2.0
US,debt_gdp,2026-03-31,110.8,3.1,-14.6,2.0
US,debt_gdp_projection_10y,2026-03-31,118.116,-6.896,-122.941,2.0
US,domestic_private_share,2026-03-31,55.337,2.371,11.864,2.0
US,foreign_share,2026-03-31,29.741,-1.545,-2.241,2.0
US,forward_r_5y,2026-03-31,3.908,0.003,2.62,2.0
US,forward_r_minus_g_5y,2026-03-31,-1.481,-0.105,0.894,2.0
US,fx_broad_reer_12m,2026-09-30,-0.735,0.004,-0.161,0.0
US,g_nominal,2026-06-30,5.663,0.647,0.282,1.0
US,g_trend,2026-09-30,5.533,0.223,1.738,0.0
US,gold_local_ccy_12m,2026-09-30,17.748,-24.92,25.396,0.0
US,gold_local_record,2026-09-30,0.0,-1.0,0.0,0.0
US,holders_captive,2026-03-31,0.0,0.0,0.0,2.0
US,household_savings_to_debt,2026-03-31,4.311,0.056,-0.373,2.0
US,interest_to_revenue,2026-06-30,17.738,7.33,12.407,1.0
US,issuance_shortening,2026-09-30,0.706,-0.399,-1.724,0.0
US,linker_share,2026-09-30,6.827,-0.202,-0.732,0.0
US,marginal_yield,2026-09-30,5.126,1.19,4.102,0.0
US,net_foreign_asset_position_gdp,2026-06-30,-70.553,0.659,-12.384,1.0
US,policy_rate_minus_inflation,2026-09-30,-0.088,-1.19,5.138,0.0
US,primary_balance_gdp,2026-06-30,-2.05,1.151,10.689,1.0
US,quadrant,2026-03-31,,,,2.0
US,r_effective,2026-09-30,3.526,0.089,1.677,0.0
US,r_minus_g,2026-06-30,-2.031,-0.458,1.53,1.0
US,stage_estimate,2026-06-30,0.0,0.0,0.0,1.0
US,term_premium_proxy,2026-09-30,1.077,0.574,1.18,0.0
US,trajectory_unsustainable,2026-03-31,0.0,0.0,0.0,2.0
GB,avg_coupon_gap,2026-09-30,0.039,0.866,0.937,0.0
GB,avg_maturity_years,2026-09-30,13.381,-0.407,-1.619,0.0
GB,bill_share,,,,,
GB,breakeven_10y,2026-09-30,3.242,0.017,-0.614,0.0
GB,captivity_score,2025-12-31,63.31,-3.18,-11.861,3.0
GB,cb_balance_sheet_gdp,2026-06-30,25.753,-2.047,-18.515,1.0
GB,cb_balance_sheet_growth_minus_g,2026-06-30,-7.661,7.681,-28.259,1.0
GB,cb_holdings_change_4q,2026-09-30,0.0,4.0,-1.0,0.0
GB,central_bank_share,2026-09-30,22.0,0.0,-12.0,0.0
GB,debt_dynamics,2026-06-30,0.797,0.081,-8.541,1.0
GB,debt_dynamics_residual,2026-06-30,0.053,2.269,8.591,1.0
GB,debt_gdp,2026-09-30,86.65,0.35,-42.95,0.0
GB,debt_gdp_projection_10y,2026-06-30,88.051,-9.986,-101.921,1.0
GB,domestic_private_share,2025-12-31,46.0,4.0,6.923,3.0
GB,foreign_share,2025-12-31,32.0,0.0,4.077,3.0
GB,forward_r_5y,2026-06-30,4.732,-0.009,3.607,1.0
GB,forward_r_minus_g_5y,2026-06-30,-0.025,-0.19,1.766,1.0
GB,fx_broad_reer_12m,2026-09-30,0.134,-0.648,-4.268,0.0
GB,fx_vs_usd_12m,2026-09-30,-1.309,-1.638,-5.558,0.0
GB,g_nominal,2026-06-30,4.057,-1.532,2.998,1.0
GB,g_trend,2026-09-30,4.79,0.161,1.85,0.0
GB,gold_local_ccy_12m,2026-09-30,19.31,-22.891,30.722,0.0
GB,gold_local_record,2026-09-30,0.0,-1.0,0.0,0.0
GB,holders_captive,2025-12-31,1.0,0.0,0.0,3.0
GB,household_savings_to_debt,,,,,
GB,interest_to_revenue,2026-09-30,11.829,0.354,5.819,0.0
GB,issuance_shortening,,,,,
GB,linker_share,,,,,
GB,marginal_yield,2026-09-30,5.192,0.763,4.322,0.0
GB,net_foreign_asset_position_gdp,,,,,
GB,policy_rate_minus_inflation,2026-09-30,0.663,0.463,3.588,0.0
GB,primary_balance_gdp,2026-06-30,-0.081,0.92,8.492,1.0
GB,quadrant,2025-12-31,,,,3.0
GB,r_effective,2026-09-30,5.153,-0.103,3.384,0.0
GB,r_minus_g,2026-06-30,0.826,1.151,0.245,1.0
GB,stage_estimate,2026-06-30,0.0,0.0,0.0,1.0
GB,term_premium_proxy,2026-09-30,1.621,0.931,0.69,0.0
GB,trajectory_unsustainable,2025-12-31,1.0,0.0,1.0,3.0
JP,avg_coupon_gap,2025-12-31,0.864,0.697,1.648,3.0
JP,avg_maturity_years,2025-12-31,9.4,0.0,0.222,3.0
JP,bill_share,2026-06-30,10.374,-0.688,,1.0
JP,breakeven_10y,,,,,
JP,captivity_score,2025-12-31,79.807,-0.879,1.355,3.0
JP,cb_balance_sheet_gdp,2026-06-30,94.288,-15.525,-32.499,1.0
JP,cb_balance_sheet_growth_minus_g,2026-06-30,-14.677,-5.27,-24.02,1.0
JP,cb_holdings_change_4q,2026-09-30,0.0,2.0,-0.4,0.0
JP,central_bank_share,2026-09-30,46.0,0.0,2.0,0.0
JP,debt_dynamics,2025-12-31,-7.949,-2.866,-23.566,3.0
JP,debt_dynamics_residual,2025-12-31,-10.351,-2.534,-14.534,3.0
JP,debt_gdp,2026-03-31,175.6,-15.4,-53.3,2.0
JP,debt_gdp_projection_10y,2025-12-31,160.8,-17.928,-126.259,3.0
JP,domestic_private_share,2026-09-30,41.0,0.0,-2.0,0.0
JP,foreign_share,2026-09-30,13.0,0.0,0.0,0.0
JP,forward_r_5y,2025-12-31,1.238,0.424,0.901,3.0
JP,forward_r_minus_g_5y,2025-12-31,-0.727,0.321,-0.031,3.0
JP,fx_broad_reer_12m,2026-09-30,-8.076,-5.235,0.596,0.0
JP,fx_vs_usd_12m,2026-09-30,-5.901,-2.712,-0.592,0.0
JP,g_nominal,2026-06-30,3.814,-0.793,2.685,1.0
JP,g_trend,2026-09-30,2.019,0.071,0.986,0.0
JP,gold_local_ccy_12m,2026-09-30,25.133,-22.236,27.603,0.0
JP,gold_local_record,2026-09-30,0.0,-1.0,0.0,0.0
JP,holders_captive,2025-12-31,1.0,0.0,0.0,3.0
JP,household_savings_to_debt,,,,,
JP,interest_to_revenue,2025-12-31,4.18,0.204,-0.473,3.0
JP,issuance_shortening,2026-06-30,-1.471,-0.384,,1.0
JP,linker_share,,,,,
JP,marginal_yield,2026-09-30,2.615,1.235,2.612,0.0
JP,net_foreign_asset_position_gdp,,,,,
JP,policy_rate_minus_inflation,2026-09-30,-0.898,1.48,-0.574,0.0
JP,primary_balance_gdp,2025-12-31,0.477,0.683,7.827,3.0
JP,quadrant,2025-12-31,,,,3.0
JP,r_effective,2025-12-31,0.842,0.104,0.087,3.0
JP,r_minus_g,2025-12-31,-3.812,-1.28,-7.719,3.0
JP,stage_estimate,2025-12-31,0.0,0.0,0.0,3.0
JP,term_premium_proxy,2026-09-30,1.105,0.401,0.909,0.0
JP,trajectory_unsustainable,2025-12-31,0.0,0.0,0.0,3.0
AU,avg_coupon_gap,2025-12-31,0.79,-0.001,2.712,3.0
AU,avg_maturity_years,2025-12-31,7.0,0.0,-0.2,3.0
AU,bill_share,,,,,
AU,breakeven_10y,2026-06-30,2.365,0.24,0.21,1.0
AU,captivity_score,2025-12-31,41.187,-2.286,9.538,3.0
AU,cb_balance_sheet_gdp,2026-06-30,12.438,-2.095,-13.392,1.0
AU,cb_balance_sheet_growth_minus_g,2026-06-30,-15.22,-9.144,-103.793,1.0
AU,cb_holdings_change_4q,2026-09-30,0.0,4.0,-20.0,0.0
AU,central_bank_share,2026-09-30,24.0,0.0,-6.0,0.0
AU,debt_dynamics,2025-12-31,0.531,-0.04,-8.629,3.0
AU,debt_dynamics_residual,2025-12-31,0.669,0.94,-8.371,3.0
AU,debt_gdp,2026-03-31,51.1,0.1,-8.1,2.0
AU,debt_gdp_projection_10y,2025-12-31,54.427,4.935,-58.759,3.0
AU,domestic_private_share,2025-12-31,31.0,4.0,-11.0,3.0
AU,foreign_share,2025-12-31,45.0,0.0,-3.0,3.0
AU,forward_r_5y,2025-12-31,4.568,0.42,3.007,3.0
AU,forward_r_minus_g_5y,2025-12-31,-1.011,0.179,1.611,3.0
AU,fx_broad_reer_12m,2026-09-30,8.15,9.555,8.342,0.0
AU,fx_vs_usd_12m,2026-09-30,5.68,10.441,4.301,0.0
AU,g_nominal,2026-06-30,5.567,1.999,0.389,1.0
AU,g_trend,2026-09-30,5.844,0.346,1.975,0.0
AU,gold_local_ccy_12m,2026-09-30,11.419,-38.38,20.324,0.0
AU,gold_local_record,2026-09-30,0.0,-1.0,0.0,0.0
AU,holders_captive,2025-12-31,0.0,0.0,0.0,3.0
AU,household_savings_to_debt,,,,,
AU,interest_to_revenue,2025-12-31,5.175,0.472,1.532,3.0
AU,issuance_shortening,,,,,
AU,linker_share,,,,,
AU,marginal_yield,2026-09-30,5.136,1.276,4.127,0.0
AU,net_foreign_asset_position_gdp,,,,,
AU,policy_rate_minus_inflation,2026-06-30,0.408,-1.347,4.122,1.0
AU,primary_balance_gdp,2025-12-31,-0.89,-0.316,6.509,3.0
AU,quadrant,2025-12-31,,,,3.0
AU,r_effective,2025-12-31,4.051,0.407,1.031,3.0
AU,r_minus_g,2025-12-31,-0.728,-0.721,-4.862,3.0
AU,stage_estimate,2025-12-31,0.0,0.0,0.0,3.0
AU,term_premium_proxy,2026-09-30,0.786,-0.185,-0.804,0.0
AU,trajectory_unsustainable,2025-12-31,0.0,0.0,0.0,3.0
CA,avg_coupon_gap,2025-12-31,-0.488,0.554,2.23,3.0
CA,avg_maturity_years,2025-12-31,6.8,0.0,0.356,3.0
CA,bill_share,,,,,
CA,breakeven_10y,2026-09-30,2.01,0.5,0.75,0.0
CA,captivity_score,2025-12-31,50.813,-0.914,-12.013,3.0
CA,cb_balance_sheet_gdp,2026-06-30,6.948,-0.766,-13.32,1.0
CA,cb_balance_sheet_growth_minus_g,2026-06-30,-10.368,4.603,4.324,1.0
CA,cb_holdings_change_4q,2026-09-30,0.0,3.2,-4.0,0.0
CA,central_bank_share,2026-09-30,22.0,0.0,-20.0,0.0
CA,debt_dynamics,2025-12-31,-2.171,-0.13,-16.488,3.0
CA,debt_dynamics_residual,2025-12-31,4.771,-1.57,-9.612,3.0
CA,debt_gdp,2026-03-31,97.1,1.6,-13.8,2.0
CA,debt_gdp_projection_10y,2025-12-31,68.969,-1.507,-99.267,3.0
CA,domestic_private_share,2025-12-31,50.0,1.6,10.462,3.0
CA,foreign_share,2025-12-31,28.0,0.0,5.538,3.0
CA,forward_r_5y,2025-12-31,3.27,-0.23,2.029,3.0
CA,forward_r_minus_g_5y,2025-12-31,-1.666,-0.535,0.406,3.0
CA,fx_broad_reer_12m,2026-09-30,-1.089,1.833,-4.406,0.0
CA,fx_vs_usd_12m,2026-09-30,-1.992,0.995,-7.121,0.0
CA,g_nominal,2026-06-30,4.448,-0.547,-1.356,1.0
CA,g_trend,2026-09-30,5.266,0.445,2.076,0.0
CA,gold_local_ccy_12m,2026-09-30,20.141,-26.92,32.295,0.0
CA,gold_local_record,2026-09-30,0.0,-1.0,0.0,0.0
CA,holders_captive,2025-12-31,0.0,0.0,-1.0,3.0
CA,household_savings_to_debt,,,,,
CA,interest_to_revenue,2025-12-31,7.497,-0.776,0.422,3.0
CA,issuance_shortening,,,,,
CA,linker_share,,,,,
CA,marginal_yield,2026-09-30,3.742,0.852,2.624,0.0
CA,net_foreign_asset_position_gdp,,,,,
CA,policy_rate_minus_inflation,2026-09-30,-0.784,-0.925,3.349,0.0
CA,primary_balance_gdp,2025-12-31,1.399,-0.034,9.369,3.0
CA,quadrant,2025-12-31,,,,3.0
CA,r_effective,2025-12-31,3.572,-0.58,0.372,3.0
CA,r_minus_g,2025-12-31,-0.826,-0.144,-8.047,3.0
CA,stage_estimate,2025-12-31,0.0,0.0,0.0,3.0
CA,term_premium_proxy,2026-09-30,0.62,-0.08,-0.36,0.0
CA,trajectory_unsustainable,2025-12-31,0.0,0.0,0.0,3.0
CH,avg_coupon_gap,2025-12-31,-1.009,0.235,0.619,3.0
CH,avg_maturity_years,2025-12-31,11.0,0.0,0.0,3.0
CH,bill_share,,,,,
CH,breakeven_10y,,,,,
CH,captivity_score,2025-12-31,56.044,0.0,0.0,3.0
CH,cb_balance_sheet_gdp,2026-06-30,102.897,5.76,-38.834,1.0
CH,cb_balance_sheet_growth_minus_g,2026-06-30,6.001,6.107,-0.199,1.0
CH,cb_holdings_change_4q,2025-12-31,0.0,0.0,0.0,3.0
CH,central_bank_share,2025-12-31,0.0,0.0,0.0,3.0
CH,debt_dynamics,2025-12-31,-1.112,0.106,-4.953,3.0
CH,debt_dynamics_residual,2025-12-31,1.512,0.194,2.653,3.0
CH,debt_gdp,2026-03-31,26.5,1.0,-3.7,2.0
CH,debt_gdp_projection_10y,2025-12-31,14.39,0.055,-37.613,3.0
CH,domestic_private_share,2025-12-31,85.0,0.0,0.0,3.0
CH,foreign_share,2025-12-31,15.0,0.0,0.0,3.0
CH,forward_r_5y,2025-12-31,0.965,0.045,0.95,3.0
CH,forward_r_minus_g_5y,2025-12-31,-1.663,-0.205,-0.327,3.0
CH,fx_broad_reer_12m,2026-09-30,-3.011,-3.912,1.387,0.0
CH,fx_vs_usd_12m,2026-09-30,-4.576,-10.576,-2.959,0.0
CH,g_nominal,2026-06-30,1.208,-2.504,-1.493,1.0
CH,g_trend,2026-09-30,2.714,0.145,1.432,0.0
CH,gold_local_ccy_12m,2026-09-30,23.395,-11.197,29.525,0.0
CH,gold_local_record,2026-09-30,0.0,-1.0,0.0,0.0
CH,holders_captive,2025-12-31,0.0,0.0,0.0,3.0
CH,household_savings_to_debt,,,,,
CH,interest_to_revenue,2025-12-31,1.078,-0.026,0.24,3.0
CH,issuance_shortening,,,,,
CH,linker_share,,,,,
CH,marginal_yield,2026-09-30,0.514,0.321,0.899,0.0
CH,net_foreign_asset_position_gdp,,,,,
CH,policy_rate_minus_inflation,2026-09-30,-0.807,-0.583,0.885,0.0
CH,primary_balance_gdp,2025-12-31,0.849,-0.01,3.564,3.0
CH,quadrant,2025-12-31,,,,3.0
CH,r_effective,2025-12-31,1.384,-0.052,0.384,3.0
CH,r_minus_g,2025-12-31,-1.021,0.378,-5.098,3.0
CH,stage_estimate,2025-12-31,0.0,0.0,0.0,3.0
CH,term_premium_proxy,2026-09-30,0.514,0.053,-0.032,0.0
CH,trajectory_unsustainable,2025-12-31,0.0,0.0,0.0,3.0
EA,avg_coupon_gap,2026-03-31,0.714,0.309,2.477,2.0
EA,avg_maturity_years,2025-12-31,7.634,0.0,0.272,3.0
EA,bill_share,2026-03-31,6.459,0.223,-2.545,2.0
EA,breakeven_10y,,,,,
EA,captivity_score,2025-12-31,48.802,-0.867,-2.752,3.0
EA,cb_balance_sheet_gdp,2026-03-31,39.299,-1.898,-24.981,2.0
EA,cb_balance_sheet_growth_minus_g,2026-03-31,-4.765,3.21,-52.714,2.0
EA,cb_holdings_change_4q,2026-03-31,-2.385,0.34,-2.353,2.0
EA,central_bank_share,2026-03-31,12.402,-2.385,-7.413,2.0
EA,debt_dynamics,2026-03-31,0.231,0.335,-11.564,2.0
EA,debt_dynamics_residual,2026-03-31,0.669,0.765,-2.536,2.0
EA,debt_gdp,2026-03-31,85.6,0.9,-26.8,2.0
EA,debt_gdp_projection_10y,2025-12-31,83.599,0.03,-60.879,3.0
EA,domestic_private_share,2025-12-31,43.0,2.418,4.082,3.0
EA,ecb_backstop_active,2026-09-30,1.0,0.0,0.0,0.0
EA,foreign_share,2025-12-31,43.872,0.018,2.709,3.0
EA,forward_r_5y,2025-12-31,2.587,0.203,2.324,3.0
EA,forward_r_minus_g_5y,2025-12-31,-1.481,0.132,0.432,3.0
EA,fx_broad_reer_12m,2026-09-30,-1.195,-4.311,0.953,0.0
EA,fx_vs_usd_12m,2026-09-30,-3.323,-8.617,-2.078,0.0
EA,g_nominal,2026-03-31,3.428,-0.294,7.255,2.0
EA,g_trend,2026-09-30,4.122,0.061,2.083,0.0
EA,gold_local_ccy_12m,2026-09-30,21.796,-13.699,28.279,0.0
EA,gold_local_record,2026-09-30,0.0,-1.0,0.0,0.0
EA,holders_captive,2025-12-31,0.0,0.0,0.0,3.0
EA,household_savings_to_debt,,,,,
EA,interest_to_revenue,2026-03-31,4.049,-0.061,0.812,2.0
EA,issuance_shortening,2026-03-31,-0.064,0.149,-3.266,2.0
EA,linker_share,,,,,
EA,marginal_yield,2026-09-30,3.425,0.738,3.674,0.0
EA,net_foreign_asset_position_gdp,,,,,
EA,policy_rate_minus_inflation,2026-09-30,-0.999,-0.769,2.365,0.0
EA,primary_balance_gdp,2026-03-31,-1.164,-0.093,5.452,2.0
EA,quadrant,2025-12-31,,,,3.0
EA,r_effective,2026-03-31,2.326,-0.012,0.836,2.0
EA,r_minus_g,2026-03-31,-1.102,0.282,-6.419,2.0
EA,stage_estimate,2026-03-31,0.0,0.0,0.0,2.0
EA,term_premium_proxy,2026-09-30,0.443,-0.717,-0.342,0.0
EA,trajectory_unsustainable,2025-12-31,0.0,0.0,0.0,3.0
DE,avg_coupon_gap,2026-03-31,1.059,0.099,2.474,2.0
DE,avg_maturity_years,2025-12-31,7.0,0.0,0.2,3.0
DE,bill_share,2026-03-31,4.545,0.109,-5.851,2.0
DE,breakeven_10y,,,,,
DE,captivity_score,2025-12-31,41.615,-0.396,-0.434,3.0
DE,cb_holdings_change_4q,2026-03-31,-3.194,0.115,-3.001,2.0
DE,central_bank_share,2026-03-31,16.067,-3.194,-8.887,2.0
DE,debt_dynamics,2026-03-31,1.104,0.442,-6.201,2.0
DE,debt_dynamics_residual,2026-03-31,0.496,1.858,-1.799,2.0
DE,debt_gdp,2026-03-31,58.7,1.6,-17.3,2.0
DE,debt_gdp_projection_10y,2025-12-31,65.856,2.937,-23.138,3.0
DE,domestic_private_share,2025-12-31,36.018,3.126,6.119,3.0
DE,ecb_backstop_active,2026-09-30,1.0,0.0,0.0,0.0
DE,foreign_share,2025-12-31,47.0,0.0,1.615,3.0
DE,forward_r_5y,2025-12-31,2.456,0.438,2.487,3.0
DE,forward_r_minus_g_5y,2025-12-31,-1.485,0.479,1.749,3.0
DE,fx_broad_reer_12m,2026-09-30,-1.403,-3.132,-0.918,0.0
DE,g_nominal,2026-06-30,3.532,0.542,1.273,1.0
DE,g_trend,2026-09-30,3.949,0.011,1.052,0.0
DE,gold_local_ccy_12m,2026-09-30,21.796,-13.699,28.279,0.0
DE,gold_local_record,2026-09-30,0.0,-1.0,0.0,0.0
DE,holders_captive,2025-12-31,0.0,0.0,0.0,3.0
DE,household_savings_to_debt,,,,,
DE,interest_to_revenue,2026-03-31,2.287,0.034,0.914,2.0
DE,issuance_shortening,2026-03-31,-1.864,0.875,-8.049,2.0
DE,linker_share,,,,,
DE,marginal_yield,2026-09-30,3.185,0.492,3.548,0.0
DE,net_foreign_asset_position_gdp,,,,,
DE,policy_rate_minus_inflation,2026-09-30,-0.612,-0.189,3.501,0.0
DE,primary_balance_gdp,2026-03-31,-2.01,-0.671,2.896,2.0
DE,quadrant,2025-12-31,,,,3.0
DE,r_effective,2026-03-31,1.851,0.07,0.8,2.0
DE,r_minus_g,2026-03-31,-1.586,-0.415,-5.199,2.0
DE,stage_estimate,2026-03-31,0.0,0.0,0.0,2.0
DE,target2_balance_gdp,2026-06-30,22.591,-0.978,-8.199,1.0
DE,term_premium_proxy,2026-09-30,0.026,-0.676,-0.332,0.0
DE,trajectory_unsustainable,2025-12-31,0.0,0.0,0.0,3.0
FR,avg_coupon_gap,2026-03-31,1.671,0.226,3.007,2.0
FR,avg_maturity_years,2025-12-31,8.5,0.0,0.3,3.0
FR,bill_share,2026-03-31,8.917,0.25,-2.57,2.0
FR,breakeven_10y,,,,,
FR,captivity_score,2025-12-31,37.739,-0.502,-2.072,3.0
FR,cb_holdings_change_4q,2026-03-31,-2.176,0.3,-2.026,2.0
FR,central_bank_share,2026-03-31,10.867,-2.176,-7.11,2.0
FR,debt_dynamics,2026-03-31,3.021,0.155,-11.043,2.0
FR,debt_dynamics_residual,2026-03-31,-0.421,0.945,-4.357,2.0
FR,debt_gdp,2026-03-31,109.4,2.6,-23.5,2.0
FR,debt_gdp_projection_10y,2025-12-31,134.142,-3.413,-53.191,3.0
FR,domestic_private_share,2025-12-31,34.408,2.259,3.132,3.0
FR,ecb_backstop_active,2026-09-30,1.0,0.0,0.0,0.0
FR,foreign_share,2025-12-31,54.0,0.0,3.615,3.0
FR,forward_r_5y,2025-12-31,2.906,0.33,2.648,3.0
FR,forward_r_minus_g_5y,2025-12-31,-0.269,0.299,1.268,3.0
FR,fx_broad_reer_12m,2026-09-30,-0.323,-0.459,1.623,0.0
FR,g_nominal,2026-06-30,1.857,-0.603,-1.504,1.0
FR,g_trend,2026-09-30,3.209,0.03,1.524,0.0
FR,gold_local_ccy_12m,2026-09-30,21.796,-13.699,28.279,0.0
FR,gold_local_record,2026-09-30,0.0,-1.0,0.0,0.0
FR,holders_captive,2025-12-31,0.0,0.0,0.0,3.0
FR,household_savings_to_debt,,,,,
FR,interest_to_revenue,2026-03-31,4.195,0.058,1.682,2.0
FR,issuance_shortening,2026-03-31,0.983,-0.607,-3.443,2.0
FR,linker_share,,,,,
FR,marginal_yield,2026-09-30,4.0,0.49,3.96,0.0
FR,net_foreign_asset_position_gdp,,,,,
FR,policy_rate_minus_inflation,2026-09-30,-0.107,-0.954,2.056,0.0
FR,primary_balance_gdp,2026-03-31,-2.96,0.635,5.697,2.0
FR,quadrant,2025-12-31,,,,3.0
FR,r_effective,2026-03-31,1.969,-0.016,0.703,2.0
FR,r_minus_g,2026-03-31,0.057,0.75,-4.649,2.0
FR,spread_to_anchor_bp,2026-09-30,81.5,-0.2,41.2,0.0
FR,stage_estimate,2026-03-31,0.0,0.0,0.0,2.0
FR,target2_balance_gdp,2026-06-30,-6.512,0.041,-5.685,1.0
FR,term_premium_proxy,2026-09-30,0.841,-0.678,0.08,0.0
FR,trajectory_unsustainable,2025-12-31,0.0,0.0,0.0,3.0
IT,avg_coupon_gap,2026-03-31,0.891,0.016,2.578,2.0
IT,avg_maturity_years,2025-12-31,7.1,0.0,0.2,3.0
IT,bill_share,2026-03-31,5.008,-0.09,-0.607,2.0
IT,breakeven_10y,,,,,
IT,captivity_score,2025-12-31,49.207,-0.385,-2.145,3.0
IT,cb_holdings_change_4q,2026-03-31,-1.82,0.615,-2.01,2.0
IT,central_bank_share,2026-03-31,9.524,-1.82,-6.341,2.0
IT,debt_dynamics,2026-03-31,-0.545,-0.811,-19.768,2.0
IT,debt_dynamics_residual,2026-03-31,1.545,-2.189,-6.932,2.0
IT,debt_gdp,2026-03-31,137.3,1.0,-38.9,2.0
IT,debt_gdp_projection_10y,2025-12-31,132.504,0.139,-114.424,3.0
IT,domestic_private_share,2025-12-31,59.916,1.974,3.249,3.0
IT,ecb_backstop_active,2026-09-30,1.0,0.0,0.0,0.0
IT,foreign_share,2025-12-31,30.0,0.0,2.615,3.0
IT,forward_r_5y,2025-12-31,3.305,0.122,2.096,3.0
IT,forward_r_minus_g_5y,2025-12-31,0.101,-0.013,-0.425,3.0
IT,fx_broad_reer_12m,2026-09-30,-0.31,-0.904,1.329,0.0
IT,g_nominal,2026-06-30,2.671,0.222,0.02,1.0
IT,g_trend,2026-09-30,3.263,0.085,2.716,0.0
IT,gold_local_ccy_12m,2026-09-30,21.796,-13.699,28.279,0.0
IT,gold_local_record,2026-09-30,0.0,0.0,0.0,0.0
IT,holders_captive,2025-12-31,0.0,0.0,0.0,3.0
IT,household_savings_to_debt,,,,,
IT,interest_to_revenue,2026-03-31,7.885,-0.472,0.527,2.0
IT,issuance_shortening,2026-03-31,-0.093,-0.417,0.087,2.0
IT,linker_share,,,,,
IT,marginal_yield,2026-09-30,3.986,0.427,3.209,0.0
IT,net_foreign_asset_position_gdp,,,,,
IT,policy_rate_minus_inflation,2026-09-30,-1.092,-1.524,1.449,0.0
IT,primary_balance_gdp,2026-03-31,0.699,0.314,7.828,2.0
IT,quadrant,2025-12-31,,,,3.0
IT,r_effective,2026-03-31,2.842,-0.17,0.451,2.0
IT,r_minus_g,2026-03-31,0.114,-0.379,-8.031,2.0
IT,spread_to_anchor_bp,2026-09-30,80.1,-6.5,-33.9,0.0
IT,stage_estimate,2026-03-31,0.0,-6.0,0.0,2.0
IT,target2_balance_gdp,2026-06-30,-14.635,3.012,15.131,1.0
IT,term_premium_proxy,2026-09-30,0.827,-0.741,-0.671,0.0
IT,trajectory_unsustainable,2025-12-31,0.0,0.0,-1.0,3.0
NL,avg_coupon_gap,2026-03-31,1.236,-0.025,2.932,2.0
NL,avg_maturity_years,2025-12-31,8.5,0.0,0.5,3.0
NL,bill_share,2026-03-31,9.249,2.661,2.838,2.0
NL,breakeven_10y,,,,,
NL,captivity_score,2025-12-31,45.817,-0.627,0.099,3.0
NL,cb_holdings_change_4q,2026-03-31,-3.443,-1.3,-3.186,2.0
NL,central_bank_share,2026-03-31,19.909,-3.443,-7.492,2.0
NL,debt_dynamics,2026-03-31,-0.242,1.176,-6.242,2.0
NL,debt_dynamics_residual,2026-03-31,0.442,1.024,1.842,2.0
NL,debt_gdp,2026-03-31,40.7,0.2,-19.9,2.0
NL,debt_gdp_projection_10y,2025-12-31,39.698,8.01,-36.799,3.0
NL,domestic_private_share,2025-12-31,37.611,2.95,8.381,3.0
NL,ecb_backstop_active,2026-09-30,1.0,0.0,0.0,0.0
NL,foreign_share,2025-12-31,42.0,0.0,-1.56,3.0
NL,forward_r_5y,2025-12-31,2.427,0.376,2.215,3.0
NL,forward_r_minus_g_5y,2025-12-31,-2.853,0.077,-0.451,3.0
NL,fx_broad_reer_12m,2026-09-30,-0.559,-3.799,1.271,0.0
NL,g_nominal,2026-06-30,4.782,-0.896,1.328,1.0
NL,g_trend,2026-09-30,5.412,0.181,2.801,0.0
NL,gold_local_ccy_12m,2026-09-30,21.796,-13.699,28.279,0.0
NL,gold_local_record,2026-09-30,0.0,-1.0,0.0,0.0
NL,holders_captive,2025-12-31,0.0,0.0,0.0,3.0
NL,household_savings_to_debt,,,,,
NL,interest_to_revenue,2026-03-31,1.704,0.096,0.177,2.0
NL,issuance_shortening,2026-03-31,2.81,4.566,3.137,2.0
NL,linker_share,,,,,
NL,marginal_yield,2026-09-30,3.285,0.402,3.624,0.0
NL,net_foreign_asset_position_gdp,,,,,
NL,policy_rate_minus_inflation,2026-09-30,-0.913,0.266,1.793,0.0
NL,primary_balance_gdp,2026-03-31,-0.954,-0.562,3.264,2.0
NL,quadrant,2025-12-31,,,,3.0
NL,r_effective,2026-03-31,1.791,0.116,0.426,2.0
NL,r_minus_g,2026-03-31,-2.953,1.304,-6.135,2.0
NL,spread_to_anchor_bp,2026-09-30,10.0,-9.0,7.6,0.0
NL,stage_estimate,2026-03-31,0.0,0.0,0.0,2.0
NL,target2_balance_gdp,2026-06-30,4.14,-3.338,2.511,1.0
NL,term_premium_proxy,2026-09-30,0.126,-0.766,-0.256,0.0
NL,trajectory_unsustainable,2025-12-31,0.0,0.0,0.0,3.0

```

## 2. Eight-quarter history

```csv
quarter,country,debt_gdp,primary_balance_gdp,r_effective,g_nominal,r_minus_g,debt_dynamics,debt_dynamics_residual,marginal_yield,avg_coupon_gap,forward_r_5y,g_trend,forward_r_minus_g_5y,debt_gdp_projection_10y,foreign_share,central_bank_share,domestic_private_share,avg_maturity_years,bill_share,linker_share,household_savings_to_debt,net_foreign_asset_position_gdp,captivity_score,term_premium_proxy,breakeven_10y,policy_rate_minus_inflation,cb_balance_sheet_gdp,cb_balance_sheet_growth_minus_g,cb_holdings_change_4q,issuance_shortening,fx_vs_usd_12m,fx_broad_reer_12m,gold_local_ccy_12m,gold_local_record,auction_tail,spread_to_anchor_bp,target2_balance_gdp,ecb_backstop_active,fx_reserves_12m,interest_to_revenue,stage_estimate,quadrant,trajectory_unsustainable,holders_captive
2024-12-31,US,106.2,-3.338,3.418,5.589,-2.171,1.049,-0.249,4.448,1.03,4.154,5.265,-1.112,127.127,29.867,16.041,54.092,5.963,21.889,7.351,4.286,-75.314,52.264,0.687,2.34,1.504,23.437,-16.309,-3.391,6.436,,6.232,30.701,1.0,-0.071,,,,,10.493,0.0,sustainable_free,0.0,0.0
2025-03-31,US,107.7,-3.256,3.445,5.358,-1.913,1.245,1.355,4.094,0.649,3.905,5.281,-1.375,125.011,31.286,15.748,52.966,6.0,21.546,7.125,4.255,-70.482,51.72,0.499,2.38,1.993,22.675,-15.305,-2.38,4.85,,4.085,38.23,1.0,0.006,,,,,10.589,0.0,sustainable_free,0.0,0.0
2025-06-30,US,106.3,-3.201,3.442,5.015,-1.573,1.573,1.227,4.032,0.59,3.86,5.29,-1.43,122.728,31.383,15.643,52.974,6.0,20.195,7.264,4.431,-71.212,51.996,0.46,2.29,1.695,22.152,-12.884,-1.777,2.237,,-2.323,44.153,1.0,-0.095,,,,,10.408,0.0,sustainable_free,0.0,0.0
2025-09-30,US,109.7,-2.887,3.437,5.044,-1.606,1.157,0.843,3.936,0.499,3.788,5.31,-1.522,121.791,30.489,14.884,54.628,6.0,21.541,7.029,4.415,-72.318,51.772,0.503,2.36,1.102,21.682,-11.705,-1.758,1.105,,-0.739,42.668,1.0,0.129,,,,,10.427,0.0,sustainable_free,0.0,0.0
2025-12-31,US,110.9,-2.519,3.467,5.038,-1.572,0.85,3.85,3.896,0.429,3.766,5.339,-1.573,118.891,30.027,14.669,55.304,6.0,21.641,7.052,4.403,-70.877,51.863,0.571,2.25,0.623,21.518,-8.601,-1.372,0.107,,-5.441,62.727,1.0,0.046,,,,,10.495,0.0,sustainable_free,0.0,0.0
2026-03-31,US,110.8,-2.351,3.466,5.279,-1.813,0.398,2.702,4.096,0.63,3.908,5.389,-1.481,118.116,29.741,14.922,55.337,5.91,22.122,6.779,4.311,-67.964,51.895,0.654,2.3,0.305,21.272,-6.512,-0.826,-0.385,,-4.423,62.789,1.0,0.065,,,,,17.192,0.0,sustainable_free,0.0,0.0
2026-06-30,US,,-2.05,3.632,5.663,-2.031,-0.109,,4.32,0.688,,5.46,,,,,,5.948,21.536,6.967,,-70.553,,0.697,2.24,-0.102,21.196,-4.56,,0.209,,-0.194,26.096,0.0,0.044,,,,,17.738,0.0,,,
2026-09-30,US,,,3.526,,,,,5.126,1.6,,5.533,,,,,,5.876,22.373,6.827,,,,1.077,2.36,-0.088,,,,0.706,,-0.735,17.748,0.0,-0.06,,,,,,,,,
2024-12-31,GB,85.8,-0.87,4.929,5.007,-0.077,0.8,-5.4,4.386,-0.543,4.67,4.513,0.157,95.843,32.0,26.0,42.0,14.093,,,,,66.49,-0.233,3.362,2.178,28.884,-15.909,-4.0,,-1.742,3.166,33.018,1.0,,,,,,11.083,0.0,unsustainable_captive,1.0,1.0
2025-03-31,GB,85.1,-0.838,5.07,5.452,-0.382,0.502,-3.702,4.453,-0.617,4.772,4.538,0.235,95.489,32.0,22.0,46.0,13.991,,,,,63.981,0.153,3.298,1.868,28.846,-13.35,-4.0,,2.05,2.229,35.454,1.0,,,,,,11.041,0.0,unsustainable_captive,1.0,1.0
2025-06-30,GB,86.6,-1.001,5.265,5.589,-0.324,0.716,-2.216,4.194,-1.071,4.74,4.575,0.165,98.037,32.0,22.0,46.0,13.89,,,,,63.758,0.191,3.25,0.671,27.8,-15.342,-4.0,,8.56,3.21,32.786,1.0,,,,,,11.378,0.0,unsustainable_captive,1.0,1.0
2025-09-30,GB,86.3,-0.959,5.256,5.389,-0.132,0.842,-3.742,4.429,-0.827,4.85,4.629,0.221,97.81,32.0,22.0,46.0,13.788,,,,,63.534,0.691,3.224,0.2,26.873,-14.986,-4.0,,0.328,0.782,42.201,1.0,,,,,,11.475,0.0,unsustainable_captive,1.0,1.0
2025-12-31,GB,88.9,-0.666,5.256,4.807,0.449,1.052,2.048,4.251,-1.005,4.77,4.68,0.09,96.353,32.0,22.0,46.0,13.686,,,,,63.31,0.716,3.207,0.431,25.982,-10.533,-4.0,,7.396,-0.437,51.521,1.0,,,,,,11.052,0.0,unsustainable_captive,1.0,1.0
2026-03-31,GB,86.5,-0.201,5.11,4.367,0.743,0.833,0.567,4.692,-0.417,4.913,4.724,0.189,90.098,,22.0,,13.585,,,,,,1.112,3.301,0.453,25.947,-10.487,0.0,,2.233,-0.867,59.233,1.0,,,,,,11.402,0.0,,,
2026-06-30,GB,87.45,-0.081,4.884,4.057,0.826,0.797,0.053,4.556,-0.327,4.732,4.756,-0.025,88.051,,22.0,,13.483,,,,,,0.992,3.106,1.158,25.753,-7.661,0.0,,-3.374,-2.681,30.499,0.0,,,,,,11.072,0.0,,,
2026-09-30,GB,86.65,,5.153,,,,,5.192,0.039,,4.79,,,,22.0,,13.381,,,,,,1.621,3.242,0.663,,,0.0,,-1.309,0.134,19.31,0.0,,,,,,11.829,,,,
2024-12-31,JP,196.0,-0.206,0.739,3.27,-2.532,-5.082,-7.818,0.906,0.168,0.815,1.862,-1.047,178.728,13.1,48.0,38.9,9.4,10.876,,,,80.686,0.512,,-3.419,117.461,-3.533,1.0,-1.218,-10.453,-2.175,45.958,1.0,,,,,,3.976,0.0,sustainable_captive,0.0,1.0
2025-03-31,JP,191.0,-0.035,0.761,3.951,-3.19,-6.565,-9.335,1.24,0.479,0.979,1.89,-0.911,174.936,13.0,46.0,41.0,9.4,10.684,,,,79.867,0.643,,-3.049,113.125,-7.475,-2.0,-1.586,0.881,3.312,37.023,1.0,,,,,,4.028,0.0,sustainable_captive,0.0,1.0
2025-06-30,JP,188.7,0.136,0.794,4.607,-3.813,-7.854,-5.846,1.176,0.382,0.967,1.925,-0.958,170.394,13.0,46.0,41.0,9.4,11.062,,,,79.734,0.716,,-2.916,109.813,-9.407,-2.0,-1.088,11.59,7.406,29.18,1.0,,,,,,4.079,0.0,sustainable_captive,0.0,1.0
2025-09-30,JP,183.2,0.307,0.811,4.676,-3.865,-8.067,-9.533,1.38,0.569,1.071,1.947,-0.876,165.095,13.0,46.0,41.0,9.4,10.879,,,,79.798,0.704,,-2.378,105.413,-12.312,-2.0,-0.603,-3.19,-2.841,47.369,1.0,,,,,,4.13,0.0,sustainable_captive,0.0,1.0
2025-12-31,JP,177.7,0.477,0.842,4.654,-3.812,-7.949,-10.351,1.706,0.864,1.238,1.965,-0.727,160.8,13.0,46.0,41.0,9.4,10.855,,,,79.807,0.899,,-1.272,101.702,-14.041,-2.0,-0.515,0.364,-5.497,62.137,1.0,,,,,,4.18,0.0,sustainable_captive,0.0,1.0
2026-03-31,JP,175.6,,,4.276,,,,1.97,,,1.986,,,13.0,46.0,41.0,,10.488,,,,,0.991,,-0.661,98.564,-13.422,0.0,-0.9,-5.771,-10.388,72.758,1.0,,,,,,,,,,
2026-06-30,JP,,,,3.814,,,,2.167,,,2.014,,,13.0,46.0,41.0,,10.374,,,,,1.308,,-0.702,94.288,-14.677,0.0,-1.471,-11.34,-11.631,42.224,0.0,,,,,,,,,,
2026-09-30,JP,,,,,,,,2.615,,,2.019,,,13.0,46.0,41.0,,,,,,,1.105,,-0.898,,,0.0,,-5.901,-8.076,25.133,0.0,,,,,,,,,,
2024-12-31,AU,49.4,-0.574,3.644,3.651,-0.008,0.57,-0.27,4.434,0.791,4.148,5.338,-1.19,49.493,45.0,28.0,27.0,7.0,,,,,43.473,0.084,,1.938,15.345,-24.897,-1.4,,-9.108,-2.239,43.798,1.0,,,,,,4.704,0.0,sustainable_free,0.0,0.0
2025-03-31,AU,51.0,-0.653,3.687,3.632,0.056,0.681,0.519,4.542,0.855,4.236,5.379,-1.144,51.883,45.0,24.0,31.0,7.0,,,,,41.187,0.442,,1.7,15.487,-22.44,-4.0,,-3.858,-2.783,43.777,1.0,,,,,,4.822,0.0,sustainable_free,0.0,0.0
2025-06-30,AU,50.2,-0.732,3.898,3.567,0.331,0.892,1.008,3.861,-0.037,3.874,5.433,-1.559,50.109,45.0,24.0,31.0,7.0,,,,,41.187,0.971,2.125,1.755,14.533,-6.076,-4.0,,-1.117,-4.985,45.782,1.0,,,,,,4.94,0.0,sustainable_free,0.0,0.0
2025-09-30,AU,51.4,-0.811,3.849,4.083,-0.234,0.693,0.307,3.861,0.012,3.856,5.498,-1.642,51.505,45.0,24.0,31.0,7.0,,,,,41.187,0.971,2.125,0.381,14.206,-10.831,-4.0,,-4.761,-1.405,49.799,1.0,,,,,,5.058,0.0,sustainable_free,0.0,0.0
2025-12-31,AU,50.6,-0.89,4.051,4.779,-0.728,0.531,0.669,4.84,0.79,4.568,5.579,-1.011,54.427,45.0,24.0,31.0,7.0,,,,,41.187,1.24,,-0.026,13.262,-14.226,-4.0,,7.656,2.535,51.154,1.0,,,,,,5.175,0.0,sustainable_free,0.0,0.0
2026-03-31,AU,51.1,,,5.246,,,,5.047,,,5.669,,,,24.0,,,,,,,,0.947,,0.006,12.931,-17.371,0.0,,8.997,10.153,49.352,1.0,,,,,,,,,,
2026-06-30,AU,,,,5.567,,,,4.711,,,5.756,,,,24.0,,,,,,,,0.318,2.365,0.408,12.438,-15.22,0.0,,4.87,8.958,20.24,0.0,,,,,,,,,,
2026-09-30,AU,,,,,,,,5.136,,,5.844,,,,24.0,,,,,,,,0.786,,,,,0.0,,5.68,8.15,11.419,0.0,,,,,,,,,,
2024-12-31,CA,93.5,1.433,4.152,4.834,-0.682,-2.042,6.342,3.11,-1.042,3.5,4.63,-1.131,70.475,28.0,23.6,48.4,6.8,,,,,51.727,0.3,1.72,1.418,8.919,-17.314,-6.4,,-8.319,-4.362,42.561,1.0,,,,,,8.273,0.0,sustainable_free,0.0,0.0
2025-03-31,CA,95.5,1.424,4.064,5.321,-1.257,-2.548,8.648,2.766,-1.298,3.255,4.664,-1.409,70.29,28.0,22.0,50.0,6.8,,,,,50.813,0.51,1.6,0.435,7.924,-23.852,-6.4,,-5.835,-4.373,46.795,1.0,,,,,,8.079,0.0,sustainable_free,0.0,0.0
2025-06-30,CA,95.2,1.416,3.909,4.995,-1.086,-2.397,7.197,3.004,-0.905,3.346,4.725,-1.379,70.244,28.0,22.0,50.0,6.8,,,,,50.813,0.69,1.63,0.891,7.714,-14.97,-4.8,,0.47,-1.716,43.479,1.0,,,,,,7.885,0.0,sustainable_free,0.0,0.0
2025-09-30,CA,96.1,1.407,3.682,4.894,-1.211,-2.54,5.14,2.89,-0.792,3.192,4.82,-1.628,69.223,28.0,22.0,50.0,6.8,,,,,50.813,0.7,1.51,0.141,7.364,-19.954,-3.2,,-2.987,-2.922,47.061,1.0,,,,,,7.691,0.0,sustainable_free,0.0,0.0
2025-12-31,CA,96.1,1.399,3.572,4.398,-0.826,-2.171,4.771,3.084,-0.488,3.27,4.936,-1.666,68.969,28.0,22.0,50.0,6.8,,,,,50.813,0.84,1.55,-0.107,7.411,-17.643,-1.6,,5.018,0.432,54.952,1.0,,,,,,7.497,0.0,sustainable_free,0.0,0.0
2026-03-31,CA,97.1,,,3.666,,,,3.204,,,5.035,,,,22.0,,,,,,,,0.64,1.63,-0.135,6.986,-12.264,0.0,,3.053,1.891,57.966,1.0,,,,,,,,,,
2026-06-30,CA,,,,4.448,,,,3.124,,,5.148,,,,22.0,,,,,,,,0.64,1.67,-0.548,6.948,-10.368,0.0,,-4.118,-3.431,31.512,0.0,,,,,,,,,,
2026-09-30,CA,,,,,,,,3.742,,,5.266,,,,22.0,,,,,,,,0.62,2.01,-0.784,,,0.0,,-1.992,-1.089,20.141,0.0,,,,,,,,,,
2024-12-31,CH,25.8,0.859,1.436,2.835,-1.399,-1.219,1.319,0.192,-1.245,0.92,2.378,-1.458,14.335,15.0,0.0,85.0,11.0,,,,,56.044,0.313,,-0.126,99.184,4.644,0.0,,-7.311,-1.705,41.011,1.0,,,,,,1.105,0.0,sustainable_free,0.0,0.0
2025-03-31,CH,25.5,0.856,1.41,3.63,-2.22,-1.438,0.738,0.35,-1.06,0.969,2.431,-1.461,14.088,15.0,0.0,85.0,11.0,,,,,56.044,0.411,,-0.092,99.553,-1.512,0.0,,1.945,-1.146,35.593,1.0,,,,,,1.098,0.0,sustainable_free,0.0,0.0
2025-06-30,CH,25.7,0.854,1.428,3.712,-2.284,-1.441,1.441,0.222,-1.206,0.927,2.502,-1.574,14.083,15.0,0.0,85.0,11.0,,,,,56.044,0.471,,-0.078,97.137,-0.106,0.0,,13.278,2.158,27.256,1.0,,,,,,1.091,0.0,sustainable_free,0.0,0.0
2025-09-30,CH,25.8,0.851,1.393,3.136,-1.742,-1.304,1.104,0.194,-1.2,0.896,2.569,-1.673,14.014,15.0,0.0,85.0,11.0,,,,,56.044,0.461,,-0.224,100.721,3.202,0.0,,6.001,0.902,34.592,1.0,,,,,,1.085,0.0,sustainable_free,0.0,0.0
2025-12-31,CH,26.2,0.849,1.384,2.405,-1.021,-1.112,1.512,0.374,-1.009,0.965,2.628,-1.663,14.39,15.0,0.0,85.0,11.0,,,,,56.044,0.374,,-0.063,101.366,2.253,0.0,,14.264,1.487,42.413,1.0,,,,,,1.078,0.0,sustainable_free,0.0,0.0
2026-03-31,CH,26.5,,,1.417,,,,0.444,,,2.66,,,,,,,,,,,,0.444,,-0.315,100.838,1.309,,,10.166,4.616,47.768,1.0,,,,,,,,,,
2026-06-30,CH,,,,1.208,,,,0.354,,,2.674,,,,,,,,,,,,0.354,,-0.451,102.897,6.001,,,-1.782,-0.983,28.383,0.0,,,,,,,,,,
2026-09-30,CH,,,,,,,,0.514,,,2.714,,,,,,,,,,,,0.514,,-0.807,,,,,-4.576,-3.011,23.395,0.0,,,,,,,,,,
2024-12-31,EA,85.1,-1.156,2.293,3.863,-1.57,-0.183,-0.017,2.448,0.155,2.384,3.997,-1.613,83.568,43.854,15.564,40.582,7.634,6.802,,,,49.669,0.728,,0.567,42.073,-11.402,-2.692,-0.092,-6.427,-1.424,39.679,1.0,,,,1.0,,4.061,0.0,sustainable_free,0.0,0.0
2025-03-31,EA,84.7,-1.071,2.338,3.722,-1.384,-0.104,-0.096,2.743,0.405,2.576,4.026,-1.45,83.642,43.803,14.787,41.409,7.633,6.235,,,,49.551,1.247,,0.322,41.197,-7.975,-2.725,-0.213,0.046,-0.983,38.166,1.0,,,,1.0,,4.109,0.0,sustainable_free,0.0,0.0
2025-06-30,EA,85.7,-1.015,2.353,3.771,-1.418,-0.178,1.778,2.542,0.188,2.463,4.049,-1.585,82.971,43.834,14.135,42.03,7.635,6.071,,,,49.329,1.161,,0.013,39.548,-9.608,-2.632,-0.413,9.887,2.063,31.183,1.0,,,,1.0,,4.082,0.0,sustainable_free,0.0,0.0
2025-09-30,EA,85.7,-1.104,2.294,3.699,-1.405,-0.105,-0.195,2.687,0.393,2.525,4.061,-1.536,84.166,43.907,13.647,42.446,7.637,6.131,,,,49.085,1.16,,-0.229,39.642,-7.264,-2.474,-0.551,5.294,3.115,35.495,1.0,,,,1.0,,4.067,0.0,sustainable_free,0.0,0.0
2025-12-31,EA,85.0,-1.063,2.325,3.687,-1.362,-0.096,-0.004,2.771,0.446,2.587,4.067,-1.481,83.599,43.872,13.128,43.0,7.634,6.42,,,,48.802,1.104,,0.036,40.001,-5.106,-2.436,-0.157,13.38,4.536,43.523,1.0,,,,1.0,,4.065,0.0,sustainable_free,0.0,0.0
2026-03-31,EA,85.6,-1.164,2.326,3.428,-1.102,0.231,0.669,3.04,0.714,,4.067,,,,12.402,,,6.459,,,,,0.751,,-0.553,39.299,-4.765,-2.385,-0.064,6.688,2.404,52.585,1.0,,,,1.0,,4.049,0.0,,,
2026-06-30,EA,,,,,,,,3.011,,,4.09,,,,,,,,,,,,0.891,,-0.499,,,,,-2.999,-1.136,29.995,0.0,,,,1.0,,,,,,
2026-09-30,EA,,,,,,,,3.425,,,4.122,,,,,,,,,,,,0.443,,-0.999,,,,,-3.323,-1.195,21.796,0.0,,,,1.0,,,,,,
2024-12-31,DE,58.2,-1.614,1.742,3.134,-1.392,0.795,-1.495,2.178,0.436,2.017,3.982,-1.964,62.919,47.0,20.109,32.891,7.0,5.4,,,,42.011,0.167,,0.359,,,-3.23,-2.236,,-0.423,39.679,1.0,,,23.837,1.0,,2.234,0.0,sustainable_free,0.0,0.0
2025-03-31,DE,57.1,-1.339,1.781,2.953,-1.171,0.662,-1.362,2.741,0.96,2.383,3.964,-1.58,61.461,47.0,19.261,33.739,7.0,4.436,,,,42.152,0.746,,0.308,,,-3.308,-2.739,,-0.662,38.166,1.0,,,24.171,1.0,,2.252,0.0,sustainable_free,0.0,0.0
2025-06-30,DE,57.6,-1.161,1.799,2.99,-1.191,0.484,0.316,2.52,0.721,2.246,3.949,-1.703,59.587,47.0,18.468,34.532,7.0,3.855,,,,42.17,0.675,,-0.01,,,-3.15,-3.663,,0.994,31.183,1.0,,,23.569,1.0,,2.232,0.0,sustainable_free,0.0,0.0
2025-09-30,DE,57.9,-1.173,1.799,3.169,-1.369,0.372,-0.972,2.693,0.894,2.355,3.939,-1.584,60.568,47.0,17.642,35.358,7.0,4.043,,,,41.91,0.702,,-0.423,,,-3.152,-3.86,,1.729,35.495,1.0,,,23.334,1.0,,2.234,0.0,sustainable_free,0.0,0.0
2025-12-31,DE,58.2,-1.652,1.829,3.368,-1.539,0.756,-0.756,2.813,0.984,2.456,3.941,-1.485,65.856,47.0,16.982,36.018,7.0,4.438,,,,41.615,0.705,,0.174,,,-3.126,-2.662,,2.013,43.523,1.0,,,22.557,1.0,,2.269,0.0,sustainable_free,0.0,0.0
2026-03-31,DE,58.7,-2.01,1.851,3.437,-1.586,1.104,0.496,2.91,1.059,,3.937,,,,16.067,,,4.545,,,,,0.321,,-0.723,,,-3.194,-1.864,,1.394,52.585,1.0,,,22.529,1.0,,2.287,0.0,,,
2026-06-30,DE,,,,3.532,,,,2.964,,,3.937,,,,,,,,,,,,0.488,,-0.049,,,,,,-1.382,29.995,0.0,,,22.591,1.0,,,,,,
2026-09-30,DE,,,,,,,,3.185,,,3.949,,,,,,,,,,,,0.026,,-0.612,,,,,,-1.403,21.796,0.0,,,,1.0,,,,,,
2024-12-31,FR,106.7,-3.747,1.938,3.494,-1.556,2.101,-1.201,3.01,1.072,2.576,3.144,-0.567,137.555,54.0,13.852,32.148,8.5,8.832,,,,38.241,0.999,,1.682,,,-2.395,1.472,,-1.842,39.679,1.0,,83.2,-3.682,1.0,,4.003,0.0,sustainable_free,0.0,0.0
2025-03-31,FR,106.8,-3.595,1.984,2.677,-0.693,2.866,-1.366,3.43,1.446,2.845,3.168,-0.322,138.98,54.0,13.042,32.958,8.5,8.667,,,,38.109,1.435,,1.731,,,-2.475,1.59,,-1.882,38.166,1.0,,68.9,-5.883,1.0,,4.137,0.0,sustainable_free,0.0,0.0
2025-06-30,FR,108.7,-3.501,1.956,2.46,-0.504,2.975,1.325,3.24,1.284,2.715,3.179,-0.464,138.239,54.0,12.366,33.634,8.5,8.88,,,,37.875,1.395,,1.034,,,-2.438,1.728,,-0.218,31.183,1.0,,72.0,-6.553,1.0,,4.135,0.0,sustainable_free,0.0,0.0
2025-09-30,FR,109.6,-3.33,1.947,1.962,-0.015,3.315,-1.715,3.51,1.563,2.868,3.179,-0.311,139.208,54.0,12.122,33.878,8.5,8.676,,,,37.89,1.519,,0.847,,,-2.171,1.593,,0.136,35.495,1.0,,81.7,-6.764,1.0,,4.167,0.0,sustainable_free,0.0,0.0
2025-12-31,FR,107.7,-2.956,1.988,1.988,0.0,2.956,-1.956,3.56,1.572,2.906,3.175,-0.269,134.142,54.0,11.592,34.408,8.5,8.75,,,,37.739,1.452,,1.213,,,-2.259,1.431,,0.706,43.523,1.0,,74.7,-5.297,1.0,,4.205,0.0,sustainable_free,0.0,0.0
2026-03-31,FR,109.4,-2.96,1.969,1.911,0.057,3.021,-0.421,3.64,1.671,,3.17,,,,10.867,,,8.917,,,,,1.051,,0.312,,,-2.176,0.983,,0.169,52.585,1.0,,73.0,-5.037,1.0,,4.195,0.0,,,
2026-06-30,FR,,,,1.857,,,,3.68,,,3.169,,,,,,,,,,,,1.204,,0.486,,,,,,-1.401,29.995,0.0,,71.6,-6.512,1.0,,,,,,
2026-09-30,FR,,,,,,,,4.0,,,3.209,,,,,,,,,,,,0.841,,-0.107,,,,,,-0.323,21.796,0.0,,81.5,,1.0,,,,,,
2024-12-31,IT,135.0,0.403,2.979,3.022,-0.043,-0.461,3.261,3.321,0.342,3.183,3.069,0.114,132.366,30.0,12.059,57.941,7.1,5.22,,,,49.592,1.31,,1.75,,,-2.345,0.375,,-1.991,39.679,0.0,,114.3,-18.838,1.0,,8.264,6.0,sustainable_free,0.0,0.0
2025-03-31,IT,136.3,0.385,3.012,2.519,0.493,0.267,3.733,3.887,0.875,3.538,3.111,0.427,137.891,30.0,11.344,58.656,7.1,5.098,,,,49.467,1.892,,0.592,,,-2.435,0.325,,-0.824,38.166,0.0,,114.6,-18.403,1.0,,8.356,6.0,sustainable_free,0.0,0.0
2025-06-30,IT,138.9,0.597,2.957,2.449,0.508,0.076,6.424,3.501,0.544,3.282,3.149,0.134,134.564,30.0,10.816,59.184,7.1,5.136,,,,49.33,1.656,,0.344,,,-2.385,0.138,,0.545,31.183,0.0,,98.1,-17.647,1.0,,8.251,6.0,sustainable_free,0.0,0.0
2025-09-30,IT,137.6,0.448,2.935,2.508,0.426,0.13,1.87,3.559,0.624,3.308,3.178,0.13,134.682,30.0,10.469,59.531,7.1,5.001,,,,49.295,1.568,,0.432,,,-2.152,-0.039,,0.594,35.495,0.0,,86.6,-17.018,1.0,,8.157,0.0,sustainable_free,0.0,0.0
2025-12-31,IT,137.6,0.626,2.937,2.579,0.358,-0.142,2.742,3.552,0.615,3.305,3.204,0.101,132.504,30.0,10.084,59.916,7.1,4.995,,,,49.207,1.444,,0.847,,,-1.974,-0.041,,1.123,43.523,0.0,,73.9,-15.823,1.0,,8.046,0.0,sustainable_free,0.0,0.0
2026-03-31,IT,137.3,0.699,2.842,2.728,0.114,-0.545,1.545,3.733,0.891,,3.224,,,,9.524,,,5.008,,,,,1.144,,0.288,,,-1.82,-0.093,,0.172,52.585,0.0,,82.3,-15.64,1.0,,7.885,0.0,,,
2026-06-30,IT,,,,2.671,,,,3.734,,,3.238,,,,,,,,,,,,1.258,,-0.798,,,,,,-0.271,29.995,0.0,,77.0,-14.635,1.0,,,,,,
2026-09-30,IT,,,,,,,,3.986,,,3.263,,,,,,,,,,,,0.827,,-1.092,,,,,,-0.31,21.796,0.0,,80.1,,1.0,,,,,,
2024-12-31,NL,42.2,0.011,1.637,6.201,-4.565,-2.047,-0.353,2.447,0.81,2.051,4.981,-2.93,31.688,42.0,23.339,34.661,8.5,10.379,,,,46.444,0.436,,-1.094,,,-3.05,-1.462,,0.699,39.679,1.0,,26.9,5.967,1.0,,1.61,0.0,sustainable_free,0.0,0.0
2025-03-31,NL,40.5,-0.392,1.675,5.932,-4.257,-1.418,-0.582,2.936,1.261,2.353,5.085,-2.732,34.599,42.0,23.353,34.647,8.5,6.588,,,,47.785,0.941,,-1.14,,,-2.144,-1.756,,1.103,38.166,1.0,,19.5,8.648,1.0,,1.609,0.0,sustainable_free,0.0,0.0
2025-06-30,NL,40.6,-0.699,1.708,5.678,-3.97,-0.941,0.241,2.757,1.049,2.289,5.17,-2.881,36.939,42.0,23.084,34.916,8.5,4.705,,,,48.386,0.912,,-0.992,,,-2.312,-0.766,,2.508,31.183,1.0,,23.7,7.478,1.0,,1.633,0.0,sustainable_free,0.0,0.0
2025-09-30,NL,40.1,-0.802,1.759,5.404,-3.645,-0.692,-0.208,2.883,1.124,2.39,5.231,-2.841,37.614,42.0,21.672,36.328,8.5,7.027,,,,47.234,0.892,,-1.178,,,-2.786,-0.133,,3.24,35.495,1.0,,19.0,6.802,1.0,,1.641,0.0,sustainable_free,0.0,0.0
2025-12-31,NL,42.1,-0.87,1.729,4.964,-3.234,-0.495,0.395,2.968,1.239,2.427,5.28,-2.853,39.698,42.0,20.389,37.611,8.5,10.188,,,,45.817,0.86,,-0.912,,,-2.95,2.058,,4.361,43.523,1.0,,15.5,3.576,1.0,,1.665,0.0,sustainable_free,0.0,0.0
2026-03-31,NL,40.7,-0.954,1.791,4.744,-2.953,-0.242,0.442,3.027,1.236,,5.312,,,,19.909,,,9.249,,,,,0.438,,-0.684,,,-3.443,2.81,,1.979,52.585,1.0,,11.7,6.087,1.0,,1.704,0.0,,,
2026-06-30,NL,,,,4.782,,,,3.077,,,5.348,,,,,,,,,,,,0.601,,-0.665,,,,,,-0.161,29.995,0.0,,11.3,4.14,1.0,,,,,,
2026-09-30,NL,,,,,,,,3.285,,,5.412,,,,,,,,,,,,0.126,,-0.913,,,,,,-0.559,21.796,0.0,,10.0,,1.0,,,,,,

```

## 3. Transitions (last eight quarters)

```
country,quarter,kind,from,to
IT,2024-12-31,quadrant,unsustainable_free,sustainable_free
IT,2024-12-31,stage,3.0,6.0
IT,2025-09-30,stage,6.0,0.0

```

## 4. Backtest calibration

### lead_summary
indicator,events_with_data,warned_share,median_lead_quarters,mean_share_on_warning_side
breakeven_10y,2,1.0,20.0,1.0
policy_rate_minus_inflation,24,0.8333333333333334,20.0,0.4166666666666667
gold_local_ccy_12m,28,0.8214285714285714,19.0,0.3392857142857143
avg_coupon_gap,16,0.8125,19.0,0.403125
primary_balance_gdp,28,0.75,20.0,0.5357142857142857
forward_r_minus_g_5y,4,0.75,9.0,0.3125
r_minus_g,25,0.72,20.0,0.49
spread_to_anchor_bp,7,0.7142857142857143,20.0,0.42142857142857143
fx_vs_usd_12m,28,0.7142857142857143,18.5,0.3
cb_holdings_change_4q,17,0.7058823529411765,20.0,0.4755835667600374
term_premium_proxy,16,0.6875,11.0,0.353125
target2_balance_gdp,6,0.6666666666666666,8.0,0.35000000000000003
issuance_shortening,8,0.625,11.0,0.175
captivity_score,4,0.5,14.5,0.5
debt_gdp,26,0.46153846153846156,20.0,0.39166666666666666
fx_broad_reer_12m,20,0.45,18.0,0.10500000000000001
foreign_share,25,0.12,3.0,0.12
bill_share,9,0.1111111111111111,11.0,0.1111111111111111

### forward_r
country,n,rmse_forward_r,rmse_current_r,bias_forward_r,bias_current_r,forward_better
AU,24,1.2102770333233768,1.0927560922316015,-0.4905224506668116,0.6457002955504328,False
CA,24,1.4704033788345074,0.5395598246210528,-1.3104762319755838,0.08964545197387282,False
CH,20,0.9422848038773681,0.32632037968139527,-0.916122580548738,-0.16152480934369867,False
DE,21,1.0138855107804996,0.5842665274146667,-0.7861502236428154,0.1168392092062193,False
EA,21,1.2335160620859724,0.57906403210796,-1.0697007364436988,-0.04866688746405248,False
FR,21,0.9310361476123914,0.5042343034231307,-0.751818263202741,0.03453437730196545,False
GB,27,2.7438988076083204,2.30981161373087,-2.062589292676736,-1.4246621650834637,False
GR,21,1.5855913428982282,0.5080922601456223,0.7865853758149293,-0.05908516976594479,False
IT,21,0.850451177107378,0.4227609318073185,-0.6396467658944553,-0.08308047741894901,False
JP,24,0.3033403147104674,0.216653298114345,-0.28618868335612996,0.1809261495673092,False
NL,21,0.8067417884815071,0.48281015026980173,-0.6370774917543238,0.2591325857634766,False
SE,20,1.3420989672160104,0.922396398677427,-1.0512087662310745,-0.6016890998342276,False
US,83,1.4863354332772394,2.0269176211099182,-0.3357849057350531,1.0127779773133545,True

## 5. Previous report (2026-Q2)

(no previous report)

## 6. Data issues

Problems:
GB.avg_maturity_years.UK_DMO: failed to update (ValueError: no gilts parsed from D1A)
GB.bill_share.UK_DMO: failed to update (ParseError: not well-formed (invalid token): line 18, column 2398)
GB.linker_share.UK_DMO: failed to update (ValueError: no gilts parsed from D1A)
GB.marketable_debt_lcu.UK_DMO: failed to update (ParseError: not well-formed (invalid token): line 18, column 2398)

Structural values filled for the report quarter (hand-maintained or annual series, interpolated between observations or carried at most four quarters):
US household_fin_assets_lcu: carried forward (FRED)
US niip_gdp: carried forward (FRED)
GB cb_gov_share: carried forward (MANUAL)
GB avg_maturity_years: interpolated (MANUAL)
JP cb_gov_share: carried forward (MANUAL)
JP foreign_share: carried forward (MANUAL)
AU cb_gov_share: carried forward (MANUAL)
CA cb_gov_share: carried forward (MANUAL)
EA ecb_backstop_active: carried forward (MANUAL)

Known gaps, no free source (not failures):
UK bill share comes from the DMO gilt snapshot, first taken in 2026-Q4: GB bill_share
linker share wired for the US and UK only: GB linker_share, JP linker_share, AU linker_share, CA linker_share, CH linker_share, EA linker_share, DE linker_share, FR linker_share, IT linker_share, NL linker_share
household financial accounts wired for the US only (Fed Z.1): GB household_savings_to_debt, JP household_savings_to_debt, AU household_savings_to_debt, CA household_savings_to_debt, CH household_savings_to_debt, EA household_savings_to_debt, DE household_savings_to_debt, FR household_savings_to_debt, IT household_savings_to_debt, NL household_savings_to_debt
NIIP wired for the US only (FRED); IMF IIP not in DataMapper: GB net_foreign_asset_position_gdp, JP net_foreign_asset_position_gdp, AU net_foreign_asset_position_gdp, CA net_foreign_asset_position_gdp, CH net_foreign_asset_position_gdp, EA net_foreign_asset_position_gdp, DE net_foreign_asset_position_gdp, FR net_foreign_asset_position_gdp, IT net_foreign_asset_position_gdp, NL net_foreign_asset_position_gdp
UK bill share starts with the 2026 DMO snapshot; needs 8 quarters of history: GB issuance_shortening
no free JGBi breakeven series: JP breakeven_10y
AOFM data hub is behind bot protection; no other free source: AU bill_share
needs a bill share (see AU.bill_share): AU issuance_shortening
no free Government of Canada bill-share series wired: CA bill_share
needs a bill share (see CA.bill_share): CA issuance_shortening
no free Swiss money-market debt share series wired: CH bill_share
Switzerland issues no inflation-linked bonds: CH breakeven_10y
needs a bill share (see CH.bill_share): CH issuance_shortening
no free euro inflation-swap or linker breakeven series: EA breakeven_10y
no free Bund linker breakeven series: DE breakeven_10y
no free OATi breakeven series: FR breakeven_10y
no free BTP Italia breakeven series: IT breakeven_10y
the Netherlands issues no linkers: NL breakeven_10y

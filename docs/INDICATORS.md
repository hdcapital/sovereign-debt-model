# Indicators

Generated from the indicator registry (`src/sdm/indicators/blocks.py`) and `config/indicators.yaml` by
`python -m sdm.cli docs`; edit the docstrings and config, not this file. All quarterly, per country, full history.
Direction `above`/`below` is the warning side of the threshold. Detailed source priority: `docs/DATA_SOURCES.md`.

## Trajectory block

| Indicator | Units | Formula / definition | Source series | Threshold | Informs | What it leads to |
|---|---|---|---|---|---|---|
| `debt_gdp` | % GDP | Gross general government debt as a share of GDP. | BIS total credit; Eurostat; IMF GDD; FRED; ONS | above 90 | context | The size of the stock the transfer     has to act on. On its own it predicts almost nothing: Russia defaulted near 55%, Japan     carries over 200% with no crisis. It matters through the arithmetic, (r minus g) times     this number, and through who holds it. |
| `primary_balance_gdp` | % GDP | Budget balance excluding interest, trailing four quarters, surplus positive. | ONS, Fiscal Data/NIPA, ECB GFS, Eurostat; IMF GDD `pb` annual | below 0 | stage 0, quadrant | This is     the fuel. A primary deficit that does not close in expansions means the debt ratio     rises whenever r exceeds g, with no further decisions required. |
| `r_effective` | % | Average interest rate actually paid on the stock: interest over four quarters divided     by the debt a year earlier. | interest: Fiscal Data, ONS, ECB D41, IMF `ie`; debt level | — | trajectory | It lags the market because most debt is fixed coupon, so     today's r understates where the interest bill is going. |
| `g_nominal` | % | Nominal GDP growth over four quarters. | FRED, ONS, ECB MNA, OECD via FRED; IMF/WB annual | — | trajectory | Inflation counts in full, which is exactly why     the repression exit works: it raises g without raising the coupon on existing debt. |
| `r_minus_g` | pp | The snowball term. | derived | above 0 | stage 1 | Positive with a primary deficit means the debt ratio rises on     autopilot; the trigger stage is r crossing above g. |
| `debt_dynamics` | pp of GDP | The identity's predicted annual change in debt/GDP: (r minus g) times last year's     ratio minus the primary balance. | derived | — | diagnostic | Compare with the actual change; a large residual means     off-budget financing or valuation effects are moving the stock. |
| `debt_dynamics_residual` | pp of GDP | Actual change in debt/GDP minus the identity's prediction (the stock-flow     adjustment). | derived | — | diagnostic | Persistently positive means the headline deficit understates the borrowing. |
| `marginal_yield` | % | What new borrowing costs: a blend of the 2-year and 10-year yields weighted by the     typical issuance mix. | FRED, BoE, MoF, RBA, BoC, SNB, ECB IRS | — | stage 1 | Where r is heading as the stock rolls over. |
| `avg_coupon_gap` | pp | Marginal yield minus the average rate paid. | derived | above 0 | stage 1 | Positive means interest cost is already     committed: the bill keeps rising with no further shock as old coupons roll into new. |
| `forward_r_5y` | % | The average rate the stock will carry in five years if yields stay where they are and     issuance continues on the current pattern: each year 1/average-maturity of the stock     reprices at the marginal yield, plus all deficit issuance. | derived | — | quadrant | More informative than     today's r, which is a lagging average. |
| `g_trend` | % | Trend nominal growth: ten-year trailing mean of four-quarter growth. | derived | — | quadrant | What g is likely     to be over the horizon of the forward-r projection. |
| `forward_r_minus_g_5y` | pp | The model's trajectory variable: forward r minus trend g. | derived | above 0 | quadrant, stage 1 | Above zero together with a     primary deficit, the path is unsustainable and the only questions left are who pays and     through which channel. |
| `debt_gdp_projection_10y` | % GDP | Debt/GDP ten years out under forward r, trend g and the current primary balance:     the identity iterated annually. | derived | — | narrative | Where the stock goes if nothing changes. |

## Captivity block

| Indicator | Units | Formula / definition | Source series | Threshold | Informs | What it leads to |
|---|---|---|---|---|---|---|
| `foreign_share` | % of debt | Share of the debt held by non-residents. | Arslanalp-Tsuda to 2016; FRED FDHBFIN; manual after | above 40 | captivity | These are the holders who can leave within a     cycle; a high share is what turns an unsustainable path into a crisis rather than a grind. |
| `central_bank_share` | % of debt | Share of the debt held by the central bank, the ultimate captive buyer. | Arslanalp-Tsuda; FRED FDHBFRBN; ECB PSPP cumulative; manual | — | captivity, stage 4 | A rising share     after hikes have paused is the fiscal-dominance tell. For a union member this is the ECB's     holdings, and the captivity score discounts it because that bid is political, not structural. |
| `domestic_private_share` | % of debt | Residual: debt held by domestic banks, pensions, insurers and households. | derived | — | captivity | The pool     that financial repression acts on. |
| `avg_maturity_years` | years | Average remaining maturity of the stock. | DMO snapshot; manual (approximate) | — | captivity, forward r | Short debt means holders are effectively     free (they are repaid soon and choose whether to come back) and that r converges to the     market yield fast. |
| `bill_share` | % of marketable debt | Bills under one year as a share of marketable debt. | Fiscal Data MSPD, MoF suii, ECB SEC, DMO | above 25 | captivity, stage 4 | A treasury that shifts into bills     is dodging the term premium; it also hands the holders a quick exit. |
| `linker_share` | % of marketable debt | Inflation-linked share. | Fiscal Data MSPD, DMO | — | captivity | Linkers cannot be inflated away, so a large share narrows the     repression exit and pushes the adjustment onto taxes or the currency. |
| `household_savings_to_debt` | ratio | Household financial assets relative to government debt: the size of the domestic pool     that can be made to hold the paper. | FRED Z.1 (US only) | — | captivity | Japan's large ratio is why its grind has lasted. |
| `net_foreign_asset_position_gdp` | % GDP | Net international investment position over GDP. | FRED IIP (US only) | — | captivity | Creditor nations fund themselves;     debtor nations depend on the foreigners who can leave. |
| `captivity_score` | 0-100 | Composite captivity, 0 to 100, with weights from config/indicators.yaml: domestic     share, central-bank share (scaled by who controls the central bank), average maturity,     reserve-currency status or NIIP, and the short/linked share entered negatively. | derived | below 60 | quadrant | It does     not make debt sustainable; it decides whether an unsustainable path resolves as a decades     long repression grind (captive) or a crisis within a cycle (free). |

## Pressure block

| Indicator | Units | Formula / definition | Source series | Threshold | Informs | What it leads to |
|---|---|---|---|---|---|---|
| `term_premium_proxy` | pp | Compensation the market demands for holding duration. | FRED THREEFYTP10 (US); 10y-2y elsewhere | above 1.5 | stage 2 | Kim-Wright estimate where it     exists (US), otherwise 10-year minus 2-year yield, labelled a proxy. Rising term premium     is the pricing stage: the market starting to charge for the risk. |
| `breakeven_10y` | % | Ten-year inflation breakeven: nominal minus real yield. | FRED, BoE; 10y minus real yield (AU, CA) | above 3 | stage 2 | The market pricing the     inflation exit. |
| `policy_rate_minus_inflation` | pp | Real policy rate. | BIS CBPOL, BIS long CPI | below 0 | stages 3-4 | Negative and widening while inflation is above target is the bank     choosing the bond market over the currency: stages 3 and 4. |
| `cb_balance_sheet_gdp` | % GDP | Central bank total assets over GDP. | BIS CBTA; FRED; RBA; SNB; ECB ILM | — | stage 4 | A union member shows the Eurosystem's sheet. |
| `cb_balance_sheet_growth_minus_g` | pp | Four-quarter growth of the central bank's balance sheet minus nominal GDP growth. | derived | — | stage 4 |     Above zero is monetisation: the sheet outgrowing the economy. |
| `cb_holdings_change_4q` | pp of debt | Change in the central bank's share of the debt over four quarters. | derived | above 0 | stages 3-4 | Rising after the     hiking cycle has stalled is fiscal dominance in progress. |
| `issuance_shortening` | pp of marketable debt | Change in the bill share over eight quarters. | derived | above 3 | stage 4 | The treasury retreating from the long     end because the long end is charging for the risk. |
| `fx_vs_usd_12m` | % | Twelve-month change of the currency against the dollar, appreciation positive. | FRED, BIS XRU | below -10 | stage 5 | For a     floater the currency is the pressure gauge: a yield can be pinned, a currency cannot     be pinned without reserves. Blank for the US and for union members (see spread). |
| `fx_broad_reer_12m` | % | Twelve-month change in the broad real effective exchange rate. | BIS EER | below -10 | stage 5 | The currency gauge     net of partners' inflation, and the one that works for the US. |
| `gold_local_ccy_12m` | % | Twelve-month change in gold priced in local currency. | LBMA mirror / World Bank / Yahoo x FX | above 20 | stage 5 | Hard-asset flight shows up here     before it shows up in the yield, because the yield can be managed and gold cannot. |
| `gold_local_record` | flag | 1 when gold in local currency is at an all-time high. | derived | — | stage 5 | The stage-5 tell. |
| `auction_tail` | ratio (inverted) | Auction demand proxy: the trailing two-year average bid-to-cover minus the current     value, so a rising number means weaker demand (true tails need when-issued yields, which     are not free). | Fiscal Data auctions (bid-to-cover) | — | stage 2 | Dealers demanding a concession to absorb supply is the pricing stage. |
| `spread_to_anchor_bp` | bp | Ten-year spread to the anchor (Bund for euro members, Treasuries for pegs). | ECB IRS vs DE | above 200 | stages 3, 5 (union) | For a     country that cannot print, this replaces the currency as the pressure gauge: a widening     spread with a central bank announcing a backstop is stage 3; a blow-out is stage 5. |
| `target2_balance_gdp` | % GDP | TARGET2 balance over GDP (liability negative). | ECB TGB | below -20 | stage 5 (union) | Deposit flight inside the union shows     up here when it cannot show up in the exchange rate. |
| `ecb_backstop_active` | flag | 1 while an ECB sovereign backstop is in force (SMP, OMT, PEPP flexibility, TPI).. | manual flag | — | stage 3 (union) |  |
| `fx_reserves_12m` | % | Twelve-month change in official reserves. | World Bank | — | stage 5 (peg) | A peg under attack burns these first. |
| `interest_to_revenue` | % | Interest as a share of government revenue. | World Bank; IMF `rev` | — | context | The political temperature: the share of     the budget already spoken for by past borrowing. |

## Quadrant and stage

| Output | Definition |
|---|---|
| `trajectory_unsustainable` | `forward_r_minus_g_5y > 0.0` and `primary_balance_gdp < 0.0` |
| `holders_captive` | `captivity_score > 60` |
| `quadrant` | sustainable_captive / sustainable_free / unsustainable_captive / unsustainable_free |
| `stage_estimate` | highest firing stage in `config/stages.yaml` with prerequisites; undefined until 12 quarters of primary balance exist |
| transitions | any quarter where `quadrant` or `stage_estimate` changes; `data/clean/transitions.csv` |

## Captivity score weights

| Component | Weight | Scaled from | to |
|---|---|---|---|
| domestic_share | 0.30 | 30 | 95 |
| central_bank_share | 0.20 | 0 | 50 |
| avg_maturity | 0.20 | 2 | 15 |
| reserve_niip | 0.15 | -100 | 50 |
| bill_linker_share | 0.15 | 0 | 50 |

Central-bank component credit by control: {'own': 1.0, 'shared': 0.5, 'none': 0.0}. Reserve-currency score 100 (US), partial 65 (euro area).

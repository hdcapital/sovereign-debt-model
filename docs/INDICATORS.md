# Indicators

Skeleton (phase 1). Each row is filled in as the indicator is implemented in
`src/sdm/indicators/`; the docstring of each function is the source of truth for the
"what it leads to" text and is pulled into the dashboard. Thresholds live in
`config/indicators.yaml` and are repeated here for reading convenience.

Notation: `d` = debt/GDP, `pb` = primary balance/GDP, `r` = effective rate, `g` = nominal growth.
All indicators are quarterly, per country, full history. Status: ☐ not started · ◐ partial · ☑ done+tested.

## Trajectory block

| Indicator | Status | Definition | Formula | Source series | Threshold | Informs | What it leads to |
|---|---|---|---|---|---|---|---|
| `debt_gdp` | ☐ | Gross general government debt / nominal GDP | `D_t / (4q rolling nominal GDP)` | BIS total credit (govt), IMF WEO, national | 90% (context only) | fuel | Scale of the stock the transfer must act on. Not a predictor on its own. |
| `primary_balance_gdp` | ☐ | Budget balance ex interest, 4q rolling, % GDP | `Σ4q(revenue − non-interest spend) / Σ4q GDP` | IMF WEO/FM, Eurostat, Fiscal Data, ONS | < 0 | stage 0 | The fuel. A deficit that does not close in expansions keeps the spiral fed. |
| `r_effective` | ☐ | Average interest rate on the stock | `Σ4q interest_paid / D_{t−4}` | WEO (NLB − PB), Fiscal Data, ONS, Eurostat | — | trajectory | The rate the budget actually pays today; lags markets. |
| `g_nominal` | ☐ | 4q nominal GDP growth | `GDP_t / GDP_{t−4} − 1` | national accounts via FRED/OECD/Eurostat | — | trajectory | The denominator's growth; inflation counts in full. |
| `r_minus_g` | ☐ | Snowball term | `r_effective − g_nominal` | derived | > 0 | stage 1 | Positive with a primary deficit means debt rises on autopilot. |
| `debt_dynamics` | ☐ | Identity-predicted annual Δd, vs actual | `(r−g)·d_{t−4} − pb` and `d_t − d_{t−4}` | derived | residual > 2pp flags SFA | diagnostic | Large stock-flow residuals mean off-budget financing or valuation effects. |
| `marginal_yield` | ☐ | Issuance-weighted market yield | `w2·y2 + w10·y10` (issuance mix where known; else 10y) | FRED/OECD MEI, ECB, BoE, MoF, RBA, BoC | — | stage 1 | What new borrowing costs; where `r` is heading. |
| `avg_coupon_gap` | ☐ | Marginal minus average | `marginal_yield − r_effective` | derived | > 0 | stage 1 | Interest cost already baked in: the bill rises with no further shock. |
| `forward_r_5y` | ☐ | Projected `r` in 5y at current yields | roll `1/avg_maturity` of stock per year + deficit issuance at `marginal_yield` | derived | — | trajectory | The rate the budget will face; more informative than current `r`. |
| `forward_r_minus_g_5y` | ☐ | Forward snowball | `forward_r_5y − g_trend` | derived | > 0 | quadrant | The model's trajectory variable: unsustainable if > 0 with a deficit. |
| `debt_gdp_projection_10y` | ☐ | Path of `d` under forward r, trend g, current pb | iterate the identity 40 quarters | derived | — | narrative | Where the stock goes if nothing changes. |

## Captivity block

| Indicator | Status | Definition | Formula | Source series | Threshold | Informs | What it leads to |
|---|---|---|---|---|---|---|---|
| `foreign_share` | ☐ | % of debt held by non-residents | holdings_foreign / total | IMF Arslanalp–Tsuda, TIC/FRED, DMO, BoJ FoF, ABS | > 40% | captivity | Free holders: the base that can leave within a cycle. |
| `central_bank_share` | ☐ | % held by own/shared central bank | CB holdings / total, × control credit | Arslanalp–Tsuda, FRED, BoE APF, BoJ, ECB PSPP/PEPP | — | captivity, stage 4 | The ultimate captive buyer; rising share is the stage-4 tell. |
| `domestic_private_share` | ☐ | Residual | `100 − foreign − central_bank` | derived | — | captivity | The pool repression acts on. |
| `avg_maturity_years` | ☐ | Weighted average remaining maturity | from DMO statistics | Fiscal Data/Treasury Bulletin, DMO, MoF, AOFM, ECB GFS, OECD SBO | < 5y | captivity, forward r | Short stock = holders effectively free and `r` converges fast. |
| `bill_share` | ☐ | Marketable debt < 1y / marketable total | — | MSPD, DMO, MoF, ECB SEC | > 25% | captivity, stage 4 | Rising bill share is the treasury shortening to dodge term premium. |
| `linker_share` | ☐ | Inflation-linked / marketable total | — | MSPD, DMO, national DMOs | — | captivity | Linkers cannot be inflated away; reduce the repression exit. |
| `household_savings_to_debt` | ☐ | Household financial assets / govt debt | — | OECD financial accounts, Fed Z.1, BoJ FoF, ONS | — | captivity | Size of the domestic pool that can be made to hold the debt. |
| `net_foreign_asset_position_gdp` | ☐ | NIIP / GDP | — | IMF IIP (via API) | — | captivity | Creditor nations can fund themselves; debtors depend on foreigners. |
| `captivity_score` | ☐ | 0–100 composite | weights in `config/indicators.yaml` | derived | 60 | quadrant | Sorts unsustainable countries into grind (captive) vs crisis (free). |

## Pressure / stage block

| Indicator | Status | Definition | Formula | Source series | Threshold | Informs | What it leads to |
|---|---|---|---|---|---|---|---|
| `term_premium_proxy` | ☐ | 10y minus expected policy path | Kim–Wright/ACM (US); else `y10 − y2` labelled proxy | FRED, NY Fed | rising > 0.5pp/4q | stage 2 | Market starting to charge for the risk. |
| `breakeven_10y` | ☐ | 10y inflation breakeven | nominal − linker yield | FRED, BoE, MoF, RBA, BoC | rising > 0.5pp/4q | stage 2 | Market pricing the inflation exit. |
| `policy_rate_minus_inflation` | ☐ | Real policy rate | `policy − CPI yoy` | BIS CBPOL, FRED/OECD CPI | < 0 | stages 3–4 | Negative and widening = bank has chosen the bond market. |
| `cb_balance_sheet_gdp` | ☐ | CB total assets / GDP, and 4q growth vs `g` | — | FRED, each central bank | growth > g | stage 4 | Balance sheet outgrowing the economy = monetisation. |
| `cb_holdings_change_4q` | ☐ | Δ central_bank_share over 4q | — | derived | > 0 | stages 3–4 | Rising CB share after hikes paused = fiscal dominance. |
| `issuance_shortening` | ☐ | Δ bill_share over 8q | — | derived | > 3pp | stage 4 | Treasury retreating from the long end. |
| `fx_vs_usd_12m` | ☐ | 12m change vs USD | — | FRED, BIS | < −10% | stage 5 | The currency is the pressure gauge for floaters. |
| `fx_broad_reer_12m` | ☐ | 12m change in broad REER | — | BIS EER | < −10% | stage 5 | Same, net of partners' inflation. |
| `gold_local_ccy_12m` | ☐ | 12m change in gold priced in local currency | `gold_usd × usd_per_local` | stooq/FRED/WGC × FX | > 20%, record high | stage 5 | Hard-asset flight visible before the yield moves. |
| `auction_tail` | ☐ | Tail / bid-to-cover proxy | — | Fiscal Data auctions (US), DMO (UK) | rising | stage 2 | Dealers demanding concession to absorb supply. |
| `spread_to_anchor_bp` | ☐ | 10y spread to Bund (union members, pegs) | — | ECB IRS / FRED MEI | > 200bp | stages 3,5 (union) | The member's pressure gauge. |
| `target2_balance_gdp` | ☐ | TARGET2 balance / GDP (members) | — | ECB SDW TGB | < −20% | stage 5 (union) | Deposit flight inside the union. |
| `stage_estimate` | ☐ | Rule-based 0–6 | `config/stages.yaml` | derived | — | report | Where in the spiral the country sits. |

## Quadrant

| Indicator | Status | Definition | Formula | Threshold | What it leads to |
|---|---|---|---|---|---|
| `trajectory_unsustainable` | ☐ | bool | `forward_r_minus_g_5y > 0 AND primary_balance_gdp < 0` | config | The stock grows with no further decisions. |
| `holders_captive` | ☐ | bool | `captivity_score > 60` | config | Resolution is a grind, not a crisis. |
| `quadrant` | ☐ | label | sustainable_captive / sustainable_free / unsustainable_captive / unsustainable_free | — | Which exit, and on what clock. |
| `transition_flag` | ☐ | bool + text | quadrant or stage changed vs previous quarter | — | The only thing the model claims to time. |

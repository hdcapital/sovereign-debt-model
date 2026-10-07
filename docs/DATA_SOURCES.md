# Data sources, per indicator

The plan for phase 2. Difficulty: **E** easy (stable API, long history, all core countries),
**M** medium (API exists but partial coverage, or Excel/CSV scraping of a stable page),
**H** hard (manual, registration, or no free source; expect a stub + `DATA_GAPS.md` entry).

Status 2026-10-07: every host below is currently blocked by the cloud environment's network
policy (see `DATA_GAPS.md`). Nothing has been pulled yet; "verify" marks claims I have not
been able to confirm against the live API.

## Primary APIs (one collector each, `src/sdm/collect/<source>.py`)

| Source | Endpoint | Auth | Used for | Notes |
|---|---|---|---|---|
| IMF | `api.imf.org/external/sdmx/2.1` (new SDMX 2.1/3.0 gateway) with `imf.org/external/datamapper/api/v1` as the simple fallback for WEO | none | WEO: debt/GDP, primary balance, net lending, nominal GDP (annual, all countries, 1980–); IFS/BOP: NIIP; Fiscal Monitor | `dataservices.imf.org` is being retired; the collector tries the new gateway first, then DataMapper. **Verify** which is live. |
| FRED | `api.stlouisfed.org/fred` | free key (`FRED_API_KEY`) | US yields, policy rate, CPI, breakevens (T10YIE), Kim–Wright term premium (THREEFYTP10), Fed balance sheet (WALCL), Fed Treasury holdings (TREAST, FDHBFRBN), foreign holdings (FDHBFIN), FX majors (DEXxx), OECD MEI long rates (IRLTLT01xx) and CPI (CPALTT01xx) for every core country, ECB/BoJ balance sheets (ECBASSETSW, JPNASSETS) | Single richest source. Need the key from you. |
| BIS | `stats.bis.org/api/v2` (SDMX) | none | policy rates (WS_CBPOL, long history, all countries), general-government credit/GDP quarterly (WS_TC), broad REER (WS_EER), USD FX (WS_XRU) | Quarterly debt/GDP for every country from one place. |
| OECD | `sdmx.oecd.org/public/rest` | none | quarterly government accounts (interest paid, primary balance for EU/OECD), quarterly national accounts, household financial accounts | Dataflow IDs changed in 2024 migration; **verify**. |
| World Bank | `api.worldbank.org/v2` | none | EM backfill: debt/GDP, GDP, interest/revenue | Annual only. |
| US Treasury Fiscal Data | `api.fiscaldata.treasury.gov/services/api/fiscal_service` | none | average interest rates on debt (`avg_interest_rates`, 2001–), MSPD (bill/TIPS share, 2001–), monthly interest expense, auction results (`auctions_query`, 1979–), TIC foreign holdings | Gold standard for average vs marginal. Pre-2001 from Treasury Bulletin (manual). |
| ECB Data Portal | `data-api.ecb.europa.eu/service/data` | none | member 10y rates (IRS convergence series, 1990s–), euro area yield curve (YC), TARGET2 (TGB), PSPP/PEPP holdings by country (published as Excel on ecb.europa.eu, monthly), government debt securities and residual maturity (GFS/SEC, **verify**), ECB balance sheet (ILM) | |
| Bank of England | `bankofengland.co.uk/boeapps/database` (CSV export, "IADB") | none | Bank Rate, gilt yield curve (nominal, real, implied inflation, 1985–), APF holdings | CSV via query string; stable for a decade. |
| UK DMO | `dmo.gov.uk/data` (Excel/CSV) | none | gilt portfolio: average maturity, index-linked share, holdings by sector, auction results incl. tails | Scrape of a stable download page. **M**. |
| ONS | `api.ons.gov.uk` / timeseries CSV | none | PSF: debt, interest, primary balance monthly; nominal GDP quarterly | |
| Japan MoF | `mof.go.jp/english/policy/jgbs` Excel | none | JGB average maturity, average coupon, composition by instrument, holder breakdown (quarterly "JGB Newsletter") | Excel scraping; stable layout. **M**. |
| Bank of Japan | `stat-search.boj.or.jp` CSV | none | flow of funds: JGB holdings by sector (1998–; 1980– on old base), BoJ balance sheet, policy rate | |
| RBA / AOFM / ABS | RBA statistical tables CSV (F1, F2, A1), AOFM Excel, ABS 5302 | none | AU yields, cash rate, RBA holdings, average term to maturity, non-resident holdings | **M**. |
| Bank of Canada / StatCan | Valet API (`bankofcanada.ca/valet`), StatCan WDS | none | CA yields, policy rate, BoC holdings, RRB breakevens; GDP, holdings by sector | **E–M**. |
| SNB | `data.snb.ch` CSV | none | CH yields, policy rate, balance sheet, federal debt | **M**. |
| IMF Arslanalp–Tsuda | Excel on imf.org (sovereign investor base, AE and EM files) | none | foreign / central bank / domestic bank / nonbank shares, quarterly, 2004– | **Single best captivity source.** URL moves between updates; collector tries known URLs and falls back to a committed copy in `data/manual/`. |
| IMF Public Finances in Modern History (Mauro et al.) | Excel on imf.org | none | primary balance, interest, r−g for 55 countries, 1800–2011 | Backtest fiscal history for 1976/1992 events. **M**. |
| Jordà–Schularick–Taylor Macrohistory | `macrohistory.net` xlsx | terms acceptance | annual debt/GDP, long rate, CPI, bond returns, FX for 18 AEs 1870–2020 | Forward real bond returns for the backtest. Download may need a human click. **M–H**. |
| Gold / FX fallback | `stooq.com` CSV; World Gold Council monthly | none | gold USD daily | FRED's LBMA series is discontinued. **M**. |

## Per indicator

| Indicator | Core countries: primary → fallback | Backtest-only EMs | Difficulty | Flag |
|---|---|---|---|---|
| `debt_gdp` | BIS WS_TC general govt (quarterly) → IMF WEO (annual, stepped) | WEO, World Bank | E | — |
| `primary_balance_gdp` | US: Fiscal Data MTS; UK: ONS PSF; EA/DE/FR/IT/NL: Eurostat/OECD quarterly govt accounts; JP/AU/CA/CH: WEO annual stepped (OECD quarterly where published) | WEO annual, Mauro et al. pre-1990 | M | JP, AU, CA, CH quarterly primary balance is thin; expect annual-stepped series. |
| `r_effective` | interest paid: US Fiscal Data; UK ONS; EA members Eurostat D41; others WEO (net lending − primary balance) | WEO, Mauro et al. | M | Same quarterly thinness outside US/UK/EA. |
| `g_nominal` | FRED (US), ONS, Eurostat, Cabinet Office, ABS, StatCan, SECO; all via OECD QNA as one source | WEO annual, World Bank | E | — |
| `marginal_yield` | 10y: FRED MEI `IRLTLT01` for all; 2y: FRED (US), BoE, ECB YC/IRS, MoF, RBA, BoC, SNB; issuance mix: Fiscal Data, DMO, MoF only | 10y from IMF IFS/World Bank | M | Issuance weighting only for US/UK/JP; others use 2y/10y default blend or 10y only, labelled. |
| `avg_coupon_gap` | derived | derived | E | — |
| `forward_r_5y` | derived from `avg_maturity_years`, `marginal_yield`, deficit | derived | M | Only as good as maturity data. |
| `debt_gdp_projection_10y` | derived | derived | E | — |
| `foreign_share` | Arslanalp–Tsuda (2004–) → US FRED FDHBFIN (1970–), UK DMO/ONS (1987–), JP BoJ FoF, AU ABS 5302, CA StatCan, EA ECB SHS | Arslanalp–Tsuda EM file (2004–); manual before | M | Pre-2004 for the 1976–2001 events is hand-coded with citations. **Hard for the backtest.** |
| `central_bank_share` | Arslanalp–Tsuda → FRED FDHBFRBN (1970–), BoE APF (2009–), BoJ FoF, ECB PSPP/PEPP by country, RBA, BoC | Arslanalp–Tsuda, central bank sites | M | ECB holdings by country only from 2015 (PSPP); pre-2015 member CB share is ~0 by construction. |
| `domestic_private_share` | residual | residual | E | — |
| `avg_maturity_years` | US: Treasury Bulletin/Fiscal Data (**verify** API field); UK: DMO; JP: MoF; AU: AOFM; CA: Debt Management Report (annual); EA members: ECB GFS residual maturity (**verify**) → OECD Sovereign Borrowing Outlook annual (manual) | OECD/IMF program documents (manual) | M–H | **Flag.** No single API. Expect annual manual series for CA, CH, NL, and all EMs. |
| `bill_share` | US MSPD; UK DMO; JP MoF; EA members ECB SEC short-term govt securities; AU AOFM; CA BoC; CH SNB | ECB SEC (GR), manual | M | — |
| `linker_share` | US MSPD (TIPS); UK DMO; JP MoF; DE/FR/IT national DMO annual; AU AOFM; CA BoC (RRB) | n/a (mostly 0) | M | — |
| `household_savings_to_debt` | OECD financial accounts (annual); Fed Z.1 via FRED; BoJ FoF; ONS; Eurostat | NaN | M–H | **Flag.** Annual, patchy; may stub for CH/AU. |
| `net_foreign_asset_position_gdp` | IMF IIP via API (quarterly 2000s–, annual before) | IMF IIP, World Bank | E–M | — |
| `captivity_score` | derived | derived | E | — |
| `term_premium_proxy` | US: FRED THREEFYTP10 (Kim–Wright) or NY Fed ACM xls; others: 10y − 2y proxy | 10y − policy rate proxy | E | Proxy clearly labelled outside the US. |
| `breakeven_10y` | US FRED T10YIE (2003–); UK BoE implied inflation (1985–); CA BoC RRB; AU RBA; JP MoF JGBi (sparse); EA/DE/FR/IT/NL/CH: none free | NaN | M | **Flag.** No euro-member or Swiss breakevens without a terminal. |
| `policy_rate_minus_inflation` | BIS CBPOL + FRED MEI CPI | BIS CBPOL + IMF/World Bank CPI | E | — |
| `cb_balance_sheet_gdp` | FRED (Fed, ECB, BoJ), BoE, RBA, BoC, SNB sites | central bank sites, IMF IFS central bank survey | M | — |
| `cb_holdings_change_4q` | derived | derived | E | — |
| `issuance_shortening` | derived | derived | E | — |
| `fx_vs_usd_12m` | FRED DEX* daily (1971–) → BIS WS_XRU | BIS WS_XRU, IMF IFS | E | — |
| `fx_broad_reer_12m` | BIS WS_EER broad (1994–) and narrow (1964–) | BIS WS_EER | E | — |
| `gold_local_ccy_12m` | stooq XAUUSD → WGC monthly, × FX | same | M | FRED LBMA series gone; stooq is unofficial but stable. |
| `auction_tail` | US Fiscal Data `auctions_query` bid-to-cover (tail needs WI yields, not free); UK DMO tails in bp | NaN | H | **Flag.** Proxy only. |
| `spread_to_anchor_bp` | ECB IRS member 10y − DE; FRED MEI as fallback | GR same; EM pegs: 10y local − US 10y | E | — |
| `target2_balance_gdp` | ECB TGB | ECB TGB (GR) | E | — |
| `inflation_minus_target` | CPI as above − `inflation_target` in universe.yaml | same | E | — |
| Bond total returns (backtest only) | duration approximation from 10y yields; JST annual returns as cross-check | same | M | Approximation, documented in BACKTEST.md. |

## What I expect to be hard, in order

1. **Historical holder shares** (captivity before 2004) for the EM and 1970s–90s events. This
   is hand-coded from IMF program documents and the literature. It is the single biggest risk
   to the backtest's captivity leg.
2. **Average maturity** outside US/UK/JP/AU. Annual and manual for several countries.
3. **Breakevens** for euro members and Switzerland. None free; stage-2 relies on term premium
   there.
4. **Auction tails.** Proxy only.
5. **Quarterly primary balance and interest** for JP, AU, CA, CH. Likely annual-stepped.
6. **The IMF API migration.** Which endpoint is live changes the collector; cheap to switch.
7. **Network policy of this environment.** Every host above is currently denied. This blocks
   phase 2 entirely until changed.

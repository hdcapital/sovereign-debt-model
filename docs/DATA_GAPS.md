# Data gaps

What is missing, approximate, or stubbed, and what is done about it. The collectors append
a "LAST ERROR" to the catalog note of any series that fails; the quarterly email lists stale
and failed series in its "Data issues" section.

## Hand-maintained series (data/manual/, every row cites its source and a confidence flag)

| Series | Why manual | Coverage | Confidence |
|---|---|---|---|
| `avg_maturity_years` for every country except the UK | No API publishes it; OECD Sovereign Borrowing Outlook and national DMO annual reports are PDFs | 2015–2025, annual, stepped | approximate: values are read from annual reports from memory and marked for verification |
| `cb_gov_share`, `foreign_share` after 2016 for JP, AU, CA, GB, CH, DE, FR, IT, NL, GR | Arslanalp–Tsuda's public workbook ends in 2016; the IMF's updated dataset sits behind the data portal | 2017–2025, annual | approximate |
| Holder shares at the historical crisis dates (UK 1976, Italy 1992, Sweden 1992, Mexico 1994, Canada 1994, Russia 1998, Argentina 2001, Greece 2010, Brazil 2015, Turkey 2018/21, Argentina 2018, Russia 2014) | No dataset covers them | one point per event | approximate, from IMF program documents and the literature |
| `ecb_backstop_active` | A policy flag, not a statistic | 2009–2025 | high |

**Replacing the approximations is the single most valuable data task.** The US average
maturity can be computed exactly from Fiscal Data's MSPD table 3 (every security with its
maturity date); the UK's comes from the DMO snapshot from 2026 on. The rest need the OECD
SBO tables or a Bloomberg pull.

## Sources that are partially reachable

| Source | Status (verified 2026-10-07) | Effect |
|---|---|---|
| UK DMO | Only the gilts-in-issue XML (D1A) is served; every other report is behind ShieldSquare bot protection | Average maturity, linker share and sub-1y share are computed from the snapshot each run; no history before 2026 except the manual table |
| Japan MoF holder breakdown | Published in the quarterly JGB Newsletter PDF only | BoJ and overseas shares are manual after 2016 |
| BoJ flow of funds | Time-series search has no stable CSV URL | not used |
| AOFM, ABS | AOFM times out behind Cloudflare; the ABS SDMX API works but was not wired this phase | AU holder shares manual after 2016 |
| StatCan | The vector API needs a POST body | not used; BoC Valet covers Canadian yields |
| OECD SDMX | Data queries return 403 for the government accounts dataflows tried | not used; national sources and the IMF cover the same ground |
| stooq, LBMA | JavaScript challenge / 403 | gold comes from the datasets/gold-prices LBMA mirror, the World Bank Pink Sheet and Yahoo GC=F instead |
| ONS `api.ons.gov.uk` | Retired November 2024 | the ons.gov.uk timeseries JSON endpoints are used |
| IMF DataMapper `GGXONLB_NGDP`, `GGR_NGDP` | Empty for every country | the Global Debt Database ids `pb`, `rev`, `ie` are used (1950s onwards, annual, no euro-area aggregate) |
| BIS total credit | No general-government series for AR, RU, BR, MX; no central bank assets for RU | IMF/World Bank annual for those |
| FRED OECD MEI | CPI series for the euro area, Argentina and long rates for Brazil/Turkey do not exist | BIS long CPI covers CPI for all; no 10y for BR/TR (manual or JST not available either) |

## Known definitional seams (documented, not fixed)

- `debt_gdp` uses the BIS core-debt series at market value for consistency across countries;
  it runs below the face-value headline (US 111% vs the 120%+ gross federal figure).
- UK interest (`JW2P`) is public-sector interest and dividends paid, which includes the RPI
  uplift on index-linked gilts; it runs above the IMF's figure. The budget bears it, so it
  is kept.
- Quarterly flows for JP, AU, CA, CH come from annual IMF data spread over the year's four
  quarters; the current year is blank until the IMF publishes it.
- Euro-area aggregate holder shares are not available (Arslanalp–Tsuda has no aggregate), so
  the EA row has no captivity score. A debt-weighted member average is planned.
- Breakevens exist for US, UK, AU, CA (derived from indexed bonds); none for euro members,
  Switzerland or Japan.
- Auction demand is bid-to-cover for US 10-year auctions only.
- Series splicing: when a lower-priority source fills quarters the primary lacks, it is
  shifted to the primary's level at the junction (ratio for stocks and flows, additive for
  rates). `data/clean/panel_sources.csv` records which source supplied every cell.

## Environment

The Claude Code cloud container's network policy denied every data host, so collectors are
developed against responses recorded by `.github/workflows/probe.yml` (results in
`data/raw/_probe/`) and run for real by `.github/workflows/update.yml` on GitHub-hosted
runners, which commit the data back.

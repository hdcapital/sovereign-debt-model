# Data gaps

Sources that are unreachable, need registration, or do not cover what the model wants.
Updated by every collector run; hand-edited entries are marked.

## Environment (hand-edited, 2026-10-07)

**All data hosts are denied by the cloud environment's network policy.** Probed on
2026-10-07, every one of the following returned a 403 from the egress proxy:

`api.imf.org`, `dataservices.imf.org`, `www.imf.org`, `data.imf.org`, `api.stlouisfed.org`,
`stats.bis.org`, `sdmx.oecd.org`, `api.worldbank.org`, `data-api.ecb.europa.eu`,
`www.bankofengland.co.uk`, `www.ons.gov.uk`, `www.dmo.gov.uk`, `www.boj.or.jp`,
`www.mof.go.jp`, `www.rba.gov.au`, `api.rba.gov.au`, `api.fiscaldata.treasury.gov`,
`stooq.com`, `query1.finance.yahoo.com`.

Only PyPI and GitHub are allowed. Phase 2 (collectors) needs the environment's network access
widened, or these hosts added to its allowed domains, before any real data can be pulled.
Until then collectors are written against documented API shapes and tested with recorded
fixtures.

## Known source limitations (anticipated, to be confirmed in phase 2)

| Need | Gap | Plan |
|---|---|---|
| Holder breakdown before 2004 | Arslanalp–Tsuda starts 2004 | Hand-coded holder shares with citations in `data/manual/holders_historical.csv` for the backtest events (UK 1976, IT 1992, SE 1992, MX 1994, RU 1998, AR 2001). |
| Average maturity, non-US/UK/JP | No single API; OECD Sovereign Borrowing Outlook is annual, published as a report | Annual manual series per country, stepped quarterly, flagged as such. |
| Auction tails | Only US (bid-to-cover; true tails need WI yields) and UK (DMO publishes tails) | Use bid-to-cover as the US proxy; tail in bp for UK; NaN elsewhere. |
| 10y breakevens | Free series only for US, UK, CA, AU, JP (sparse); none for EA members, CH | NaN where absent; stage-2 rule falls through to term premium. |
| Bond total returns for the backtest | No free total-return indices | Duration-approximation from yields: `ret ≈ y_{t−1} − D·Δy + ½·C·Δy²`; cross-check against Jordà–Schularick–Taylor annual returns. |
| Gold price history | FRED's LBMA series was discontinued | stooq `XAUUSD` daily, World Gold Council monthly as fallback. |
| Household financial assets | OECD financial accounts are annual and patchy outside the OECD core | Annual, stepped; NaN for backtest-only EMs. |

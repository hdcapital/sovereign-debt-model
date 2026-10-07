# Decisions log

Every judgement call, newest first. Reversible choices are made here and noted; irreversible
ones are asked first.

## Phase 2–3 (2026-10-07)

- **Data pulls run on GitHub Actions, not in the development container.** The container's
  egress policy blocks every data host; GitHub runners do not. A probe workflow records raw
  responses for development; the update workflow commits refreshed data to the branch.
- **Raw cache keeps the latest response only** (`data/raw/<source>/<id>.<ext>`); revisions
  are kept in the clean store, where a changed value is appended with a new vintage and the
  old row remains. Latest vintage wins when reading.
- **Clean store is CSV per source**, long format, so diffs and spot checks need no tooling.
  The quarterly panel (`panel.csv`) and the indicator table are derived files.
- **Concept vocabulary** (`sdm.collect.concepts`) is the contract between collectors and
  indicators; a collector cannot emit an unknown concept and a `KIND` (stock/flow/rate)
  decides how it aggregates to quarters.
- **Annual observations cover their own four quarters** (flows split by four). That is the
  observation's period, not a forward fill. Beyond the last observation at most one quarter
  is carried, per the brief.
- **Source priority with level splicing.** `source_priority` in `config/indicators.yaml`
  picks the primary source per concept; lower sources fill gaps after being shifted to the
  primary's level at the junction. Documented seams in DATA_GAPS.md.
- **FRED without a key** uses the public fredgraph CSV export; the API is used when
  `FRED_API_KEY` is set. Same series ids either way.
- **Gold** from three sources (LBMA mirror, World Bank Pink Sheet, Yahoo futures) in that
  priority, because stooq and LBMA are bot-blocked.
- **IMF primary balance, revenue and interest** come from the Global Debt Database ids
  (`pb`, `rev`, `ie`) because the WEO ids return nothing from DataMapper.
- **US fiscal flows are federal** (Fiscal Data, NIPA), not general government; the US
  debt level is debt held by the public. This matches how the US debate is conducted and
  the sources the brief named.
- **ECB holdings by member = cumulative PSPP net purchases** (book value). PEPP by
  jurisdiction is published bi-monthly and is not yet parsed, so member central-bank shares
  are understated from 2020.
- **Stage estimate is undefined until the fuel stage can be decided** (12 quarters of
  primary balance history); otherwise it is the highest firing stage with prerequisites.
- **Trend g is a 10-year trailing mean** of four-quarter nominal growth. In 2026 this still
  carries the 2021–23 inflation burst, which makes forward r − g look benign for the US;
  the report should say so, and a 20-year window is a one-line config change.
- **Manual tables carry a confidence flag** (`approximate` / `high`) that is propagated to
  the catalog notes; approximate values are read from annual reports and must be verified
  before any number is quoted externally.

- **"Stale" means more than four quarters behind the last complete quarter.** Annual
  IMF series legitimately lag two to three quarters; listing them every time would bury the
  real failures. The full staleness count is still in `indicators_latest.csv`.
- **Indicators that do not apply to a market** (spreads for floaters, the currency for
  union members, auction tails outside the US, reserves outside pegs) are neither shown nor
  counted as missing (`sdm.indicators.applicability`).

- **Email transport: Gmail app password over SMTP, OAuth kept as fallback.** The brief asked
  for the Gmail API with OAuth; the owner chose the app-password route for simplicity on
  2026-10-07. `GMAIL_APP_PASSWORD` selects SMTP; without it the OAuth path runs.

## Phase 1 (2026-10-07)

- **Package layout.** The brief names `src/collect/`, `src/indicators/`, `src/backtest/`,
  `src/report/`. These live as subpackages of one installable package, `src/sdm/`, so that
  imports are `sdm.collect`, `sdm.indicators`, etc. A bare `src/collect` would be an unnamed
  top-level package and clash with other projects' `collect` modules.
- **Python version.** Brief says 3.11+. The container has 3.13; `requires-python = ">=3.11"`
  and no 3.12+ syntax is used.
- **Narrative model.** `claude-sonnet-5-5` (current Sonnet). The brief named `claude-sonnet-4-5`
  "or whichever current Sonnet model". Config key `narrative.model` in `config/report.yaml`.
- **Euro area is a `sovereign_float` with `is_bloc: true`.** The aggregate can print; members
  cannot. Members carry `monetary_regime: currency_union_member`, `central_bank_control: shared`,
  `anchor: DE`. Germany is its own anchor so its spread is zero by construction; it is still
  scored as a union member because it cannot print either.
- **Captivity: `central_bank_control` is a multiplier on the central-bank component**, not a
  separate weighted term. own = 1.0, shared = 0.5, none = 0.0. Rationale: the thing that is
  partial for a union member is exactly the credibility of the central-bank bid, so scaling that
  component is the honest representation. Weights sum to 1 without a sixth term.
- **Reserve-currency component.** The US gets a fixed score of 100 on the `reserve_niip`
  component regardless of NIIP; the euro-area aggregate gets 65 (`reserve_currency_partial`).
  Everyone else uses NIIP/GDP scaled from −100% to +50%.
- **Bill + linker share enters the captivity score negatively**, as `100 − scaled_share`.
- **Backtest episodes of core countries** (Italy 1992, Canada 1994, UK 1976) are entries in
  `tiers.backtest_episodes` referencing the core country code and a window, rather than
  duplicate country entries. The core country's current regime is unchanged; the regime at the
  event is read from `regime_history`.
- **Regime spans are inclusive of the end date.** The day a peg breaks (Black Wednesday,
  Russia 10 Nov 2014) is read as the peg, since the event is the peg's failure.
- **Historical regimes.** Italy 1979–92 and 1996–98, France, Netherlands, Sweden (to 1992),
  Mexico (to 1994), Brazil (1994–99), Russia (1995–2014), Turkey (2000–01), Argentina (1991–2002),
  UK (1990–92) are recorded as `pegged`. ERM membership is treated as a peg because the exit
  mechanics (reserve loss, speculative attack) are a peg's, even though the bands were wide.
- **Event type vocabulary** adds `bond-market` to the brief's list, for episodes where the
  bond market, not the currency, broke (UK 2022 LDI, Italy 2011, Italy 2018, euro area 2011–12,
  France 2024). These are stage-2/3 tells rather than resolutions and are labelled as such.
- **Stage estimate = highest firing stage with prerequisites.** Stage N cannot fire unless its
  `requires` stage fires. Stage 6 only detects the consolidation branch by rule; the repression
  and default branches are labelled by hand in `data/events.csv`.
- **Stage 3 "hikes pause with inflation above target"** is encoded as: real policy rate < 0,
  inflation more than 1pp above target, policy rate not rising over 2 quarters.
- **Forward-fill guard.** Global `max_forward_fill_periods: 1`. Annual series are stepped at
  most one quarter; otherwise the indicator is NaN and the gap is listed in the report's
  "Data issues" section.
- **Trend g** for the forward snowball is a 10-year trailing mean of 4q nominal growth.
- **Marginal yield** default blend 40% 2y / 60% 10y where no issuance mix is available.
- **Email cadence.** Quarterly on the 15th of Jan/Apr/Jul/Oct at 06:00 UTC; monthly on the
  15th of every other month, and only sent if a transition or 1.5σ move fired.
- **Data cache is versioned.** `data/raw/` is committed (small JSON/CSV responses with vintage
  dates in the filename) so every report is reproducible from the repo alone. Binary archives
  are ignored.

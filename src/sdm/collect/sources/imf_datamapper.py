"""IMF DataMapper API (WEO): annual fiscal aggregates for every country, 1980 onwards.

GET https://www.imf.org/external/datamapper/api/v1/<INDICATOR>/<ISO3>[/<ISO3>...]
-> {"values": {"<INDICATOR>": {"<ISO3>": {"1980": 12.3, ...}}}}

WEO numbers include IMF projections for the next ~5 years; we keep only observations
up to the current year minus one (projections are not data).
"""

from __future__ import annotations

from datetime import date

import pandas as pd

from sdm.collect.base import Collector, SeriesSpec
from sdm.config import load_universe

BASE = "https://www.imf.org/external/datamapper/api/v1"

# DataMapper indicator -> (concept, units, note)
INDICATORS: dict[str, tuple[str, str, str]] = {
    "GGXWDG_NGDP": ("gg_debt_gdp", "% GDP", "WEO general government gross debt"),
    "pb": ("gg_primary_balance_gdp", "% GDP", "IMF Global Debt Database / Fiscal Monitor: primary balance"),
    "GGXCNL_NGDP": ("gg_net_lending_gdp", "% GDP", "WEO general government net lending/borrowing"),
    "rev": ("gg_revenue_gdp", "% GDP", "IMF Global Debt Database / Fiscal Monitor: revenue"),
    "NGDP_RPCH": ("rgdp_growth", "% y/y", "WEO real GDP growth"),
    "PCPIPCH": ("cpi_yoy", "% y/y", "WEO CPI inflation, annual average"),
    "ie": ("gg_interest_gdp", "% GDP", "IMF Global Debt Database: interest paid on public debt"),
}

ISO3_OVERRIDE = {"EA": "EURO"}  # DataMapper code for the euro area aggregate


class ImfDataMapperCollector(Collector):
    name = "imf_datamapper"

    def series(self) -> list[SeriesSpec]:
        uni = load_universe()
        out: list[SeriesSpec] = []
        for cc, c in uni.countries.items():
            iso3 = ISO3_OVERRIDE.get(cc, c.iso3)
            for ind, (concept, units, note) in INDICATORS.items():
                if cc == "EA" and ind in {"pb", "rev", "ie"}:
                    continue  # the Global Debt Database has no euro-area aggregate
                out.append(
                    SeriesSpec(
                        cc,
                        concept,
                        "IMF_WEO",
                        f"{BASE}/{ind}/{iso3}",
                        "A",
                        units,
                        note,
                        params={"indicator": ind, "iso3": iso3},
                    )
                )
        return out

    def fetch(self, spec: SeriesSpec) -> pd.DataFrame:
        payload = self.http.get_json(spec.url)
        self.cache_raw(spec.series_id, payload, "json")
        ind, iso3 = spec.params["indicator"], spec.params["iso3"]
        values = payload.get("values", {}).get(ind, {}).get(iso3)
        if not values:
            raise ValueError(
                f"no values for {ind}/{iso3}: keys={list(payload.get('values', {}).get(ind, {}))[:5]}"
            )
        cutoff = date.today().year - 1
        rows = [
            (pd.Timestamp(f"{y}-12-31"), v) for y, v in values.items() if int(y) <= cutoff and v is not None
        ]
        return pd.DataFrame(rows, columns=["date", "value"])

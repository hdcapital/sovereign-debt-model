"""World Bank API: annual backfill for the backtest countries.

GET https://api.worldbank.org/v2/country/<ISO3>/indicator/<ID>?format=json&per_page=1000
-> [meta, [{"date": "2020", "value": 12.3, ...}, ...]]
"""

from __future__ import annotations

import pandas as pd

from sdm.collect.base import Collector, SeriesSpec
from sdm.config import load_universe

BASE = "https://api.worldbank.org/v2/country"

INDICATORS = {
    "GC.DOD.TOTL.GD.ZS": ("gg_debt_gdp", "% GDP", "Central government debt, total (% of GDP)"),
    "NY.GDP.MKTP.CN": ("ngdp_lcu", "LCU bn", "GDP, current LCU (scaled from units)"),
    "FP.CPI.TOTL.ZG": ("cpi_yoy", "% y/y", "Inflation, consumer prices (annual %)"),
    "GC.XPN.INTP.RV.ZS": ("interest_to_revenue", "% revenue", "Interest payments (% of revenue)"),
    "PA.NUS.FCRF": ("fx_lcu_per_usd", "LCU per USD", "Official exchange rate, period average"),
    "FI.RES.TOTL.CD": (
        "fx_reserves_usd",
        "USD bn",
        "Total reserves incl. gold (current US$; scaled)",
    ),
}
SCALE = {"NY.GDP.MKTP.CN": 1e-9, "FI.RES.TOTL.CD": 1e-9}


class WorldBankCollector(Collector):
    name = "worldbank"

    def series(self) -> list[SeriesSpec]:
        uni = load_universe()
        out = []
        for cc in uni.backtest_only:
            iso3 = uni[cc].iso3
            for ind, (concept, units, note) in INDICATORS.items():
                out.append(
                    SeriesSpec(
                        cc,
                        concept,
                        "WORLDBANK",
                        f"{BASE}/{iso3}/indicator/{ind}",
                        "A",
                        units,
                        note,
                        params={"ind": ind},
                    )
                )
        return out

    def fetch(self, spec: SeriesSpec) -> pd.DataFrame:
        payload = self.http.get_json(spec.url, {"format": "json", "per_page": "1000"})
        self.cache_raw(spec.series_id, payload, "json")
        if not isinstance(payload, list) or len(payload) < 2 or not payload[1]:
            raise ValueError(f"unexpected payload: {str(payload)[:200]}")
        rows = [
            (pd.Timestamp(f"{o['date']}-12-31"), o["value"]) for o in payload[1] if o.get("value") is not None
        ]
        df = pd.DataFrame(rows, columns=["date", "value"])
        df["value"] = df["value"] * SCALE.get(spec.params["ind"], 1.0)
        return df

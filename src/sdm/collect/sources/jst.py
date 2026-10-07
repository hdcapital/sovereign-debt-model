"""Jorda-Schularick-Taylor Macrohistory Database (release R6): annual, 18 advanced
economies, 1870-2020. Distributed as a Stata .dta. Used for the backtest's long history
(debt/GDP, long rate, CPI, nominal GDP, FX, bond total returns) and as the backfill for
core-country series before the modern APIs start."""

from __future__ import annotations

import io

import pandas as pd

from sdm.collect.base import Collector, SeriesSpec

URL = "https://www.macrohistory.net/app/download/9834512469/JSTdatasetR6.xlsx"

ISO = {
    "US": "USA",
    "GB": "GBR",
    "JP": "JPN",
    "AU": "AUS",
    "CA": "CAN",
    "CH": "CHE",
    "DE": "DEU",
    "FR": "FRA",
    "IT": "ITA",
    "NL": "NLD",
    "SE": "SWE",
}

# concept -> (column, transform, units, note)
COLS = {
    "gg_debt_gdp": ("debtgdp", 100.0, "% GDP", "public debt / GDP"),
    "yield_10y": ("ltrate", 1.0, "%", "long-term government bond yield"),
    "yield_3m": ("stir", 1.0, "%", "short-term interest rate (bills / money market)"),
    "cpi_index": ("cpi", 1.0, "index", "consumer price index"),
    "ngdp_lcu": ("gdp", 1.0, "LCU bn (JST units)", "nominal GDP, local currency (JST units; see ReadMe)"),
    "gg_revenue_lcu": ("revenue", 1.0, "LCU (JST units)", "government revenue"),
    "gg_expenditure_lcu": ("expenditure", 1.0, "LCU (JST units)", "government expenditure"),
    "fx_lcu_per_usd": ("xrusd", 1.0, "LCU per USD", "exchange rate vs USD"),
    "bond_total_return": ("bond_tr", 100.0, "%", "total return on long government bonds"),
    "equity_total_return": ("eq_tr", 100.0, "%", "total return on equities"),
}


class JstCollector(Collector):
    name = "jst"
    _df: pd.DataFrame | None = None

    def series(self) -> list[SeriesSpec]:
        return [
            SeriesSpec(
                cc,
                concept,
                "JST",
                URL,
                "A",
                units,
                f"JST R6 {col}: {note}",
                params={"iso": iso, "col": col, "k": k},
            )
            for cc, iso in ISO.items()
            for concept, (col, k, units, note) in COLS.items()
        ]

    def _data(self) -> pd.DataFrame:
        if self._df is None:
            raw = self.http.get_bytes(URL)
            self.cache_raw("JSTdatasetR6", raw, "dta")
            self._df = pd.read_stata(io.BytesIO(raw))
        return self._df

    def fetch(self, spec: SeriesSpec) -> pd.DataFrame:
        df = self._data()
        sel = df[df["iso"] == spec.params["iso"]]
        col = spec.params["col"]
        out = pd.DataFrame(
            {
                "date": pd.to_datetime(sel["year"].astype(int).astype(str) + "-12-31"),
                "value": pd.to_numeric(sel[col], errors="coerce") * spec.params["k"],
            }
        )
        return out.dropna()

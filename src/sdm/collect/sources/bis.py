"""BIS SDMX v2 API (verified 2026-10-07): policy rates, USD FX, broad REER, general
government credit/GDP, central bank total assets, long CPI series.

GET https://stats.bis.org/api/v2/data/dataflow/BIS/<flow>/<version>/<key>?format=csv
CSV has TIME_PERIOD and OBS_VALUE; quarterly periods look like 2024-Q1, monthly 2024-06.
"""

from __future__ import annotations

import io
from datetime import date

import pandas as pd

from sdm.collect.base import Collector, SeriesSpec

BASE = "https://stats.bis.org/api/v2/data/dataflow/BIS"

# universe code -> BIS REF_AREA, currency
AREAS: dict[str, tuple[str, str]] = {
    "US": ("US", "USD"),
    "GB": ("GB", "GBP"),
    "JP": ("JP", "JPY"),
    "AU": ("AU", "AUD"),
    "CA": ("CA", "CAD"),
    "CH": ("CH", "CHF"),
    "EA": ("XM", "EUR"),
    "DE": ("DE", "EUR"),
    "FR": ("FR", "EUR"),
    "IT": ("IT", "EUR"),
    "NL": ("NL", "EUR"),
    "AR": ("AR", "ARS"),
    "TR": ("TR", "TRY"),
    "RU": ("RU", "RUB"),
    "BR": ("BR", "BRL"),
    "MX": ("MX", "MXN"),
    "GR": ("GR", "EUR"),
    "SE": ("SE", "SEK"),
}
EURO_MEMBERS = {"DE", "FR", "IT", "NL", "GR"}
NO_TC = {"AR", "RU", "BR", "MX"}  # BIS total credit has no general-government series
NO_CBTA = {"RU"}


def parse_period(p: str) -> pd.Timestamp:
    p = str(p)
    if "-W" in p:  # ISO week, e.g. 1998-W53 -> the Friday of that week
        y, w = p.split("-W")
        try:
            return pd.Timestamp(date.fromisocalendar(int(y), int(w), 5))
        except ValueError:
            return pd.Timestamp(date.fromisocalendar(int(y), 52, 5))
    if "-Q" in p:
        y, q = p.split("-Q")
        return pd.Period(f"{y}Q{q}", freq="Q").end_time.normalize()
    if len(p) == 7:  # YYYY-MM
        return pd.Period(p, freq="M").end_time.normalize()
    if len(p) == 4:
        return pd.Timestamp(f"{p}-12-31")
    return pd.Timestamp(p)


class BisCollector(Collector):
    name = "bis"

    def series(self) -> list[SeriesSpec]:
        out: list[SeriesSpec] = []
        for cc, (area, ccy) in AREAS.items():
            if cc not in EURO_MEMBERS:
                out.append(
                    SeriesSpec(
                        cc,
                        "policy_rate",
                        "BIS",
                        f"{BASE}/WS_CBPOL/1.0/M.{area}",
                        "M",
                        "%",
                        "BIS central bank policy rates, end of month",
                    )
                )
                out.append(
                    SeriesSpec(
                        cc,
                        "cb_total_assets_lcu",
                        "BIS",
                        f"{BASE}/WS_CBTA/1.0/M.{area}",
                        "M",
                        "LCU bn",
                        "BIS central bank total assets, break-adjusted (source units scaled by UNIT_MULT)",
                        params={"unit_mult": True},
                    )
                )
            if cc not in EURO_MEMBERS and cc != "US":
                out.append(
                    SeriesSpec(
                        cc,
                        "fx_lcu_per_usd",
                        "BIS",
                        f"{BASE}/WS_XRU/1.0/M.{area}.{ccy}.A",
                        "M",
                        "LCU per USD",
                        "BIS US dollar exchange rates, monthly average",
                    )
                )
            out.append(
                SeriesSpec(
                    cc,
                    "reer_broad",
                    "BIS",
                    f"{BASE}/WS_EER/1.0/M.R.B.{area}",
                    "M",
                    "index 2020=100",
                    "BIS real effective exchange rate, broad basket, CPI-based",
                )
            )
            out.append(
                SeriesSpec(
                    cc,
                    "cpi_index",
                    "BIS",
                    f"{BASE}/WS_LONG_CPI/1.0/M.{area}.628",
                    "M",
                    "index 2010=100",
                    "BIS long consumer price series",
                )
            )
            out.append(
                SeriesSpec(
                    cc,
                    "gg_debt_gdp",
                    "BIS",
                    f"{BASE}/WS_TC/2.0/Q.{area}.G.A.M.770.A",
                    "Q",
                    "% GDP",
                    "BIS credit to general government, core debt, market value, % of GDP",
                )
            )
        return out

    def fetch(self, spec: SeriesSpec) -> pd.DataFrame:
        text = self.http.get_text(spec.url, params={"format": "csv"})
        self.cache_raw(spec.series_id, text, "csv")
        df = pd.read_csv(io.StringIO(text))
        if "TIME_PERIOD" not in df.columns:
            raise ValueError(f"unexpected columns {list(df.columns)[:8]}")
        if "UNIT_MEASURE" in df.columns and (df["UNIT_MEASURE"] == "XDC").any():
            df = df[df["UNIT_MEASURE"] == "XDC"]  # local currency rows only (the file also carries USD)
        if "COMP_METHOD" in df.columns and (df["COMP_METHOD"] == "B").any():
            df = df[df["COMP_METHOD"] == "B"]  # break-adjusted
        df = df.drop_duplicates("TIME_PERIOD", keep="last")
        value = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
        if spec.params.get("unit_mult") and "UNIT_MULT" in df.columns:
            # express in billions whatever the source multiplier
            mult = pd.to_numeric(df["UNIT_MULT"], errors="coerce").fillna(0)
            value = value * (10.0 ** (mult - 9))
        return pd.DataFrame({"date": df["TIME_PERIOD"].map(parse_period), "value": value})

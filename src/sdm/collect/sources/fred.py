"""FRED (St. Louis Fed).

With ``FRED_API_KEY`` set, uses the JSON API. Without it, falls back to the public
``fredgraph.csv`` export (verified 2026-10-07), which needs no key and returns the full
history as DATE,<ID> with "." for missing.
"""

from __future__ import annotations

import io
import os

import pandas as pd

from sdm.collect.base import Collector, SeriesSpec

API = "https://api.stlouisfed.org/fred/series/observations"
GRAPH = "https://fred.stlouisfed.org/graph/fredgraph.csv"

# (country, concept, fred_id, frequency, units, note)
SERIES: list[tuple[str, str, str, str, str, str]] = [
    ("US", "yield_10y", "DGS10", "D", "%", "10-year Treasury constant maturity"),
    ("US", "yield_2y", "DGS2", "D", "%", "2-year Treasury constant maturity"),
    ("US", "yield_3m", "DGS3MO", "D", "%", "3-month Treasury constant maturity"),
    ("US", "yield_30y", "DGS30", "D", "%", "30-year Treasury constant maturity"),
    ("US", "real_yield_10y", "DFII10", "D", "%", "10-year TIPS constant maturity"),
    ("US", "breakeven_10y", "T10YIE", "D", "%", "10-year breakeven inflation"),
    ("US", "term_premium_10y", "THREEFYTP10", "D", "%", "Kim-Wright 10-year term premium"),
    ("US", "cpi_index", "CPIAUCSL", "M", "index", "CPI all urban, SA"),
    ("US", "cb_gov_holdings_lcu", "FDHBFRBN", "Q", "USD bn", "Federal debt held by Federal Reserve banks"),
    (
        "US",
        "foreign_gov_holdings_lcu",
        "FDHBFIN",
        "Q",
        "USD bn",
        "Federal debt held by foreign and international investors",
    ),
    ("US", "cg_debt_lcu", "FYGFDPUN", "Q", "USD bn", "Federal debt held by the public (millions; scaled)"),
    ("US", "gg_debt_gdp", "GFDEGDQ188S", "Q", "% GDP", "Federal debt: total public debt as % of GDP"),
    ("US", "ngdp_lcu", "GDP", "Q", "USD bn", "Nominal GDP, SAAR, divided by 4 to a quarterly flow"),
    (
        "US",
        "cg_interest_lcu",
        "A091RC1Q027SBEA",
        "Q",
        "USD bn",
        "Federal interest payments, SAAR, divided by 4",
    ),
    ("US", "cg_receipts_lcu", "FGRECPT", "Q", "USD bn", "Federal current receipts, SAAR, divided by 4"),
    ("US", "cg_outlays_lcu", "FGEXPND", "Q", "USD bn", "Federal current expenditures, SAAR, divided by 4"),
    (
        "US",
        "household_fin_assets_lcu",
        "BOGZ1FL194090005Q",
        "Q",
        "USD bn",
        "Household and nonprofit total financial assets (Z.1, millions; scaled)",
    ),
    (
        "US",
        "niip_gdp",
        "IIPUSNETIQ",
        "Q",
        "USD bn",
        "US net international investment position (millions; scaled; converted to % GDP in indicators)",
    ),
    ("GB", "fx_lcu_per_usd", "DEXUSUK", "D", "GBP per USD", "inverted from USD per GBP"),
    ("JP", "fx_lcu_per_usd", "DEXJPUS", "D", "JPY per USD", ""),
    ("AU", "fx_lcu_per_usd", "DEXUSAL", "D", "AUD per USD", "inverted from USD per AUD"),
    ("CA", "fx_lcu_per_usd", "DEXCAUS", "D", "CAD per USD", ""),
    ("CH", "fx_lcu_per_usd", "DEXSZUS", "D", "CHF per USD", ""),
    ("EA", "fx_lcu_per_usd", "DEXUSEU", "D", "EUR per USD", "inverted from USD per EUR"),
    ("BR", "fx_lcu_per_usd", "DEXBZUS", "D", "BRL per USD", ""),
    ("MX", "fx_lcu_per_usd", "DEXMXUS", "D", "MXN per USD", ""),
    ("SE", "fx_lcu_per_usd", "DEXSDUS", "D", "SEK per USD", ""),
    ("EA", "cb_total_assets_lcu", "ECBASSETSW", "W", "EUR bn", "ECB total assets (millions; scaled)"),
    ("JP", "cb_total_assets_lcu", "JPNASSETS", "M", "JPY bn", "BoJ total assets (100 million yen; scaled)"),
    ("GB", "ngdp_lcu", "UKNGDP", "Q", "GBP bn", "UK nominal GDP, SA, millions scaled"),
    (
        "JP",
        "ngdp_lcu",
        "JPNNGDP",
        "Q",
        "JPY bn",
        "Japan nominal GDP, SAAR? (checked in indicators via level ratio)",
    ),
]
# OECD MEI long rates on FRED for countries without a national 10y source
MEI_LONG = {
    "GB": "GB",
    "JP": "JP",
    "AU": "AU",
    "CA": "CA",
    "CH": "CH",
    "EA": "EZ",
    "DE": "DE",
    "FR": "FR",
    "IT": "IT",
    "NL": "NL",
    "GR": "GR",
    "SE": "SE",
    "MX": "MX",
    "RU": "RU",
}
MEI_GDP = {"GB": "GBR", "JP": "JPN", "AU": "AUS", "CA": "CAN", "CH": "CHE", "DE": "DEU"}
SCALE = {
    "FYGFDPUN": 1e-3,
    "ECBASSETSW": 1e-3,
    "JPNASSETS": 1e-1,
    "BOGZ1FL194090005Q": 1e-3,
    "IIPUSNETIQ": 1e-3,
    "UKNGDP": 1e-3,
    "JPNNGDP": 0.25,
    "GDP": 0.25,
    "A091RC1Q027SBEA": 0.25,
    "FGRECPT": 0.25,
    "FGEXPND": 0.25,
}
INVERT = {"DEXUSUK", "DEXUSAL", "DEXUSEU"}


def _all_series() -> list[tuple[str, str, str, str, str, str]]:
    out = list(SERIES)
    for cc, a in MEI_LONG.items():
        out.append(
            (cc, "yield_10y", f"IRLTLT01{a}M156N", "M", "%", "OECD MEI long-term government bond yield")
        )
    for cc, a in MEI_GDP.items():
        out.append(
            (
                cc,
                "ngdp_lcu",
                f"{a}GDPNQDSMEI",
                "Q",
                "LCU bn",
                "OECD MEI nominal GDP, SA, national currency units scaled to bn",
            )
        )
    return out


class FredCollector(Collector):
    name = "fred"

    def series(self) -> list[SeriesSpec]:
        return [
            SeriesSpec(
                cc,
                concept,
                "FRED",
                f"https://fred.stlouisfed.org/series/{fid}",
                freq,
                units,
                f"{fid}: {note}".strip(": "),
                params={"id": fid},
                variant=fid,
            )
            for cc, concept, fid, freq, units, note in _all_series()
        ]

    def fetch(self, spec: SeriesSpec) -> pd.DataFrame:
        fid = spec.params["id"]
        key = os.environ.get("FRED_API_KEY", "").strip()
        if key:
            payload = self.http.get_json(API, {"series_id": fid, "api_key": key, "file_type": "json"})
            self.cache_raw(fid, payload, "json")
            df = pd.DataFrame(payload["observations"])[["date", "value"]]
        else:
            text = self.http.get_text(GRAPH, {"id": fid})
            self.cache_raw(fid, text, "csv")
            df = pd.read_csv(io.StringIO(text))
            if df.shape[1] != 2:
                raise ValueError(f"unexpected fredgraph columns {list(df.columns)}")
            df.columns = ["date", "value"]
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna()
        scale = SCALE.get(fid, 1e-9 if fid.endswith("GDPNQDSMEI") else 1.0)
        if scale != 1.0:
            df["value"] = df["value"] * scale
        if fid in INVERT:
            df["value"] = 1.0 / df["value"]
        return df

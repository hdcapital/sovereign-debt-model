"""ONS time series (verified 2026-10-07; the old api.ons.gov.uk was retired Nov 2024).

GET https://www.ons.gov.uk/<topic path>/timeseries/<id>/<dataset>/data
-> {"months": [{"date": "2024 JAN", "value": "..."}], "quarters": [{"date": "2024 Q1"}], "years": [...]}
"""

from __future__ import annotations

import pandas as pd

from sdm.collect.base import Collector, SeriesSpec

PSF = "https://www.ons.gov.uk/economy/governmentpublicsectorandtaxes/publicsectorfinance/timeseries"
GDP = "https://www.ons.gov.uk/economy/grossdomesticproductgdp/timeseries"
CPI = "https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries"

# (concept, url, freq key, units, note, scale)
SERIES = [
    (
        "gg_debt_gdp",
        f"{PSF}/hf6x/pusf/data",
        "months",
        "% GDP",
        "HF6X: PSND ex public sector banks, % of GDP",
        1.0,
    ),
    (
        "gg_net_lending_lcu",
        f"{PSF}/j5ii/pusf/data",
        "months",
        "GBP bn",
        "J5II: public sector net lending ex banks, £m monthly (ONS stores borrowing as negative)",
        1e-3,
    ),
    (
        "gg_interest_lcu",
        f"{PSF}/jw2p/pusf/data",
        "months",
        "GBP bn",
        "JW2P: public sector interest paid to private sector and RoW, £m monthly",
        1e-3,
    ),
    (
        "cg_receipts_lcu",
        f"{PSF}/anbv/pusf/data",
        "months",
        "GBP bn",
        "ANBV: central government current receipts, £m monthly",
        1e-3,
    ),
    (
        "ngdp_lcu",
        f"{GDP}/ybha/qna/data",
        "quarters",
        "GBP bn",
        "YBHA: GDP at current market prices, SA, £m",
        1e-3,
    ),
    ("cpi_index", f"{CPI}/d7bt/mm23/data", "months", "index 2015=100", "D7BT: CPI all items index", 1.0),
]


def parse_ons_date(s: str, key: str) -> pd.Timestamp:
    s = s.strip()
    if key == "months":
        return pd.Period(pd.to_datetime(s, format="%Y %b"), freq="M").end_time.normalize()
    if key == "quarters":
        y, q = s.split()
        return pd.Period(f"{y}{q}", freq="Q").end_time.normalize()
    return pd.Timestamp(f"{s}-12-31")


class OnsCollector(Collector):
    name = "ons"

    def series(self) -> list[SeriesSpec]:
        return [
            SeriesSpec(
                "GB", concept, "ONS", url, key[0].upper(), units, note, params={"key": key, "scale": scale}
            )
            for concept, url, key, units, note, scale in SERIES
        ]

    def fetch(self, spec: SeriesSpec) -> pd.DataFrame:
        payload = self.http.get_json(spec.url)
        self.cache_raw(spec.series_id, payload, "json")
        key = spec.params["key"]
        obs = payload.get(key) or []
        if not obs:
            raise ValueError(f"no {key} in response; keys={list(payload)[:10]}")
        df = pd.DataFrame(obs)
        return pd.DataFrame(
            {
                "date": df["date"].map(lambda s: parse_ons_date(s, key)),
                "value": pd.to_numeric(df["value"], errors="coerce") * spec.params["scale"],
            }
        )

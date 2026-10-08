"""Eurostat JSON-stat API: quarterly government debt and non-financial accounts as % of GDP
for euro members (and Sweden). Verified shape from the probe before use."""

from __future__ import annotations

import pandas as pd

from sdm.collect.base import Collector, SeriesSpec

BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
GEO = {"DE": "DE", "FR": "FR", "IT": "IT", "NL": "NL", "GR": "EL", "SE": "SE", "EA": "EA20"}


class EurostatCollector(Collector):
    name = "eurostat"

    def series(self) -> list[SeriesSpec]:
        out = []
        for cc, geo in GEO.items():
            out.append(
                SeriesSpec(
                    cc,
                    "gg_debt_gdp",
                    "EUROSTAT",
                    f"{BASE}/gov_10q_ggdebt",
                    "Q",
                    "% GDP",
                    "Quarterly Maastricht debt, % of GDP",
                    params={"geo": geo, "q": {"unit": "PC_GDP", "sector": "S13", "na_item": "GD"}},
                )
            )
            out.append(
                SeriesSpec(
                    cc,
                    "gg_interest_gdp",
                    "EUROSTAT",
                    f"{BASE}/gov_10q_ggnfa",
                    "Q",
                    "% GDP",
                    "Quarterly interest payable (D41PAY), % of quarterly GDP",
                    params={
                        "geo": geo,
                        "q": {
                            "unit": "PC_GDP",
                            "sector": "S13",
                            "na_item": "D41PAY",
                            "s_adj": "NSA",
                        },
                    },
                )
            )
            out.append(
                SeriesSpec(
                    cc,
                    "gg_net_lending_gdp",
                    "EUROSTAT",
                    f"{BASE}/gov_10q_ggnfa",
                    "Q",
                    "% GDP",
                    "Quarterly net lending/borrowing, % of GDP",
                    params={
                        "geo": geo,
                        "q": {"unit": "PC_GDP", "sector": "S13", "na_item": "B9", "s_adj": "NSA"},
                    },
                )
            )
            out.append(
                SeriesSpec(
                    cc,
                    "gg_revenue_gdp",
                    "EUROSTAT",
                    f"{BASE}/gov_10q_ggnfa",
                    "Q",
                    "% GDP",
                    "Quarterly total revenue (TR), % of quarterly GDP",
                    params={
                        "geo": geo,
                        "q": {"unit": "PC_GDP", "sector": "S13", "na_item": "TR", "s_adj": "NSA"},
                    },
                )
            )
        # Switzerland reports national accounts to Eurostat; replaces the discontinued OECD MEI series
        out.append(
            SeriesSpec(
                "CH",
                "ngdp_lcu",
                "EUROSTAT",
                f"{BASE}/namq_10_gdp",
                "Q",
                "CHF bn",
                "GDP at market prices, current prices, SCA, CHF m (scaled)",
                params={
                    "geo": "CH",
                    "q": {"unit": "CP_MNAC", "s_adj": "SCA", "na_item": "B1GQ"},
                    "scale": 1e-3,
                },
            )
        )
        return out

    def fetch(self, spec: SeriesSpec) -> pd.DataFrame:
        params = {"geo": spec.params["geo"], **spec.params["q"]}
        payload = self.http.get_json(spec.url, params)
        self.cache_raw(spec.series_id, payload, "json")
        ids, sizes = payload["id"], payload["size"]
        if any(n != 1 for i, n in zip(ids, sizes, strict=True) if i != "time"):
            raise ValueError(f"query not fully pinned: {dict(zip(ids, sizes, strict=True))}")
        time_idx = payload["dimension"]["time"]["category"]["index"]
        values = payload["value"]
        rows = []
        for label, i in time_idx.items():
            v = values.get(str(i))
            if v is not None:
                y, q = label.split("-Q")
                rows.append((pd.Period(f"{y}Q{q}", freq="Q").end_time.normalize(), v))
        if not rows:
            raise ValueError("no values")
        df = pd.DataFrame(rows, columns=["date", "value"])
        df["value"] = df["value"] * spec.params.get("scale", 1.0)
        return df

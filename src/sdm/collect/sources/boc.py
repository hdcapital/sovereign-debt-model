"""Bank of Canada Valet API.

GET https://www.bankofcanada.ca/valet/observations/<series,...>/json?start_date=1970-01-01
-> {"observations": [{"d": "2024-01-02", "V39079": {"v": "5.00"}}, ...]}
"""

from __future__ import annotations

import pandas as pd

from sdm.collect.base import Collector, SeriesSpec

BASE = "https://www.bankofcanada.ca/valet/observations"

SERIES = [
    ("yield_2y", "BD.CDN.2YR.DQ.YLD", "D", "%", "2-year benchmark bond yield"),
    ("yield_5y", "BD.CDN.5YR.DQ.YLD", "D", "%", "5-year benchmark bond yield"),
    ("yield_10y", "BD.CDN.10YR.DQ.YLD", "D", "%", "10-year benchmark bond yield"),
    ("yield_30y", "BD.CDN.LONG.DQ.YLD", "D", "%", "Long-term benchmark bond yield"),
    ("real_yield_10y", "BD.CDN.RRB.DQ.YLD", "D", "%", "Real return bond yield (long)"),
    ("breakeven_10y", "BD.CDN.BEI.DQ.YLD", "D", "%", "Long-term breakeven inflation rate"),
]


class BocCollector(Collector):
    name = "boc"

    def series(self) -> list[SeriesSpec]:
        return [
            SeriesSpec(
                "CA",
                concept,
                "BOC",
                f"{BASE}/{sid}/json",
                freq,
                units,
                f"{sid}: {note}",
                params={"id": sid},
            )
            for concept, sid, freq, units, note in SERIES
        ]

    def fetch(self, spec: SeriesSpec) -> pd.DataFrame:
        payload = self.http.get_json(spec.url, {"start_date": "1970-01-01"})
        self.cache_raw(spec.params["id"], payload, "json")
        sid = spec.params["id"]
        rows = [(o["d"], o.get(sid, {}).get("v")) for o in payload.get("observations", [])]
        if not rows:
            raise ValueError(f"no observations: {str(payload)[:200]}")
        return pd.DataFrame(rows, columns=["date", "value"])

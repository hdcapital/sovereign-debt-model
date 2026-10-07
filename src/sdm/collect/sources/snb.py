"""Swiss National Bank data portal CSV cubes (verified 2026-10-07).

GET https://data.snb.ch/api/cube/<cube>/data/csv/en -> metadata lines, blank, then
'"Date";"D0";"Value"' rows separated by semicolons. rendoblim = Confederation bond spot
yields (D0 = 1J..30J), snbbipo = SNB balance sheet (D0 = T0 total assets)."""

from __future__ import annotations

import io

import pandas as pd

from sdm.collect.base import Collector, SeriesSpec

BASE = "https://data.snb.ch/api/cube"

SERIES = [
    ("yield_10y", "rendoblim", {"D0": "10J"}, "M", "%", "Yield on Swiss Confederation bonds, 10-year spot"),
    ("yield_2y", "rendoblim", {"D0": "2J"}, "M", "%", "Yield on Swiss Confederation bonds, 2-year spot"),
    ("yield_5y", "rendoblim", {"D0": "5J"}, "M", "%", "Yield on Swiss Confederation bonds, 5-year spot"),
    (
        "cb_total_assets_lcu",
        "snbbipo",
        {"D0": "T0"},
        "M",
        "CHF bn",
        "SNB balance sheet total assets (CHF m scaled)",
    ),
]
SCALE = {"snbbipo": 1e-3}


def parse_snb_csv(text: str) -> pd.DataFrame:
    lines = text.lstrip("﻿").splitlines()
    hdr = next(i for i, ln in enumerate(lines) if ln.replace('"', "").startswith("Date;"))
    return pd.read_csv(io.StringIO("\n".join(lines[hdr:])), sep=";")


class SnbCollector(Collector):
    name = "snb"

    def series(self) -> list[SeriesSpec]:
        return [
            SeriesSpec(
                "CH",
                concept,
                "SNB",
                f"{BASE}/{cube}/data/csv/en",
                freq,
                units,
                note,
                params={"cube": cube, "filter": flt},
            )
            for concept, cube, flt, freq, units, note in SERIES
        ]

    def fetch(self, spec: SeriesSpec) -> pd.DataFrame:
        text = self.http.get_text(spec.url, encoding="utf-8-sig")
        self.cache_raw(spec.params["cube"], text, "csv")
        df = parse_snb_csv(text)
        for col, val in spec.params["filter"].items():
            df = df[df[col].astype(str) == val]
        if df.empty:
            raise ValueError(f"filter {spec.params['filter']} matched nothing")
        dates = (
            df["Date"]
            .astype(str)
            .map(lambda s: pd.Period(s, freq="M").end_time.normalize() if len(s) == 7 else pd.Timestamp(s))
        )
        return pd.DataFrame(
            {
                "date": dates,
                "value": pd.to_numeric(df["Value"], errors="coerce") * SCALE.get(spec.params["cube"], 1.0),
            }
        )

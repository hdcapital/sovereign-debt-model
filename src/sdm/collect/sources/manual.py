"""Hand-maintained series with citations: data/manual/*.csv.

Each file is long format: country,concept,date,value,source,notes. Used for series that no
free API provides (average maturity for several countries, historical holder shares for the
backtest events). Every row carries its citation; the catalog notes point at the file."""

from __future__ import annotations

import pandas as pd

from sdm.collect.base import Collector, SeriesSpec
from sdm.paths import DATA_MANUAL


class ManualCollector(Collector):
    name = "manual"

    def _frames(self) -> pd.DataFrame:
        frames = [pd.read_csv(p) for p in sorted(DATA_MANUAL.glob("*.csv"))]
        if not frames:
            return pd.DataFrame(columns=["country", "concept", "date", "value", "source", "notes"])
        return pd.concat(frames, ignore_index=True)

    def series(self) -> list[SeriesSpec]:
        df = self._frames()
        out = []
        for (cc, concept), g in df.groupby(["country", "concept"]):
            src = str(g["source"].iloc[0])
            out.append(
                SeriesSpec(
                    str(cc),
                    str(concept),
                    "MANUAL",
                    "data/manual/",
                    "A",
                    "",
                    f"hand-maintained; {src[:120]}",
                )
            )
        return out

    def fetch(self, spec: SeriesSpec) -> pd.DataFrame:
        df = self._frames()
        sel = df[(df["country"] == spec.country) & (df["concept"] == spec.concept)]
        return sel[["date", "value"]]

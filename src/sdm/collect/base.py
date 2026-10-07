"""Common collector interface.

Every source implements :class:`Collector`. The base class handles raw caching with a vintage
stamp, the tidy long-format schema, quarterly resampling under the configured rules, and
catalog bookkeeping. Subclasses only implement :meth:`Collector.fetch`.

Tidy schema (one row per observation)::

    series_id   str   e.g. "US.debt_gdp.BIS"
    country     str   universe code
    concept     str   e.g. "debt_gdp"
    date        date  period end
    value       float
    vintage     date  date the observation was downloaded (revisions keep the old row)
"""

from __future__ import annotations

import abc
import json
import logging
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from sdm.paths import DATA_CLEAN, DATA_RAW

log = logging.getLogger(__name__)

TIDY_COLUMNS = ["series_id", "country", "concept", "date", "value", "vintage"]


@dataclass(frozen=True)
class SeriesSpec:
    """What a collector promises to deliver for one (country, concept)."""

    series_id: str
    country: str
    concept: str
    source: str
    url: str
    frequency: str  # D, M, Q, A
    units: str
    notes: str = ""


class Collector(abc.ABC):
    """Base class. Subclasses set ``name`` and implement ``series`` and ``fetch``."""

    name: str = "base"

    @property
    def raw_dir(self) -> Path:
        return DATA_RAW / self.name

    @abc.abstractmethod
    def series(self) -> list[SeriesSpec]:
        """The series this collector maintains."""

    @abc.abstractmethod
    def fetch(self, spec: SeriesSpec) -> pd.DataFrame:
        """Return a frame with columns [date, value] at native frequency."""

    def cache_raw(self, spec: SeriesSpec, payload: Any, suffix: str = "json") -> Path:
        """Write the raw response under data/raw/<source>/<series_id>.<vintage>.<suffix>."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / f"{spec.series_id}.{date.today().isoformat()}.{suffix}"
        if suffix == "json":
            path.write_text(json.dumps(payload, indent=1, default=str), encoding="utf-8")
        else:
            path.write_bytes(payload if isinstance(payload, bytes) else str(payload).encode())
        return path

    def tidy(self, spec: SeriesSpec, frame: pd.DataFrame) -> pd.DataFrame:
        out = frame[["date", "value"]].copy()
        out["date"] = pd.to_datetime(out["date"]).dt.date
        out["value"] = pd.to_numeric(out["value"], errors="coerce")
        out = out.dropna(subset=["value"])
        out["series_id"] = spec.series_id
        out["country"] = spec.country
        out["concept"] = spec.concept
        out["vintage"] = date.today()
        return out[TIDY_COLUMNS].sort_values("date").reset_index(drop=True)

    def write_clean(self, spec: SeriesSpec, tidy: pd.DataFrame) -> Path:
        """Append new observations and revisions; keep every vintage of a changed value."""
        DATA_CLEAN.mkdir(parents=True, exist_ok=True)
        path = DATA_CLEAN / f"{spec.series_id}.parquet"
        if path.exists():
            old = pd.read_parquet(path)
            merged = pd.concat([old, tidy], ignore_index=True)
            # Keep one row per (date, value); a revision is a new (date, value) with a new vintage.
            merged = merged.drop_duplicates(subset=["date", "value"], keep="first")
        else:
            merged = tidy
        merged = merged.sort_values(["date", "vintage"]).reset_index(drop=True)
        merged.to_parquet(path, index=False)
        return path


def latest_vintage(tidy: pd.DataFrame) -> pd.DataFrame:
    """Collapse a multi-vintage tidy frame to the most recent value per date."""
    return tidy.sort_values("vintage").drop_duplicates(subset=["date"], keep="last")

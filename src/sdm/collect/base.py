"""Common collector interface.

Every source implements :class:`Collector`. The base class handles raw caching, the tidy
long-format schema, revision-aware writes to ``data/clean/<source>.csv`` and catalog
bookkeeping. Subclasses implement :meth:`Collector.series` and :meth:`Collector.fetch`.

Tidy schema (one row per observation)::

    series_id   str   "<COUNTRY>.<concept>.<SOURCE>"
    country     str   universe code (or "XX" for global series such as gold)
    concept     str   name from sdm.collect.concepts
    date        date  period end
    value       float
    vintage     datetime (UTC, seconds) when the observation was downloaded; a revision adds a new row

Collectors never forward-fill. Resampling happens in sdm.indicators.panel under the
explicit rules in config/indicators.yaml.
"""

from __future__ import annotations

import abc
import csv
import json
import logging
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from sdm.collect.concepts import CONCEPTS
from sdm.collect.http import Http
from sdm.paths import CATALOG, DATA_CLEAN, DATA_RAW

log = logging.getLogger(__name__)


def now_vintage() -> pd.Timestamp:
    """Download timestamp, UTC to the second, naive (CSV friendly)."""
    return pd.Timestamp.now(tz="UTC").tz_localize(None).floor("s")


TIDY_COLUMNS = ["series_id", "country", "concept", "date", "value", "vintage"]
CATALOG_COLUMNS = [
    "series_id",
    "country",
    "concept",
    "source",
    "url",
    "frequency",
    "units",
    "first_obs",
    "last_obs",
    "vintage",
    "n_obs",
    "notes",
]


@dataclass(frozen=True)
class SeriesSpec:
    """What a collector promises to deliver for one (country, concept)."""

    country: str
    concept: str
    source: str
    url: str
    frequency: str  # D, W, M, Q, A
    units: str
    notes: str = ""
    params: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.concept not in CONCEPTS:
            raise ValueError(f"unknown concept {self.concept!r} for {self.country}/{self.source}")

    @property
    def series_id(self) -> str:
        return f"{self.country}.{self.concept}.{self.source}"


@dataclass
class FetchResult:
    spec: SeriesSpec
    ok: bool
    n_obs: int = 0
    n_new: int = 0
    n_revised: int = 0
    error: str = ""
    last_obs: date | None = None


class Collector(abc.ABC):
    """Base class. Subclasses set ``name`` and implement ``series`` and ``fetch``."""

    name: str = "base"

    def __init__(self, http: Http | None = None) -> None:
        self.http = http or Http()

    @property
    def raw_dir(self) -> Path:
        return DATA_RAW / self.name

    @property
    def clean_path(self) -> Path:
        return DATA_CLEAN / f"{self.name}.csv"

    @abc.abstractmethod
    def series(self) -> list[SeriesSpec]:
        """The series this collector maintains."""

    @abc.abstractmethod
    def fetch(self, spec: SeriesSpec) -> pd.DataFrame:
        """Return a frame with columns [date, value] at native frequency."""

    # ---------------------------------------------------------------- raw cache
    def cache_raw(self, name: str, payload: bytes | str | Any, suffix: str = "json") -> Path:
        """Keep the latest raw response under data/raw/<source>/<name>.<suffix>."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / f"{name}.{suffix}"
        if isinstance(payload, bytes):
            path.write_bytes(payload)
        elif isinstance(payload, str):
            path.write_text(payload, encoding="utf-8")
        else:
            path.write_text(json.dumps(payload, indent=1, default=str), encoding="utf-8")
        return path

    # ---------------------------------------------------------------- tidy + store
    @staticmethod
    def tidy(
        spec: SeriesSpec, frame: pd.DataFrame, vintage: date | pd.Timestamp | None = None
    ) -> pd.DataFrame:
        out = frame[["date", "value"]].copy()
        out["date"] = pd.to_datetime(out["date"]).dt.date
        out["value"] = pd.to_numeric(out["value"], errors="coerce")
        out = out.dropna(subset=["value", "date"]).drop_duplicates(subset=["date"], keep="last")
        out["series_id"] = spec.series_id
        out["country"] = spec.country
        out["concept"] = spec.concept
        out["vintage"] = pd.Timestamp(vintage) if vintage is not None else now_vintage()
        return out[TIDY_COLUMNS].sort_values("date").reset_index(drop=True)

    def load_clean(self) -> pd.DataFrame:
        if not self.clean_path.exists():
            return pd.DataFrame(columns=TIDY_COLUMNS)
        df = pd.read_csv(self.clean_path, dtype={"series_id": str, "country": str, "concept": str})
        if df.empty:
            return pd.DataFrame(columns=TIDY_COLUMNS)
        df["date"] = pd.to_datetime(df["date"]).dt.date
        df["vintage"] = pd.to_datetime(df["vintage"])
        return df

    def merge_series(self, existing: pd.DataFrame, new: pd.DataFrame) -> tuple[pd.DataFrame, int, int]:
        """Merge one series' new tidy rows into the existing store.

        A value that matches the latest vintage for that date is not re-added; a different
        value is appended with today's vintage (the old row stays, so revisions are visible).
        Returns (merged, n_new_dates, n_revised_dates)."""
        sid = new["series_id"].iloc[0] if len(new) else None
        old = existing[existing["series_id"] == sid] if sid else existing.iloc[0:0]
        rest = existing[existing["series_id"] != sid] if sid else existing
        if old.empty:
            return pd.concat([rest, new], ignore_index=True), len(new), 0
        latest = (
            old.sort_values("vintage", kind="stable")
            .drop_duplicates("date", keep="last")
            .set_index("date")["value"]
        )
        add_rows = []
        n_new = n_rev = 0
        for row in new.itertuples(index=False):
            prev = latest.get(row.date)
            if prev is None:
                n_new += 1
                add_rows.append(row)
            elif abs(float(prev) - float(row.value)) > 1e-9 * max(1.0, abs(float(prev))):
                n_rev += 1
                add_rows.append(row)
        added = pd.DataFrame(add_rows, columns=TIDY_COLUMNS) if add_rows else new.iloc[0:0]
        return pd.concat([rest, old, added], ignore_index=True), n_new, n_rev

    def write_clean(self, df: pd.DataFrame) -> None:
        DATA_CLEAN.mkdir(parents=True, exist_ok=True)
        df = df.copy()
        df["vintage"] = pd.to_datetime(df["vintage"])
        df = df.sort_values(["series_id", "date", "vintage"], kind="stable").reset_index(drop=True)
        df["vintage"] = df["vintage"].dt.strftime("%Y-%m-%dT%H:%M:%S")
        df.to_csv(self.clean_path, index=False)

    # ---------------------------------------------------------------- run
    def run(self, only: set[str] | None = None) -> list[FetchResult]:
        """Fetch every series (or those in ``only``), merge, write, return per-series results."""
        store = self.load_clean()
        results: list[FetchResult] = []
        for spec in self.series():
            if only and spec.series_id not in only and spec.concept not in only and spec.country not in only:
                continue
            try:
                frame = self.fetch(spec)
                tidy = self.tidy(spec, frame)
                if tidy.empty:
                    raise ValueError("no observations parsed")
                store, n_new, n_rev = self.merge_series(store, tidy)
                results.append(FetchResult(spec, True, len(tidy), n_new, n_rev, last_obs=tidy["date"].max()))
                log.info(
                    "%s: %d obs, %d new, %d revised, last %s",
                    spec.series_id,
                    len(tidy),
                    n_new,
                    n_rev,
                    tidy["date"].max(),
                )
            except Exception as e:  # noqa: BLE001 - a broken source must not stop the run
                log.warning("%s: FAILED %s", spec.series_id, e)
                results.append(FetchResult(spec, False, error=f"{type(e).__name__}: {e}"[:500]))
        self.write_clean(store)
        update_catalog(self, store, results)
        return results


def update_catalog(collector: Collector, store: pd.DataFrame, results: list[FetchResult]) -> None:
    """Rewrite this collector's rows in data/catalog.csv from the clean store."""
    rows: dict[str, dict[str, Any]] = {}
    if CATALOG.exists():
        with CATALOG.open(encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                rows[r["series_id"]] = r
    by_spec = {r.spec.series_id: r for r in results}
    for spec in collector.series():
        s = store[store["series_id"] == spec.series_id]
        res = by_spec.get(spec.series_id)
        prev = rows.get(spec.series_id, {})
        latest = s.sort_values("vintage", kind="stable").drop_duplicates("date", keep="last") if len(s) else s
        rows[spec.series_id] = {
            "series_id": spec.series_id,
            "country": spec.country,
            "concept": spec.concept,
            "source": spec.source,
            "url": spec.url,
            "frequency": spec.frequency,
            "units": spec.units,
            "first_obs": str(latest["date"].min()) if len(latest) else prev.get("first_obs", ""),
            "last_obs": str(latest["date"].max()) if len(latest) else prev.get("last_obs", ""),
            "vintage": str(s["vintage"].max()) if len(s) else prev.get("vintage", ""),
            "n_obs": str(len(latest)) if len(latest) else prev.get("n_obs", "0"),
            "notes": (spec.notes + (f" | LAST ERROR: {res.error}" if res and not res.ok else "")).strip(),
        }
    with CATALOG.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CATALOG_COLUMNS)
        w.writeheader()
        for sid in sorted(rows):
            w.writerow({k: rows[sid].get(k, "") for k in CATALOG_COLUMNS})


def latest_vintage_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Collapse a multi-vintage tidy frame to the most recent value per (series, date)."""
    return (
        df.sort_values("vintage", kind="stable")
        .drop_duplicates(subset=["series_id", "date"], keep="last")
        .sort_values(["series_id", "date"])
        .reset_index(drop=True)
    )


def load_all_clean(latest_only: bool = True) -> pd.DataFrame:
    """Every clean series from every source, optionally collapsed to the latest vintage."""
    frames = []
    for path in sorted(DATA_CLEAN.glob("*.csv")):
        if path.name.startswith(("panel", "indicators", "transitions")):
            continue
        df = pd.read_csv(path, dtype={"series_id": str, "country": str, "concept": str})
        if df.empty:
            continue
        frames.append(df)
    if not frames:
        return pd.DataFrame(columns=TIDY_COLUMNS)
    df = pd.concat(frames, ignore_index=True)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["vintage"] = pd.to_datetime(df["vintage"], errors="coerce")
    df = df.dropna(subset=["date", "value"])
    df["date"] = df["date"].dt.date
    if latest_only:
        return latest_vintage_frame(df)
    return df.sort_values(["series_id", "date"]).reset_index(drop=True)

"""Quarterly panel: one row per (country, quarter), one column per concept.

Built from the clean store (``data/clean/*.csv``) by:
1. choosing, per (country, concept, quarter), the highest-priority source that has data
   (``source_priority`` in config/indicators.yaml), lower-priority sources filling gaps;
2. aggregating each series to quarterly by concept kind (sdm.collect.concepts.KIND):
   stocks and rates take the last observation in the quarter, flows sum monthly values
   (a quarter with fewer than 3 months is NaN) and spread annual values over four quarters;
3. never forward-filling beyond ``max_forward_fill_periods`` (default 1 quarter).

The result is written to data/clean/panel.csv with a companion panel_sources.csv saying
which source supplied each cell, so every number in a report can be traced.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd

from sdm.collect.base import load_all_clean
from sdm.collect.concepts import KIND
from sdm.config import load_indicator_config
from sdm.paths import DATA_CLEAN

log = logging.getLogger(__name__)

PANEL_PATH = DATA_CLEAN / "panel.csv"
SOURCES_PATH = DATA_CLEAN / "panel_sources.csv"


@dataclass
class Panel:
    values: pd.DataFrame  # index (country, quarter end Timestamp), columns concepts
    sources: pd.DataFrame  # same shape, source name strings


def infer_freq(dates: pd.Series) -> str:
    """D/W/M/Q/A from the median spacing of observations."""
    d = pd.to_datetime(dates).sort_values().diff().dt.days.dropna()
    if d.empty:
        return "A"
    med = float(d.median())
    if med <= 3:
        return "D"
    if med <= 10:
        return "W"
    if med <= 45:
        return "M"
    if med <= 120:
        return "Q"
    return "A"


def to_quarterly(series: pd.Series, kind: str, max_ffill: int = 1) -> pd.Series:
    """Aggregate one series (DatetimeIndex, native frequency) to quarter-end values."""
    s = series.dropna().sort_index()
    if s.empty:
        return s
    freq = infer_freq(pd.Series(s.index))
    q = s.index.to_period("Q")
    if freq == "A":
        # one observation per year covers the four quarters of that year
        rows = []
        for ts, v in s.items():
            year = ts.year
            for qq in range(1, 5):
                p = pd.Period(f"{year}Q{qq}", freq="Q")
                rows.append((p.end_time.normalize(), v / 4.0 if kind == "flow" else v))
        out = pd.Series(dict(rows)).sort_index()
        out.index = pd.DatetimeIndex(out.index)
        return out
    if kind == "flow":
        if freq == "Q":
            out = s.groupby(q).last()
        elif freq == "M":
            g = s.groupby(q)
            out = g.sum()
            out[g.count() < 3] = float("nan")
        else:  # daily/weekly flows are unusual; sum what is there
            out = s.groupby(q).sum()
    else:
        out = s.groupby(q).last()
    out.index = out.index.to_timestamp(how="end").normalize()
    full = pd.date_range(out.index.min(), out.index.max(), freq="QE")
    out = out.reindex(full)
    if max_ffill:
        out = out.ffill(limit=max_ffill)
    return out.dropna()


def splice(primary: pd.Series, secondary: pd.Series, kind: str, overlap_quarters: int = 4) -> pd.Series:
    """Shift a lower-priority series so it joins the primary without a level break.

    Stocks and flows are scaled by the ratio of the two over their last overlapping
    quarters; rates and ratios are shifted additively. Without any overlap the secondary
    is used as is."""
    common = primary.index.intersection(secondary.index)
    if len(common) == 0:
        return secondary
    common = common.sort_values()[-overlap_quarters:]
    a, b = primary.loc[common], secondary.loc[common]
    if kind in ("stock", "flow") and (b.abs() > 0).all() and (a.abs() > 0).all():
        factor = float((a / b).mean())
        if 0.2 < factor < 5.0:
            return secondary * factor
        return secondary
    return secondary + float((a - b).mean())


def _priority_for(concept: str, cfg: dict[str, list[str]]) -> list[str]:
    return list(cfg.get(concept, cfg["default"]))


def build_panel(clean: pd.DataFrame | None = None, write: bool = True) -> Panel:
    cfg = load_indicator_config()
    prio_cfg: dict[str, list[str]] = cfg.raw.get("source_priority", {"default": []})
    max_ffill = cfg.max_forward_fill_periods
    df = clean if clean is not None else load_all_clean()
    if df.empty:
        raise RuntimeError("clean store is empty; run `sdm update` first")
    df["source"] = df["series_id"].str.split(".").str[2]
    df["date"] = pd.to_datetime(df["date"])

    cells: dict[tuple[str, str], pd.Series] = {}
    srcs: dict[tuple[str, str], pd.Series] = {}
    for (country, concept), g in df.groupby(["country", "concept"]):
        order = _priority_for(concept, prio_cfg)
        rank = {src: i for i, src in enumerate(order)}
        ids = list(dict.fromkeys(g["series_id"]))  # first-appearance order within a source
        ids.sort(key=lambda sid: rank.get(sid.split(".")[2], len(order)))
        merged: pd.Series | None = None
        merged_src: pd.Series | None = None
        for sid in ids:
            src = sid.split(".")[2]
            sub = g[g["series_id"] == sid].set_index("date")["value"]
            qs = to_quarterly(sub, KIND.get(concept, "rate"), max_ffill)
            if qs.empty:
                continue
            tag = pd.Series(src, index=qs.index)
            if merged is None:
                merged, merged_src = qs, tag
            else:
                qs = splice(merged, qs, KIND.get(concept, "rate"))
                new_idx = qs.index.difference(merged.index)
                merged = pd.concat([merged, qs.loc[new_idx]]).sort_index()
                merged_src = pd.concat([merged_src, tag.loc[new_idx]]).sort_index()
        if merged is not None:
            cells[(country, concept)] = merged
            srcs[(country, concept)] = merged_src

    values = pd.DataFrame({k: v for k, v in cells.items()})
    sources = pd.DataFrame({k: v for k, v in srcs.items()})
    values = values.stack(level=0, future_stack=True).swaplevel().sort_index()
    sources = sources.stack(level=0, future_stack=True).swaplevel().sort_index()
    values.index.names = ["country", "quarter"]
    sources.index.names = ["country", "quarter"]
    values = values.dropna(how="all")
    sources = sources.reindex(values.index)
    panel = Panel(values=values, sources=sources)
    if write:
        DATA_CLEAN.mkdir(parents=True, exist_ok=True)
        values.to_csv(PANEL_PATH)
        sources.to_csv(SOURCES_PATH)
        log.info("panel: %d rows x %d concepts -> %s", *values.shape, PANEL_PATH)
    return panel


def load_panel() -> Panel:
    values = pd.read_csv(PANEL_PATH, index_col=[0, 1], parse_dates=[1])
    sources = pd.read_csv(SOURCES_PATH, index_col=[0, 1], parse_dates=[1])
    return Panel(values=values, sources=sources)

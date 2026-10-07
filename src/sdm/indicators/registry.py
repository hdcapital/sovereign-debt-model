"""Indicator registry. Each indicator is a pure function ``f(ctx) -> pd.Series`` registered
with metadata; the docstring is the reader-facing explanation shown on the dashboard."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass
class Ctx:
    """Everything an indicator may read: the country's quarterly concepts, the indicators
    computed so far, the country config and the indicator config. Index is quarter end."""

    country: str
    c: pd.DataFrame  # concepts
    ind: pd.DataFrame  # indicators computed so far (same index)
    country_cfg: Any
    cfg: Any
    bloc: pd.DataFrame | None = None  # the bloc's concept frame for union members
    anchor: pd.DataFrame | None = None  # the anchor country's concept frame

    def col(self, name: str) -> pd.Series:
        if name in self.c.columns:
            return self.c[name]
        return pd.Series(float("nan"), index=self.c.index, dtype="float64")

    def i(self, name: str) -> pd.Series:
        if name in self.ind.columns:
            return self.ind[name]
        return pd.Series(float("nan"), index=self.c.index, dtype="float64")


@dataclass
class IndicatorMeta:
    name: str
    block: str
    units: str
    fn: Callable[[Ctx], pd.Series]
    doc: str
    helper: bool = False  # helper series are computed but not shown on the dashboard
    tags: list[str] = field(default_factory=list)


REGISTRY: dict[str, IndicatorMeta] = {}


def indicator(
    block: str, units: str, helper: bool = False
) -> Callable[[Callable[[Ctx], pd.Series]], Callable[[Ctx], pd.Series]]:
    def deco(fn: Callable[[Ctx], pd.Series]) -> Callable[[Ctx], pd.Series]:
        REGISTRY[fn.__name__] = IndicatorMeta(
            fn.__name__, block, units, fn, (fn.__doc__ or "").strip(), helper
        )
        return fn

    return deco


def pct_change_n(s: pd.Series, n: int) -> pd.Series:
    return (s / s.shift(n) - 1.0) * 100.0


def diff_n(s: pd.Series, n: int) -> pd.Series:
    return s - s.shift(n)


def rolling_sum4(s: pd.Series) -> pd.Series:
    return s.rolling(4, min_periods=4).sum()

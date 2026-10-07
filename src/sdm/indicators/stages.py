"""Stage engine: evaluates config/stages.yaml against an indicator frame.

Rule grammar (see the YAML): conditions {ind, op, value, lookback, min_hits, negate} combined
with ``all`` / ``any``; a stage fires only if its ``requires`` stage fires. The estimate is
the highest firing stage. Regime overrides replace a stage's rule for that monetary regime.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _cond_series(cond: dict[str, Any], ind: pd.DataFrame) -> pd.Series:
    """Boolean series (NaN where undecidable) for one leaf condition."""
    name = cond["ind"]
    if name not in ind.columns:
        return pd.Series(np.nan, index=ind.index, dtype="float64")
    s = ind[name]
    op = cond["op"]
    val = float(cond.get("value", 0.0))
    look = int(cond.get("lookback", 0))
    if op in ("gt", "lt", "ge", "le"):
        base = {"gt": s > val, "lt": s < val, "ge": s >= val, "le": s <= val}[op].astype(float)
        base = base.where(s.notna())
        if look and cond.get("min_hits"):
            hits = base.rolling(look, min_periods=look).sum()
            base = (hits >= int(cond["min_hits"])).astype(float).where(hits.notna())
    elif op in ("rising", "falling"):
        chg = s - s.shift(max(look, 1))
        base = ((chg > val) if op == "rising" else (chg < val)).astype(float).where(chg.notna())
    elif op == "record_high":
        base = (s >= s.cummax()).astype(float).where(s.notna())
    else:
        raise ValueError(f"unknown op {op}")
    if cond.get("negate"):
        base = 1.0 - base
    return base


def _rule_series(rule: dict[str, Any], ind: pd.DataFrame) -> pd.Series:
    """Evaluate a nested all/any rule. Unknown (NaN) conditions count as not satisfied for
    ``all`` and are ignored for ``any`` unless every branch is unknown."""
    parts_all = [_eval(c, ind) for c in rule.get("all", [])]
    parts_any = [_eval(c, ind) for c in rule.get("any", [])]
    out = pd.Series(1.0, index=ind.index)
    if parts_all:
        m = pd.concat(parts_all, axis=1)
        out = out * (m.fillna(0).min(axis=1))
        out = out.where(m.notna().any(axis=1))
    if parts_any:
        m = pd.concat(parts_any, axis=1)
        anyv = m.fillna(0).max(axis=1).where(m.notna().any(axis=1))
        out = out * anyv
    return out


def _eval(cond: dict[str, Any], ind: pd.DataFrame) -> pd.Series:
    if "all" in cond or "any" in cond:
        return _rule_series(cond, ind)
    return _cond_series(cond, ind)


def stage_rules_for(regime: str, rules: dict[str, Any]) -> dict[int, dict[str, Any]]:
    stages = {int(k): dict(v) for k, v in rules["stages"].items()}
    for sid, spec in rules.get("regime_overrides", {}).get(regime, {}).items():
        stages[int(sid)] = dict(spec)
    return stages


def estimate_stages(ind: pd.DataFrame, regime: str, rules: dict[str, Any]) -> pd.DataFrame:
    """Return a frame with one boolean-ish column per stage (``stage_k``) and ``stage_estimate``."""
    stages = stage_rules_for(regime, rules)
    fired: dict[int, pd.Series] = {}
    for sid in sorted(stages):
        spec = stages[sid]
        f = _rule_series(spec, ind)
        req = spec.get("requires")
        if req is not None:
            f = f * fired[int(req)].fillna(0)
        fired[sid] = f
    out = pd.DataFrame({f"stage_{k}": v for k, v in fired.items()}, index=ind.index)
    est = pd.Series(0.0, index=ind.index)
    for sid in sorted(fired):
        est = est.where(~(fired[sid] >= 1.0), float(sid))
    # no estimate while the fuel stage itself cannot be decided (not enough history)
    out["stage_estimate"] = est.where(fired[0].notna())
    return out

"""Compute the quarterly indicator table from the panel.

Outputs (data/clean/):
    indicators.csv          long history, index (country, quarter), one column per indicator
    indicators_latest.csv   one row per core country: latest value, 1y and 5y change, stage,
                            quadrant, and the quarter each value refers to
    transitions.csv         every quarter in which a country's quadrant or stage changed
"""

from __future__ import annotations

import logging
from datetime import date

import numpy as np
import pandas as pd

from sdm.config import load_indicator_config, load_stage_rules, load_universe
from sdm.indicators import blocks  # noqa: F401  (registers the indicators)
from sdm.indicators.applicability import indicator_applies
from sdm.indicators.panel import Panel, load_panel
from sdm.indicators.registry import REGISTRY, Ctx
from sdm.indicators.stages import estimate_stages
from sdm.paths import DATA_CLEAN

log = logging.getLogger(__name__)

INDICATORS_PATH = DATA_CLEAN / "indicators.csv"
LATEST_PATH = DATA_CLEAN / "indicators_latest.csv"
TRANSITIONS_PATH = DATA_CLEAN / "transitions.csv"

QUADRANTS = {
    (False, True): "sustainable_captive",
    (False, False): "sustainable_free",
    (True, True): "unsustainable_captive",
    (True, False): "unsustainable_free",
}


def _country_frame(panel: Panel, code: str) -> pd.DataFrame | None:
    if code not in panel.values.index.get_level_values(0):
        return None
    df = panel.values.loc[code].copy()
    df.index = pd.DatetimeIndex(df.index)
    # global series (gold) are attached to every country
    if "XX" in panel.values.index.get_level_values(0):
        g = panel.values.loc["XX"]
        for col in g.columns:
            if col not in df.columns:
                df[col] = g[col].reindex(df.index)
    return df.sort_index()


def compute_country(panel: Panel, code: str, when: date | None = None) -> pd.DataFrame:
    uni = load_universe()
    cfg = load_indicator_config()
    rules = load_stage_rules()
    ccfg = uni[code]
    c = _country_frame(panel, code)
    if c is None or c.empty:
        raise ValueError(f"no panel data for {code}")
    bloc = _country_frame(panel, ccfg.bloc) if ccfg.bloc else None
    anchor_code = ccfg.anchor if ccfg.anchor and ccfg.anchor != code else None
    if anchor_code is None and ccfg.monetary_regime == "pegged":
        anchor_code = "US"
    anchor = _country_frame(panel, anchor_code) if anchor_code else None
    ind = pd.DataFrame(index=c.index)
    ctx = Ctx(country=code, c=c, ind=ind, country_cfg=ccfg, cfg=cfg, bloc=bloc, anchor=anchor)
    for name, meta in REGISTRY.items():
        try:
            ind[name] = meta.fn(ctx).reindex(c.index).astype(float)
        except Exception as e:  # noqa: BLE001 - one broken indicator must not stop the table
            log.warning("%s.%s failed: %s", code, name, e)
            ind[name] = np.nan
        ctx.ind = ind
    # stages use the regime in force each quarter
    regimes = pd.Series([ccfg.regime_at(ts.date()) for ts in c.index], index=c.index)
    stage_cols = pd.DataFrame(index=c.index)
    for regime in regimes.unique():
        sub = estimate_stages(ind, regime, rules)
        mask = regimes == regime
        for col in sub.columns:
            stage_cols.loc[mask, col] = sub.loc[mask, col]
    ind = pd.concat([ind, stage_cols], axis=1)
    ind["monetary_regime"] = regimes
    # quadrant
    q = cfg.quadrant
    unsus = (ind["forward_r_minus_g_5y"] > q["unsustainable"]["forward_r_minus_g_5y_gt"]) & (
        ind["primary_balance_gdp"] < q["unsustainable"]["primary_balance_gdp_lt"]
    )
    captive = ind["captivity_score"] > q["captive"]["captivity_score_gt"]
    known = (
        ind["forward_r_minus_g_5y"].notna()
        & ind["primary_balance_gdp"].notna()
        & ind["captivity_score"].notna()
    )
    ind["trajectory_unsustainable"] = unsus.astype(float).where(known)
    ind["holders_captive"] = captive.astype(float).where(known)
    ind["quadrant"] = [
        QUADRANTS[(bool(u), bool(k))] if ok else None for u, k, ok in zip(unsus, captive, known, strict=True)
    ]
    ind["country"] = code
    return ind


def _bloc_aggregate_shares(panel: Panel, bloc_ind: pd.DataFrame, members: tuple[str, ...]) -> pd.DataFrame:
    """Debt-weighted member average for holder shares the bloc itself does not report."""
    out = bloc_ind.copy()
    for col in ("foreign_share", "central_bank_share", "avg_maturity_years", "bill_share", "linker_share"):
        if col in out and out[col].notna().sum() > 4:
            continue
        num = pd.Series(0.0, index=out.index)
        den = pd.Series(0.0, index=out.index)
        for m in members:
            try:
                mi = compute_country(panel, m)
            except ValueError:
                continue
            w = mi["debt_level"].reindex(out.index)
            v = mi[col].reindex(out.index) if col in mi else pd.Series(np.nan, index=out.index)
            ok = w.notna() & v.notna()
            num[ok] += (w * v)[ok]
            den[ok] += w[ok]
        agg = (num / den.where(den > 0)).where(den > 0)
        out[col] = out[col].combine_first(agg) if col in out else agg
    return out


def _finish_bloc(panel: Panel, code: str, ind: pd.DataFrame) -> pd.DataFrame:
    """Fill the bloc's holder shares from members and recompute what depends on them."""
    uni = load_universe()
    cfg = load_indicator_config()
    ind = _bloc_aggregate_shares(panel, ind, uni[code].members)
    c = _country_frame(panel, code)
    ctx = Ctx(country=code, c=c, ind=ind, country_cfg=uni[code], cfg=cfg)
    for name in ("domestic_private_share", "captivity_score", "cb_holdings_change_4q", "issuance_shortening"):
        ind[name] = REGISTRY[name].fn(ctx).reindex(c.index)
        ctx.ind = ind
    q = cfg.quadrant
    unsus = (ind["forward_r_minus_g_5y"] > q["unsustainable"]["forward_r_minus_g_5y_gt"]) & (
        ind["primary_balance_gdp"] < q["unsustainable"]["primary_balance_gdp_lt"]
    )
    captive = ind["captivity_score"] > q["captive"]["captivity_score_gt"]
    known = (
        ind["forward_r_minus_g_5y"].notna()
        & ind["primary_balance_gdp"].notna()
        & ind["captivity_score"].notna()
    )
    ind["trajectory_unsustainable"] = unsus.astype(float).where(known)
    ind["holders_captive"] = captive.astype(float).where(known)
    ind["quadrant"] = [
        QUADRANTS[(bool(u), bool(k))] if ok else None for u, k, ok in zip(unsus, captive, known, strict=True)
    ]
    return ind


def transitions_for(ind: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col, label in (("quadrant", "quadrant"), ("stage_estimate", "stage")):
        s = ind[col]
        prev = s.shift(1)
        for ts in ind.index:
            a, b = prev.get(ts), s.get(ts)
            if (
                a is None
                or b is None
                or (isinstance(a, float) and np.isnan(a))
                or (isinstance(b, float) and np.isnan(b))
            ):
                continue
            if a != b:
                rows.append(
                    {
                        "country": ind["country"].iloc[0],
                        "quarter": ts.date(),
                        "kind": label,
                        "from": a,
                        "to": b,
                    }
                )
    return pd.DataFrame(rows, columns=["country", "quarter", "kind", "from", "to"])


def compute_all(
    panel: Panel | None = None, write: bool = True
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    panel = panel or load_panel()
    uni = load_universe()
    frames, trans = [], []
    for code in uni.all_codes:
        try:
            ind = compute_country(panel, code)
            if uni[code].is_bloc:
                ind = _finish_bloc(panel, code, ind)
        except ValueError as e:
            log.warning("%s", e)
            continue
        ind.index.name = "quarter"
        frames.append(ind.reset_index().set_index(["country", "quarter"]))
        trans.append(transitions_for(ind))
    all_ind = pd.concat(frames).sort_index()
    transitions = pd.concat(trans, ignore_index=True) if trans else pd.DataFrame()
    latest = latest_table(all_ind)
    if write:
        all_ind.to_csv(INDICATORS_PATH)
        latest.to_csv(LATEST_PATH, index=False)
        transitions.to_csv(TRANSITIONS_PATH, index=False)
        log.info("indicators: %s rows -> %s", len(all_ind), INDICATORS_PATH)
    return all_ind, latest, transitions


def last_complete_quarter(today: date | None = None) -> pd.Timestamp:
    """The most recent quarter that has fully elapsed."""
    t = pd.Timestamp(today or date.today())
    return (t.to_period("Q") - 1).end_time.normalize()


def latest_table(all_ind: pd.DataFrame, stale_quarters: int = 2) -> pd.DataFrame:
    """One row per (country, indicator): latest non-null value, its quarter, 1y/5y change.
    ``stale_quarters`` counts how far the latest value lags the last complete quarter."""
    uni = load_universe()
    ref_q = last_complete_quarter()
    shown = [n for n, m in REGISTRY.items() if not m.helper] + ["stage_estimate", "captivity_score"]
    shown = list(dict.fromkeys(shown))
    rows = []
    for code in uni.all_codes:
        if code not in all_ind.index.get_level_values(0):
            continue
        df = all_ind.loc[code]
        last_q = ref_q
        for name in shown + ["quadrant", "trajectory_unsustainable", "holders_captive"]:
            if name not in df.columns:
                continue
            s = df[name].dropna()
            if s.empty:
                rows.append(
                    {
                        "country": code,
                        "indicator": name,
                        "quarter": None,
                        "value": None,
                        "chg_1y": None,
                        "chg_5y": None,
                        "stale_quarters": None,
                    }
                )
                continue
            q = s.index[-1]
            v = s.iloc[-1]
            age = max(0, (last_q.to_period("Q") - q.to_period("Q")).n)
            numeric = name not in ("quadrant",)
            rows.append(
                {
                    "country": code,
                    "indicator": name,
                    "quarter": q.date(),
                    "value": v,
                    "chg_1y": (v - s.get(q - pd.offsets.QuarterEnd(4), np.nan)) if numeric else None,
                    "chg_5y": (v - s.get(q - pd.offsets.QuarterEnd(20), np.nan)) if numeric else None,
                    "stale_quarters": age,
                }
            )
    out = pd.DataFrame(rows)
    out["tier"] = out["country"].map(lambda c: uni[c].tier)
    out["applies"] = [
        indicator_applies(n, uni[c]) for n, c in zip(out["indicator"], out["country"], strict=True)
    ]
    return out


def latest_wide(latest: pd.DataFrame, core_only: bool = True) -> pd.DataFrame:
    """Country x indicator matrix of latest values, for printing and the report."""
    df = latest[latest["tier"] == "core"] if core_only else latest
    return df.pivot(index="country", columns="indicator", values="value")

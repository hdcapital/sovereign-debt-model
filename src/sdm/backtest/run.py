"""Backtest against data/events.csv.

Tests (numbered as in the brief):
1. Lead time: for each indicator with a threshold, how many quarters before each event it
   first crossed the warning side (within a 20-quarter window) and stayed there.
2. Quadrant: was the country in unsustainable_free before the crisis events, and how often
   did unsustainable_free persist for more than 12 quarters with no event (false positives).
3. Forward returns: real 10-year bond returns and local-currency gold returns over the next
   5 and 10 years by quadrant, with an OLS regression on quadrant dummies.
4. Forward r: RMSE of forward_r_5y vs the realised r_effective five years later, against
   the naive forecast (current r).
Outputs: reports/backtest/*.csv and reports/backtest/BACKTEST.md.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

from sdm.config import load_indicator_config
from sdm.indicators.compute import INDICATORS_PATH
from sdm.paths import EVENTS, REPORTS

log = logging.getLogger(__name__)

OUT = REPORTS / "backtest"
LEAD_WINDOW = 20  # quarters before the event in which a crossing counts as a warning
FALSE_POSITIVE_QUARTERS = 12  # > 3 years of unsustainable_free with no event


@dataclass
class BacktestResult:
    lead_times: pd.DataFrame
    lead_summary: pd.DataFrame
    quadrant_before: pd.DataFrame
    false_positives: pd.DataFrame
    forward_returns: pd.DataFrame
    regression: pd.DataFrame
    forward_r: pd.DataFrame
    coverage: pd.DataFrame


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    ind = pd.read_csv(INDICATORS_PATH, index_col=[0, 1], parse_dates=[1])
    events = pd.read_csv(EVENTS, parse_dates=["crisis_start", "crisis_end"])
    return ind, events


def _quarter(ts: pd.Timestamp) -> pd.Timestamp:
    return ts.to_period("Q").end_time.normalize()


# ----------------------------------------------------------------------------- 1. lead times


def warning_side(s: pd.Series, value: float, direction: str) -> pd.Series:
    return (s > value) if direction == "above" else (s < value)


def lead_times(ind: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    thresholds = load_indicator_config().thresholds
    rows = []
    for ev in events.itertuples(index=False):
        if ev.country not in ind.index.get_level_values(0):
            continue
        df = ind.loc[ev.country]
        q0 = _quarter(ev.crisis_start)
        window = df.loc[q0 - pd.offsets.QuarterEnd(LEAD_WINDOW) : q0 - pd.offsets.QuarterEnd(1)]
        for name, (val, direction) in thresholds.items():
            if name not in df.columns:
                continue
            s = window[name].dropna()
            if s.empty:
                rows.append(
                    {
                        "event_id": ev.event_id,
                        "country": ev.country,
                        "type": ev.type,
                        "indicator": name,
                        "available": False,
                        "warned": None,
                        "lead_quarters": None,
                        "share_of_window_on_warning_side": None,
                    }
                )
                continue
            w = warning_side(s, val, direction)
            first = w[w].index.min() if w.any() else None
            rows.append(
                {
                    "event_id": ev.event_id,
                    "country": ev.country,
                    "type": ev.type,
                    "indicator": name,
                    "available": True,
                    "warned": bool(w.any()),
                    "lead_quarters": int((q0.to_period("Q") - first.to_period("Q")).n)
                    if first is not None
                    else None,
                    "share_of_window_on_warning_side": float(w.mean()),
                }
            )
    return pd.DataFrame(rows)


def lead_summary(lt: pd.DataFrame) -> pd.DataFrame:
    avail = lt[lt["available"]]
    g = avail.groupby("indicator")
    out = pd.DataFrame(
        {
            "events_with_data": g.size(),
            "warned_share": g["warned"].mean(),
            "median_lead_quarters": g["lead_quarters"].median(),
            "mean_share_on_warning_side": g["share_of_window_on_warning_side"].mean(),
        }
    )
    return out.sort_values("warned_share", ascending=False)


# ----------------------------------------------------------------------------- 2. quadrant


def quadrant_before_events(ind: pd.DataFrame, events: pd.DataFrame, lookback: int = 8) -> pd.DataFrame:
    rows = []
    for ev in events.itertuples(index=False):
        if ev.country not in ind.index.get_level_values(0):
            continue
        df = ind.loc[ev.country]
        q0 = _quarter(ev.crisis_start)
        window = df.loc[q0 - pd.offsets.QuarterEnd(lookback) : q0 - pd.offsets.QuarterEnd(1)]
        qs = window["quadrant"].dropna()
        st = window["stage_estimate"].dropna()
        rows.append(
            {
                "event_id": ev.event_id,
                "country": ev.country,
                "type": ev.type,
                "quarters_with_quadrant": len(qs),
                "share_unsustainable_free": float((qs == "unsustainable_free").mean()) if len(qs) else None,
                "share_unsustainable": float(qs.str.startswith("unsustainable").mean()) if len(qs) else None,
                "modal_quadrant": qs.mode().iloc[0] if len(qs) else None,
                "max_stage": float(st.max()) if len(st) else None,
                "captivity_score": float(window["captivity_score"].dropna().iloc[-1])
                if window["captivity_score"].notna().any()
                else None,
            }
        )
    return pd.DataFrame(rows)


def false_positives(ind: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    """Runs of unsustainable_free longer than FALSE_POSITIVE_QUARTERS with no event within
    the run or the following 8 quarters."""
    rows = []
    for cc in ind.index.get_level_values(0).unique():
        s = ind.loc[cc]["quadrant"]
        flag = (s == "unsustainable_free").astype(int)
        run_id = (flag != flag.shift()).cumsum()
        for _, g in flag[flag == 1].groupby(run_id[flag == 1]):
            start, end = g.index.min(), g.index.max()
            n = len(g)
            ev = events[
                (events["country"] == cc)
                & (events["crisis_start"] >= start)
                & (events["crisis_start"] <= end + pd.offsets.QuarterEnd(8))
            ]
            rows.append(
                {
                    "country": cc,
                    "start": start.date(),
                    "end": end.date(),
                    "quarters": n,
                    "event_followed": bool(len(ev)),
                    "event_id": ev["event_id"].iloc[0] if len(ev) else None,
                    "false_positive": n > FALSE_POSITIVE_QUARTERS and not len(ev),
                }
            )
    return pd.DataFrame(
        rows, columns=["country", "start", "end", "quarters", "event_followed", "event_id", "false_positive"]
    )


# ----------------------------------------------------------------------------- 3. forward returns


def bond_return_approx(y: pd.Series, horizon_q: int, duration_years: float = 8.0) -> pd.Series:
    """Cumulative nominal return of rolling 10-year bonds over ``horizon_q`` quarters from
    quarterly yields: carry y/4 minus duration times the yield change each quarter (plus
    convexity). Annualised percent."""
    y = y / 100.0
    dy = y.diff()
    q_ret = y.shift(1) / 4.0 - duration_years * dy + 0.5 * (duration_years**2) * dy**2
    cum = (1 + q_ret).rolling(horizon_q).apply(np.prod, raw=True)
    ann = cum ** (4.0 / horizon_q) - 1.0
    return ann.shift(-horizon_q) * 100.0  # aligned to the start of the window


def forward_returns(ind: pd.DataFrame, panel_yields: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cc in ind.index.get_level_values(0).unique():
        df = ind.loc[cc]
        if cc not in panel_yields.index.get_level_values(0):
            continue
        p = panel_yields.loc[cc]
        y10 = p["yield_10y"].reindex(df.index) if "yield_10y" in p else pd.Series(np.nan, index=df.index)
        cpi = p["cpi_index"].reindex(df.index) if "cpi_index" in p else pd.Series(np.nan, index=df.index)
        gold = df["gold_local_ccy"] if "gold_local_ccy" in df else pd.Series(np.nan, index=df.index)
        for h in (20, 40):
            infl = ((cpi.shift(-h) / cpi) ** (4.0 / h) - 1.0) * 100.0
            bond = bond_return_approx(y10, h)
            gold_ret = ((gold.shift(-h) / gold) ** (4.0 / h) - 1.0) * 100.0
            tmp = pd.DataFrame(
                {
                    "country": cc,
                    "quarter": df.index,
                    "horizon_years": h // 4,
                    "quadrant": df["quadrant"].values,
                    "captivity_score": df["captivity_score"].values,
                    "real_bond_return_ann": (bond - infl).values,
                    "real_gold_return_ann": (gold_ret - infl).values,
                    "gold_minus_bond_ann": (gold_ret - bond).values,
                }
            )
            rows.append(tmp)
    out = pd.concat(rows, ignore_index=True)
    return out.dropna(subset=["quadrant"])


def regress_on_quadrant(fr: pd.DataFrame) -> pd.DataFrame:
    """Mean forward returns by quadrant and horizon, with an OLS on quadrant dummies
    (base: sustainable_captive) and Newey-West style caveat: observations overlap, so the
    t-statistics are optimistic and are reported with the overlap-adjusted effective n."""
    rows = []
    for h, g in fr.groupby("horizon_years"):
        for col in ("real_bond_return_ann", "real_gold_return_ann", "gold_minus_bond_ann"):
            sub = g.dropna(subset=[col])
            if len(sub) < 40:
                continue
            means = sub.groupby("quadrant")[col].agg(["mean", "median", "count"])
            dummies = pd.get_dummies(sub["quadrant"], drop_first=False).astype(float)
            base = "sustainable_captive" if "sustainable_captive" in dummies else dummies.columns[0]
            x = dummies.drop(columns=[base])
            x.insert(0, "const", 1.0)
            yv = sub[col].values
            beta, *_ = np.linalg.lstsq(x.values, yv, rcond=None)
            resid = yv - x.values @ beta
            n, k = x.shape
            eff_n = max(n / (h * 4), k + 1)  # overlapping windows: one independent obs per horizon
            sigma2 = resid @ resid / (n - k)
            cov = sigma2 * np.linalg.pinv(x.values.T @ x.values) * (n / eff_n)
            se = np.sqrt(np.diag(cov))
            for name, b_, s_ in zip(x.columns, beta, se, strict=True):
                rows.append(
                    {
                        "horizon_years": h,
                        "return": col,
                        "term": name,
                        "coef": b_,
                        "se_overlap_adj": s_,
                        "t": b_ / s_ if s_ > 0 else np.nan,
                        "n": n,
                        "effective_n": round(eff_n, 1),
                    }
                )
            for q, r in means.iterrows():
                rows.append(
                    {
                        "horizon_years": h,
                        "return": col,
                        "term": f"mean:{q}",
                        "coef": r["mean"],
                        "se_overlap_adj": np.nan,
                        "t": np.nan,
                        "n": int(r["count"]),
                        "effective_n": np.nan,
                    }
                )
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------- 4. forward r


def forward_r_accuracy(ind: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cc in ind.index.get_level_values(0).unique():
        df = ind.loc[cc]
        if "forward_r_5y" not in df or "r_effective" not in df:
            continue
        realised = df["r_effective"].shift(-20)
        fwd, now = df["forward_r_5y"], df["r_effective"]
        m = realised.notna() & fwd.notna() & now.notna()
        if m.sum() < 8:
            continue
        rows.append(
            {
                "country": cc,
                "n": int(m.sum()),
                "rmse_forward_r": float(np.sqrt(((fwd - realised)[m] ** 2).mean())),
                "rmse_current_r": float(np.sqrt(((now - realised)[m] ** 2).mean())),
                "bias_forward_r": float((fwd - realised)[m].mean()),
                "bias_current_r": float((now - realised)[m].mean()),
            }
        )
    out = pd.DataFrame(rows)
    if len(out):
        out["forward_better"] = out["rmse_forward_r"] < out["rmse_current_r"]
    return out


# ----------------------------------------------------------------------------- driver


def coverage(ind: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    rows = []
    key = [
        "debt_gdp",
        "primary_balance_gdp",
        "r_effective",
        "g_nominal",
        "captivity_score",
        "forward_r_minus_g_5y",
        "quadrant",
    ]
    for ev in events.itertuples(index=False):
        if ev.country not in ind.index.get_level_values(0):
            rows.append({"event_id": ev.event_id, **{k: False for k in key}})
            continue
        df = ind.loc[ev.country]
        q0 = _quarter(ev.crisis_start)
        window = df.loc[q0 - pd.offsets.QuarterEnd(8) : q0]
        rows.append(
            {
                "event_id": ev.event_id,
                **{k: bool(window[k].notna().any()) if k in window else False for k in key},
            }
        )
    return pd.DataFrame(rows)


def run_backtest(write: bool = True) -> BacktestResult:
    from sdm.indicators.panel import load_panel

    ind, events = load_inputs()
    panel = load_panel().values
    lt = lead_times(ind, events)
    res = BacktestResult(
        lead_times=lt,
        lead_summary=lead_summary(lt),
        quadrant_before=quadrant_before_events(ind, events),
        false_positives=false_positives(ind, events),
        forward_returns=forward_returns(ind, panel),
        regression=pd.DataFrame(),
        forward_r=forward_r_accuracy(ind),
        coverage=coverage(ind, events),
    )
    res.regression = regress_on_quadrant(res.forward_returns)
    if write:
        OUT.mkdir(parents=True, exist_ok=True)
        for name in (
            "lead_times",
            "lead_summary",
            "quadrant_before",
            "false_positives",
            "regression",
            "forward_r",
            "coverage",
        ):
            getattr(res, name).to_csv(OUT / f"{name}.csv", index=name == "lead_summary")
        res.forward_returns.to_csv(OUT / "forward_returns.csv", index=False)
        from sdm.backtest.report import write_backtest_md

        write_backtest_md(res, events)
    return res

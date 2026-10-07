"""Monthly check: after a data update and indicator recompute, decide whether anything
warrants an email: a quadrant or stage transition in the latest quarter, or any core
indicator that moved more than ``sigma_threshold`` standard deviations (of its own monthly
changes over the last ``sigma_window_months``) since the previous run."""

from __future__ import annotations

import json
import logging
from datetime import date

import pandas as pd

from sdm.config import load_indicator_config, load_universe
from sdm.indicators import blocks  # noqa: F401
from sdm.indicators.compute import INDICATORS_PATH, LATEST_PATH, TRANSITIONS_PATH, last_complete_quarter
from sdm.indicators.registry import REGISTRY
from sdm.paths import DATA

log = logging.getLogger(__name__)

SNAPSHOT = DATA / "monthly_snapshot.json"


def current_values() -> dict[str, float]:
    latest = pd.read_csv(LATEST_PATH)
    core = latest[latest["tier"] == "core"]
    out = {}
    for r in core.itertuples(index=False):
        v = pd.to_numeric(r.value, errors="coerce")
        if pd.notna(v):
            out[f"{r.country}.{r.indicator}"] = float(v)
    return out


def sigma_moves(previous: dict[str, float], current: dict[str, float]) -> list[dict]:
    cfg = load_indicator_config().raw["monthly_alert"]
    thr, window_m = float(cfg["sigma_threshold"]), int(cfg["sigma_window_months"])
    ind = pd.read_csv(INDICATORS_PATH, index_col=[0, 1], parse_dates=[1])
    shown = [n for n, m in REGISTRY.items() if not m.helper]
    moves = []
    for key, now in current.items():
        if key not in previous:
            continue
        cc, name = key.split(".", 1)
        if name not in shown or cc not in ind.index.get_level_values(0):
            continue
        s = ind.loc[cc][name].dropna().tail(window_m // 3)
        if len(s) < 8:
            continue
        sigma = float(s.diff().std()) / (3**0.5)  # quarterly change sigma -> monthly
        if sigma <= 0:
            continue
        z = (now - previous[key]) / sigma
        if abs(z) >= thr:
            moves.append(
                {"country": cc, "indicator": name, "from": previous[key], "to": now, "z": round(float(z), 2)}
            )
    return sorted(moves, key=lambda m: -abs(m["z"]))


def new_transitions(since: date) -> pd.DataFrame:
    if not TRANSITIONS_PATH.exists():
        return pd.DataFrame()
    t = pd.read_csv(TRANSITIONS_PATH)
    uni = load_universe()
    t = t[t["country"].isin(uni.core)]
    return t[pd.to_datetime(t["quarter"]).dt.date >= since]


def run_monthly() -> tuple[bool, str, dict]:
    """Return (should_email, html_body, details). Also refresh the snapshot."""
    current = current_values()
    previous: dict = {}
    prev_date = None
    if SNAPSHOT.exists():
        snap = json.loads(SNAPSHOT.read_text())
        previous, prev_date = snap.get("values", {}), snap.get("date")
    since = (
        pd.Timestamp(prev_date).date()
        if prev_date
        else (last_complete_quarter() - pd.offsets.QuarterEnd(1)).date()
    )
    trans = new_transitions(since)
    moves = sigma_moves(previous, current) if previous else []
    fire = bool(len(trans)) or bool(moves)
    rows_t = "".join(
        f"<tr><td>{r.quarter}</td><td>{r.country}</td><td>{r.kind}</td><td>{r['from']}</td><td>{r['to']}</td></tr>"
        for _, r in trans.iterrows()
    )
    rows_m = "".join(
        f"<tr><td>{m['country']}</td><td>{m['indicator']}</td><td>{m['from']:.2f}</td><td>{m['to']:.2f}</td><td>{m['z']:+.1f}σ</td></tr>"
        for m in moves
    )
    body = f"""<html><body style="font:15px/1.5 system-ui,sans-serif;max-width:720px">
<h2>Sovereign Debt Monitor: monthly check, {date.today().isoformat()}</h2>
<p>This mail is sent only when a transition or a move larger than the configured threshold fired.</p>
<h3>Transitions since {since}</h3>
{('<table border="0" cellpadding="4"><tr><th>quarter</th><th>market</th><th>kind</th><th>from</th><th>to</th></tr>' + rows_t + "</table>") if rows_t else "<p>none</p>"}
<h3>Moves above threshold since the previous check{f" ({prev_date})" if prev_date else ""}</h3>
{('<table border="0" cellpadding="4"><tr><th>market</th><th>indicator</th><th>from</th><th>to</th><th>z</th></tr>' + rows_m + "</table>") if rows_m else "<p>none</p>"}
<p>Dashboard and indicator table attached.</p></body></html>"""
    SNAPSHOT.write_text(json.dumps({"date": date.today().isoformat(), "values": current}, indent=0))
    return fire, body, {"transitions": len(trans), "moves": moves[:20], "since": str(since)}

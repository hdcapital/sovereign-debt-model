"""Regression tests for the data gaps found in the first live quarterly report (2026-Q3)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import sdm.indicators.blocks as b
from sdm.config import load_indicator_config, load_universe
from sdm.indicators.panel import Panel, fill_structural, native_yoy, to_quarterly
from sdm.indicators.registry import Ctx

FIX = Path(__file__).parent / "fixtures"
Q = pd.date_range("2018-03-31", periods=36, freq="QE")


def _panel(rows: dict[tuple[str, str], pd.Series]) -> Panel:
    wide = pd.DataFrame({k: v for k, v in rows.items()})
    vals = wide.stack(level=0, future_stack=True).swaplevel().sort_index()
    vals.index.names = ["country", "quarter"]
    return Panel(values=vals, sources=vals.map(lambda _: "TEST"))


def test_global_gold_attaches_even_when_country_column_exists() -> None:
    from sdm.indicators.compute import _country_frame

    gold = pd.Series(np.linspace(1000, 2000, len(Q)), index=Q)
    fx = pd.Series(150.0, index=Q)
    p = _panel({("XX", "gold_usd"): gold, ("JP", "fx_lcu_per_usd"): fx})
    frame = _country_frame(p, "JP")
    assert frame["gold_usd"].notna().all()
    ctx = Ctx("JP", frame, pd.DataFrame(index=frame.index), load_universe()["JP"], load_indicator_config())
    local = b.gold_local_ccy(ctx)
    assert abs(local.iloc[-1] - 2000 * 150) < 1e-6


def test_single_snapshot_is_one_quarter_not_a_year() -> None:
    s = pd.Series([13.3], index=pd.to_datetime(["2026-10-06"]))
    q = to_quarterly(s, "rate")
    assert list(q.index) == [pd.Timestamp("2026-12-31")]


def test_structural_series_interpolate_inside_and_carry_at_most_n() -> None:
    idx = pd.to_datetime(["2020-12-31", "2022-12-31"])
    s = pd.Series([6.0, 8.0], index=idx)
    out, tag = fill_structural(s, pd.Series("MANUAL", index=idx), carry=4)
    assert abs(out.loc["2021-12-31"] - 7.0) < 1e-9 and tag.loc["2021-12-31"] == "MANUAL+interp"
    assert out.loc["2023-12-31"] == 8.0 and tag.loc["2023-12-31"] == "MANUAL+carry"
    assert pd.Timestamp("2024-03-31") not in out.index
    assert tag.loc["2022-12-31"] == "MANUAL"


def test_native_yoy_compares_same_month() -> None:
    months = pd.date_range("2025-01-31", "2026-08-31", freq="ME")
    vals = pd.Series(np.arange(len(months), dtype=float) + 100.0, index=months)
    vals.loc["2025-09-30"] = 90.0  # a September dip that the old quarter-on-quarter maths would pick up
    yoy = native_yoy(vals)
    expected = (vals.loc["2026-08-31"] / vals.loc["2025-08-31"] - 1) * 100
    assert abs(yoy.loc["2026-08-31"] - expected) < 1e-9


def test_mof_bill_share_uses_jgbs_plus_financing_bills() -> None:
    from sdm.collect.sources.mof_jp import MofJpCollector

    class Replay:
        def get_bytes(self, url: str, params: dict | None = None) -> bytes:
            return (FIX / "mof_suii.xls").read_bytes()

    c = MofJpCollector(http=Replay())
    c.cache_raw = lambda *a, **k: None  # type: ignore[method-assign]
    df = c._suii()
    share = (df["short"] / df["total"] * 100).iloc[-1]
    assert 5 < share < 20  # was ~46% when the total matched the FILP sub-total row


def test_captivity_requires_core_components() -> None:
    uni = load_universe()
    c = pd.DataFrame(
        {"foreign_share": 30.0, "cb_gov_share": 15.0, "bill_share": 20.0, "linker_share": 7.0}, index=Q
    )
    c["avg_maturity_years"] = [6.0] * 20 + [np.nan] * 16
    ctx = Ctx("US", c, pd.DataFrame(index=Q), uni["US"], load_indicator_config())
    for name in (
        "foreign_share",
        "central_bank_share",
        "avg_maturity_years",
        "bill_share",
        "linker_share",
        "net_foreign_asset_position_gdp",
    ):
        ctx.ind[name] = b.__dict__[name](ctx)
    score = b.captivity_score(ctx)
    assert score.iloc[:20].notna().all() and score.iloc[20:].isna().all()


def test_union_member_term_premium_uses_bloc_two_year() -> None:
    uni = load_universe()
    c = pd.DataFrame({"yield_10y": 3.6, "policy_rate": 2.0}, index=Q)
    bloc = pd.DataFrame({"yield_2y": 3.0}, index=Q)
    ctx = Ctx("IT", c, pd.DataFrame(index=Q), uni["IT"], load_indicator_config(), bloc=bloc)
    ctx.ind["policy_rate"] = c["policy_rate"]
    assert abs(b.term_premium_proxy(ctx).iloc[-1] - 0.6) < 1e-9


def test_anchor_has_no_spread_to_itself() -> None:
    from sdm.indicators.applicability import indicator_applies, is_known_gap

    uni = load_universe()
    assert not indicator_applies("spread_to_anchor_bp", uni["DE"])
    assert indicator_applies("spread_to_anchor_bp", uni["FR"])
    assert is_known_gap("CH", "breakeven_10y") and not is_known_gap("US", "breakeven_10y")


def test_latest_table_stops_at_last_complete_quarter() -> None:
    from sdm.indicators.compute import latest_table

    idx = pd.MultiIndex.from_product(
        [["US"], pd.date_range("2025-03-31", "2026-12-31", freq="QE")], names=["country", "quarter"]
    )
    ind = pd.DataFrame({"debt_gdp": np.arange(len(idx), dtype=float)}, index=idx)
    lt = latest_table(ind, through=pd.Timestamp("2026-09-30"))
    row = lt[(lt["country"] == "US") & (lt["indicator"] == "debt_gdp")].iloc[0]
    assert str(row["quarter"]) == "2026-09-30"

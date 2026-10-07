from __future__ import annotations

import numpy as np
import pandas as pd

from sdm.config import load_stage_rules
from sdm.indicators.stages import estimate_stages

IDX = pd.date_range("2018-03-31", periods=16, freq="QE")


def _frame(**cols: list[float] | float) -> pd.DataFrame:
    data = {}
    for k, v in cols.items():
        data[k] = v if isinstance(v, list) else [v] * len(IDX)
    return pd.DataFrame(data, index=IDX)


def test_stage_zero_needs_persistent_deficit() -> None:
    rules = load_stage_rules()
    ind = _frame(primary_balance_gdp=-2.0)
    out = estimate_stages(ind, "sovereign_float", rules)
    assert np.isnan(out["stage_estimate"].iloc[5])  # not enough history for 12q lookback
    assert out["stage_estimate"].iloc[-1] == 0.0
    ind = _frame(primary_balance_gdp=1.0)
    out = estimate_stages(ind, "sovereign_float", rules)
    assert out["stage_estimate"].iloc[-1] == 0.0  # fuel absent, nothing fires, stage 0 by default
    assert out["stage_0"].iloc[-1] == 0.0


def test_stage_one_requires_stage_zero() -> None:
    rules = load_stage_rules()
    ind = _frame(primary_balance_gdp=1.0, forward_r_minus_g_5y=1.0, avg_coupon_gap=1.0)
    assert estimate_stages(ind, "sovereign_float", rules)["stage_estimate"].iloc[-1] == 0.0
    ind = _frame(primary_balance_gdp=-2.0, forward_r_minus_g_5y=1.0, avg_coupon_gap=1.0)
    assert estimate_stages(ind, "sovereign_float", rules)["stage_estimate"].iloc[-1] == 1.0


def test_stage_four_fiscal_dominance() -> None:
    rules = load_stage_rules()
    ind = _frame(
        primary_balance_gdp=-3.0,
        forward_r_minus_g_5y=1.0,
        avg_coupon_gap=1.0,
        policy_rate_minus_inflation=-2.0,
        inflation_minus_target=2.0,
        policy_rate=4.0,
        cb_holdings_change_4q=2.0,
        cb_balance_sheet_growth_minus_g=5.0,
    )
    out = estimate_stages(ind, "sovereign_float", rules)
    assert out["stage_estimate"].iloc[-1] == 4.0


def test_union_member_stage_three_uses_spread() -> None:
    rules = load_stage_rules()
    spread = [100.0] * 10 + [200.0] * 6
    ind = _frame(
        primary_balance_gdp=-2.0, forward_r_minus_g_5y=1.0, avg_coupon_gap=0.5, spread_to_anchor_bp=spread
    )
    out = estimate_stages(ind, "currency_union_member", rules)
    assert out["stage_estimate"].iloc[11] == 3.0  # spread +100bp over the last 4 quarters
    assert out["stage_estimate"].iloc[-1] == 1.0  # the rise has stopped; back to stage 1
    out_float = estimate_stages(ind, "sovereign_float", rules)
    assert out_float["stage_estimate"].iloc[11] == 1.0  # a floater ignores the spread

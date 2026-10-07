"""Hand-computed fixtures for the indicator functions, plus the debt-dynamics identity
checked against IMF numbers for one country-year."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import sdm.indicators.blocks as b
from sdm.config import load_indicator_config, load_universe
from sdm.indicators.registry import Ctx

Q = pd.date_range("2015-03-31", periods=48, freq="QE")  # 12 years


def make_ctx(country: str = "US", **concepts: pd.Series | float | list[float]) -> Ctx:
    c = pd.DataFrame(index=Q)
    for k, v in concepts.items():
        c[k] = v if isinstance(v, pd.Series) else (v if isinstance(v, list) else [v] * len(Q))
    uni = load_universe()
    return Ctx(
        country=country, c=c, ind=pd.DataFrame(index=Q), country_cfg=uni[country], cfg=load_indicator_config()
    )


def run(ctx: Ctx, *names: str) -> pd.DataFrame:
    for name in names:
        ctx.ind[name] = b.__dict__[name](ctx)
    return ctx.ind


def test_r_effective_is_interest_over_lagged_debt() -> None:
    # debt 1000 flat, interest 10 per quarter -> 40 per year -> r = 4%
    ctx = make_ctx(gg_debt_lcu=1000.0, gg_interest_lcu=10.0, ngdp_lcu=250.0)
    ind = run(ctx, "ngdp_4q", "debt_gdp", "debt_level", "interest_4q", "r_effective")
    assert abs(ind["r_effective"].iloc[-1] - 4.0) < 1e-9
    assert abs(ind["debt_gdp"].iloc[-1] - 100.0) < 1e-9  # 1000 / (4 x 250)


def test_g_nominal_and_r_minus_g() -> None:
    gdp = pd.Series([100.0 * 1.01**i for i in range(len(Q))], index=Q)  # 1% per quarter
    ctx = make_ctx(ngdp_lcu=gdp, gg_debt_lcu=1000.0, gg_interest_lcu=12.5)
    ind = run(
        ctx, "ngdp_4q", "debt_gdp", "debt_level", "interest_4q", "r_effective", "g_nominal", "r_minus_g"
    )
    assert abs(ind["g_nominal"].iloc[-1] - (1.01**4 - 1) * 100) < 1e-6
    assert abs(ind["r_minus_g"].iloc[-1] - (5.0 - (1.01**4 - 1) * 100)) < 1e-6


def test_primary_balance_from_net_lending_and_interest() -> None:
    # net lending -5 per quarter, interest 10 per quarter, GDP 250 per quarter
    ctx = make_ctx(gg_net_lending_lcu=-5.0, gg_interest_lcu=10.0, ngdp_lcu=250.0, gg_debt_lcu=1000.0)
    ind = run(ctx, "ngdp_4q", "debt_gdp", "debt_level", "interest_4q", "primary_balance_gdp")
    # (-20 + 40) / 1000 = +2% of GDP
    assert abs(ind["primary_balance_gdp"].iloc[-1] - 2.0) < 1e-9


def test_debt_dynamics_identity_against_imf_italy_2023() -> None:
    """IMF WEO (Oct 2024) Italy: debt/GDP 2022 = 138.3, 2023 = 134.6; primary balance 2023
    = -3.4% of GDP; effective rate ~3.1%; nominal GDP growth 2023 = 6.2%. The identity
    gives (3.1 - 6.2)/100 x 138.3 - (-3.4) = -0.9; actual change -3.7; residual -2.8
    (stock-flow adjustment). We check the identity term to the rounding of the inputs."""
    r, g, d_prev, pb = 3.1, 6.2, 138.3, -3.4
    pred = (r - g) / 100.0 * d_prev - pb
    assert abs(pred - (-0.887)) < 0.01
    ctx = make_ctx("IT")
    ctx.ind["r_minus_g"] = pd.Series(r - g, index=Q)
    ctx.ind["debt_gdp"] = pd.Series([d_prev] * 4 + [134.6] * (len(Q) - 4), index=Q)
    ctx.ind["primary_balance_gdp"] = pd.Series(pb, index=Q)
    dyn = b.debt_dynamics(ctx)
    assert abs(dyn.iloc[4] - pred) < 1e-9
    ctx.ind["debt_dynamics"] = dyn
    resid = b.debt_dynamics_residual(ctx)
    assert abs(resid.iloc[4] - ((134.6 - 138.3) - pred)) < 1e-9


def test_marginal_yield_blend_and_coupon_gap() -> None:
    ctx = make_ctx(yield_2y=4.0, yield_10y=5.0)
    ctx.ind["r_effective"] = pd.Series(3.0, index=Q)
    ind = run(ctx, "marginal_yield", "avg_coupon_gap")
    assert abs(ind["marginal_yield"].iloc[-1] - (0.4 * 4.0 + 0.6 * 5.0)) < 1e-9
    assert abs(ind["avg_coupon_gap"].iloc[-1] - 1.6) < 1e-9


def test_forward_r_converges_towards_marginal_yield() -> None:
    # r0 = 2, yield 5, maturity 5y, balanced primary budget, debt 100% -> after 5y well above 2, below 5
    path = b._forward_r_path(2.0, 5.0, 5.0, 0.0, 100.0, 5)
    assert 3.0 < path[-1] < 5.0
    assert all(np.diff(path) > 0)
    # a bigger deficit (more issuance at the marginal yield) converges faster
    faster = b._forward_r_path(2.0, 5.0, 5.0, -5.0, 100.0, 5)
    assert faster[-1] > path[-1]
    # no maturity -> no estimate
    assert np.isnan(b._forward_r_path(2.0, 5.0, np.nan, 0.0, 100.0, 5)[-1])


def test_debt_projection_rises_when_r_exceeds_g_with_deficit() -> None:
    ctx = make_ctx(avg_maturity_years=6.0)
    ctx.ind["r_effective"] = pd.Series(4.0, index=Q)
    ctx.ind["marginal_yield"] = pd.Series(4.0, index=Q)
    ctx.ind["primary_balance_gdp"] = pd.Series(-2.0, index=Q)
    ctx.ind["debt_gdp"] = pd.Series(100.0, index=Q)
    ctx.ind["g_trend"] = pd.Series(3.0, index=Q)
    proj = b.debt_gdp_projection_10y(ctx)
    # d_{t+1} = d (1.04/1.03) + 2 each year, ten times
    d = 100.0
    for _ in range(10):
        d = d * 1.04 / 1.03 + 2.0
    assert abs(proj.iloc[-1] - d) < 1e-6


def test_captivity_score_weights_and_control_credit() -> None:
    cfg = load_indicator_config().captivity
    # Japan-like: 13% foreign, 46% central bank, 9y maturity, NIIP +70%, 10% bills, 0 linkers
    ctx = make_ctx(
        "JP",
        foreign_share=13.0,
        cb_gov_share=46.0,
        avg_maturity_years=9.0,
        niip_gdp=70.0,
        bill_share=10.0,
        linker_share=0.0,
    )
    ind = run(
        ctx,
        "foreign_share",
        "central_bank_share",
        "avg_maturity_years",
        "bill_share",
        "linker_share",
        "net_foreign_asset_position_gdp",
        "captivity_score",
    )
    sc = cfg.scale
    expected = (
        cfg.weights["domestic_share"]
        * (87 - sc["domestic_share"][0])
        / (sc["domestic_share"][1] - sc["domestic_share"][0])
        * 100
        + cfg.weights["central_bank_share"] * min(100, 46 / sc["central_bank_share"][1] * 100)
        + cfg.weights["avg_maturity"] * (9 - 2) / 13 * 100
        + cfg.weights["reserve_niip"] * min(100, (70 + 100) / 150 * 100)
        + cfg.weights["bill_linker_share"] * (100 - 10 / 50 * 100)
    )
    assert abs(ind["captivity_score"].iloc[-1] - expected) < 1e-6
    # same numbers for a union member: central-bank component gets half credit
    ctx_it = make_ctx(
        "IT",
        foreign_share=13.0,
        cb_gov_share=46.0,
        avg_maturity_years=9.0,
        niip_gdp=70.0,
        bill_share=10.0,
        linker_share=0.0,
    )
    ind_it = run(
        ctx_it,
        "foreign_share",
        "central_bank_share",
        "avg_maturity_years",
        "bill_share",
        "linker_share",
        "net_foreign_asset_position_gdp",
        "captivity_score",
    )
    assert ind_it["captivity_score"].iloc[-1] < ind["captivity_score"].iloc[-1]
    # the US gets the reserve-currency score regardless of NIIP
    ctx_us = make_ctx(
        "US",
        foreign_share=30.0,
        cb_gov_share=15.0,
        avg_maturity_years=6.0,
        niip_gdp=-80.0,
        bill_share=22.0,
        linker_share=7.0,
    )
    ind_us = run(
        ctx_us,
        "foreign_share",
        "central_bank_share",
        "avg_maturity_years",
        "bill_share",
        "linker_share",
        "net_foreign_asset_position_gdp",
        "captivity_score",
    )
    assert ind_us["captivity_score"].iloc[-1] > 0


def test_fx_and_gold_pressure_gauges() -> None:
    fx = pd.Series([100.0] * 44 + [120.0] * 4, index=Q)  # local currency weakens 20% vs USD in the last year
    gold = pd.Series(2000.0, index=Q)
    ctx = make_ctx("JP", fx_lcu_per_usd=fx, gold_usd=gold)
    ind = run(ctx, "fx_vs_usd_12m", "gold_local_ccy", "gold_local_ccy_12m", "gold_local_record")
    assert abs(ind["fx_vs_usd_12m"].iloc[-1] - (100 / 120 - 1) * 100) < 1e-9
    assert abs(ind["gold_local_ccy_12m"].iloc[-1] - 20.0) < 1e-9
    assert ind["gold_local_record"].iloc[-1] == 1.0


def test_real_policy_rate_and_target_gap() -> None:
    cpi = pd.Series([100.0 * 1.0075**i for i in range(len(Q))], index=Q)  # ~3% a year
    ctx = make_ctx("GB", cpi_index=cpi, policy_rate=2.0)
    ind = run(ctx, "cpi_yoy", "policy_rate", "inflation_minus_target", "policy_rate_minus_inflation")
    infl = (1.0075**4 - 1) * 100
    assert abs(ind["policy_rate_minus_inflation"].iloc[-1] - (2.0 - infl)) < 1e-9
    assert abs(ind["inflation_minus_target"].iloc[-1] - (infl - 2.0)) < 1e-9


def test_union_member_spread_uses_anchor() -> None:
    uni = load_universe()
    c = pd.DataFrame({"yield_10y": [4.0] * len(Q)}, index=Q)
    anchor = pd.DataFrame({"yield_10y": [2.5] * len(Q)}, index=Q)
    ctx = Ctx("IT", c, pd.DataFrame(index=Q), uni["IT"], load_indicator_config(), anchor=anchor)
    assert abs(b.spread_to_anchor_bp(ctx).iloc[-1] - 150.0) < 1e-9


@pytest.mark.parametrize("name", ["debt_gdp", "primary_balance_gdp", "captivity_score", "forward_r_5y"])
def test_docstrings_explain_what_it_leads_to(name: str) -> None:
    from sdm.indicators.registry import REGISTRY

    assert len(REGISTRY[name].doc) > 80

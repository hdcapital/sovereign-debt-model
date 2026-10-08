"""The indicators. Each docstring says why it matters and what it leads to, in the terms of
docs/MODEL.md; the dashboard shows that text next to the chart."""

from __future__ import annotations

import numpy as np
import pandas as pd

from sdm.indicators.registry import Ctx, diff_n, indicator, pct_change_n, rolling_sum4

# ----------------------------------------------------------------------------- helpers


@indicator("helper", "LCU bn", helper=True)
def ngdp_4q(ctx: Ctx) -> pd.Series:
    """Nominal GDP over the trailing four quarters. The denominator for every ratio."""
    return rolling_sum4(ctx.col("ngdp_lcu"))


@indicator("helper", "LCU bn", helper=True)
def debt_level(ctx: Ctx) -> pd.Series:
    """Gross government debt in local currency: the reported level where a source gives it,
    otherwise debt/GDP times trailing GDP."""
    lvl = ctx.col("gg_debt_lcu").combine_first(ctx.col("cg_debt_lcu"))
    derived = debt_gdp(ctx) / 100.0 * ngdp_4q(ctx)
    return lvl.combine_first(derived)


@indicator("helper", "LCU bn", helper=True)
def interest_4q(ctx: Ctx) -> pd.Series:
    """Interest paid over the trailing four quarters, in local currency."""
    flow = ctx.col("gg_interest_lcu").combine_first(ctx.col("cg_interest_lcu"))
    from_flow = rolling_sum4(flow)
    # ratios are % of the period's own GDP (annual IMF or quarterly Eurostat); average over 4 quarters
    from_ratio = ctx.col("gg_interest_gdp").rolling(4, min_periods=4).mean() / 100.0 * ctx.i("ngdp_4q")
    return from_flow.combine_first(from_ratio)


@indicator("helper", "%", helper=True)
def cpi_yoy(ctx: Ctx) -> pd.Series:
    """Consumer price inflation, year on year."""
    native = ctx.col("cpi_yoy")  # computed at monthly frequency in the panel, IMF annual as fallback
    return native.combine_first(pct_change_n(ctx.col("cpi_index"), 4))


@indicator("helper", "%", helper=True)
def policy_rate(ctx: Ctx) -> pd.Series:
    """Policy rate; a union member inherits the bloc's rate."""
    own = ctx.col("policy_rate")
    if own.notna().any() or ctx.bloc is None:
        return own
    return ctx.bloc["policy_rate"].reindex(ctx.c.index) if "policy_rate" in ctx.bloc else own


@indicator("helper", "%", helper=True)
def inflation_minus_target(ctx: Ctx) -> pd.Series:
    """Inflation gap to the central bank's target. Positive and persistent while the bank
    stops hiking is the stage-3 tell."""
    tgt = ctx.country_cfg.inflation_target
    if tgt is None:
        return pd.Series(np.nan, index=ctx.c.index)
    return ctx.i("cpi_yoy") - tgt


# ----------------------------------------------------------------------------- trajectory


@indicator("trajectory", "% GDP")
def debt_gdp(ctx: Ctx) -> pd.Series:
    """Gross general government debt as a share of GDP. The size of the stock the transfer
    has to act on. On its own it predicts almost nothing: Russia defaulted near 55%, Japan
    carries over 200% with no crisis. It matters through the arithmetic, (r minus g) times
    this number, and through who holds it."""
    reported = ctx.col("gg_debt_gdp")
    derived = ctx.col("gg_debt_lcu").combine_first(ctx.col("cg_debt_lcu")) / ngdp_4q(ctx) * 100.0
    return reported.combine_first(derived)


@indicator("trajectory", "% GDP")
def primary_balance_gdp(ctx: Ctx) -> pd.Series:
    """Budget balance excluding interest, trailing four quarters, surplus positive. This is
    the fuel. A primary deficit that does not close in expansions means the debt ratio
    rises whenever r exceeds g, with no further decisions required."""
    n4 = ctx.i("ngdp_4q")
    interest = ctx.i("interest_4q")
    nl_lcu = rolling_sum4(ctx.col("gg_net_lending_lcu"))
    nl_from_cg = rolling_sum4(ctx.col("cg_receipts_lcu") - ctx.col("cg_outlays_lcu"))
    nl_from_ratio = ctx.col("gg_net_lending_gdp").rolling(4, min_periods=4).mean() / 100.0 * n4
    net_lending = nl_lcu.combine_first(nl_from_cg).combine_first(nl_from_ratio)
    computed = (net_lending + interest) / n4 * 100.0
    reported = ctx.col("gg_primary_balance_gdp")
    return computed.combine_first(reported)


@indicator("trajectory", "%")
def r_effective(ctx: Ctx) -> pd.Series:
    """Average interest rate actually paid on the stock: interest over four quarters divided
    by the debt a year earlier. It lags the market because most debt is fixed coupon, so
    today's r understates where the interest bill is going."""
    return ctx.i("interest_4q") / ctx.i("debt_level").shift(4) * 100.0


@indicator("trajectory", "%")
def g_nominal(ctx: Ctx) -> pd.Series:
    """Nominal GDP growth over four quarters. Inflation counts in full, which is exactly why
    the repression exit works: it raises g without raising the coupon on existing debt."""
    n4 = ctx.i("ngdp_4q")
    g = pct_change_n(n4, 4)
    return g.combine_first(ctx.col("ngdp_growth"))


@indicator("trajectory", "pp")
def r_minus_g(ctx: Ctx) -> pd.Series:
    """The snowball term. Positive with a primary deficit means the debt ratio rises on
    autopilot; the trigger stage is r crossing above g."""
    return ctx.i("r_effective") - ctx.i("g_nominal")


@indicator("trajectory", "pp of GDP")
def debt_dynamics(ctx: Ctx) -> pd.Series:
    """The identity's predicted annual change in debt/GDP: (r minus g) times last year's
    ratio minus the primary balance. Compare with the actual change; a large residual means
    off-budget financing or valuation effects are moving the stock."""
    d4 = ctx.i("debt_gdp").shift(4)
    return (ctx.i("r_minus_g") / 100.0) * d4 - ctx.i("primary_balance_gdp")


@indicator("trajectory", "pp of GDP")
def debt_dynamics_residual(ctx: Ctx) -> pd.Series:
    """Actual change in debt/GDP minus the identity's prediction (the stock-flow
    adjustment). Persistently positive means the headline deficit understates the borrowing."""
    actual = diff_n(ctx.i("debt_gdp"), 4)
    return actual - ctx.i("debt_dynamics")


@indicator("trajectory", "%")
def marginal_yield(ctx: Ctx) -> pd.Series:
    """What new borrowing costs: a blend of the 2-year and 10-year yields weighted by the
    typical issuance mix. Where r is heading as the stock rolls over."""
    w = ctx.cfg.raw["trajectory"]["marginal_yield"]["default_weights"]
    y10 = ctx.col("yield_10y")
    y2 = ctx.col("yield_2y").combine_first(ctx.col("yield_5y"))
    blend = w["y2"] * y2 + w["y10"] * y10
    return blend.combine_first(y10)


@indicator("trajectory", "pp")
def avg_coupon_gap(ctx: Ctx) -> pd.Series:
    """Marginal yield minus the average rate paid. Positive means interest cost is already
    committed: the bill keeps rising with no further shock as old coupons roll into new."""
    return ctx.i("marginal_yield") - ctx.i("r_effective")


def _forward_r_path(r0: float, y: float, m: float, pb: float, d: float, years: int) -> list[float]:
    """Roll 1/m of the stock per year into yield y, plus deficit issuance at y."""
    if any(np.isnan(v) for v in (r0, y, m, pb, d)) or m <= 0 or d <= 0:
        return [np.nan] * years
    rho = 1.0 / m
    r = r0
    path = []
    for _ in range(years):
        nu = max(0.0, -pb / d) + r / 100.0  # total borrowing as share of stock
        r = ((1 - rho) * r + (rho + nu) * y) / (1 + nu)
        path.append(r)
    return path


@indicator("trajectory", "%")
def forward_r_5y(ctx: Ctx) -> pd.Series:
    """The average rate the stock will carry in five years if yields stay where they are and
    issuance continues on the current pattern: each year 1/average-maturity of the stock
    reprices at the marginal yield, plus all deficit issuance. More informative than
    today's r, which is a lagging average."""
    horizon = int(ctx.cfg.raw["trajectory"]["forward_r"]["horizon_years"])
    r0, y = ctx.i("r_effective"), ctx.i("marginal_yield")
    m = ctx.i("avg_maturity_years").combine_first(ctx.col("avg_maturity_years"))
    pb, d = ctx.i("primary_balance_gdp"), ctx.i("debt_gdp")
    out = pd.Series(np.nan, index=ctx.c.index)
    for t in ctx.c.index:
        path = _forward_r_path(
            r0.get(t, np.nan),
            y.get(t, np.nan),
            m.get(t, np.nan),
            pb.get(t, np.nan),
            d.get(t, np.nan),
            horizon,
        )
        out[t] = path[-1]
    return out


@indicator("trajectory", "%")
def g_trend(ctx: Ctx) -> pd.Series:
    """Trend nominal growth: ten-year trailing mean of four-quarter growth. What g is likely
    to be over the horizon of the forward-r projection."""
    w = int(ctx.cfg.raw["trajectory"]["g_trend"]["window_quarters"])
    return ctx.i("g_nominal").rolling(w, min_periods=max(8, w // 4)).mean()


@indicator("trajectory", "pp")
def forward_r_minus_g_5y(ctx: Ctx) -> pd.Series:
    """The model's trajectory variable: forward r minus trend g. Above zero together with a
    primary deficit, the path is unsustainable and the only questions left are who pays and
    through which channel."""
    return ctx.i("forward_r_5y") - ctx.i("g_trend")


@indicator("trajectory", "% GDP")
def debt_gdp_projection_10y(ctx: Ctx) -> pd.Series:
    """Debt/GDP ten years out under forward r, trend g and the current primary balance:
    the identity iterated annually. Where the stock goes if nothing changes."""
    horizon = int(ctx.cfg.raw["trajectory"]["debt_projection"]["horizon_years"])
    r0, y = ctx.i("r_effective"), ctx.i("marginal_yield")
    m = ctx.i("avg_maturity_years").combine_first(ctx.col("avg_maturity_years"))
    pb, d0, g = ctx.i("primary_balance_gdp"), ctx.i("debt_gdp"), ctx.i("g_trend")
    out = pd.Series(np.nan, index=ctx.c.index)
    for t in ctx.c.index:
        path = _forward_r_path(
            r0.get(t, np.nan),
            y.get(t, np.nan),
            m.get(t, np.nan),
            pb.get(t, np.nan),
            d0.get(t, np.nan),
            horizon,
        )
        d, gg, p = d0.get(t, np.nan), g.get(t, np.nan), pb.get(t, np.nan)
        if np.isnan(d) or np.isnan(gg) or np.isnan(p) or np.isnan(path[0]):
            continue
        for r in path:
            d = d * (1 + r / 100.0) / (1 + gg / 100.0) - p
        out[t] = d
    return out


# ----------------------------------------------------------------------------- captivity


@indicator("captivity", "% of debt")
def foreign_share(ctx: Ctx) -> pd.Series:
    """Share of the debt held by non-residents. These are the holders who can leave within a
    cycle; a high share is what turns an unsustainable path into a crisis rather than a grind."""
    share = ctx.col("foreign_share")
    derived = ctx.col("foreign_gov_holdings_lcu") / ctx.i("debt_level") * 100.0
    return share.combine_first(derived)


@indicator("captivity", "% of debt")
def central_bank_share(ctx: Ctx) -> pd.Series:
    """Share of the debt held by the central bank, the ultimate captive buyer. A rising share
    after hikes have paused is the fiscal-dominance tell. For a union member this is the ECB's
    holdings, and the captivity score discounts it because that bid is political, not structural."""
    share = ctx.col("cb_gov_share")
    derived = ctx.col("cb_gov_holdings_lcu") / ctx.i("debt_level") * 100.0
    return share.combine_first(derived)


@indicator("captivity", "% of debt")
def domestic_private_share(ctx: Ctx) -> pd.Series:
    """Residual: debt held by domestic banks, pensions, insurers and households. The pool
    that financial repression acts on."""
    return 100.0 - ctx.i("foreign_share") - ctx.i("central_bank_share")


@indicator("captivity", "years")
def avg_maturity_years(ctx: Ctx) -> pd.Series:
    """Average remaining maturity of the stock. Short debt means holders are effectively
    free (they are repaid soon and choose whether to come back) and that r converges to the
    market yield fast."""
    return ctx.col("avg_maturity_years")


@indicator("captivity", "% of marketable debt")
def bill_share(ctx: Ctx) -> pd.Series:
    """Bills under one year as a share of marketable debt. A treasury that shifts into bills
    is dodging the term premium; it also hands the holders a quick exit."""
    share = ctx.col("bill_share")
    derived = ctx.col("bills_outstanding_lcu") / ctx.col("marketable_debt_lcu") * 100.0
    return share.combine_first(derived)


@indicator("captivity", "% of marketable debt")
def linker_share(ctx: Ctx) -> pd.Series:
    """Inflation-linked share. Linkers cannot be inflated away, so a large share narrows the
    repression exit and pushes the adjustment onto taxes or the currency."""
    share = ctx.col("linker_share")
    derived = ctx.col("linkers_outstanding_lcu") / ctx.col("marketable_debt_lcu") * 100.0
    return share.combine_first(derived)


@indicator("captivity", "ratio")
def household_savings_to_debt(ctx: Ctx) -> pd.Series:
    """Household financial assets relative to government debt: the size of the domestic pool
    that can be made to hold the paper. Japan's large ratio is why its grind has lasted."""
    return ctx.col("household_fin_assets_lcu") / ctx.i("debt_level")


@indicator("captivity", "% GDP")
def net_foreign_asset_position_gdp(ctx: Ctx) -> pd.Series:
    """Net international investment position over GDP. Creditor nations fund themselves;
    debtor nations depend on the foreigners who can leave."""
    niip = ctx.col("niip_gdp")
    # the US series arrives as a USD level; convert when the magnitude says so
    if niip.abs().max() > 1000:
        niip = niip / ctx.i("ngdp_4q") * 100.0
    return niip


def _scale(s: pd.Series, lo: float, hi: float) -> pd.Series:
    return ((s - lo) / (hi - lo) * 100.0).clip(0, 100)


@indicator("captivity", "0-100")
def captivity_score(ctx: Ctx) -> pd.Series:
    """Composite captivity, 0 to 100, with weights from config/indicators.yaml: domestic
    share, central-bank share (scaled by who controls the central bank), average maturity,
    reserve-currency status or NIIP, and the short/linked share entered negatively. It does
    not make debt sustainable; it decides whether an unsustainable path resolves as a decades
    long repression grind (captive) or a crisis within a cycle (free)."""
    cap = ctx.cfg.captivity
    sc = cap.scale
    domestic = 100.0 - ctx.i("foreign_share")
    cb = ctx.i("central_bank_share") * cap.central_bank_control_credit[ctx.country_cfg.central_bank_control]
    mat = ctx.i("avg_maturity_years")
    if ctx.country_cfg.reserve_currency:
        reserve = pd.Series(cap.reserve_currency_score, index=ctx.c.index)
    elif getattr(ctx.country_cfg, "reserve_currency_partial", False):
        reserve = pd.Series(cap.reserve_currency_partial_score, index=ctx.c.index)
    else:
        reserve = _scale(ctx.i("net_foreign_asset_position_gdp"), *sc["reserve_niip"])
    short = ctx.i("bill_share").fillna(0) + ctx.i("linker_share").fillna(0)
    short = short.where(ctx.i("bill_share").notna() | ctx.i("linker_share").notna())
    comps = pd.DataFrame(
        {
            "domestic_share": _scale(domestic, *sc["domestic_share"]),
            "central_bank_share": _scale(cb, *sc["central_bank_share"]),
            "avg_maturity": _scale(mat, *sc["avg_maturity"]),
            "reserve_niip": reserve,
            "bill_linker_share": 100.0 - _scale(short, *sc["bill_linker_share"]),
        }
    )
    w = pd.Series(cap.weights)
    avail = comps.notna()
    weighted = (comps.fillna(0) * w).sum(axis=1)
    wsum = (avail * w).sum(axis=1)
    score = weighted / wsum.where(wsum > 0)
    # require the core components (holders, central bank, maturity); bill/linker share is optional because
    # several markets publish none. Without this rule the score jumps when a component appears or vanishes.
    core = comps[["domestic_share", "central_bank_share", "avg_maturity"]].notna().all(axis=1)
    return score.where(core)


# ----------------------------------------------------------------------------- pressure


@indicator("pressure", "pp")
def term_premium_proxy(ctx: Ctx) -> pd.Series:
    """Compensation the market demands for holding duration. Kim-Wright estimate where it
    exists (US), otherwise 10-year minus 2-year yield, labelled a proxy. Rising term premium
    is the pricing stage: the market starting to charge for the risk."""
    tp = ctx.col("term_premium_10y")
    short = ctx.col("yield_2y")
    if ctx.bloc is not None and "yield_2y" in ctx.bloc:
        # union members: the bloc's AAA 2-year is the expected policy path, the same leg the bloc uses
        short = short.combine_first(ctx.bloc["yield_2y"].reindex(ctx.c.index))
    short = short.combine_first(ctx.col("yield_3m")).combine_first(ctx.i("policy_rate"))
    proxy = ctx.col("yield_10y") - short
    return tp.combine_first(proxy)


@indicator("pressure", "%")
def breakeven_10y(ctx: Ctx) -> pd.Series:
    """Ten-year inflation breakeven: nominal minus real yield. The market pricing the
    inflation exit."""
    be = ctx.col("breakeven_10y")
    derived = ctx.col("yield_10y") - ctx.col("real_yield_10y")
    return be.combine_first(derived)


@indicator("pressure", "pp")
def policy_rate_minus_inflation(ctx: Ctx) -> pd.Series:
    """Real policy rate. Negative and widening while inflation is above target is the bank
    choosing the bond market over the currency: stages 3 and 4."""
    return ctx.i("policy_rate") - ctx.i("cpi_yoy")


@indicator("pressure", "% GDP")
def cb_balance_sheet_gdp(ctx: Ctx) -> pd.Series:
    """Central bank total assets over GDP. A union member shows the Eurosystem's sheet."""
    assets = ctx.col("cb_total_assets_lcu")
    gdp = ctx.i("ngdp_4q")
    if assets.notna().sum() == 0 and ctx.bloc is not None and "cb_total_assets_lcu" in ctx.bloc:
        return pd.Series(np.nan, index=ctx.c.index)
    return assets / gdp * 100.0


@indicator("pressure", "pp")
def cb_balance_sheet_growth_minus_g(ctx: Ctx) -> pd.Series:
    """Four-quarter growth of the central bank's balance sheet minus nominal GDP growth.
    Above zero is monetisation: the sheet outgrowing the economy."""
    return pct_change_n(ctx.col("cb_total_assets_lcu"), 4) - ctx.i("g_nominal")


@indicator("pressure", "pp of debt")
def cb_holdings_change_4q(ctx: Ctx) -> pd.Series:
    """Change in the central bank's share of the debt over four quarters. Rising after the
    hiking cycle has stalled is fiscal dominance in progress."""
    return diff_n(ctx.i("central_bank_share"), 4)


@indicator("pressure", "pp of marketable debt")
def issuance_shortening(ctx: Ctx) -> pd.Series:
    """Change in the bill share over eight quarters. The treasury retreating from the long
    end because the long end is charging for the risk."""
    w = int(ctx.cfg.raw["pressure"]["issuance_shortening_window_quarters"])
    return diff_n(ctx.i("bill_share"), w)


@indicator("pressure", "%")
def fx_vs_usd_12m(ctx: Ctx) -> pd.Series:
    """Twelve-month change of the currency against the dollar, appreciation positive. For a
    floater the currency is the pressure gauge: a yield can be pinned, a currency cannot
    be pinned without reserves. Blank for the US and for union members (see spread)."""
    fx = ctx.col("fx_lcu_per_usd")
    return (fx.shift(4) / fx - 1.0) * 100.0


@indicator("pressure", "%")
def fx_broad_reer_12m(ctx: Ctx) -> pd.Series:
    """Twelve-month change in the broad real effective exchange rate. The currency gauge
    net of partners' inflation, and the one that works for the US."""
    return pct_change_n(ctx.col("reer_broad"), 4)


@indicator("helper", "LCU/oz", helper=True)
def gold_local_ccy(ctx: Ctx) -> pd.Series:
    """Gold priced in local currency."""
    gold = ctx.col("gold_usd")
    fx = ctx.col("fx_lcu_per_usd")
    if ctx.country_cfg.currency == "USD":
        return gold
    if ctx.bloc is not None and "fx_lcu_per_usd" in ctx.bloc:
        # union members price gold in the shared currency; their own pre-union rate only fills earlier years
        fx = ctx.bloc["fx_lcu_per_usd"].reindex(ctx.c.index).combine_first(fx)
    return gold * fx


@indicator("pressure", "%")
def gold_local_ccy_12m(ctx: Ctx) -> pd.Series:
    """Twelve-month change in gold priced in local currency. Hard-asset flight shows up here
    before it shows up in the yield, because the yield can be managed and gold cannot."""
    return pct_change_n(ctx.i("gold_local_ccy"), 4)


@indicator("pressure", "flag")
def gold_local_record(ctx: Ctx) -> pd.Series:
    """1 when gold in local currency is at an all-time high. The stage-5 tell."""
    g = ctx.i("gold_local_ccy")
    return (g >= g.cummax()).astype(float).where(g.notna())


@indicator("pressure", "ratio (inverted)")
def auction_tail(ctx: Ctx) -> pd.Series:
    """Auction demand proxy: the trailing two-year average bid-to-cover minus the current
    value, so a rising number means weaker demand (true tails need when-issued yields, which
    are not free). Dealers demanding a concession to absorb supply is the pricing stage."""
    btc = ctx.col("auction_bid_to_cover")
    return btc.rolling(8, min_periods=4).mean() - btc


@indicator("pressure", "bp")
def spread_to_anchor_bp(ctx: Ctx) -> pd.Series:
    """Ten-year spread to the anchor (Bund for euro members, Treasuries for pegs). For a
    country that cannot print, this replaces the currency as the pressure gauge: a widening
    spread with a central bank announcing a backstop is stage 3; a blow-out is stage 5."""
    if ctx.anchor is None or "yield_10y" not in ctx.anchor:
        return pd.Series(np.nan, index=ctx.c.index)
    return (ctx.col("yield_10y") - ctx.anchor["yield_10y"].reindex(ctx.c.index)) * 100.0


@indicator("pressure", "% GDP")
def target2_balance_gdp(ctx: Ctx) -> pd.Series:
    """TARGET2 balance over GDP (liability negative). Deposit flight inside the union shows
    up here when it cannot show up in the exchange rate."""
    return ctx.col("target2_balance_lcu") / ctx.i("ngdp_4q") * 100.0


@indicator("pressure", "flag")
def ecb_backstop_active(ctx: Ctx) -> pd.Series:
    """1 while an ECB sovereign backstop is in force (SMP, OMT, PEPP flexibility, TPI)."""
    own = ctx.col("ecb_backstop_active")
    if own.notna().any():
        return own.ffill()
    if ctx.bloc is not None and "ecb_backstop_active" in ctx.bloc:
        return ctx.bloc["ecb_backstop_active"].reindex(ctx.c.index).ffill()
    return pd.Series(np.nan, index=ctx.c.index)


@indicator("pressure", "%")
def fx_reserves_12m(ctx: Ctx) -> pd.Series:
    """Twelve-month change in official reserves. A peg under attack burns these first."""
    return pct_change_n(ctx.col("fx_reserves_usd"), 4)


@indicator("pressure", "%")
def interest_to_revenue(ctx: Ctx) -> pd.Series:
    """Interest as a share of government revenue. The political temperature: the share of
    the budget already spoken for by past borrowing."""
    rep = ctx.col("interest_to_revenue")
    rev = ctx.col("gg_revenue_gdp").rolling(4, min_periods=4).mean() / 100.0 * ctx.i("ngdp_4q")
    rev = rev.combine_first(rolling_sum4(ctx.col("cg_receipts_lcu")))
    return rep.combine_first(ctx.i("interest_4q") / rev * 100.0)

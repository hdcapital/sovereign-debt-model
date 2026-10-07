"""Which indicators apply to which country. Non-applicable indicators are neither shown on
the dashboard nor listed as data issues."""

from __future__ import annotations

from typing import Any

UNION_ONLY = {"spread_to_anchor_bp", "target2_balance_gdp", "ecb_backstop_active"}
FLOATER_ONLY = {"fx_vs_usd_12m"}
PEG_ONLY = {"fx_reserves_12m"}
US_ONLY = {"auction_tail"}


def indicator_applies(name: str, ccfg: Any) -> bool:
    regime = ccfg.monetary_regime
    if name in UNION_ONLY:
        return (
            regime == "currency_union_member"
            or getattr(ccfg, "is_bloc", False)
            and name == "ecb_backstop_active"
        )
    if name in FLOATER_ONLY:
        return regime in ("sovereign_float", "pegged") and ccfg.currency != "USD"
    if name in PEG_ONLY:
        return regime == "pegged" or ccfg.tier == "backtest_only"
    if name in US_ONLY:
        return ccfg.code == "US"
    if name == "spread_to_anchor_bp":
        return regime in ("currency_union_member", "pegged")
    return True

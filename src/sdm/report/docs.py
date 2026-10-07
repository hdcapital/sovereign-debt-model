"""Regenerate docs/INDICATORS.md from the indicator registry and config, so the table can
never drift from the code."""

from __future__ import annotations

from sdm.config import load_indicator_config
from sdm.indicators import blocks  # noqa: F401
from sdm.indicators.registry import REGISTRY
from sdm.paths import DOCS

STAGE_USE = {
    "debt_gdp": "context",
    "primary_balance_gdp": "stage 0, quadrant",
    "r_effective": "trajectory",
    "g_nominal": "trajectory",
    "r_minus_g": "stage 1",
    "debt_dynamics": "diagnostic",
    "debt_dynamics_residual": "diagnostic",
    "marginal_yield": "stage 1",
    "avg_coupon_gap": "stage 1",
    "forward_r_5y": "quadrant",
    "g_trend": "quadrant",
    "forward_r_minus_g_5y": "quadrant, stage 1",
    "debt_gdp_projection_10y": "narrative",
    "foreign_share": "captivity",
    "central_bank_share": "captivity, stage 4",
    "domestic_private_share": "captivity",
    "avg_maturity_years": "captivity, forward r",
    "bill_share": "captivity, stage 4",
    "linker_share": "captivity",
    "household_savings_to_debt": "captivity",
    "net_foreign_asset_position_gdp": "captivity",
    "captivity_score": "quadrant",
    "term_premium_proxy": "stage 2",
    "breakeven_10y": "stage 2",
    "policy_rate_minus_inflation": "stages 3-4",
    "cb_balance_sheet_gdp": "stage 4",
    "cb_balance_sheet_growth_minus_g": "stage 4",
    "cb_holdings_change_4q": "stages 3-4",
    "issuance_shortening": "stage 4",
    "fx_vs_usd_12m": "stage 5",
    "fx_broad_reer_12m": "stage 5",
    "gold_local_ccy_12m": "stage 5",
    "gold_local_record": "stage 5",
    "auction_tail": "stage 2",
    "spread_to_anchor_bp": "stages 3, 5 (union)",
    "target2_balance_gdp": "stage 5 (union)",
    "ecb_backstop_active": "stage 3 (union)",
    "fx_reserves_12m": "stage 5 (peg)",
    "interest_to_revenue": "context",
}
SOURCES = {
    "debt_gdp": "BIS total credit; Eurostat; IMF GDD; FRED; ONS",
    "primary_balance_gdp": "ONS, Fiscal Data/NIPA, ECB GFS, Eurostat; IMF GDD `pb` annual",
    "r_effective": "interest: Fiscal Data, ONS, ECB D41, IMF `ie`; debt level",
    "g_nominal": "FRED, ONS, ECB MNA, OECD via FRED; IMF/WB annual",
    "marginal_yield": "FRED, BoE, MoF, RBA, BoC, SNB, ECB IRS",
    "avg_maturity_years": "DMO snapshot; manual (approximate)",
    "foreign_share": "Arslanalp-Tsuda to 2016; FRED FDHBFIN; manual after",
    "central_bank_share": "Arslanalp-Tsuda; FRED FDHBFRBN; ECB PSPP cumulative; manual",
    "bill_share": "Fiscal Data MSPD, MoF suii, ECB SEC, DMO",
    "linker_share": "Fiscal Data MSPD, DMO",
    "household_savings_to_debt": "FRED Z.1 (US only)",
    "net_foreign_asset_position_gdp": "FRED IIP (US only)",
    "term_premium_proxy": "FRED THREEFYTP10 (US); 10y-2y elsewhere",
    "breakeven_10y": "FRED, BoE; 10y minus real yield (AU, CA)",
    "policy_rate_minus_inflation": "BIS CBPOL, BIS long CPI",
    "cb_balance_sheet_gdp": "BIS CBTA; FRED; RBA; SNB; ECB ILM",
    "fx_vs_usd_12m": "FRED, BIS XRU",
    "fx_broad_reer_12m": "BIS EER",
    "gold_local_ccy_12m": "LBMA mirror / World Bank / Yahoo x FX",
    "auction_tail": "Fiscal Data auctions (bid-to-cover)",
    "spread_to_anchor_bp": "ECB IRS vs DE",
    "target2_balance_gdp": "ECB TGB",
    "ecb_backstop_active": "manual flag",
    "fx_reserves_12m": "World Bank",
    "interest_to_revenue": "World Bank; IMF `rev`",
}


def write_indicators_md() -> str:
    cfg = load_indicator_config()
    th = cfg.thresholds
    lines = [
        "# Indicators",
        "",
        "Generated from the indicator registry (`src/sdm/indicators/blocks.py`) and `config/indicators.yaml` by",
        "`python -m sdm.cli docs`; edit the docstrings and config, not this file. All quarterly, per country, full history.",
        "Direction `above`/`below` is the warning side of the threshold. Detailed source priority: `docs/DATA_SOURCES.md`.",
        "",
    ]
    for block in ("trajectory", "captivity", "pressure"):
        lines += [
            f"## {block.title()} block",
            "",
            "| Indicator | Units | Formula / definition | Source series | Threshold | Informs | What it leads to |",
            "|---|---|---|---|---|---|---|",
        ]
        for name, m in REGISTRY.items():
            if m.block != block or m.helper:
                continue
            t = th.get(name)
            thr = f"{t[1]} {t[0]:g}" if t else "—"
            doc = m.doc.replace("\n", " ").replace("|", "/")
            first, _, rest = doc.partition(". ")
            lines.append(
                f"| `{name}` | {m.units} | {first}. | {SOURCES.get(name, 'derived')} | {thr} | {STAGE_USE.get(name, '')} | {rest} |"
            )
        lines.append("")
    q = cfg.quadrant
    lines += [
        "## Quadrant and stage",
        "",
        "| Output | Definition |",
        "|---|---|",
        f"| `trajectory_unsustainable` | `forward_r_minus_g_5y > {q['unsustainable']['forward_r_minus_g_5y_gt']}` and `primary_balance_gdp < {q['unsustainable']['primary_balance_gdp_lt']}` |",
        f"| `holders_captive` | `captivity_score > {q['captive']['captivity_score_gt']}` |",
        "| `quadrant` | sustainable_captive / sustainable_free / unsustainable_captive / unsustainable_free |",
        "| `stage_estimate` | highest firing stage in `config/stages.yaml` with prerequisites; undefined until 12 quarters of primary balance exist |",
        "| transitions | any quarter where `quadrant` or `stage_estimate` changes; `data/clean/transitions.csv` |",
        "",
        "## Captivity score weights",
        "",
        "| Component | Weight | Scaled from | to |",
        "|---|---|---|---|",
    ]
    for k, w in cfg.captivity.weights.items():
        lo, hi = cfg.captivity.scale[k]
        lines.append(f"| {k} | {w:.2f} | {lo:g} | {hi:g} |")
    lines += [
        "",
        f"Central-bank component credit by control: {cfg.captivity.central_bank_control_credit}. "
        f"Reserve-currency score {cfg.captivity.reserve_currency_score:g} (US), partial {cfg.captivity.reserve_currency_partial_score:g} (euro area).",
        "",
    ]
    out = DOCS / "INDICATORS.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return str(out)

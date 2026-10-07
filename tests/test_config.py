"""Configuration is the model's tunable surface; these tests make a bad edit fail fast."""

from __future__ import annotations

import csv
from datetime import date

import pytest

from sdm.config import (
    ConfigError,
    load_indicator_config,
    load_report_config,
    load_stage_rules,
    load_universe,
    stage_indicator_names,
)
from sdm.paths import EVENTS


def test_universe_tiers_match_brief() -> None:
    uni = load_universe()
    assert uni.core == ("US", "GB", "JP", "AU", "CA", "CH", "EA", "DE", "FR", "IT", "NL")
    assert set(uni.backtest_only) == {"AR", "TR", "RU", "BR", "MX", "GR", "SE"}
    assert {e.id for e in uni.episodes} == {"IT-1992", "CA-1994", "GB-1976"}


def test_every_country_has_a_regime_and_gauge() -> None:
    uni = load_universe()
    for c in uni.countries.values():
        assert c.monetary_regime in {
            "sovereign_float",
            "currency_union_member",
            "pegged",
            "dollarised",
        }
        assert c.pressure_gauge in {"currency", "spread"}


def test_union_members_are_consistent() -> None:
    uni = load_universe()
    for code in ("DE", "FR", "IT", "NL", "GR"):
        c = uni[code]
        assert c.monetary_regime == "currency_union_member"
        assert c.central_bank_control == "shared"
        assert c.anchor == "DE"
        assert c.bloc == "EA"
        assert c.pressure_gauge == "spread"
    assert uni["EA"].is_bloc
    assert uni["EA"].monetary_regime == "sovereign_float"


def test_regime_history_is_used_for_backtest_dates() -> None:
    uni = load_universe()
    assert uni["IT"].regime_at(date(1992, 6, 30)) == "pegged"
    assert uni["IT"].regime_at(date(1994, 6, 30)) == "sovereign_float"
    assert uni["IT"].regime_at(date(2011, 11, 1)) == "currency_union_member"
    assert uni["AR"].regime_at(date(2001, 12, 1)) == "pegged"
    assert uni["AR"].regime_at(date(2018, 8, 1)) == "sovereign_float"
    assert uni["GB"].regime_at(date(1976, 9, 1)) == "sovereign_float"
    assert uni["GB"].regime_at(date(1992, 9, 1)) == "pegged"
    assert uni["GR"].regime_at(date(1995, 1, 1)) == "sovereign_float"
    assert uni["GR"].regime_at(date(2012, 3, 1)) == "currency_union_member"


def test_only_us_is_a_full_reserve_currency() -> None:
    uni = load_universe()
    assert [c.code for c in uni.countries.values() if c.reserve_currency] == ["US"]
    assert uni["EA"].reserve_currency_partial


def test_captivity_weights_sum_to_one_and_are_the_briefs_defaults() -> None:
    cfg = load_indicator_config().captivity
    assert cfg.weights == {
        "domestic_share": 0.30,
        "central_bank_share": 0.20,
        "avg_maturity": 0.20,
        "reserve_niip": 0.15,
        "bill_linker_share": 0.15,
    }
    assert cfg.central_bank_control_credit["own"] == 1.0
    assert cfg.central_bank_control_credit["none"] == 0.0
    assert 0 < cfg.central_bank_control_credit["shared"] < 1


def test_quadrant_thresholds_present() -> None:
    q = load_indicator_config().quadrant
    assert q["unsustainable"]["forward_r_minus_g_5y_gt"] == 0.0
    assert q["unsustainable"]["primary_balance_gdp_lt"] == 0.0
    assert q["captive"]["captivity_score_gt"] == 60


def test_forward_fill_guard_is_one_period() -> None:
    assert load_indicator_config().max_forward_fill_periods == 1


def test_stage_rules_cover_0_to_6_with_prerequisites() -> None:
    rules = load_stage_rules()
    assert set(rules["stages"]) == set(range(7))
    assert rules["stages"][0].get("requires") is None
    for sid in range(1, 7):
        assert "requires" in rules["stages"][sid]
    assert "currency_union_member" in rules["regime_overrides"]
    assert "pegged" in rules["regime_overrides"]


def test_stage_rules_reference_known_or_planned_indicators() -> None:
    # Every indicator a stage rule references must be in the thresholds table or in the
    # explicit list of helper series the stage engine will compute (phase 3).
    helper = {
        "policy_rate",
        "inflation_minus_target",
        "cb_balance_sheet_growth_minus_g",
        "gold_local_ccy",
        "ecb_backstop_active",
        "fx_reserves_12m",
        "auction_tail",
    }
    known = set(load_indicator_config().thresholds) | helper
    unknown = stage_indicator_names() - known
    assert not unknown, f"stage rules reference undefined indicators: {sorted(unknown)}"


def test_report_config_targets_owner_and_sonnet() -> None:
    cfg = load_report_config()
    assert cfg["owner_email"] == "danielconorsims@gmail.com"
    assert "sonnet" in cfg["narrative"]["model"]
    assert cfg["subject_template"].startswith("Sovereign Debt Monitor")


def test_events_csv_is_well_formed_and_in_universe() -> None:
    uni = load_universe()
    valid_types = {
        "currency",
        "default",
        "inflation",
        "repression-episode",
        "IMF-program",
        "successful-consolidation",
        "bond-market",
    }
    with EVENTS.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) >= 13
    ids = [r["event_id"] for r in rows]
    assert len(ids) == len(set(ids))
    required = {
        "GB-1976",
        "IT-1992",
        "SE-1992",
        "MX-1994",
        "CA-1994",
        "RU-1998",
        "AR-2001",
        "GR-2010",
        "BR-2015",
        "TR-2018",
        "GB-2022",
        "AR-2018",
        "JP-2022",
    }
    assert required <= set(ids)
    for r in rows:
        assert r["country"] in uni.countries, r["event_id"]
        assert r["type"] in valid_types, r["event_id"]
        start = date.fromisoformat(r["crisis_start"])
        end = date.fromisoformat(r["crisis_end"])
        assert start <= end, r["event_id"]
        # regime recorded on the event must agree with universe.yaml's regime_history
        assert uni[r["country"]].regime_at(start) == r["regime_at_event"], r["event_id"]


def test_config_error_type_is_a_value_error() -> None:
    with pytest.raises(ValueError):
        raise ConfigError("x")

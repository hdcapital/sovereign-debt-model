"""Typed loaders for the YAML configuration in ``config/``.

The configuration is the tunable surface of the model (universe, weights, thresholds, stage
rules). This module validates it on load so that a bad edit fails at startup, not in the
middle of a quarterly run.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from functools import lru_cache
from typing import Any, Literal

import yaml

from sdm.paths import CONFIG

MonetaryRegime = Literal["sovereign_float", "currency_union_member", "pegged", "dollarised"]
CentralBankControl = Literal["own", "shared", "none"]
Tier = Literal["core", "backtest_only"]

VALID_REGIMES: frozenset[str] = frozenset(
    {"sovereign_float", "currency_union_member", "pegged", "dollarised"}
)
VALID_CONTROL: frozenset[str] = frozenset({"own", "shared", "none"})
VALID_TIERS: frozenset[str] = frozenset({"core", "backtest_only"})
VALID_GAUGES: frozenset[str] = frozenset({"currency", "spread"})


class ConfigError(ValueError):
    """Raised when a config file is internally inconsistent."""


@dataclass(frozen=True)
class RegimeSpan:
    start: date
    end: date
    regime: str
    note: str = ""


@dataclass(frozen=True)
class Country:
    code: str
    name: str
    iso3: str
    currency: str
    tier: str
    monetary_regime: str
    central_bank: str
    central_bank_control: str
    reserve_currency: bool
    pressure_gauge: str
    anchor: str | None
    inflation_target: float | None
    fiscal_year_start_month: int
    bloc: str | None = None
    is_bloc: bool = False
    members: tuple[str, ...] = ()
    reserve_currency_partial: bool = False
    regime_history: tuple[RegimeSpan, ...] = ()

    def regime_at(self, when: date) -> str:
        """Monetary regime in force on ``when`` (current regime if no span covers it).

        Spans are inclusive of their end date: the day a peg breaks belongs to the peg,
        because that is the regime whose mechanics produced the event.
        """
        for span in self.regime_history:
            if span.start <= when <= span.end:
                return span.regime
        return self.monetary_regime

    @property
    def is_core(self) -> bool:
        return self.tier == "core"


@dataclass(frozen=True)
class BacktestEpisode:
    id: str
    country: str
    start: date
    end: date
    regime: str
    note: str = ""


@dataclass(frozen=True)
class Universe:
    core: tuple[str, ...]
    backtest_only: tuple[str, ...]
    episodes: tuple[BacktestEpisode, ...]
    countries: dict[str, Country] = field(default_factory=dict)

    def __getitem__(self, code: str) -> Country:
        return self.countries[code]

    @property
    def all_codes(self) -> tuple[str, ...]:
        return tuple(self.countries)


def _as_date(value: Any) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def _load_yaml(name: str) -> dict[str, Any]:
    path = CONFIG / name
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ConfigError(f"{path} must be a mapping at top level")
    return data


def _parse_country(code: str, raw: dict[str, Any]) -> Country:
    history = tuple(
        RegimeSpan(
            start=_as_date(h["from"]),
            end=_as_date(h["to"]),
            regime=str(h["regime"]),
            note=str(h.get("note", "")),
        )
        for h in raw.get("regime_history", [])
    )
    country = Country(
        code=code,
        name=str(raw["name"]),
        iso3=str(raw["iso3"]),
        currency=str(raw["currency"]),
        tier=str(raw["tier"]),
        monetary_regime=str(raw["monetary_regime"]),
        central_bank=str(raw["central_bank"]),
        central_bank_control=str(raw["central_bank_control"]),
        reserve_currency=bool(raw.get("reserve_currency", False)),
        pressure_gauge=str(raw["pressure_gauge"]),
        anchor=raw.get("anchor"),
        inflation_target=(
            None if raw.get("inflation_target") is None else float(raw["inflation_target"])
        ),
        fiscal_year_start_month=int(raw.get("fiscal_year_start_month", 1)),
        bloc=raw.get("bloc"),
        is_bloc=bool(raw.get("is_bloc", False)),
        members=tuple(raw.get("members", [])),
        reserve_currency_partial=bool(raw.get("reserve_currency_partial", False)),
        regime_history=history,
    )
    _validate_country(country)
    return country


def _validate_country(c: Country) -> None:
    if c.tier not in VALID_TIERS:
        raise ConfigError(f"{c.code}: bad tier {c.tier!r}")
    if c.monetary_regime not in VALID_REGIMES:
        raise ConfigError(f"{c.code}: bad monetary_regime {c.monetary_regime!r}")
    if c.central_bank_control not in VALID_CONTROL:
        raise ConfigError(f"{c.code}: bad central_bank_control {c.central_bank_control!r}")
    if c.pressure_gauge not in VALID_GAUGES:
        raise ConfigError(f"{c.code}: bad pressure_gauge {c.pressure_gauge!r}")
    if c.monetary_regime == "currency_union_member":
        if c.central_bank_control != "shared":
            raise ConfigError(f"{c.code}: union member must have central_bank_control: shared")
        if c.anchor is None or c.bloc is None:
            raise ConfigError(f"{c.code}: union member needs anchor and bloc")
        if c.pressure_gauge != "spread":
            raise ConfigError(f"{c.code}: union member pressure gauge must be 'spread'")
    if c.monetary_regime == "sovereign_float" and c.central_bank_control != "own":
        raise ConfigError(f"{c.code}: sovereign_float must have central_bank_control: own")
    for span in c.regime_history:
        if span.regime not in VALID_REGIMES:
            raise ConfigError(f"{c.code}: bad regime in history {span.regime!r}")
        if span.end <= span.start:
            raise ConfigError(f"{c.code}: regime span ends before it starts ({span})")
    if not 1 <= c.fiscal_year_start_month <= 12:
        raise ConfigError(f"{c.code}: fiscal_year_start_month out of range")


@lru_cache(maxsize=1)
def load_universe() -> Universe:
    raw = _load_yaml("universe.yaml")
    tiers = raw["tiers"]
    countries = {code: _parse_country(code, spec) for code, spec in raw["countries"].items()}
    core = tuple(tiers["core"])
    backtest_only = tuple(tiers["backtest_only"])
    for code in core + backtest_only:
        if code not in countries:
            raise ConfigError(f"tier lists unknown country {code}")
    for code, c in countries.items():
        expected = "core" if code in core else "backtest_only"
        if c.tier != expected:
            raise ConfigError(f"{code}: tier {c.tier!r} disagrees with tiers list ({expected})")
        if c.anchor is not None and c.anchor not in countries:
            raise ConfigError(f"{code}: anchor {c.anchor} is not in the universe")
        if c.bloc is not None and not countries[c.bloc].is_bloc:
            raise ConfigError(f"{code}: bloc {c.bloc} is not flagged is_bloc")
    episodes = tuple(
        BacktestEpisode(
            id=str(e["id"]),
            country=str(e["country"]),
            start=_as_date(e["window"][0]),
            end=_as_date(e["window"][1]),
            regime=str(e["regime"]),
            note=str(e.get("note", "")),
        )
        for e in tiers.get("backtest_episodes", [])
    )
    for ep in episodes:
        if ep.country not in countries:
            raise ConfigError(f"episode {ep.id}: unknown country {ep.country}")
        if ep.regime not in VALID_REGIMES:
            raise ConfigError(f"episode {ep.id}: bad regime {ep.regime}")
    return Universe(core=core, backtest_only=backtest_only, episodes=episodes, countries=countries)


@dataclass(frozen=True)
class CaptivityConfig:
    weights: dict[str, float]
    scale: dict[str, tuple[float, float]]
    reserve_currency_score: float
    reserve_currency_partial_score: float
    central_bank_control_credit: dict[str, float]


@dataclass(frozen=True)
class IndicatorConfig:
    raw: dict[str, Any]
    captivity: CaptivityConfig
    thresholds: dict[str, tuple[float, str]]
    max_forward_fill_periods: int

    @property
    def quadrant(self) -> dict[str, Any]:
        return dict(self.raw["quadrant"])


@lru_cache(maxsize=1)
def load_indicator_config() -> IndicatorConfig:
    raw = _load_yaml("indicators.yaml")
    cap = raw["captivity"]
    weights = {k: float(v) for k, v in cap["weights"].items()}
    total = sum(weights.values())
    if abs(total - 1.0) > 1e-9:
        raise ConfigError(f"captivity weights sum to {total}, not 1.0")
    scale = {k: (float(v["lo"]), float(v["hi"])) for k, v in cap["scale"].items()}
    missing = set(weights) - set(scale)
    if missing:
        raise ConfigError(f"captivity components without scale: {sorted(missing)}")
    credit = {k: float(v) for k, v in cap["central_bank_control_credit"].items()}
    if set(credit) != VALID_CONTROL:
        raise ConfigError("central_bank_control_credit must define own, shared, none")
    thresholds = {k: (float(v["value"]), str(v["direction"])) for k, v in raw["thresholds"].items()}
    for k, (_, direction) in thresholds.items():
        if direction not in {"above", "below"}:
            raise ConfigError(f"threshold {k}: direction must be above|below")
    return IndicatorConfig(
        raw=raw,
        captivity=CaptivityConfig(
            weights=weights,
            scale=scale,
            reserve_currency_score=float(cap["reserve_currency_score"]),
            reserve_currency_partial_score=float(cap["reserve_currency_partial_score"]),
            central_bank_control_credit=credit,
        ),
        thresholds=thresholds,
        max_forward_fill_periods=int(raw["max_forward_fill_periods"]),
    )


VALID_OPS: frozenset[str] = frozenset({"gt", "lt", "ge", "le", "rising", "falling", "record_high"})


def _validate_condition(cond: dict[str, Any], where: str) -> None:
    if "all" in cond or "any" in cond:
        for key in ("all", "any"):
            for sub in cond.get(key, []):
                _validate_condition(sub, where)
        return
    if "ind" not in cond or "op" not in cond:
        raise ConfigError(f"{where}: condition needs ind and op: {cond}")
    if cond["op"] not in VALID_OPS:
        raise ConfigError(f"{where}: bad op {cond['op']!r}")
    if cond["op"] != "record_high" and "value" not in cond:
        raise ConfigError(f"{where}: op {cond['op']} needs a value")


def _validate_stage(stage_id: int, spec: dict[str, Any], known: set[int]) -> None:
    where = f"stage {stage_id}"
    if "name" not in spec:
        raise ConfigError(f"{where}: missing name")
    if "all" not in spec and "any" not in spec:
        raise ConfigError(f"{where}: needs all: or any:")
    req = spec.get("requires")
    if req is not None and int(req) not in known:
        raise ConfigError(f"{where}: requires unknown stage {req}")
    for key in ("all", "any"):
        for cond in spec.get(key, []):
            _validate_condition(cond, where)


@lru_cache(maxsize=1)
def load_stage_rules() -> dict[str, Any]:
    raw = _load_yaml("stages.yaml")
    stages = {int(k): v for k, v in raw["stages"].items()}
    if set(stages) != set(range(7)):
        raise ConfigError("stages.yaml must define stages 0..6")
    for sid, spec in stages.items():
        _validate_stage(sid, spec, set(stages))
    overrides = raw.get("regime_overrides", {})
    for regime, per_stage in overrides.items():
        if regime not in VALID_REGIMES:
            raise ConfigError(f"regime_overrides: unknown regime {regime}")
        for sid, spec in per_stage.items():
            _validate_stage(int(sid), spec, set(stages))
    return {"stages": stages, "regime_overrides": overrides}


@lru_cache(maxsize=1)
def load_report_config() -> dict[str, Any]:
    raw = _load_yaml("report.yaml")
    for key in ("owner_email", "subject_template", "narrative", "schedule", "email"):
        if key not in raw:
            raise ConfigError(f"report.yaml missing {key}")
    return raw


def stage_indicator_names() -> set[str]:
    """All indicator names referenced anywhere in stages.yaml."""
    names: set[str] = set()

    def walk(cond: dict[str, Any]) -> None:
        if "ind" in cond:
            names.add(str(cond["ind"]))
        for key in ("all", "any"):
            for sub in cond.get(key, []):
                walk(sub)

    rules = load_stage_rules()
    for spec in rules["stages"].values():
        walk(spec)
    for per_stage in rules["regime_overrides"].values():
        for spec in per_stage.values():
            walk(spec)
    return names

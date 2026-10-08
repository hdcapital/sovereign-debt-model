"""Collector registry and the ``update`` orchestrator."""

from __future__ import annotations

import importlib
import json
import logging
from datetime import UTC, datetime
from pathlib import Path

from sdm.collect.base import Collector, FetchResult
from sdm.collect.http import Http
from sdm.paths import DATA

log = logging.getLogger(__name__)

# module name -> class name. Order matters only for logging.
COLLECTORS: dict[str, str] = {
    "sdm.collect.sources.bis": "BisCollector",
    "sdm.collect.sources.imf_datamapper": "ImfDataMapperCollector",
    "sdm.collect.sources.fred": "FredCollector",
    "sdm.collect.sources.fiscaldata": "FiscalDataCollector",
    "sdm.collect.sources.gold": "GoldCollector",
    "sdm.collect.sources.boe": "BoeCollector",
    "sdm.collect.sources.ons": "OnsCollector",
    "sdm.collect.sources.dmo": "DmoCollector",
    "sdm.collect.sources.mof_jp": "MofJpCollector",
    "sdm.collect.sources.rba": "RbaCollector",
    "sdm.collect.sources.boc": "BocCollector",
    "sdm.collect.sources.snb": "SnbCollector",
    "sdm.collect.sources.ecb": "EcbCollector",
    "sdm.collect.sources.eurostat": "EurostatCollector",
    "sdm.collect.sources.worldbank": "WorldBankCollector",
    "sdm.collect.sources.arslanalp_tsuda": "ArslanalpTsudaCollector",
    "sdm.collect.sources.jst": "JstCollector",
    "sdm.collect.sources.manual": "ManualCollector",
}

UPDATE_LOG = DATA / "update_log.json"


def load_collectors(names: set[str] | None = None, http: Http | None = None) -> list[Collector]:
    out: list[Collector] = []
    for module, cls in COLLECTORS.items():
        short = module.rsplit(".", 1)[-1]
        if names and short not in names:
            continue
        try:
            mod = importlib.import_module(module)
        except ModuleNotFoundError as e:
            log.warning("collector %s not available: %s", short, e)
            continue
        out.append(getattr(mod, cls)(http=http))
    return out


def run_update(names: set[str] | None = None, only: set[str] | None = None) -> dict[str, list[FetchResult]]:
    """Run every collector, log what changed to data/update_log.json, return results."""
    results: dict[str, list[FetchResult]] = {}
    for collector in load_collectors(names):
        log.info("== %s", collector.name)
        try:
            results[collector.name] = collector.run(only=only)
        except Exception as e:  # noqa: BLE001
            log.error("collector %s crashed: %s", collector.name, e)
            results[collector.name] = []
    write_update_log(results)
    if names is None and only is None:
        prune_catalog(load_collectors())
    return results


def prune_catalog(collectors: list[Collector]) -> int:
    """Remove catalog rows for series no current collector produces (renamed or retired ids)."""
    import pandas as pd

    from sdm.paths import CATALOG

    if not CATALOG.exists():
        return 0
    live = {spec.series_id for c in collectors for spec in c.series()}
    cat = pd.read_csv(CATALOG)
    keep = cat["series_id"].isin(live)
    if (~keep).any():
        log.info("catalog: pruning %d retired series", int((~keep).sum()))
        cat[keep].to_csv(CATALOG, index=False)
    return int((~keep).sum())


def write_update_log(results: dict[str, list[FetchResult]]) -> Path:
    entry = {
        "run_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "sources": {
            name: {
                "ok": sum(r.ok for r in rs),
                "failed": [r.spec.series_id for r in rs if not r.ok],
                "errors": {r.spec.series_id: r.error for r in rs if not r.ok},
                "new_obs": sum(r.n_new for r in rs),
                "revised_obs": sum(r.n_revised for r in rs),
                "changed": [r.spec.series_id for r in rs if r.n_new or r.n_revised],
            }
            for name, rs in results.items()
        },
    }
    history: list = []
    if UPDATE_LOG.exists():
        try:
            history = json.loads(UPDATE_LOG.read_text())
        except json.JSONDecodeError as e:
            # a merge of two runs' logs can leave conflict markers; keep a copy, start fresh
            log.warning("update_log.json unreadable (%s); archiving it and starting a new log", e)
            UPDATE_LOG.rename(UPDATE_LOG.with_suffix(".corrupt.json"))
    history = (history + [entry])[-50:]
    UPDATE_LOG.write_text(json.dumps(history, indent=1))
    return UPDATE_LOG


def summarize(results: dict[str, list[FetchResult]]) -> str:
    lines = []
    for name, rs in results.items():
        ok = sum(r.ok for r in rs)
        bad = [r for r in rs if not r.ok]
        new = sum(r.n_new for r in rs)
        rev = sum(r.n_revised for r in rs)
        lines.append(f"{name:16s} ok={ok:3d} failed={len(bad):3d} new={new:6d} revised={rev:5d}")
        for r in bad:
            lines.append(f"    FAIL {r.spec.series_id}: {r.error[:160]}")
    return "\n".join(lines)

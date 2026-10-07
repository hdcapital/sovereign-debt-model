"""Command-line entry point. ``python -m sdm.cli <command>`` or ``sdm <command>``.

Phase 1 wires the commands; the ones not yet implemented say so and exit non-zero so a
Makefile target can never silently succeed.
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Callable

from sdm import __version__
from sdm.config import (
    load_indicator_config,
    load_report_config,
    load_stage_rules,
    load_universe,
)

log = logging.getLogger("sdm")


def cmd_check(_: argparse.Namespace) -> int:
    """Validate every config file and print the universe."""
    uni = load_universe()
    load_indicator_config()
    load_stage_rules()
    load_report_config()
    print(f"sdm {__version__}: config OK")
    print(f"core ({len(uni.core)}): {', '.join(uni.core)}")
    print(f"backtest_only ({len(uni.backtest_only)}): {', '.join(uni.backtest_only)}")
    print(f"episodes ({len(uni.episodes)}): {', '.join(e.id for e in uni.episodes)}")
    return 0


def _not_implemented(phase: int) -> Callable[[argparse.Namespace], int]:
    def run(args: argparse.Namespace) -> int:
        print(f"`{args.command}` is not implemented yet (phase {phase}).", file=sys.stderr)
        return 2

    return run


def cmd_update(args: argparse.Namespace) -> int:
    """Refresh every data source incrementally and log what changed."""
    from sdm.collect.registry import run_update, summarize

    names = set(args.source) if args.source else None
    only = set(args.only) if args.only else None
    results = run_update(names, only)
    print(summarize(results))
    failed = sum(1 for rs in results.values() for r in rs if not r.ok)
    total = sum(len(rs) for rs in results.values())
    print(f"{total - failed}/{total} series updated; log at data/update_log.json")
    return 0 if total and failed < total else 1


def cmd_indicators(args: argparse.Namespace) -> int:
    """Build the quarterly panel and compute every indicator for every country."""
    import pandas as pd

    from sdm.config import load_universe
    from sdm.indicators.compute import compute_all, latest_wide
    from sdm.indicators.panel import build_panel

    panel = build_panel()
    all_ind, latest, transitions = compute_all(panel)
    uni = load_universe()
    cols = [
        "debt_gdp",
        "primary_balance_gdp",
        "r_effective",
        "g_nominal",
        "marginal_yield",
        "avg_coupon_gap",
        "forward_r_5y",
        "forward_r_minus_g_5y",
        "captivity_score",
        "stage_estimate",
        "quadrant",
    ]
    wide = latest_wide(latest).reindex(uni.core)
    pd.set_option("display.width", 200)
    print(wide[[c for c in cols if c in wide.columns]].round(2).to_string())
    print(f"\n{len(all_ind)} country-quarters, {len(transitions)} transitions -> data/clean/")
    return 0


COMMANDS: dict[str, tuple[Callable[[argparse.Namespace], int], str]] = {
    "check": (cmd_check, "validate configuration"),
    "update": (cmd_update, "refresh all data sources incrementally"),
    "indicators": (cmd_indicators, "compute the quarterly indicator table"),
    "backtest": (_not_implemented(4), "run the backtest and write BACKTEST.md"),
    "dashboard": (_not_implemented(5), "build the HTML dashboard"),
    "report": (_not_implemented(6), "generate the narrative quarterly report"),
    "email": (_not_implemented(7), "send (or --dry-run) the latest report"),
    "monthly": (_not_implemented(8), "monthly check: update + alert-only email"),
    "quarterly": (_not_implemented(8), "full quarterly run"),
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sdm", description="Sovereign debt spiral monitor")
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, (_, help_text) in COMMANDS.items():
        p = sub.add_parser(name, help=help_text)
        if name == "email":
            p.add_argument("--dry-run", action="store_true", help="write to reports/outbox/")
        if name == "update":
            p.add_argument("--source", nargs="*", help="collector names to run (default all)")
            p.add_argument("--only", nargs="*", help="series ids, concepts or countries to restrict to")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    handler, _ = COMMANDS[args.command]
    return handler(args)


if __name__ == "__main__":
    sys.exit(main())

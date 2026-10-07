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


def cmd_docs(args: argparse.Namespace) -> int:
    """Regenerate docs/INDICATORS.md from the registry and config."""
    from sdm.report.docs import write_indicators_md

    print(write_indicators_md())
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


def cmd_backtest(args: argparse.Namespace) -> int:
    """Run the backtest against data/events.csv and write reports/backtest/BACKTEST.md."""
    from sdm.backtest.run import run_backtest

    res = run_backtest()
    print(res.lead_summary.round(2).to_string())
    print()
    print(res.forward_r.round(2).to_string() if len(res.forward_r) else "forward-r test: not enough history")
    print("\nreports/backtest/BACKTEST.md written")
    return 0


def cmd_dashboard(args: argparse.Namespace) -> int:
    """Build reports/dashboard/latest.html and a dated copy."""
    from sdm.report.dashboard import build_dashboard

    latest, dated = build_dashboard()
    print(f"{latest}\n{dated}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    """Generate reports/quarterly/YYYY-Qn.md (+ .html) with Claude; --no-api assembles the prompt only."""
    from sdm.report.narrative import generate_report

    md, html = generate_report(use_api=not args.no_api, label=args.period)
    print(f"{md}\n{html}")
    return 0


def cmd_email(args: argparse.Namespace) -> int:
    """Send the latest quarterly report by Gmail (or write it to reports/outbox/ with --dry-run)."""
    from sdm.report.email import send_quarterly
    from sdm.report.narrative import period_label

    period = args.period or period_label()
    out = send_quarterly(period, dry_run=args.dry_run, to=args.to)
    print(out)
    return 0


def cmd_monthly(args: argparse.Namespace) -> int:
    """Update data, recompute indicators and dashboard; email only if something fired."""
    from sdm.report.dashboard import build_dashboard
    from sdm.report.email import send_alert
    from sdm.report.monthly import run_monthly
    from sdm.report.narrative import period_label

    if not args.skip_update:
        cmd_update(argparse.Namespace(source=None, only=None))
    cmd_indicators(args)
    build_dashboard()
    fire, body, details = run_monthly()
    n_t, n_m = details["transitions"], len(details["moves"])
    print(f"monthly check: transitions={n_t} moves={n_m} since={details['since']}")
    if fire:
        out = send_alert(period_label(), body, dry_run=args.dry_run, to=args.to)
        print(f"alert sent: {out}")
    else:
        print("nothing fired; no email")
    return 0


def cmd_quarterly(args: argparse.Namespace) -> int:
    """The full quarterly run."""
    from sdm.report.dashboard import build_dashboard
    from sdm.report.email import send_quarterly
    from sdm.report.narrative import generate_report, period_label

    if not args.skip_update:
        cmd_update(argparse.Namespace(source=None, only=None))
    cmd_indicators(args)
    cmd_backtest(args)
    build_dashboard()
    period = args.period or period_label()
    generate_report(use_api=not args.no_api, label=period)
    out = send_quarterly(period, dry_run=args.dry_run, to=args.to)
    print(f"quarterly {period}: {out}")
    return 0


COMMANDS: dict[str, tuple[Callable[[argparse.Namespace], int], str]] = {
    "check": (cmd_check, "validate configuration"),
    "docs": (cmd_docs, "regenerate docs/INDICATORS.md from the registry and config"),
    "update": (cmd_update, "refresh all data sources incrementally"),
    "indicators": (cmd_indicators, "compute the quarterly indicator table"),
    "backtest": (cmd_backtest, "run the backtest and write BACKTEST.md"),
    "dashboard": (cmd_dashboard, "build the HTML dashboard"),
    "report": (cmd_report, "generate the narrative quarterly report"),
    "email": (cmd_email, "send (or --dry-run) the latest report"),
    "monthly": (
        cmd_monthly,
        "monthly check: update + indicators; email only on a transition or 1.5-sigma move",
    ),
    "quarterly": (
        cmd_quarterly,
        "full quarterly run: update, indicators, backtest, dashboard, report, email",
    ),
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sdm", description="Sovereign debt spiral monitor")
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, (_, help_text) in COMMANDS.items():
        p = sub.add_parser(name, help=help_text)
        if name in ("email", "monthly", "quarterly"):
            p.add_argument(
                "--dry-run", action="store_true", help="write the email to reports/outbox/ instead of sending"
            )
            p.add_argument("--to", help="recipient address (default: OWNER_EMAIL env, else config)")
        if name in ("email", "quarterly"):
            p.add_argument("--period", help="period label, e.g. 2026-Q3 (default: last complete quarter)")
        if name in ("monthly", "quarterly"):
            p.add_argument("--skip-update", action="store_true", help="do not refresh data first")
        if name == "quarterly":
            p.add_argument("--no-api", action="store_true", help="skip the Claude call")
        if name == "report":
            p.add_argument("--no-api", action="store_true", help="assemble the prompt, skip the API call")
            p.add_argument(
                "--period", help="report period label, e.g. 2026-Q3 (default: last complete quarter)"
            )
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

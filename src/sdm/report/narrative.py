"""Generate the quarterly narrative with Claude.

Prompt = docs/MODEL.md (system) + prompts/report_instructions.md + the latest indicator table,
the eight-quarter history, the transitions log, backtest calibration stats, the data-issues
list and the previous quarter's report. Output: reports/quarterly/YYYY-Qn.md and .html.

Without ANTHROPIC_API_KEY (or with --no-api) the assembled prompt is written to
reports/outbox/prompt-YYYY-Qn.md and a placeholder report is produced, so the rest of the
pipeline can be exercised offline.
"""

from __future__ import annotations

import logging
import os
from datetime import date

import pandas as pd

from sdm.config import load_report_config, load_universe
from sdm.indicators.compute import INDICATORS_PATH, LATEST_PATH, TRANSITIONS_PATH, last_complete_quarter
from sdm.indicators.registry import REGISTRY
from sdm.paths import DOCS, PROMPTS, REPORTS

log = logging.getLogger(__name__)

QUARTERLY_DIR = REPORTS / "quarterly"
OUTBOX = REPORTS / "outbox"
BACKTEST_DIR = REPORTS / "backtest"


def period_label(today: date | None = None) -> str:
    q = last_complete_quarter(today)
    return f"{q.year}-Q{q.quarter}"


def previous_period_label(label: str) -> str:
    y, q = label.split("-Q")
    y, q = int(y), int(q)
    return f"{y - 1}-Q4" if q == 1 else f"{y}-Q{q - 1}"


def shown_indicators() -> list[str]:
    names = [n for n, m in REGISTRY.items() if not m.helper]
    return names + ["stage_estimate", "quadrant", "trajectory_unsustainable", "holders_captive"]


def latest_core_csv() -> str:
    uni = load_universe()
    latest = pd.read_csv(LATEST_PATH)
    core = latest[latest["tier"] == "core"].drop(columns=["tier"])
    core = core[core["indicator"].isin(shown_indicators())]
    if "applies" in core:
        core = core[core["applies"].astype(bool)].drop(columns=["applies"])
    core["country"] = pd.Categorical(core["country"], categories=list(uni.core), ordered=True)
    core = core.sort_values(["country", "indicator"])
    for col in ("value", "chg_1y", "chg_5y"):
        core[col] = (
            pd.to_numeric(core[col], errors="coerce")
            .round(3)
            .astype(object)
            .where(core[col].notna(), core[col])
        )
    return core.to_csv(index=False)


def history_csv(quarters: int) -> str:
    uni = load_universe()
    ind = pd.read_csv(INDICATORS_PATH, index_col=[0, 1], parse_dates=[1])
    cols = [c for c in shown_indicators() if c in ind.columns]
    frames = []
    for code in uni.core:
        if code in ind.index.get_level_values(0):
            df = ind.loc[code][cols].tail(quarters).round(3)
            df.insert(0, "country", code)
            frames.append(df.reset_index())
    return pd.concat(frames).to_csv(index=False)


def transitions_text(quarters: int = 8) -> str:
    if not TRANSITIONS_PATH.exists():
        return "none"
    t = pd.read_csv(TRANSITIONS_PATH)
    uni = load_universe()
    t = t[t["country"].isin(uni.core)]
    cutoff = (last_complete_quarter() - pd.offsets.QuarterEnd(quarters)).date()
    t = t[pd.to_datetime(t["quarter"]).dt.date >= cutoff]
    return t.to_csv(index=False) if len(t) else "none in the last eight quarters"


def backtest_text() -> str:
    parts = []
    for name in ("lead_summary", "forward_r"):
        p = BACKTEST_DIR / f"{name}.csv"
        if p.exists():
            parts.append(f"### {name}\n{p.read_text().strip()}")
    return "\n\n".join(parts) if parts else "no backtest results available"


def data_issues_text() -> str:
    latest = pd.read_csv(LATEST_PATH)
    core = latest[(latest["tier"] == "core") & latest["indicator"].isin(shown_indicators())]
    if "applies" in core:
        core = core[core["applies"].astype(bool)]
    num = pd.to_numeric(core["value"], errors="coerce")
    stale_after = int(load_report_config()["email"].get("stale_after_quarters", 4))
    stale = core[
        (pd.to_numeric(core["stale_quarters"], errors="coerce") > stale_after)
        | (num.isna() & (core["indicator"] != "quadrant"))
    ]
    lines = [
        f"{r.country} {r.indicator}: "
        + (
            "no data"
            if pd.isna(r.value)
            else f"last value {r.quarter}, {int(r.stale_quarters)} quarters stale"
        )
        for r in stale.itertuples(index=False)
    ]
    from sdm.paths import CATALOG

    if CATALOG.exists():
        cat = pd.read_csv(CATALOG)
        bad = cat[cat["notes"].astype(str).str.contains("LAST ERROR")]
        lines += [
            f"{r.series_id}: failed to update ({str(r.notes).split('LAST ERROR:')[-1].strip()[:100]})"
            for r in bad.itertuples(index=False)
        ]
        approx = cat[cat["notes"].astype(str).str.contains("approximate")]
        lines += [f"{r.series_id}: hand-maintained approximate value" for r in approx.itertuples(index=False)]
    return "\n".join(lines) if lines else "none"


def assemble_prompt(label: str) -> tuple[str, str]:
    cfg = load_report_config()
    system = (DOCS / "MODEL.md").read_text(encoding="utf-8")
    instructions = (PROMPTS / "report_instructions.md").read_text(encoding="utf-8")
    prev_path = QUARTERLY_DIR / f"{previous_period_label(label)}.md"
    previous = prev_path.read_text(encoding="utf-8") if prev_path.exists() else "(no previous report)"
    user = f"""{instructions}

---

# Inputs for {label}

Report quarter: {label}. Today: {date.today().isoformat()}.

## 1. Latest indicator table (core markets)

```csv
{latest_core_csv()}
```

## 2. Eight-quarter history

```csv
{history_csv(int(cfg["narrative"]["history_quarters"]))}
```

## 3. Transitions (last eight quarters)

```
{transitions_text()}
```

## 4. Backtest calibration

{backtest_text()}

## 5. Previous report ({previous_period_label(label)})

{previous}

## 6. Data issues

{data_issues_text()}
"""
    return system, user


def call_claude(system: str, user: str) -> str:
    import anthropic

    cfg = load_report_config()["narrative"]
    client = anthropic.Anthropic()
    with client.messages.stream(
        model=cfg["model"],
        max_tokens=int(cfg.get("max_tokens", 16000)),
        system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
        thinking={"type": "adaptive"},
        output_config={"effort": cfg.get("effort", "high")},
        messages=[{"role": "user", "content": user}],
    ) as stream:
        message = stream.get_final_message()
    if message.stop_reason == "refusal":
        detail = getattr(message, "stop_details", None)
        raise RuntimeError(f"model refused the request: {detail}")
    if message.stop_reason == "max_tokens":
        log.warning("report hit max_tokens; output may be truncated")
    text = "".join(block.text for block in message.content if block.type == "text")
    log.info(
        "report: %d output tokens, %d input (%d cached)",
        message.usage.output_tokens,
        message.usage.input_tokens,
        getattr(message.usage, "cache_read_input_tokens", 0) or 0,
    )
    return text


def render_html(markdown_text: str, label: str) -> str:
    import markdown

    body = markdown.markdown(markdown_text, extensions=["tables", "fenced_code"])
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Sovereign Debt Monitor {label}</title>
<style>body{{font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif;color:#0b0b0b;background:#fff;max-width:760px;margin:24px auto;padding:0 16px}}
h1,h2,h3{{font-weight:600}}table{{border-collapse:collapse;font-size:13px}}th,td{{border-bottom:1px solid #e1e0d9;padding:5px 8px;text-align:left}}
code{{font-size:13px}}</style></head><body>{body}</body></html>"""


def generate_report(use_api: bool = True, label: str | None = None) -> tuple[object, object]:
    label = label or period_label()
    system, user = assemble_prompt(label)
    QUARTERLY_DIR.mkdir(parents=True, exist_ok=True)
    OUTBOX.mkdir(parents=True, exist_ok=True)
    (OUTBOX / f"prompt-{label}.md").write_text(f"# SYSTEM\n\n{system}\n\n# USER\n\n{user}", encoding="utf-8")
    if use_api and os.environ.get("ANTHROPIC_API_KEY"):
        text = call_claude(system, user)
    else:
        why = "ANTHROPIC_API_KEY not set" if use_api else "--no-api"
        log.warning("report: %s; writing placeholder with the assembled prompt in reports/outbox/", why)
        text = (
            f"## TL;DR\n\n- Placeholder report for {label}: the narrative was not generated ({why}).\n"
            f"- The assembled prompt is in reports/outbox/prompt-{label}.md.\n"
            "- Indicator table, dashboard and backtest are current.\n- Set ANTHROPIC_API_KEY and run `make report`.\n"
            "- Nothing in this placeholder is an analytical claim.\n\n## Data issues\n\n" + data_issues_text()
        )
    md_path = QUARTERLY_DIR / f"{label}.md"
    md_path.write_text(text, encoding="utf-8")
    html_path = QUARTERLY_DIR / f"{label}.html"
    html_path.write_text(render_html(text, label), encoding="utf-8")
    log.info("report: %s", md_path)
    return md_path, html_path

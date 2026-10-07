from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from sdm.config import load_universe
from sdm.indicators.applicability import indicator_applies
from sdm.report.email import build_message
from sdm.report.narrative import period_label, previous_period_label


def test_applicability_rules() -> None:
    uni = load_universe()
    assert indicator_applies("spread_to_anchor_bp", uni["IT"])
    assert not indicator_applies("spread_to_anchor_bp", uni["US"])
    assert indicator_applies("fx_vs_usd_12m", uni["JP"])
    assert not indicator_applies("fx_vs_usd_12m", uni["US"])
    assert not indicator_applies("fx_vs_usd_12m", uni["FR"])
    assert indicator_applies("auction_tail", uni["US"]) and not indicator_applies("auction_tail", uni["GB"])
    assert indicator_applies("ecb_backstop_active", uni["EA"]) and not indicator_applies(
        "ecb_backstop_active", uni["CH"]
    )
    assert indicator_applies("debt_gdp", uni["AU"])


def test_period_labels() -> None:
    from datetime import date

    assert period_label(date(2026, 10, 15)) == "2026-Q3"
    assert period_label(date(2026, 1, 15)) == "2025-Q4"
    assert previous_period_label("2026-Q1") == "2025-Q4"
    assert previous_period_label("2026-Q3") == "2026-Q2"


def test_email_message_has_html_and_attachments(tmp_path: Path) -> None:
    a = tmp_path / "dash.html"
    a.write_text("<html>x</html>")
    b = tmp_path / "ind.csv"
    b.write_text("a,b\n1,2\n")
    msg = build_message(
        "Sovereign Debt Monitor — 2026-Q3",
        "<p>hello</p>",
        [a, b, tmp_path / "missing.txt"],
        to="x@example.com",
    )
    assert msg["Subject"] == "Sovereign Debt Monitor — 2026-Q3"
    parts = [p.get_content_type() for p in msg.walk()]
    assert "text/html" in parts and "text/csv" in parts
    assert sum(1 for p in msg.iter_attachments()) == 2


def test_sigma_moves_fire_on_large_change(tmp_path, monkeypatch) -> None:
    from sdm.report import monthly

    idx = pd.date_range("2016-03-31", periods=40, freq="QE")
    ind = pd.DataFrame(
        {
            "country": "US",
            "quarter": idx,
            "debt_gdp": 100 + np.cumsum(np.random.default_rng(0).normal(0.5, 0.4, 40)),
        }
    ).set_index(["country", "quarter"])
    path = tmp_path / "indicators.csv"
    ind.to_csv(path)
    monkeypatch.setattr(monthly, "INDICATORS_PATH", path)
    moves = monthly.sigma_moves({"US.debt_gdp": 119.5}, {"US.debt_gdp": 119.55})
    assert moves == []
    moves = monthly.sigma_moves({"US.debt_gdp": 119.5}, {"US.debt_gdp": 125.0})
    assert moves and moves[0]["indicator"] == "debt_gdp"

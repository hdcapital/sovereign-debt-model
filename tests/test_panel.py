from __future__ import annotations

import numpy as np
import pandas as pd

from sdm.indicators.panel import build_panel, infer_freq, to_quarterly


def test_infer_freq() -> None:
    assert infer_freq(pd.Series(pd.date_range("2020-01-01", periods=30, freq="D"))) == "D"
    assert infer_freq(pd.Series(pd.date_range("2020-01-31", periods=12, freq="ME"))) == "M"
    assert infer_freq(pd.Series(pd.date_range("2020-03-31", periods=8, freq="QE"))) == "Q"
    assert infer_freq(pd.Series(pd.date_range("2015-12-31", periods=5, freq="YE"))) == "A"


def test_monthly_flow_sums_and_requires_full_quarter() -> None:
    idx = pd.date_range("2024-01-31", periods=5, freq="ME")  # Jan..May
    s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0], index=idx)
    q = to_quarterly(s, "flow", max_ffill=0)
    assert q.loc[pd.Timestamp("2024-03-31")] == 6.0
    assert pd.Timestamp("2024-06-30") not in q.index  # only 2 of 3 months -> NaN -> dropped


def test_daily_rate_takes_last_in_quarter_and_ffills_one() -> None:
    idx = pd.date_range("2024-01-01", "2024-04-15", freq="B")
    s = pd.Series(np.arange(len(idx), dtype=float), index=idx)
    q = to_quarterly(s, "rate", max_ffill=1)
    assert q.loc[pd.Timestamp("2024-03-31")] == s.loc[:"2024-03-31"].iloc[-1]
    assert q.loc[pd.Timestamp("2024-06-30")] == s.iloc[-1]


def test_annual_covers_four_quarters_and_flow_is_split() -> None:
    s = pd.Series([40.0, 80.0], index=pd.to_datetime(["2020-12-31", "2021-12-31"]))
    r = to_quarterly(s, "rate")
    assert r.loc[pd.Timestamp("2020-03-31")] == 40.0 and r.loc[pd.Timestamp("2021-09-30")] == 80.0
    f = to_quarterly(s, "flow")
    assert f.loc[pd.Timestamp("2020-06-30")] == 10.0


def test_build_panel_source_priority_and_gap_fill(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("sdm.indicators.panel.DATA_CLEAN", tmp_path)
    monkeypatch.setattr("sdm.indicators.panel.PANEL_PATH", tmp_path / "panel.csv")
    monkeypatch.setattr("sdm.indicators.panel.SOURCES_PATH", tmp_path / "panel_sources.csv")
    rows = []
    for d, v in [("2020-12-31", 100.0), ("2021-12-31", 110.0)]:  # IMF annual
        rows.append(("US.gg_debt_gdp.IMF_WEO", "US", "gg_debt_gdp", d, v, "2024-01-01"))
    for d, v in [("2021-03-31", 105.0), ("2021-06-30", 106.0)]:  # BIS quarterly, preferred
        rows.append(("US.gg_debt_gdp.BIS", "US", "gg_debt_gdp", d, v, "2024-01-01"))
    clean = pd.DataFrame(rows, columns=["series_id", "country", "concept", "date", "value", "vintage"])
    panel = build_panel(clean, write=True)
    v = panel.values.loc["US"]["gg_debt_gdp"]
    src = panel.sources.loc["US"]["gg_debt_gdp"]
    assert v.loc[pd.Timestamp("2021-03-31")] == 105.0 and src.loc[pd.Timestamp("2021-03-31")] == "BIS"
    # IMF values are spliced onto BIS: overlap 2021Q1-Q2 has BIS 105/106 vs IMF 110 -> shift -4.5
    assert (
        abs(v.loc[pd.Timestamp("2020-06-30")] - 95.5) < 1e-9
        and src.loc[pd.Timestamp("2020-06-30")] == "IMF_WEO"
    )
    assert (
        abs(v.loc[pd.Timestamp("2021-12-31")] - 105.5) < 1e-9
        and src.loc[pd.Timestamp("2021-12-31")] == "IMF_WEO"
    )
    assert (tmp_path / "panel.csv").exists()


def test_splice_additive_for_rates_and_ratio_for_stocks() -> None:
    from sdm.indicators.panel import splice

    idx = pd.date_range("2020-03-31", periods=6, freq="QE")
    primary = pd.Series([90.0, 91.0, 92.0, 93.0, np.nan, np.nan], index=idx).dropna()
    secondary = pd.Series([80.0, 81.0, 82.0, 83.0, 84.0, 85.0], index=idx)
    out = splice(primary, secondary, "rate")
    assert abs(out.loc[idx[4]] - 94.0) < 1e-9
    stock = pd.Series([200.0, 202.0, 204.0, 206.0, np.nan, np.nan], index=idx).dropna()
    out = splice(stock, secondary, "stock")
    assert abs(out.loc[idx[4]] / 84.0 - 2.5) < 0.05

"""Collector parsers against excerpts of real responses recorded by the probe workflow.
No network: each test feeds the recorded bytes through an Http replay directory."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from sdm.collect.base import Collector, SeriesSpec, latest_vintage_frame
from sdm.collect.http import Http
from sdm.collect.sources.bis import BisCollector, parse_period
from sdm.collect.sources.eurostat import EurostatCollector
from sdm.collect.sources.fiscaldata import FiscalDataCollector
from sdm.collect.sources.imf_datamapper import ImfDataMapperCollector
from sdm.collect.sources.mof_jp import MofJpCollector
from sdm.collect.sources.rba import parse_rba_csv
from sdm.collect.sources.snb import parse_snb_csv
from sdm.collect.sources.worldbank import WorldBankCollector

FIX = Path(__file__).parent / "fixtures"


class ReplayHttp(Http):
    """Serve fixture files for exact URLs (after params are applied)."""

    def __init__(self, mapping: dict[str, Path]) -> None:
        super().__init__()
        self.mapping = mapping

    def get_bytes(self, url: str, params: dict | None = None, timeout: int = 60) -> bytes:
        import requests

        full = url if not params else requests.Request("GET", url, params=params).prepare().url
        for key, path in self.mapping.items():
            if key in (full or ""):
                return path.read_bytes()
        raise FileNotFoundError(full)


def test_bis_period_parsing() -> None:
    assert parse_period("2024-Q1") == pd.Timestamp("2024-03-31")
    assert parse_period("2026-06") == pd.Timestamp("2026-06-30")
    assert parse_period("2020") == pd.Timestamp("2020-12-31")


def test_bis_fx_series_parses(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("sdm.collect.base.DATA_RAW", tmp_path)
    c = BisCollector(http=ReplayHttp({"WS_XRU/1.0/M.JP.JPY.A": FIX / "bis_xru.csv"}))
    spec = next(s for s in c.series() if s.series_id == "JP.fx_lcu_per_usd.BIS")
    df = c.fetch(spec)
    assert len(df) == 3
    assert df["date"].iloc[-1] == pd.Timestamp("2026-08-31")
    assert abs(df["value"].iloc[-1] - 158.801365) < 1e-6


def test_rba_csv_parser() -> None:
    df = parse_rba_csv((FIX / "rba_f2_1.csv").read_text(encoding="utf-8-sig"))
    assert "FCMYGBAG10" in df.columns
    assert df["date"].iloc[0] == pd.Timestamp("2013-05-31")
    assert abs(float(df["FCMYGBAG10"].iloc[0]) - 3.324) < 1e-9


def test_snb_csv_parser() -> None:
    df = parse_snb_csv((FIX / "snb_rendoblim.csv").read_text(encoding="utf-8-sig"))
    ten = df[df["D0"] == "10J"]
    assert not ten.empty
    assert ten["Date"].iloc[-1] == "2025-07"


def test_mof_yields_parse(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("sdm.collect.base.DATA_RAW", tmp_path)
    c = MofJpCollector(http=ReplayHttp({"jgbcme": FIX / "mof_jgbcme.csv"}))
    spec = next(s for s in c.series() if s.concept == "yield_10y")
    df = c.fetch(spec)
    assert df["date"].min() == pd.Timestamp("1974-09-24")
    assert abs(df.sort_values("date")["value"].iloc[-1] - 3.057) < 1e-9


def test_fiscaldata_avg_rate_and_mspd(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("sdm.collect.base.DATA_RAW", tmp_path)
    c = FiscalDataCollector(
        http=ReplayHttp(
            {
                "avg_interest_rates": FIX / "fiscaldata_avg_rate.json",
                "mspd_table_1": FIX / "fiscaldata_mspd1.json",
            }
        )
    )
    spec = next(s for s in c.series() if s.concept == "avg_interest_rate")
    # the fixture holds every security_desc; the live API applies the filter server-side, so
    # here we only check the frame shape and the parse of the amount column
    df = c.fetch(spec)
    assert {"date", "value"} <= set(df.columns)
    spec = next(s for s in c.series() if s.concept == "bills_outstanding_lcu")
    df = c.fetch(spec)
    assert abs(df["value"].iloc[0] - 7117.9370671) < 1e-6  # millions -> billions


def test_imf_datamapper_drops_projections(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("sdm.collect.base.DATA_RAW", tmp_path)
    c = ImfDataMapperCollector(http=ReplayHttp({"GGXWDG_NGDP/USA": FIX / "imf_ggxwdg.json"}))
    spec = next(s for s in c.series() if s.series_id == "US.gg_debt_gdp.IMF_WEO")
    df = c.fetch(spec)
    assert df["date"].max().year <= date.today().year - 1
    assert df["date"].min().year <= 2005


def test_worldbank_parse(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("sdm.collect.base.DATA_RAW", tmp_path)
    c = WorldBankCollector(http=ReplayHttp({"NY.GDP.MKTP.CN": FIX / "worldbank_gdp_multi.json"}))
    spec = next(s for s in c.series() if s.series_id == "AR.ngdp_lcu.WORLDBANK")
    df = c.fetch(spec)
    assert len(df) >= 1 and df["value"].notna().all()
    assert df["value"].max() > 1e3  # ARS bn, not raw units


def test_eurostat_jsonstat_parse(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("sdm.collect.base.DATA_RAW", tmp_path)
    c = EurostatCollector(http=ReplayHttp({"gov_10q_ggdebt": FIX / "eurostat_debt.json"}))
    spec = next(s for s in c.series() if s.series_id == "IT.gg_debt_gdp.EUROSTAT")
    df = c.fetch(spec)
    assert df.iloc[0]["date"] == pd.Timestamp("2024-03-31") and df.iloc[0]["value"] == 134.2


class _Dummy(Collector):
    name = "dummy"

    def series(self) -> list[SeriesSpec]:
        return [SeriesSpec("US", "yield_10y", "DUMMY", "http://x", "D", "%")]

    def fetch(self, spec: SeriesSpec) -> pd.DataFrame:
        return pd.DataFrame({"date": ["2024-01-01", "2024-01-02"], "value": [1.0, 2.0]})


def test_merge_keeps_revisions_with_new_vintage(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("sdm.collect.base.DATA_CLEAN", tmp_path)
    monkeypatch.setattr("sdm.collect.base.DATA_RAW", tmp_path)
    monkeypatch.setattr("sdm.collect.base.CATALOG", tmp_path / "catalog.csv")
    c = _Dummy()
    spec = c.series()[0]
    first = c.tidy(spec, c.fetch(spec), vintage=date(2024, 1, 5))
    store, n_new, n_rev = c.merge_series(c.load_clean(), first)
    assert (n_new, n_rev) == (2, 0)
    revised = c.tidy(
        spec,
        pd.DataFrame({"date": ["2024-01-02", "2024-01-03"], "value": [2.5, 3.0]}),
        vintage=date(2024, 2, 1),
    )
    store, n_new, n_rev = c.merge_series(store, revised)
    assert (n_new, n_rev) == (1, 1)
    assert len(store) == 4  # old 2024-01-02 row is kept
    latest = latest_vintage_frame(store)
    assert latest.set_index("date")["value"].to_dict() == {
        date(2024, 1, 1): 1.0,
        date(2024, 1, 2): 2.5,
        date(2024, 1, 3): 3.0,
    }


def test_catalog_rows_written(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("sdm.collect.base.DATA_CLEAN", tmp_path)
    monkeypatch.setattr("sdm.collect.base.DATA_RAW", tmp_path)
    monkeypatch.setattr("sdm.collect.base.CATALOG", tmp_path / "catalog.csv")
    c = _Dummy()
    res = c.run()
    assert res[0].ok and res[0].n_obs == 2
    cat = pd.read_csv(tmp_path / "catalog.csv")
    assert cat.loc[0, "series_id"] == "US.yield_10y.DUMMY"
    assert cat.loc[0, "n_obs"] == 2

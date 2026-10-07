"""Reserve Bank of Australia statistical tables (verified 2026-10-07).

CSV tables: F2 (bond yields, daily from 2013), F1 (cash rate, daily), A1 (balance sheet,
weekly), G1 (CPI, quarterly), F11 (FX, daily). Historical daily yields before 2013 come
from the xls-hist/f02dhist.xls workbook (1995-2013). CSV layout: title line, then
Title/Description/Frequency/Type/Units/Source/Publication date/Series ID header rows, then
data rows with the date first.
"""

from __future__ import annotations

import io

import pandas as pd
import xlrd

from sdm.collect.base import Collector, SeriesSpec

BASE = "https://www.rba.gov.au/statistics/tables/csv"
F2_HIST = "https://www.rba.gov.au/statistics/tables/xls-hist/f02dhist.xls"

# (concept, table, series_id, freq, units, note)
SERIES = [
    ("yield_2y", "f2-data", "FCMYGBAG2D", "D", "%", "Australian Government 2-year bond yield"),
    ("yield_5y", "f2-data", "FCMYGBAG5D", "D", "%", "Australian Government 5-year bond yield"),
    ("yield_10y", "f2-data", "FCMYGBAG10D", "D", "%", "Australian Government 10-year bond yield"),
    (
        "real_yield_10y",
        "f2-data",
        "FCMYGBAGID",
        "D",
        "%",
        "Australian Government indexed bond yield (~10y real)",
    ),
    ("policy_rate", "f1-data", "FIRMMCRTD", "D", "%", "Cash rate target"),
    ("cb_total_assets_lcu", "a1-data", "ARBAATAW", "W", "AUD bn", "RBA total assets ($m scaled)"),
    ("cpi_index", "g1-data", "GCPIAG", "Q", "index", "CPI all groups"),
    ("fx_lcu_per_usd", "f11-data", "FXRUSD", "D", "AUD per USD", "inverted from AUD/USD"),
]
SCALE = {"ARBAATAW": 1e-3}
INVERT = {"FXRUSD"}
HIST_COL = {"FCMYGBAG2D": 1, "FCMYGBAG5D": 3, "FCMYGBAG10D": 4, "FCMYGBAGID": 5}


def parse_rba_csv(text: str) -> pd.DataFrame:
    lines = text.lstrip("﻿").splitlines()
    hdr = next(i for i, ln in enumerate(lines) if ln.startswith("Series ID"))
    ids = [c.strip() for c in lines[hdr].split(",")]
    data = "\n".join(lines[hdr + 1 :])
    df = pd.read_csv(io.StringIO(data), header=None, names=ids)
    df = df.rename(columns={ids[0]: "date"})
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
    return df.dropna(subset=["date"])


class RbaCollector(Collector):
    name = "rba"

    def series(self) -> list[SeriesSpec]:
        return [
            SeriesSpec(
                "AU",
                concept,
                "RBA",
                f"{BASE}/{table}.csv",
                freq,
                units,
                f"{sid}: {note}",
                params={"table": table, "id": sid},
            )
            for concept, table, sid, freq, units, note in SERIES
        ]

    def _hist(self, sid: str) -> pd.DataFrame:
        raw = self.http.get_bytes(F2_HIST)
        self.cache_raw("f02dhist", raw, "xls")
        sh = xlrd.open_workbook(file_contents=raw).sheet_by_index(0)
        mn = sh.row_values(10)
        col = mn.index(sid)
        rows = []
        for i in range(11, sh.nrows):
            r = sh.row_values(i)
            if isinstance(r[0], float) and r[col] not in ("", None):
                rows.append((pd.Timestamp("1899-12-30") + pd.Timedelta(days=r[0]), float(r[col])))
        return pd.DataFrame(rows, columns=["date", "value"])

    def fetch(self, spec: SeriesSpec) -> pd.DataFrame:
        text = self.http.get_text(spec.url, encoding="utf-8-sig")
        self.cache_raw(spec.params["table"], text, "csv")
        df = parse_rba_csv(text)
        sid = spec.params["id"]
        if sid not in df.columns:
            raise ValueError(f"{sid} not in {spec.params['table']}: {list(df.columns)[:12]}")
        v = pd.to_numeric(df[sid], errors="coerce") * SCALE.get(sid, 1.0)
        out = pd.DataFrame({"date": df["date"], "value": v}).dropna()
        if sid in INVERT:
            out["value"] = 1.0 / out["value"]
        if sid in HIST_COL:
            hist = self._hist(sid)
            out = pd.concat([hist[hist["date"] < out["date"].min()], out], ignore_index=True)
        return out

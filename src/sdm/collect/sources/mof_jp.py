"""Japan Ministry of Finance (verified 2026-10-07).

Yields: jgbcme_all.csv (1974 onwards) + jgbcme.csv (current year); columns Date,1Y,...,40Y.
Outstanding by maturity bucket: gbb/suii.xls ("last five years"), quarterly: general bonds
split into long (>=10y), medium (2-5y), short (<=1y). Gives the bill share.
Holder shares (BoJ, overseas) are not in a machine-readable MoF file; see data/manual/.
"""

from __future__ import annotations

import io

import pandas as pd
import xlrd

from sdm.collect.base import Collector, SeriesSpec

YIELDS_ALL = "https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/historical/jgbcme_all.csv"
YIELDS_NOW = "https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/jgbcme.csv"
SUII = "https://www.mof.go.jp/english/policy/jgbs/reference/gbb/suii.xls"


class MofJpCollector(Collector):
    name = "mof_jp"
    _yields_cache: pd.DataFrame | None = None

    def series(self) -> list[SeriesSpec]:
        s = "JP_MOF"
        out = [
            SeriesSpec(
                "JP",
                concept,
                s,
                YIELDS_ALL,
                "D",
                "%",
                f"JGB {col} constant-maturity yield",
                params={"col": col},
            )
            for concept, col in [
                ("yield_2y", "2Y"),
                ("yield_5y", "5Y"),
                ("yield_10y", "10Y"),
                ("yield_30y", "30Y"),
            ]
        ]
        out.append(
            SeriesSpec(
                "JP",
                "bill_share",
                s,
                SUII,
                "Q",
                "%",
                "T-bills (short-term general and FILP bonds) plus Financing Bills as % of JGBs + FBs, MoF 'suii' table",
                params={"k": "bill"},
            )
        )
        out.append(
            SeriesSpec(
                "JP",
                "marketable_debt_lcu",
                s,
                SUII,
                "Q",
                "JPY bn",
                "JGBs plus Financing Bills outstanding, 100m yen scaled to bn",
                params={"k": "total"},
            )
        )
        return out

    def _yields(self) -> pd.DataFrame:
        if self._yields_cache is None:
            frames = []
            for url, name in ((YIELDS_ALL, "jgbcme_all"), (YIELDS_NOW, "jgbcme")):
                raw = self.http.get_bytes(url)
                self.cache_raw(name, raw, "csv")
                lines = raw.decode("shift_jis", errors="replace").splitlines()
                start = next(i for i, ln in enumerate(lines) if ln.startswith("Date"))
                frames.append(pd.read_csv(io.StringIO("\n".join(lines[start:]))))
            df = pd.concat(frames, ignore_index=True).drop_duplicates("Date", keep="last")
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            self._yields_cache = df.dropna(subset=["Date"])
        return self._yields_cache

    def _suii(self) -> pd.DataFrame:
        """Quarterly outstanding by instrument (100 million yen). Rows are matched on their English
        labels: JGBs total, the two "Short-term (one year or less)" bond rows above "Borrowings",
        and Financing Bills. Marketable = JGBs + Financing Bills; short = short bonds + FBs."""
        raw = self.http.get_bytes(SUII)
        self.cache_raw("suii", raw, "xls")
        sh = xlrd.open_workbook(file_contents=raw).sheet_by_index(0)
        header = sh.row_values(2)
        cols = [
            (j, str(h).split("\n")[-1].strip()) for j, h in enumerate(header) if j >= 3 and str(h).strip()
        ]
        dates = {j: pd.Period(pd.to_datetime(lbl), freq="M").end_time.normalize() for j, lbl in cols}

        def label(i: int) -> str:
            return " ".join(str(c) for c in sh.row_values(i)[:3]).replace("\n", " ")

        def values(i: int) -> list[float]:
            r = sh.row_values(i)
            return [float(r[j]) if r[j] not in ("", "―") else 0.0 for j in dates]

        rows = {i: label(i) for i in range(sh.nrows)}
        jgb = next(i for i, t in rows.items() if "Government Bonds (JGBs)" in t)
        borrow = next(i for i, t in rows.items() if "Borrowings" in t)
        fbs = next(i for i, t in rows.items() if "Financing Bills" in t)
        shorts = [i for i, t in rows.items() if "Short-term (one year or less)" in t and jgb < i < borrow]
        if not shorts:
            raise ValueError("no short-term JGB rows found")
        total = [a + b for a, b in zip(values(jgb), values(fbs), strict=True)]
        short = values(fbs)
        for i in shorts:
            short = [a + b for a, b in zip(short, values(i), strict=True)]
        return pd.DataFrame({"date": list(dates.values()), "total": total, "short": short})

    def fetch(self, spec: SeriesSpec) -> pd.DataFrame:
        if "col" in spec.params:
            df = self._yields()
            return pd.DataFrame(
                {"date": df["Date"], "value": pd.to_numeric(df[spec.params["col"]], errors="coerce")}
            )
        df = self._suii()
        if spec.params["k"] == "bill":
            return pd.DataFrame({"date": df["date"], "value": df["short"] / df["total"] * 100})
        return pd.DataFrame({"date": df["date"], "value": df["total"] * 0.1})  # 100m yen -> bn yen

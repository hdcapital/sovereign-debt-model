"""Bank of England Interactive Database CSV export (verified path 2026-10-07):

https://www.bankofengland.co.uk/boeapps/iadb/fromshowcolumns.asp?csv.x=yes&Datefrom=01/Jan/1970
    &Dateto=now&SeriesCodes=<codes>&CSVF=TN&UsingCodes=Y&VPD=Y&VFD=N
-> CSV: DATE,<code>,... with dates like "02 Jan 2020".
"""

from __future__ import annotations

import io

import pandas as pd

from sdm.collect.base import Collector, SeriesSpec

BASE = "https://www.bankofengland.co.uk/boeapps/iadb/fromshowcolumns.asp"

CODES: dict[str, tuple[str, str, str, str]] = {
    "IUDBEDR": ("policy_rate", "D", "%", "Bank Rate"),
    "IUDMNPY": ("yield_10y", "D", "%", "10-year nominal par gilt yield"),
    "IUDSNPY": ("yield_5y", "D", "%", "5-year nominal par gilt yield"),
    "IUDLNPY": ("yield_30y", "D", "%", "20-year nominal par gilt yield (long slot)"),
    "IUDMIIF": ("breakeven_10y", "D", "%", "10-year implied inflation from gilts"),
    "IUDMRZC": ("real_yield_10y", "D", "%", "10-year real zero-coupon gilt yield"),
}


class BoeCollector(Collector):
    name = "boe"

    def series(self) -> list[SeriesSpec]:
        return [
            SeriesSpec("GB", concept, "BOE", BASE, freq, units, f"{code}: {note}", params={"code": code})
            for code, (concept, freq, units, note) in CODES.items()
        ]

    def fetch(self, spec: SeriesSpec) -> pd.DataFrame:
        code = spec.params["code"]
        params = {
            "csv.x": "yes",
            "Datefrom": "01/Jan/1970",
            "Dateto": "now",
            "SeriesCodes": code,
            "CSVF": "TN",
            "UsingCodes": "Y",
            "VPD": "Y",
            "VFD": "N",
        }
        text = self.http.get_text(spec.url, params)
        self.cache_raw(code, text, "csv")
        if not text.lstrip().startswith("DATE"):
            raise ValueError(f"not a CSV response: {text[:120]!r}")
        df = pd.read_csv(io.StringIO(text)).iloc[:, :2]
        df.columns = ["date", "value"]
        df["date"] = pd.to_datetime(df["date"], format="%d %b %Y", errors="coerce")
        return df.dropna(subset=["date"])

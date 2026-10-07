"""IMF Arslanalp-Tsuda sovereign investor base for advanced economies.

The IMF distributes the workbook inside a zip (wp12284.zip). Sheets "Table 1. Total",
"Table 2. Foreign", "Table 3.1 DomesticCentralBank", "Table 3.2 DomesticBank",
"Table 3.3 DomesticNonbank" are country-by-quarter grids in billions of local currency,
quarters from 2004Q1. Shares are computed here as table / total * 100.

The vintage reachable at the public URL ends in 2016; later vintages live behind the IMF
data portal and are handled by the manual collector when obtained. See docs/DATA_GAPS.md.
"""

from __future__ import annotations

import io
import zipfile

import openpyxl
import pandas as pd

from sdm.collect.base import Collector, SeriesSpec

URL = "https://www.imf.org/external/pubs/ft/wp/2012/Data/wp12284.zip"

COUNTRIES = {
    "US": "United States",
    "GB": "United Kingdom",
    "JP": "Japan",
    "AU": "Australia",
    "CA": "Canada",
    "CH": "Switzerland",
    "DE": "Germany",
    "FR": "France",
    "IT": "Italy",
    "NL": "Netherlands",
    "GR": "Greece",
    "SE": "Sweden",
}
SHEETS = {
    "foreign_share": "Table 2. Foreign",
    "cb_gov_share": "Table 3.1 DomesticCentralBank",
    "domestic_bank_share": "Table 3.2 DomesticBank",
    "domestic_nonbank_share": "Table 3.3 DomesticNonbank",
}
TOTAL = "Table 1. Total"


def _grid(ws: openpyxl.worksheet.worksheet.Worksheet) -> pd.DataFrame:
    rows = list(ws.iter_rows(values_only=True))
    header = rows[0]
    quarters = [str(h) for h in header[1:] if h is not None and str(h)[:2] == "20"]
    out = {}
    for r in rows[1:]:
        name = r[0]
        if not isinstance(name, str) or not name.strip() or str(name).startswith("="):
            continue
        vals = []
        for v in r[1 : 1 + len(quarters)]:
            try:
                vals.append(float(v))
            except (TypeError, ValueError):
                vals.append(float("nan"))
        out[name.strip()] = vals
    df = pd.DataFrame(out, index=quarters).T
    return df


class ArslanalpTsudaCollector(Collector):
    name = "arslanalp_tsuda"
    _cache: dict[str, pd.DataFrame] | None = None

    def series(self) -> list[SeriesSpec]:
        out = []
        for cc, name in COUNTRIES.items():
            for concept, sheet in SHEETS.items():
                out.append(
                    SeriesSpec(
                        cc,
                        concept,
                        "IMF_AT",
                        URL,
                        "Q",
                        "% of general government debt",
                        f"Arslanalp-Tsuda (2012 WP, 2016 vintage): {sheet} / Total, {name}",
                        params={"name": name, "sheet": sheet},
                    )
                )
        return out

    def _tables(self) -> dict[str, pd.DataFrame]:
        if self._cache is None:
            raw = self.http.get_bytes(URL)
            self.cache_raw("wp12284", raw, "zip")
            z = zipfile.ZipFile(io.BytesIO(raw))
            xlsx = next(n for n in z.namelist() if n.lower().endswith(".xlsx"))
            wb = openpyxl.load_workbook(io.BytesIO(z.read(xlsx)), read_only=True, data_only=True)
            self._cache = {sn: _grid(wb[sn]) for sn in [TOTAL, *SHEETS.values()]}
        return self._cache

    def fetch(self, spec: SeriesSpec) -> pd.DataFrame:
        tables = self._tables()
        name = spec.params["name"]
        total = tables[TOTAL]
        part = tables[spec.params["sheet"]]
        if name not in total.index or name not in part.index:
            raise ValueError(f"{name} not in workbook: {list(total.index)[:10]}")
        share = (part.loc[name] / total.loc[name] * 100.0).dropna()
        dates = [pd.Period(q, freq="Q").end_time.normalize() for q in share.index]
        return pd.DataFrame({"date": dates, "value": share.values})

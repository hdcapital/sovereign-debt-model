"""Gold in USD, three sources so the series never goes stale:

* datahub.io / datasets/gold-prices (LBMA monthly average, 1833 onwards)
* World Bank Commodity Price Data ("Pink Sheet"), monthly from 1960
* Yahoo Finance GC=F futures, monthly closes from 2000 (freshest)
"""

from __future__ import annotations

import io

import openpyxl
import pandas as pd

from sdm.collect.base import Collector, SeriesSpec
from sdm.collect.concepts import GLOBAL

DATAHUB = "https://raw.githubusercontent.com/datasets/gold-prices/main/data/monthly.csv"
WB_CMO = "https://thedocs.worldbank.org/en/doc/5d903e848db1d1b83e0ec8f744e55570-0350012021/related/CMO-Historical-Data-Monthly.xlsx"
YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F"


class GoldCollector(Collector):
    name = "gold"

    def series(self) -> list[SeriesSpec]:
        return [
            SeriesSpec(
                GLOBAL,
                "gold_usd",
                "LBMA_DATAHUB",
                DATAHUB,
                "M",
                "USD/oz",
                "LBMA monthly average via datasets/gold-prices",
            ),
            SeriesSpec(
                GLOBAL,
                "gold_usd",
                "WB_CMO",
                WB_CMO,
                "M",
                "USD/oz",
                "World Bank Pink Sheet monthly gold price",
            ),
            SeriesSpec(
                GLOBAL,
                "gold_usd",
                "YAHOO",
                YAHOO,
                "M",
                "USD/oz",
                "COMEX gold front future monthly close (GC=F)",
            ),
        ]

    def fetch(self, spec: SeriesSpec) -> pd.DataFrame:
        if spec.source == "LBMA_DATAHUB":
            text = self.http.get_text(spec.url)
            self.cache_raw("datahub_monthly", text, "csv")
            df = pd.read_csv(io.StringIO(text))
            return pd.DataFrame(
                {
                    "date": pd.PeriodIndex(df["Date"], freq="M").to_timestamp(how="end").normalize(),
                    "value": df["Price"],
                }
            )
        if spec.source == "WB_CMO":
            raw = self.http.get_bytes(spec.url)
            self.cache_raw("wb_cmo_monthly", raw, "xlsx")
            wb = openpyxl.load_workbook(io.BytesIO(raw), read_only=True, data_only=True)
            ws = wb["Monthly Prices"]
            rows = list(ws.iter_rows(values_only=True))
            header = rows[4]
            col = next(i for i, h in enumerate(header) if h and str(h).strip().lower() == "gold")
            out = []
            for r in rows[6:]:
                if r[0] and isinstance(r[0], str) and "M" in r[0]:
                    y, m = r[0].split("M")
                    try:
                        out.append((pd.Period(f"{y}-{m}", freq="M").end_time.normalize(), float(r[col])))
                    except (TypeError, ValueError):
                        pass
            return pd.DataFrame(out, columns=["date", "value"])
        if spec.source == "YAHOO":
            payload = self.http.get_json(spec.url, {"range": "max", "interval": "1mo"})
            self.cache_raw("yahoo_gc_monthly", payload, "json")
            res = payload["chart"]["result"][0]
            ts = res["timestamp"]
            close = res["indicators"]["quote"][0]["close"]
            dates = pd.to_datetime(ts, unit="s").to_period("M").to_timestamp(how="end").normalize()
            return pd.DataFrame({"date": dates, "value": close}).dropna()
        raise ValueError(spec.source)

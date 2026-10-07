"""UK Debt Management Office: the gilts-in-issue XML report (D1A) is the only DMO endpoint
that is not behind bot protection (verified 2026-10-07). It is a snapshot of every gilt
with amount outstanding and redemption date, so average remaining maturity, the
index-linked share and the sub-1-year share are computed here for the snapshot date.
History accrues one point per run; the backfill lives in data/manual/."""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pandas as pd

from sdm.collect.base import Collector, SeriesSpec

URL = "https://www.dmo.gov.uk/data/XmlDataReport?reportCode=D1A"


def parse_d1a(xml: bytes) -> pd.DataFrame:
    root = ET.fromstring(xml)
    rows = []
    for el in root.iter("View_GILTS_IN_ISSUE"):
        a = el.attrib
        rows.append(
            {
                "asof": pd.Timestamp(a["CLOSE_OF_BUSINESS_DATE"]),
                "type": a.get("INSTRUMENT_TYPE", "").strip(),
                "redemption": pd.Timestamp(a["REDEMPTION_DATE"]),
                "amount": float(
                    a.get("TOTAL_AMOUNT_INCLUDING_IL_UPLIFT") or a.get("TOTAL_AMOUNT_IN_ISSUE") or 0
                ),
            }
        )
    if not rows:
        raise ValueError("no gilts parsed from D1A")
    return pd.DataFrame(rows)


class DmoCollector(Collector):
    name = "dmo"

    def series(self) -> list[SeriesSpec]:
        s = "UK_DMO"
        return [
            SeriesSpec(
                "GB",
                "avg_maturity_years",
                s,
                URL,
                "Q",
                "years",
                "Gilts in issue: amount-weighted years to redemption (snapshot per run)",
                params={"k": "wam"},
            ),
            SeriesSpec(
                "GB",
                "linker_share",
                s,
                URL,
                "Q",
                "%",
                "Index-linked gilts incl. uplift as % of gilts in issue (snapshot per run)",
                params={"k": "linker"},
            ),
            SeriesSpec(
                "GB",
                "bill_share",
                s,
                URL,
                "Q",
                "%",
                "Gilts redeeming within 1 year as % of gilts in issue (T-bills excluded; snapshot per run)",
                params={"k": "short"},
            ),
            SeriesSpec(
                "GB",
                "marketable_debt_lcu",
                s,
                URL,
                "Q",
                "GBP bn",
                "Gilts in issue incl. IL uplift, £m scaled (snapshot per run)",
                params={"k": "total"},
            ),
        ]

    def fetch(self, spec: SeriesSpec) -> pd.DataFrame:
        raw = self.http.get_bytes(URL)
        self.cache_raw("D1A", raw, "xml")
        g = parse_d1a(raw)
        asof = g["asof"].max()
        total = g["amount"].sum()
        years = (g["redemption"] - asof).dt.days / 365.25
        k = spec.params["k"]
        if k == "wam":
            v = float((years * g["amount"]).sum() / total)
        elif k == "linker":
            v = float(g.loc[g["type"].str.lower().str.contains("index"), "amount"].sum() / total * 100)
        elif k == "short":
            v = float(g.loc[years < 1.0, "amount"].sum() / total * 100)
        else:
            v = float(total * 1e-3)
        return pd.DataFrame({"date": [asof], "value": [v]})

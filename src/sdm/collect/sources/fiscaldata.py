"""US Treasury Fiscal Data API: the gold standard for average vs marginal rate.

https://api.fiscaldata.treasury.gov/services/api/fiscal_service/<endpoint>
JSON: {"data": [...], "meta": {...}, "links": {...}}; paginate with page[number]/page[size].
"""

from __future__ import annotations

import pandas as pd

from sdm.collect.base import Collector, SeriesSpec

BASE = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"
PAGE = 10000


class FiscalDataCollector(Collector):
    name = "fiscaldata"

    def series(self) -> list[SeriesSpec]:
        s = "US_TREASURY"
        return [
            SeriesSpec(
                "US",
                "avg_interest_rate",
                s,
                f"{BASE}/v2/accounting/od/avg_interest_rates",
                "M",
                "%",
                "Average interest rate on total marketable Treasury securities",
                params={"kind": "avg_rate", "filter": "security_desc:eq:Total Marketable"},
            ),
            SeriesSpec(
                "US",
                "marketable_debt_lcu",
                s,
                f"{BASE}/v1/debt/mspd/mspd_table_1",
                "M",
                "USD bn",
                "MSPD table 1: total marketable debt outstanding (millions; scaled)",
                params={"kind": "mspd1", "class": "Total Marketable"},
            ),
            SeriesSpec(
                "US",
                "bills_outstanding_lcu",
                s,
                f"{BASE}/v1/debt/mspd/mspd_table_1",
                "M",
                "USD bn",
                "MSPD table 1: Treasury bills outstanding (millions; scaled)",
                params={"kind": "mspd1", "class": "Bills"},
            ),
            SeriesSpec(
                "US",
                "linkers_outstanding_lcu",
                s,
                f"{BASE}/v1/debt/mspd/mspd_table_1",
                "M",
                "USD bn",
                "MSPD table 1: TIPS outstanding (millions; scaled)",
                params={"kind": "mspd1", "class": "Treasury Inflation-Protected Securities"},
            ),
            SeriesSpec(
                "US",
                "cg_interest_lcu",
                s,
                f"{BASE}/v2/accounting/od/interest_expense",
                "M",
                "USD bn",
                "Interest expense on the public debt, monthly total (scaled from USD)",
                params={"kind": "interest"},
            ),
            SeriesSpec(
                "US",
                "auction_bid_to_cover",
                s,
                f"{BASE}/v1/accounting/od/auctions_query",
                "M",
                "ratio",
                "Average bid-to-cover across 10-year note auctions in the month",
                params={"kind": "auctions"},
            ),
            SeriesSpec(
                "US",
                "avg_maturity_years",
                s,
                f"{BASE}/v1/debt/mspd/mspd_table_3",
                "Q",
                "years",
                "MSPD table 3: amount-weighted years to maturity of all marketable securities, quarter ends",
                params={"kind": "wam"},
            ),
        ]

    def _get_all(self, url: str, extra: dict[str, str]) -> list[dict]:
        rows: list[dict] = []
        page = 1
        while True:
            params = {"page[size]": str(PAGE), "page[number]": str(page), **extra}
            payload = self.http.get_json(url, params)
            data = payload.get("data", [])
            rows.extend(data)
            total_pages = int(payload.get("meta", {}).get("total-pages", 1) or 1)
            if page >= total_pages or not data:
                break
            page += 1
        return rows

    def fetch(self, spec: SeriesSpec) -> pd.DataFrame:
        kind = spec.params["kind"]
        if kind == "avg_rate":
            rows = self._get_all(spec.url, {"filter": spec.params["filter"], "sort": "record_date"})
            self.cache_raw(spec.series_id, rows, "json")
            df = pd.DataFrame(rows)
            return pd.DataFrame({"date": df["record_date"], "value": df["avg_interest_rate_amt"]})
        if kind == "mspd1":
            rows = self._get_all(
                spec.url,
                {
                    "sort": "record_date",
                    "fields": "record_date,security_type_desc,security_class_desc,debt_held_public_mil_amt,total_mil_amt",
                },
            )
            self.cache_raw("mspd_table_1", rows, "json")
            df = pd.DataFrame(rows)
            cls = spec.params["class"]
            sel = df[df["security_class_desc"].str.strip().str.lower() == cls.lower()]
            if sel.empty:
                sel = df[df["security_type_desc"].str.strip().str.lower() == cls.lower()]
            if sel.empty:
                raise ValueError(
                    f"class {cls!r} not found; classes={sorted(df['security_class_desc'].unique())[:30]}"
                )
            col = "debt_held_public_mil_amt" if "debt_held_public_mil_amt" in sel else "total_mil_amt"
            return pd.DataFrame(
                {
                    "date": sel["record_date"],
                    "value": pd.to_numeric(sel[col], errors="coerce") * 1e-3,
                }
            )
        if kind == "interest":
            rows = self._get_all(
                spec.url,
                {"sort": "record_date", "filter": "expense_catg_desc:eq:INTEREST EXPENSE ON PUBLIC ISSUES"},
            )
            self.cache_raw("interest_expense", rows, "json")
            df = pd.DataFrame(rows)
            amt = pd.to_numeric(df["month_expense_amt"], errors="coerce")
            g = df.assign(v=amt).groupby("record_date")["v"].sum()
            return pd.DataFrame({"date": g.index, "value": g.values * 1e-9})
        if kind == "auctions":
            rows = self._get_all(
                spec.url,
                {
                    "sort": "auction_date",
                    "filter": "security_term:eq:10-Year",
                    "fields": "auction_date,security_type,security_term,bid_to_cover_ratio",
                },
            )
            self.cache_raw("auctions_10y", rows, "json")
            df = pd.DataFrame(rows)
            df["btc"] = pd.to_numeric(df["bid_to_cover_ratio"], errors="coerce")
            df["month"] = pd.to_datetime(df["auction_date"]).dt.to_period("M").dt.end_time.dt.normalize()
            g = df.groupby("month")["btc"].mean().dropna()
            return pd.DataFrame({"date": g.index, "value": g.values})
        if kind == "mts":
            rows = self._get_all(
                spec.url,
                {
                    "sort": "record_date",
                    "fields": "record_date,classification_desc,current_month_gross_rcpt_amt,current_month_gross_outly_amt,current_month_dfct_sur_amt",
                },
            )
            self.cache_raw("mts_table_1", rows, "json")
            df = pd.DataFrame(rows)
            month_name = pd.to_datetime(df["record_date"]).dt.strftime("%B")
            sel = df[df["classification_desc"].str.strip() == month_name]
            v = pd.to_numeric(sel[spec.params["col"]], errors="coerce") * 1e-9
            return pd.DataFrame({"date": sel["record_date"], "value": v})
        if kind == "wam":
            return self._wam(spec)
        raise ValueError(kind)

    def _wam(self, spec: SeriesSpec) -> pd.DataFrame:
        """Weighted average maturity at each quarter end from 2001. Table 3 lists every security;
        a reopened CUSIP repeats with outstanding_amt only on its first row, so sum by row."""
        today = pd.Timestamp.today()
        quarter_ends = pd.date_range("2001-03-31", today, freq="QE")
        out = []
        for i in range(0, len(quarter_ends), 8):
            chunk = ",".join(d.strftime("%Y-%m-%d") for d in quarter_ends[i : i + 8])
            rows = self._get_all(
                spec.url,
                {
                    "filter": f"record_date:in:({chunk}),security_type_desc:eq:Marketable",
                    "fields": "record_date,security_class1_desc,maturity_date,outstanding_amt",
                },
            )
            if not rows:
                continue
            df = pd.DataFrame(rows)
            df["amt"] = pd.to_numeric(df["outstanding_amt"], errors="coerce")
            df["rec"] = pd.to_datetime(df["record_date"], errors="coerce")
            df["mat"] = pd.to_datetime(df["maturity_date"], errors="coerce")
            df = df.dropna(subset=["amt", "rec", "mat"])
            df = df[(df["amt"] > 0) & (df["mat"] >= df["rec"])]
            df["years"] = (df["mat"] - df["rec"]).dt.days / 365.25
            for rec, g in df.groupby("rec"):
                out.append((rec, float((g["years"] * g["amt"]).sum() / g["amt"].sum())))
        self.cache_raw("mspd_wam", [(d.isoformat(), v) for d, v in out], "json")
        if not out:
            raise ValueError("no MSPD table 3 rows parsed")
        return pd.DataFrame(out, columns=["date", "value"])

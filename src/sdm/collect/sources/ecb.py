"""ECB Data Portal (SDMX CSV; keys verified 2026-10-07) plus the PSPP breakdown CSV.

GET https://data-api.ecb.europa.eu/service/data/<FLOW>/<KEY>?format=csvdata
"""

from __future__ import annotations

import io

import pandas as pd

from sdm.collect.base import Collector, SeriesSpec
from sdm.collect.sources.bis import parse_period

BASE = "https://data-api.ecb.europa.eu/service/data"
PSPP = "https://www.ecb.europa.eu/mopo/pdf/PSPP_breakdown_history.csv"

MEMBERS = {"DE": "DE", "FR": "FR", "IT": "IT", "NL": "NL", "GR": "GR"}
AREAS = {**MEMBERS, "EA": "U2"}
PSPP_NAMES = {"DE": "Germany", "FR": "France", "IT": "Italy", "NL": "the Netherlands", "GR": "Greece"}


class EcbCollector(Collector):
    name = "ecb"
    _pspp: pd.DataFrame | None = None

    def series(self) -> list[SeriesSpec]:
        out: list[SeriesSpec] = []
        for cc, area in AREAS.items():
            out.append(
                SeriesSpec(
                    cc,
                    "yield_10y",
                    "ECB",
                    f"{BASE}/IRS/M.{area}.L.L40.CI.0000.EUR.N.Z",
                    "M",
                    "%",
                    "Long-term interest rate for convergence purposes (10y government bond)",
                )
            )
        for cc, area in MEMBERS.items():
            out.append(
                SeriesSpec(
                    cc,
                    "target2_balance_lcu",
                    "ECB",
                    f"{BASE}/TGB/M.{area}.N.A094T.U2.EUR.E",
                    "M",
                    "EUR bn",
                    "TARGET balance, end of month (EUR m scaled)",
                    params={"scale": 1e-3},
                )
            )
            out.append(
                SeriesSpec(
                    cc,
                    "gg_debt_lcu",
                    "ECB",
                    f"{BASE}/GFS/Q.N.{area}.W0.S13.S1.C.L.LE.GD.T._Z.XDC._T.F.V.N._T",
                    "Q",
                    "EUR bn",
                    "Maastricht debt, EUR m scaled",
                    params={"scale": 1e-3},
                )
            )
            out.append(
                SeriesSpec(
                    cc,
                    "gg_interest_lcu",
                    "ECB",
                    f"{BASE}/GFS/Q.N.{area}.W0.S13.S1.C.D.D41._Z._Z._T.XDC._Z.S.V.N._T",
                    "Q",
                    "EUR bn",
                    "Interest payable (D41 debit), quarterly flow, EUR m scaled",
                    params={"scale": 1e-3},
                )
            )
            out.append(
                SeriesSpec(
                    cc,
                    "gg_net_lending_gdp",
                    "ECB",
                    f"{BASE}/GFS/Q.N.{area}.W0.S13.S1._Z.B.B9._Z._Z._Z.XDC_R_B1GQ._Z.S.V.N._T",
                    "Q",
                    "% GDP",
                    "Net lending/borrowing (B9), % of GDP, quarterly",
                )
            )
            out.append(
                SeriesSpec(
                    cc,
                    "ngdp_lcu",
                    "ECB",
                    f"{BASE}/MNA/Q.Y.{area}.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR.V.N",
                    "Q",
                    "EUR bn",
                    "Nominal GDP, SA, EUR m scaled",
                    params={"scale": 1e-3},
                )
            )
            out.append(
                SeriesSpec(
                    cc,
                    "marketable_debt_lcu",
                    "ECB",
                    f"{BASE}/GFS/Q.N.{area}.W0.S13.S1.C.L.LE.F3.T._Z.XDC._T.F.V.N._T",
                    "Q",
                    "EUR bn",
                    "General government debt securities, all original maturities, face value, EUR m scaled",
                    params={"scale": 1e-3},
                    variant="GFS",
                )
            )
            out.append(
                SeriesSpec(
                    cc,
                    "bills_outstanding_lcu",
                    "ECB",
                    f"{BASE}/GFS/Q.N.{area}.W0.S13.S1.C.L.LE.F3.S._Z.XDC._T.F.V.N._T",
                    "Q",
                    "EUR bn",
                    "General government short-term debt securities (original maturity < 1y), face value, EUR m scaled",
                    params={"scale": 1e-3},
                    variant="GFS",
                )
            )
            out.append(
                SeriesSpec(
                    cc,
                    "cb_gov_holdings_lcu",
                    "ECB_PSPP",
                    PSPP,
                    "M",
                    "EUR bn",
                    "Cumulative PSPP net purchases of the member's public sector securities (book value, EUR m scaled); PEPP excluded",
                    params={"pspp": PSPP_NAMES[cc]},
                )
            )
        out.append(
            SeriesSpec(
                "EA",
                "policy_rate",
                "ECB",
                f"{BASE}/FM/B.U2.EUR.4F.KR.DFR.LEV",
                "D",
                "%",
                "Deposit facility rate",
            )
        )
        out.append(
            SeriesSpec(
                "EA",
                "yield_2y",
                "ECB",
                f"{BASE}/YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_2Y",
                "D",
                "%",
                "Euro area AAA spot 2y",
            )
        )
        out.append(
            SeriesSpec(
                "EA",
                "cb_total_assets_lcu",
                "ECB",
                f"{BASE}/ILM/W.U2.C.T000000.Z5.Z01",
                "W",
                "EUR bn",
                "Eurosystem total assets, EUR m scaled",
                params={"scale": 1e-3},
            )
        )
        out.append(
            SeriesSpec(
                "EA",
                "ngdp_lcu",
                "ECB",
                f"{BASE}/MNA/Q.Y.I9.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR.V.N",
                "Q",
                "EUR bn",
                "Euro area nominal GDP, SA, EUR m scaled",
                params={"scale": 1e-3},
            )
        )
        out.append(
            SeriesSpec(
                "EA",
                "gg_interest_lcu",
                "ECB",
                f"{BASE}/GFS/Q.N.I9.W0.S13.S1.C.D.D41._Z._Z._T.XDC._Z.S.V.N._T",
                "Q",
                "EUR bn",
                "Euro area interest payable, quarterly flow, EUR m scaled",
                params={"scale": 1e-3},
            )
        )
        out.append(
            SeriesSpec(
                "EA",
                "gg_net_lending_gdp",
                "ECB",
                f"{BASE}/GFS/Q.N.I9.W0.S13.S1._Z.B.B9._Z._Z._Z.XDC_R_B1GQ._Z.S.V.N._T",
                "Q",
                "% GDP",
                "Euro area net lending/borrowing, % of GDP, quarterly",
            )
        )
        return out

    def _pspp_table(self) -> pd.DataFrame:
        if self._pspp is None:
            text = self.http.get_text(PSPP)
            self.cache_raw("PSPP_breakdown_history", text, "csv")
            lines = text.splitlines()
            start = next(i for i, ln in enumerate(lines) if ln.startswith("Monthly net purchases"))
            header = lines[start + 1].split(",")
            dates = [pd.to_datetime(d, dayfirst=True, errors="coerce") for d in header[1:]]
            rows = {}
            for ln in lines[start + 2 :]:
                parts = ln.split(",")
                if not parts[0] or parts[0].startswith(("In EUR", "Figures", "WAM")):
                    if parts[0].startswith("WAM"):
                        break
                    continue
                vals = [pd.to_numeric(p, errors="coerce") for p in parts[1 : 1 + len(dates)]]
                rows[parts[0].strip()] = vals
            self._pspp = pd.DataFrame(rows, index=dates).dropna(how="all")
        return self._pspp

    def fetch(self, spec: SeriesSpec) -> pd.DataFrame:
        if "pspp" in spec.params:
            t = self._pspp_table()
            name = spec.params["pspp"]
            if name not in t.columns:
                raise ValueError(f"{name} not in PSPP table: {list(t.columns)[:10]}")
            cum = t[name].fillna(0).cumsum() * 1e-3
            return pd.DataFrame({"date": t.index, "value": cum.values})
        text = self.http.get_text(spec.url, {"format": "csvdata"})
        self.cache_raw(spec.series_id, text, "csv")
        df = pd.read_csv(io.StringIO(text))
        if "TIME_PERIOD" not in df.columns:
            raise ValueError(f"unexpected columns {list(df.columns)[:6]}: {text[:150]!r}")
        v = pd.to_numeric(df["OBS_VALUE"], errors="coerce") * spec.params.get("scale", 1.0)
        return pd.DataFrame({"date": df["TIME_PERIOD"].map(parse_period), "value": v})

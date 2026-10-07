"""The concept vocabulary: the contract between collectors and indicators.

A collector may only emit concepts listed here; an indicator may only consume them.
Units are fixed per concept so sources are interchangeable."""

from __future__ import annotations

CONCEPTS: dict[str, str] = {
    # --- fiscal stocks and flows (general government unless noted; "cg_" = central government)
    "gg_debt_gdp": "gross general government debt, % of GDP",
    "gg_debt_lcu": "gross general government debt, local currency bn",
    "cg_debt_lcu": "central government debt, local currency bn (US: debt held by the public)",
    "gg_primary_balance_gdp": "primary balance, % of GDP, surplus positive (annual or 4q)",
    "gg_net_lending_gdp": "net lending/borrowing, % of GDP, surplus positive",
    "gg_interest_gdp": "interest paid, % of GDP",
    "gg_interest_lcu": "interest paid, local currency bn, flow per period",
    "gg_revenue_gdp": "revenue, % of GDP",
    "cg_receipts_lcu": "central government receipts, local currency bn, flow per period",
    "cg_outlays_lcu": "central government outlays, local currency bn, flow per period",
    "cg_interest_lcu": "central government interest expense, local currency bn, flow per period",
    "ngdp_lcu": "nominal GDP, local currency bn, flow per period (not annualised)",
    "ngdp_growth": "nominal GDP growth, % per year",
    "rgdp_growth": "real GDP growth, % per year",
    # --- prices and rates
    "cpi_index": "consumer price index level",
    "cpi_yoy": "CPI inflation, % year on year",
    "policy_rate": "central bank policy rate, %",
    "yield_3m": "3-month government bill yield, %",
    "yield_2y": "2-year government bond yield, %",
    "yield_5y": "5-year government bond yield, %",
    "yield_10y": "10-year government bond yield, %",
    "yield_30y": "30-year government bond yield, %",
    "real_yield_10y": "10-year inflation-linked real yield, %",
    "breakeven_10y": "10-year breakeven inflation, %",
    "term_premium_10y": "10-year term premium estimate, %",
    "avg_interest_rate": "average interest rate on the outstanding debt stock, %",
    # --- holders and structure
    "cb_gov_holdings_lcu": "central bank holdings of government debt, local currency bn",
    "cb_gov_share": "central bank share of government debt, %",
    "foreign_gov_holdings_lcu": "non-resident holdings of government debt, local currency bn",
    "foreign_share": "non-resident share of government debt, %",
    "domestic_bank_share": "domestic bank share of government debt, %",
    "domestic_nonbank_share": "domestic non-bank share of government debt, %",
    "avg_maturity_years": "average remaining maturity of marketable debt, years",
    "bill_share": "bills (< 1y) as % of marketable debt",
    "linker_share": "inflation-linked as % of marketable debt",
    "marketable_debt_lcu": "marketable debt outstanding, local currency bn",
    "bills_outstanding_lcu": "bills outstanding, local currency bn",
    "linkers_outstanding_lcu": "inflation-linked outstanding, local currency bn",
    "household_fin_assets_lcu": "household financial assets, local currency bn",
    "niip_gdp": "net international investment position, % of GDP",
    "target2_balance_lcu": "TARGET2 balance, EUR bn (liability negative)",
    # --- central bank and markets
    "cb_total_assets_lcu": "central bank total assets, local currency bn",
    "fx_lcu_per_usd": "exchange rate, local currency per USD",
    "reer_broad": "broad real effective exchange rate index",
    "gold_usd": "gold price, USD per troy ounce",
    "fx_reserves_usd": "official reserve assets, USD bn",
    "auction_bid_to_cover": "auction bid-to-cover ratio",
    "auction_tail_bp": "auction tail, basis points",
    "interest_to_revenue": "interest paid as % of revenue",
    "gg_revenue_lcu": "general government revenue, local currency bn, flow per period",
    "gg_expenditure_lcu": "general government expenditure, local currency bn, flow per period",
    "bond_total_return": "annual total return on long government bonds, % (backtest only)",
    "equity_total_return": "annual total return on equities, % (backtest only)",
}

GLOBAL = "XX"  # country code for series with no country (gold)

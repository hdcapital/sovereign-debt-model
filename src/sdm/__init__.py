"""Sovereign debt spiral monitor.

Subpackages:
    sdm.collect     one collector per data source -> data/raw, data/clean, data/catalog.csv
    sdm.indicators  pure functions from clean data to the quarterly indicator table
    sdm.backtest    lead-time, false-positive, forward-return and forward-r tests
    sdm.report      dashboard, narrative (Claude), email (Gmail API)
"""

__version__ = "0.1.0"

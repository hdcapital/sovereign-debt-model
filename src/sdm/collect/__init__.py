"""Data collectors. One module per source, each exposing a ``Collector`` subclass.

Contract (see ``base.py``): fetch raw -> cache to data/raw/<source>/ -> tidy long Parquet in
data/clean/ -> one catalog row per series. Collectors never silently forward-fill.
"""

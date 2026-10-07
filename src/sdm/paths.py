"""Repository paths. Everything is relative to the repo root so the code runs from a clean
clone or from GitHub Actions without configuration."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config"
DOCS = ROOT / "docs"
DATA = ROOT / "data"
DATA_RAW = DATA / "raw"
DATA_CLEAN = DATA / "clean"
DATA_MANUAL = DATA / "manual"
CATALOG = DATA / "catalog.csv"
EVENTS = DATA / "events.csv"
REPORTS = ROOT / "reports"
PROMPTS = ROOT / "prompts"
SECRETS = ROOT / ".secrets"

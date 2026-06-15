"""Sanity tests for the refactored pipeline."""
import os
import tempfile

import pandas as pd
import pytest

from src.data import build_dataset
from src.db import SalesDB
from src.analytics import HEALTH_VIEW, STALLED_DEALS_SQL, AT_RISK_DEALS_SQL, SUMMARY_SQL


def test_build_dataset_returns_expected_tables():
    with tempfile.TemporaryDirectory() as tmp:
        raw_dir = os.path.join(tmp, "data")
        # We download the real CSVs here so the test reflects the real data.
        deals, activities, teams = build_dataset(raw_dir)
        assert len(deals) > 0
        assert len(activities) > 0
        assert len(teams) > 0
        assert "value" in deals.columns
        assert "stage" in deals.columns


def test_sqlite_analytics_run():
    with tempfile.TemporaryDirectory() as tmp:
        raw_dir = os.path.join(tmp, "data")
        deals, activities, teams = build_dataset(raw_dir)
        db_path = os.path.join(tmp, "test.db")
        db = SalesDB(db_path)
        db.load_dataframe("deals", deals)
        db.load_dataframe("activity_logs", activities)
        db.load_dataframe("sales_teams", teams)
        db.run_script(HEALTH_VIEW)

        stalled = db.query(STALLED_DEALS_SQL)
        at_risk = db.query(AT_RISK_DEALS_SQL)
        summary = db.query(SUMMARY_SQL)

        assert isinstance(stalled, pd.DataFrame)
        assert isinstance(at_risk, pd.DataFrame)
        assert len(summary) == 1
        db.close()

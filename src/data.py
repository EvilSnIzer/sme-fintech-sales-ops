"""Download, clean, and transform the public CRM dataset.

This module started as a giant cell in the first draft notebook. I split it
out so I could test the transformation independently of the database and
alerting logic.
"""
import os
import random
from datetime import date, timedelta

import pandas as pd
import requests

from src.config import (
    DATASET_BASE_URL,
    PRODUCT_MAP,
    STAGE_MAP,
    SIMULATED_TODAY,
)


def _fetch_csv(filename: str, raw_dir: str) -> str:
    """Download a CSV from the public dataset if it isn't already local."""
    path = os.path.join(raw_dir, filename)
    if not os.path.exists(path):
        os.makedirs(raw_dir, exist_ok=True)
        url = DATASET_BASE_URL + filename
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(path, "wb") as f:
            f.write(response.content)
    return path


def _load_sales_pipeline(raw_dir: str) -> pd.DataFrame:
    """Load the core deals table and rename columns to our pipeline language."""
    path = _fetch_csv("sales_pipeline.csv", raw_dir)
    df = pd.read_csv(path)
    df = df.rename(
        columns={
            "opportunity_id": "deal_id",
            "sales_agent": "rep",
            "product": "product_code",
            "account": "account",
            "deal_stage": "stage",
            "engage_date": "created_date",
            "close_date": "expected_close_date",
            "close_value": "value",
        }
    )
    return df


def _load_sales_teams(raw_dir: str) -> pd.DataFrame:
    """Load sales team metadata so we can enrich rep performance later."""
    path = _fetch_csv("sales_teams.csv", raw_dir)
    return pd.read_csv(path).rename(
        columns={
            "sales_agent": "rep",
            "manager": "manager",
            "regional_office": "region",
        }
    )


def _load_accounts(raw_dir: str) -> pd.DataFrame:
    """Load account metadata to filter SME accounts."""
    path = _fetch_csv("accounts.csv", raw_dir)
    return pd.read_csv(path).rename(
        columns={
            "account": "account",
            "sector": "sector",
            "year_established": "year_established",
            "revenue": "revenue",
            "employees": "employees",
            "office_location": "office_location",
            "subsidiary_of": "parent_account",
        }
    )


def _load_products(raw_dir: str) -> pd.DataFrame:
    """Load product pricing so we can estimate open deal values."""
    path = _fetch_csv("products.csv", raw_dir)
    return pd.read_csv(path).rename(
        columns={
            "product": "product_code",
            "series": "series",
            "sales_price": "sales_price",
        }
    )


def _shift_dates_to_today(df: pd.DataFrame) -> pd.DataFrame:
    """Shift dates so the stale dataset feels like a live pipeline.

    The original data ends in 2017. We move every date forward so that the
    latest expected close is about 30 days before the simulated "today".
    That makes the stalled/at-risk logic produce meaningful results.
    """
    df["created_date"] = pd.to_datetime(df["created_date"])
    df["expected_close_date"] = pd.to_datetime(df["expected_close_date"])

    # Some deals have missing dates. Fill them so downstream SQL and activity
    # generation don't have to worry about NaT.
    df["created_date"] = df["created_date"].fillna(
        df["expected_close_date"] - pd.Timedelta(days=30)
    )
    df["expected_close_date"] = df["expected_close_date"].fillna(
        df["created_date"] + pd.Timedelta(days=30)
    )

    max_close = df["expected_close_date"].max()
    # Shift the whole timeline so the latest expected close is ~30 days in the
    # future. That gives us a mix of overdue, soon-to-close, and later deals.
    target = pd.Timestamp(SIMULATED_TODAY) + pd.Timedelta(days=30)
    offset = target - max_close

    df["created_date"] = (df["created_date"] + offset).dt.date.astype(str)
    df["expected_close_date"] = (df["expected_close_date"] + offset).dt.date.astype(str)
    return df


def _synthesize_activities(deals: pd.DataFrame, random_seed: int = 42) -> pd.DataFrame:
    """Build fake activity logs because the public dataset doesn't have them."""
    random.seed(random_seed)
    rows = []
    for _, deal in deals.iterrows():
        n = random.randint(2, 8)
        start = date.fromisoformat(deal["created_date"])
        # For open deals, activity runs up to today. For closed deals, it stops
        # at the close date.
        if deal["status"] == "Open":
            end = SIMULATED_TODAY
        else:
            end = date.fromisoformat(deal["expected_close_date"])
        if end < start:
            end = start + timedelta(days=1)
        for i in range(n):
            days = max(0, (end - start).days)
            d = start + timedelta(days=random.randint(0, days))
            rows.append(
                {
                    "activity_id": f"ACT_{deal['deal_id']}_{i}",
                    "deal_id": deal["deal_id"],
                    "activity_type": random.choice(["Call", "Email", "Meeting"]),
                    "activity_date": d.isoformat(),
                }
            )
    return pd.DataFrame(rows)


def build_dataset(raw_dir: str = "data") -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return cleaned deals, activities, and enriched rep data."""
    deals = _load_sales_pipeline(raw_dir)
    teams = _load_sales_teams(raw_dir)
    accounts = _load_accounts(raw_dir)
    products = _load_products(raw_dir)

    # Apply fintech-friendly stage and product names
    deals["stage"] = deals["stage"].map(STAGE_MAP)
    deals["product"] = deals["product_code"].map(PRODUCT_MAP).fillna(deals["product_code"])
    deals["status"] = deals["stage"].apply(
        lambda s: "Open" if s not in ("Closed Won", "Closed Lost") else "Closed"
    )

    # The public dataset leaves close_value blank for open deals. We estimate
    # their value from the product price so the ops report still has pipeline.
    deals = deals.merge(products[["product_code", "sales_price"]], on="product_code", how="left")
    deals["value"] = deals["value"].fillna(deals["sales_price"])
    deals["value"] = deals["value"].fillna(0).astype(int)
    deals = deals.drop(columns=["sales_price"])

    # Drop rows that have no activity date. The original dataset has about 500
    # pure prospecting records with no dates; they don't add useful signal.
    deals = deals.dropna(subset=["created_date"]).copy()

    # Make dates current
    deals = _shift_dates_to_today(deals)

    # Filter to SME accounts: under 500 employees or revenue under 1M
    # This is a bit arbitrary but fits the "SME fintech" narrative.
    accounts = accounts[accounts["employees"] < 500]
    deals = deals[deals["account"].isin(accounts["account"])].copy()

    # Enrich deals with rep region/manager
    deals = deals.merge(teams, on="rep", how="left")

    # Add synthetic activity logs
    activities = _synthesize_activities(deals)

    return deals, activities, teams


def save_processed(
    deals: pd.DataFrame,
    activities: pd.DataFrame,
    teams: pd.DataFrame,
    processed_dir: str = "outputs/processed",
) -> None:
    """Save processed CSVs for inspection or Power BI."""
    os.makedirs(processed_dir, exist_ok=True)
    deals.to_csv(os.path.join(processed_dir, "deals.csv"), index=False)
    activities.to_csv(os.path.join(processed_dir, "activities.csv"), index=False)
    teams.to_csv(os.path.join(processed_dir, "teams.csv"), index=False)

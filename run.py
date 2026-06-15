"""Entry point for the SME Fintech Sales Ops pipeline.

This is the cleaned-up version of the messy notebook in `notebooks/`.
I run it once for a demo, or schedule it for daily automation.
"""
import argparse

from src.config import (
    DB_PATH,
    REPORT_PATH,
    POWERBI_CSV_PATH,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
)
from src.data import build_dataset, save_processed
from src.db import SalesDB
from src.analytics import (
    HEALTH_VIEW,
    STALLED_DEALS_SQL,
    AT_RISK_DEALS_SQL,
    REP_PERFORMANCE_SQL,
    SUMMARY_SQL,
    POWERBI_EXPORT_SQL,
)
from src.reports import ExcelReport
from src.alerts import send_slack_alert


def run_pipeline_once() -> dict:
    """Execute one full pipeline run and return key metrics."""
    # 1. Build the dataset
    deals, activities, teams = build_dataset(RAW_DATA_DIR)
    save_processed(deals, activities, teams, PROCESSED_DATA_DIR)

    # 2. Load into SQLite
    db = SalesDB(DB_PATH)
    db.load_dataframe("deals", deals)
    db.load_dataframe("activity_logs", activities)
    db.load_dataframe("sales_teams", teams)
    db.run_script(HEALTH_VIEW)

    # 3. Detect patterns
    stalled = db.query(STALLED_DEALS_SQL)
    at_risk = db.query(AT_RISK_DEALS_SQL)
    rep_performance = db.query(REP_PERFORMANCE_SQL)
    summary = db.query(SUMMARY_SQL)
    powerbi_df = db.query(POWERBI_EXPORT_SQL)

    # 4. Enrich summary
    summary["stalled_count"] = len(stalled)
    summary["at_risk_count"] = len(at_risk)
    summary["stalled_value"] = stalled["value"].sum() if not stalled.empty else 0
    summary["at_risk_value"] = at_risk["value"].sum() if not at_risk.empty else 0

    summary_dict = summary.iloc[0].to_dict()

    # 5. Write Excel report
    report = ExcelReport(REPORT_PATH)
    report.write(
        {
            "Summary": summary,
            "Stalled Deals": stalled,
            "At-Risk Accounts": at_risk,
            "Rep Performance": rep_performance,
            "All Deals": db.query("SELECT * FROM v_deal_health"),
            "Activity Logs": activities,
        }
    )

    # 6. Export for Power BI
    powerbi_df.to_csv(POWERBI_CSV_PATH, index=False)

    # 7. Slack alert
    send_slack_alert(
        stalled_count=summary_dict["stalled_count"],
        at_risk_count=summary_dict["at_risk_count"],
        open_pipeline=summary_dict.get("open_pipeline_value", 0),
        report_path=REPORT_PATH,
    )

    db.close()

    return {
        "summary": summary_dict,
        "stalled_count": len(stalled),
        "at_risk_count": len(at_risk),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="SME Fintech Sales Ops Pipeline")
    parser.add_argument(
        "--run-once",
        action="store_true",
        help="Run the pipeline once now",
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Start the daily scheduler",
    )
    args = parser.parse_args()

    if args.run_once:
        run_pipeline_once()
    elif args.schedule:
        from src.scheduler import start
        start()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

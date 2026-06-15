"""Daily scheduler wrapper around the pipeline."""
import time

import schedule

from src.config import SCHEDULE_TIME
from run import run_pipeline_once


def _scheduled_job() -> None:
    print(f"[{time.ctime()}] Starting scheduled run...")
    run_pipeline_once()
    print(f"[{time.ctime()}] Scheduled run finished.")


def start() -> None:
    schedule.every().day.at(SCHEDULE_TIME).do(_scheduled_job)
    print(f"Scheduler running. Pipeline fires daily at {SCHEDULE_TIME}.")
    print("Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(60)

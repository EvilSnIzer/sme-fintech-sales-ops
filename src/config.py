"""Config loaded from environment variables.

I kept defaults here so the project works out of the box, but everything
is overridable via a .env file. That makes it easier to run on a laptop,
a server, or a CI job without changing code.
"""
import os
from datetime import date, datetime

from dotenv import load_dotenv

load_dotenv()


RAW_DATA_DIR = os.getenv("RAW_DATA_DIR", "data")
PROCESSED_DATA_DIR = os.getenv("PROCESSED_DATA_DIR", "outputs/processed")
DB_PATH = os.getenv("DB_PATH", "outputs/sales_ops.db")
REPORT_PATH = os.getenv("REPORT_PATH", "outputs/daily_ops_report.xlsx")
POWERBI_CSV_PATH = os.getenv("POWERBI_CSV_PATH", "outputs/powerbi_dataset.csv")

SLACK_ENABLED = os.getenv("SLACK_ENABLED", "false").lower() == "true"
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#sales-ops")

STALLED_DAYS = int(os.getenv("STALLED_DAYS", "7"))
AT_RISK_DAYS = int(os.getenv("AT_RISK_DAYS", "5"))
AT_RISK_CLOSE_WINDOW_DAYS = int(os.getenv("AT_RISK_CLOSE_WINDOW_DAYS", "7"))

SCHEDULE_TIME = os.getenv("SCHEDULE_TIME", "08:00")

# The public dataset is from 2016-2017, so we can pretend "today" is a fixed
# date to make the daily ops concept feel realistic.
_SIMULATED_TODAY = os.getenv("SIMULATED_TODAY", "").strip()
if _SIMULATED_TODAY:
    SIMULATED_TODAY = datetime.strptime(_SIMULATED_TODAY, "%Y-%m-%d").date()
else:
    SIMULATED_TODAY = date.today()


# Public CRM dataset from Maven Analytics, mirrored on GitHub by ikebude.
DATASET_BASE_URL = "https://raw.githubusercontent.com/ikebude/CRM-Sales-Analysis/main/"

# Mapping the generic CRM products to fintech SME products so the portfolio
# has a clear domain story instead of generic "GTX" product names.
PRODUCT_MAP = {
    "GTX Basic": "Basic Payment Gateway",
    "GTX Plus Basic": "Plus Payment Gateway",
    "GTX Plus Pro": "Pro Payment Gateway",
    "GTXPro": "Pro Lending API",
    "MG Advanced": "Advanced Cash Flow",
    "MG Special": "SME Line of Credit",
    "GTK 500": "Enterprise FX Platform",
}

STAGE_MAP = {
    "Prospecting": "Lead",
    "Engaging": "Proposal",
    "Won": "Closed Won",
    "Lost": "Closed Lost",
}

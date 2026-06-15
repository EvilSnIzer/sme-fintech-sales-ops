<p align="center"> <img src="assets/readme_hero.png" alt="SME Fintech Sales Ops Pipeline" style="width:100%; border-radius:8px;"/> </p><p align="center"> <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/> <img src="https://img.shields.io/badge/pandas-2.2-150458?style=flat-square&logo=pandas&logoColor=white" alt="pandas"/> <img src="https://img.shields.io/badge/SQLite-3-003B57?style=flat-square&logo=sqlite&logoColor=white" alt="SQLite"/> <img src="https://img.shields.io/badge/pytest-8.0-0A9E97?style=flat-square&logo=pytest&logoColor=white" alt="pytest"/> <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="MIT"/> </p>
Overview
End-to-end sales operations pipeline for SME fintech. Automates data ingestion, SQL analytics, Excel reporting, and Slack alerting — with zero manual intervention.

Quick Start
Bash

pip install -r requirements.txt
python run.py --run-once      # run once
python run.py --schedule      # daily scheduler (08:00)
Pipeline
text

CRM Dataset → Clean & Transform → SQLite → SQL Analytics
                                      ├── Stalled Deals (7+ days inactive)
                                      ├── At-Risk Accounts (proposal stage)
                                      └── Rep Performance
                                 ┌─────┴─────┐
                          Excel Report     Slack Alert / JSON draft
                                 └─────┬─────┘
                               Power BI CSV Export
Output
File	Description
outputs/daily_ops_report.xlsx	6-sheet Excel report
outputs/sales_ops.db	SQLite — deals, activity_logs, v_deal_health
outputs/powerbi_dataset.csv	Power BI export with is_stalled / is_at_risk flags
outputs/alerts/slack_alert_*.json	Local alert draft (when webhook not set)
Screenshots
Overview	Stalled	At-Risk	Reps
<img src="assets/dashboard_overview.png" width="100%"/>	<img src="assets/dashboard_stalled.png" width="100%"/>	<img src="assets/dashboard_at_risk.png" width="100%"/>	<img src="assets/dashboard_reps.png" width="100%"/>
Configuration
Bash

cp .env.example .env
Variable	Default	Description
SLACK_WEBHOOK_URL	—	Slack incoming webhook
SLACK_ENABLED	false	Enable Slack alerts
STALLED_DAYS	7	Inactivity threshold (days)
AT_RISK_DAYS	5	At-risk inactivity threshold
SCHEDULE_TIME	08:00	Daily run time
Structure
text

src/
  config.py    # env config + domain maps
  data.py      # download · clean · transform · synthesize
  db.py        # SQLite wrapper
  analytics.py # SQL detection logic
  reports.py   # Excel report builder
  alerts.py    # Slack webhook + local fallback
  scheduler.py # daily scheduler

tests/
  test_pipeline.py   # pytest checks
Test
Bash

python -m pytest tests/ -v
MIT License · EvilSnIzer

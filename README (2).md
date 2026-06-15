# SME Fintech Sales Ops Pipeline

<p align="center">
  <img src="assets/readme_hero.png" alt="SME Fintech Sales Ops Pipeline" style="width:100%; border-radius:10px;"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/pandas-2.2-150458?style=for-the-badge&logo=pandas&logoColor=white"/>
  <img src="https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white"/>
  <img src="https://img.shields.io/badge/pytest-8.0-0A9E97?style=for-the-badge&logo=pytest&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>
</p>

---

## What it does

Automated end-to-end sales operations pipeline for SME fintech. Downloads raw CRM data, cleans and transforms it, detects stalled deals and at-risk accounts via SQL, produces a formatted Excel report, and sends Slack alerts.

---

## Quick Start

```bash
pip install -r requirements.txt

# Run once
python run.py --run-once

# Schedule daily (runs at 08:00)
python run.py --schedule
```

---

## Pipeline

```
CSV Source → data.py → SQLite → analytics.py → reports.py + alerts.py
                                              ↓           ↓
                                        Excel Report  Slack Alert
                                              ↓
                                        Power BI CSV
```

---

## Output

| | |
|---|---|
| **Excel Report** | `outputs/daily_ops_report.xlsx` — 6 sheets: Summary · Stalled Deals · At-Risk Accounts · Rep Performance · All Deals · Activity Logs |
| **Database** | `outputs/sales_ops.db` — SQLite with `deals`, `activity_logs`, `sales_teams` tables + `v_deal_health` view |
| **Power BI** | `outputs/powerbi_dataset.csv` — full deal list with `is_stalled` and `is_at_risk` flags |
| **Alert Draft** | `outputs/alerts/slack_alert_*.json` — local JSON when Slack webhook is not configured |

---

## Screenshots

| Overview | Stalled Deals | At-Risk Accounts | Rep Performance |
|:---:|:---:|:---:|:---:|
| <img src="assets/dashboard_overview.png" width="100%"/> | <img src="assets/dashboard_stalled.png" width="100%"/> | <img src="assets/dashboard_at_risk.png" width="100%"/> | <img src="assets/dashboard_reps.png" width="100%"/> |

---

## Config

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|:---|:---|
| `SLACK_WEBHOOK_URL` | — | Slack incoming webhook URL |
| `SLACK_ENABLED` | `false` | Set to `true` to enable Slack alerts |
| `STALLED_DAYS` | `7` | Days of inactivity to flag as stalled |
| `AT_RISK_DAYS` | `5` | Days of inactivity to flag as at-risk |
| `SCHEDULE_TIME` | `08:00` | Daily run time |

---

## Structure

```
src/
├── config.py      # env config + product/stage maps
├── data.py        # download · clean · transform · synthesize
├── db.py          # SQLite wrapper
├── analytics.py   # SQL detection logic
├── reports.py     # Excel report builder
├── alerts.py      # Slack webhook + local fallback
└── scheduler.py   # daily scheduler

tests/
└── test_pipeline.py   # pytest checks
```

---

## Test

```bash
python -m pytest tests/ -v
```

---

MIT License · [EvilSnIzer](https://github.com/EvilSnIzer)
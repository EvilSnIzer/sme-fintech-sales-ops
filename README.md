# SME Fintech Sales Ops Pipeline

I built this as a portfolio project to show that I can automate a real sales operations workflow end-to-end with Python.

It takes a public CRM dataset, reshapes it into an SME fintech sales story, loads it into SQLite, flags stalled deals and at-risk accounts with SQL, and produces an Excel report plus a Slack alert. It can also run on a schedule with zero manual intervention.

> **Why this exists:** I wanted a project that feels like a real junior data/ops role — messy input data, cleaning, SQL analytics, reporting, and alerting — rather than a polished toy dataset.

## What it does

1. **Downloads** the public Maven Analytics CRM dataset from a GitHub mirror.
2. **Cleans & re-contextualizes** it as an SME fintech sales pipeline.
3. **Generates** synthetic activity logs (the original dataset doesn't have them).
4. **Loads** everything into SQLite.
5. **Detects**:
   - **Stalled deals** — open deals with no activity in 7 days.
   - **At-risk accounts** — proposal-stage deals closing within 7 days or quiet for 5 days.
6. **Writes** a formatted Excel report with summary, stalled deals, at-risk accounts, and rep performance.
7. **Exports** a Power BI-ready CSV.
8. **Sends** a Slack alert (or saves a local draft if no webhook is set).
9. **Schedules** daily runs with the `schedule` library.

## Tech stack

`Python · Pandas · SQLite · SQL · OpenPyXL · requests · schedule · Slack webhooks · Power BI`

## Folder structure

```
sme-fintech-sales-ops/
├── data/                  # Raw public CRM CSVs + source note
├── notebooks/
│   └── 01_first_draft.ipynb   # My messy first attempt (the "human" version)
├── src/                   # Cleaned-up production-ish code
│   ├── config.py
│   ├── data.py            # Download, clean, transform
│   ├── db.py              # SQLite wrapper
│   ├── analytics.py       # SQL detection logic
│   ├── reports.py         # Excel report builder
│   ├── alerts.py          # Slack webhook / file fallback
│   └── scheduler.py       # Daily scheduler
├── tests/                 # pytest sanity checks
├── powerbi/
│   └── import_guide.md    # How to build the Power BI dashboard
├── run.py                 # CLI entry point
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Quick start

```bash
pip install -r requirements.txt
python run.py --run-once
```

Outputs will appear in `outputs/`:
- `sales_ops.db` — SQLite database with analytic `v_deal_health` view
- `daily_ops_report.xlsx` — styled Excel ops report
- `powerbi_dataset.csv` — Power BI import file
- `alerts/slack_alert_*.json` — Slack message draft (when Slack is disabled)

## Daily scheduler

```bash
python run.py --schedule
```

This runs the pipeline every day at the time set in `.env` (default 08:00).

## Slack setup

1. Create a Slack app at https://api.slack.com/apps
2. Enable **Incoming Webhooks** and copy the webhook URL.
3. Copy `.env.example` to `.env` and set:

```bash
SLACK_ENABLED=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_CHANNEL=#sales-ops
```

If you leave `SLACK_ENABLED=false`, the pipeline still writes the alert message to `outputs/alerts/` so you can inspect it.

## Power BI

See [`powerbi/import_guide.md`](powerbi/import_guide.md) for a step-by-step guide to building the dashboard from `outputs/powerbi_dataset.csv`.

## From messy notebook to clean code

I deliberately kept `notebooks/01_first_draft.ipynb` in the repo. It is a rough, working notebook where I threw everything together to prove the idea. The `src/` folder is the cleaned-up version: config-driven, tested, modular, and easier to schedule.

## Resume bullets

- **Built an end-to-end SME fintech sales operations pipeline in Python that downloads CRM data, cleans it into a fintech context, detects stalled deals and at-risk accounts via SQL, and auto-generates Excel reports and Slack alerts.**
- **Refactored a messy exploratory notebook into a modular, testable pipeline with SQLite, Pandas, and automated scheduling.**
- **Created a Power BI-ready dataset and reporting workflow to deliver daily operational intelligence without manual intervention.**

## Notes / limitations

- The public dataset is from 2016–2017. I shift the dates so the demo feels current, but in a real production job you would use live CRM data.
- Activity logs are synthetic because the public dataset does not include daily CRM activities.
- I filtered to accounts with fewer than 500 employees to match the SME fintech story.

## Data source

Raw data from Maven Analytics, mirrored on GitHub by [ikebude/CRM-Sales-Analysis](https://github.com/ikebude/CRM-Sales-Analysis).

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

```text
sme-fintech-sales-ops/
├── data/                  # Raw public CRM CSVs + source note
├── notebooks/
│   └── 01_first_draft.ipynb   # My messy first attempt
├── src/                   # Cleaned-up modular code
│   ├── config.py
│   ├── data.py            # Download, clean, transform
│   ├── db.py              # SQLite wrapper
│   ├── analytics.py       # SQL detection logic
│   ├── reports.py         # Excel report builder
│   ├── alerts.py          # Slack webhook / file fallback
│   └── scheduler.py       # Daily scheduler
├── tests/                 # pytest sanity checks
├── assets/                # Dashboard screenshots
│   ├── dashboard_overview.png
│   ├── dashboard_reps.png
│   ├── dashboard_at_risk.png
│   ├── dashboard_products.png
│   └── dashboard_stalled.png
├── run.py                 # CLI entry point
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md

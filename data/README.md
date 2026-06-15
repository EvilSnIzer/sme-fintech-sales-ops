# Data source

The raw CSVs in this folder come from **Maven Analytics** CRM Sales Opportunities dataset,
mirrored on GitHub by [ikebude/CRM-Sales-Analysis](https://github.com/ikebude/CRM-Sales-Analysis).

- `sales_pipeline.csv` — deals, stages, agents, close values
- `sales_teams.csv` — agent manager and regional office
- `accounts.csv` — account metadata (sector, revenue, employees)
- `products.csv` — product series and price

I added a small transformation layer to make it feel like an SME fintech sales pipeline:
fintech product names, SME account filtering, and synthetic activity logs (because the
original dataset does not include daily CRM activity).

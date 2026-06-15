# Power BI Dashboard Guide

After running the pipeline, you get a cleaned CSV ready for Power BI:

```
outputs/powerbi_dataset.csv
```

## Connect

1. Open **Power BI Desktop**.
2. **Home → Get data → Text/CSV**.
3. Select `outputs/powerbi_dataset.csv`.
4. Click **Transform Data** to adjust types:
   - `created_date`, `expected_close_date`, `last_activity_date` → **Date**
   - `value`, `open_pipeline`, `stalled_value`, `at_risk_value` → **Currency**
   - `is_stalled`, `is_at_risk` → **Whole number**
5. **Close & Apply**.

## Suggested visuals

| Insight | Visual | Fields |
|---------|--------|--------|
| Pipeline health | Cards | `open_pipeline_value`, `is_stalled`, `is_at_risk` |
| Stalled deals | Table | Account, rep, product, days since last activity |
| At-risk accounts | Stacked bar | Region, `is_at_risk`, `value` |
| Rep leaderboard | Table | Rep, open pipeline, stalled count |
| Deal flow | Line chart | `created_date` (axis), count of `deal_id` |

## Refresh

Run the pipeline again (`python run.py --run-once`) and click **Refresh** in Power BI.
For Power BI Service, point the dataset to the `outputs/powerbi_dataset.csv` file on a
shared drive or OneDrive folder.

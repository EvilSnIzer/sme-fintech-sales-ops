"""SQL analytics used to detect stalled deals and at-risk accounts.

I tried writing these in Pandas first, but it was easier to reason about
window functions and date arithmetic in SQL. SQLite is good enough for a
daily pipeline on a few thousand deals.
"""
from src.config import (
    STALLED_DAYS,
    AT_RISK_DAYS,
    AT_RISK_CLOSE_WINDOW_DAYS,
)

HEALTH_VIEW = f"""
CREATE VIEW IF NOT EXISTS v_deal_health AS
SELECT
    d.deal_id,
    d.account,
    d.rep,
    d.region,
    d.manager,
    d.product,
    d.stage,
    d.status,
    d.value,
    d.created_date,
    d.expected_close_date,
    MAX(a.activity_date) AS last_activity_date,
    CAST(JULIANDAY('now') - JULIANDAY(MAX(a.activity_date)) AS INTEGER) AS days_since_last_activity,
    CAST(JULIANDAY('now') - JULIANDAY(d.created_date) AS INTEGER) AS deal_age_days
FROM deals d
LEFT JOIN activity_logs a ON d.deal_id = a.deal_id
GROUP BY d.deal_id;
"""

STALLED_DEALS_SQL = f"""
SELECT *
FROM v_deal_health
WHERE status = 'Open' AND days_since_last_activity > {STALLED_DAYS}
ORDER BY value DESC;
"""

AT_RISK_DEALS_SQL = f"""
SELECT *
FROM v_deal_health
WHERE status = 'Open'
  AND stage = 'Proposal'
  AND (
      expected_close_date BETWEEN date('now') AND date('now', '+{AT_RISK_CLOSE_WINDOW_DAYS} days')
      OR days_since_last_activity > {AT_RISK_DAYS}
  )
ORDER BY days_since_last_activity DESC, value DESC;
"""

REP_PERFORMANCE_SQL = """
SELECT
    rep,
    region,
    manager,
    COUNT(DISTINCT deal_id) AS open_deals,
    SUM(CASE WHEN status = 'Open' THEN value ELSE 0 END) AS open_pipeline,
    SUM(CASE WHEN status = 'Open' AND days_since_last_activity > 7 THEN 1 ELSE 0 END) AS stalled_count,
    ROUND(AVG(CASE WHEN status = 'Open' THEN days_since_last_activity ELSE NULL END), 1) AS avg_days_since_activity
FROM v_deal_health
GROUP BY rep
ORDER BY open_pipeline DESC;
"""

SUMMARY_SQL = """
SELECT
    COUNT(*) AS total_deals,
    SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) AS open_deals,
    SUM(CASE WHEN stage = 'Closed Won' THEN 1 ELSE 0 END) AS won_deals,
    SUM(CASE WHEN stage = 'Closed Lost' THEN 1 ELSE 0 END) AS lost_deals,
    SUM(CASE WHEN status = 'Open' THEN value ELSE 0 END) AS open_pipeline_value,
    SUM(CASE WHEN stage = 'Closed Won' THEN value ELSE 0 END) AS won_value,
    SUM(CASE WHEN stage = 'Closed Lost' THEN value ELSE 0 END) AS lost_value
FROM v_deal_health;
"""

POWERBI_EXPORT_SQL = """
SELECT
    h.*,
    CASE WHEN h.status = 'Open' AND h.days_since_last_activity > 7 THEN 1 ELSE 0 END AS is_stalled,
    CASE
        WHEN h.status = 'Open'
             AND h.stage = 'Proposal'
             AND (
                 h.expected_close_date BETWEEN date('now') AND date('now', '+7 days')
                 OR h.days_since_last_activity > 5
             )
        THEN 1
        ELSE 0
    END AS is_at_risk
FROM v_deal_health h;
"""

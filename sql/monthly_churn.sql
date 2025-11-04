-- Monthly churn (from raw.churn)
SELECT
  month,
  churned_users,
  total_users_start,
  ROUND(churned_users::numeric / NULLIF(total_users_start,0) * 100, 2) AS churn_rate_pct
FROM raw.churn
ORDER BY month;
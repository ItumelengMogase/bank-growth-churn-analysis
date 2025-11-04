-- cac_conversion_by_channel.sql
-- Output: acquisition_channel, total_spend, total_new_users, cac (USD/user), conversion_rate_pct
SELECT 
  acquisition_channel,
  SUM(acquisition_cost) AS total_spend,
  SUM(new_users) AS total_new_users,
  ROUND(SUM(acquisition_cost)::NUMERIC / NULLIF(SUM(new_users),0), 2) AS cac,
  ROUND(
    AVG(
      CASE 
        WHEN new_users > 0 THEN (first_deposit_users::NUMERIC / NULLIF(new_users,0)) 
        ELSE NULL 
      END
    ) * 100, 2
  ) AS conversion_rate_pct
FROM raw.user_acquisition
GROUP BY acquisition_channel
ORDER BY conversion_rate_pct DESC;

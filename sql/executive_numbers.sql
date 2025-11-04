-- executive_numbers.sql (Corrected, Redundant ELSE NULL removed)
-- Calculates key executive metrics using available monthly aggregated data

WITH churn_halves AS (
  -- Calculate average churn rate for first and second half of 2024 from raw.churn
  SELECT
    -- Average churn rate for Jan-Jun 2024
    ROUND(
      AVG(CASE
        WHEN EXTRACT(MONTH FROM month) BETWEEN 1 AND 6
        THEN (churned_users::NUMERIC / NULLIF(total_users_start, 0) * 100)
      END), -- ELSE NULL is implicit and removed
      2
    ) AS churn_first_half_pct,
    -- Average churn rate for Jul-Dec 2024
    ROUND(
      AVG(CASE
        WHEN EXTRACT(MONTH FROM month) BETWEEN 7 AND 12
        THEN (churned_users::NUMERIC / NULLIF(total_users_start, 0) * 100)
      END), -- ELSE NULL is implicit and removed
      2
    ) AS churn_second_half_pct
  FROM raw.churn
  WHERE EXTRACT(YEAR FROM month) = 2024 -- Filter for 2024 data
),
acquisition_totals AS (
  -- Calculate total new users and total acquisition cost for 2024 from raw.user_acquisition
  SELECT
    SUM(new_users) AS total_new_users_2024,
    SUM(acquisition_cost) AS total_acquisition_spend_2024
  FROM raw.user_acquisition
  WHERE EXTRACT(YEAR FROM month) = 2024 -- Filter for 2024 data
)

-- Combine results from both CTEs
SELECT
  at.total_new_users_2024,
  ch.churn_first_half_pct,
  ch.churn_second_half_pct,
  -- Calculate the difference in average churn rates between the halves
  ROUND((ch.churn_second_half_pct - ch.churn_first_half_pct), 2) AS churn_pct_point_change,
  at.total_acquisition_spend_2024
FROM acquisition_totals at
CROSS JOIN churn_halves ch; -- Join the two single-row results
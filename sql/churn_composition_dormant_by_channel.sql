-- churn_composition_dormant_by_channel.sql (aggregated approximation)
-- This query estimates the proportion of churn attributed to dormant accounts
-- and breaks it down by the acquisition channel of the *overall user base*,
-- as a proxy for the channel associated with churned users.

WITH monthly_churn_breakdown AS (
  -- Get churn numbers and the portion that was dormant from raw.churn
  SELECT
    month,
    churned_users,
    dormant_accounts_churned,
    -- Calculate percentage of churn that was dormant
    ROUND(
      100.0 * dormant_accounts_churned / NULLIF(churned_users, 0), 1
    ) AS pct_dormant_churn
  FROM raw.churn
  WHERE churned_users > 0 -- Only consider months where churn occurred
),
acquisition_by_month AS (
  -- Get total new users acquired per channel per month from raw.user_acquisition
  SELECT
    month,
    acquisition_channel,
    SUM(new_users) AS new_users_in_month
  FROM raw.user_acquisition
  GROUP BY month, acquisition_channel
),
-- Aggregate acquisition_channel totals across *all* months to get a "channel mix"
-- representing the overall user base composition up to each churn month.
channel_totals AS (
  SELECT
    acquisition_channel,
    SUM(new_users_in_month) AS total_users_acquired -- Approximation of channel's share of total base
  FROM acquisition_by_month
  GROUP BY acquisition_channel
),
-- Join churn breakdown with channel totals
churn_with_channel_totals AS (
  SELECT
    mc.month,
    mc.churned_users,
    mc.dormant_accounts_churned,
    mc.pct_dormant_churn,
    ct.acquisition_channel,
    ct.total_users_acquired -- Channel's contribution to the overall user base
  FROM monthly_churn_breakdown mc
  CROSS JOIN channel_totals ct -- Join every churn month with every channel's total
  -- Optional: Add a filter if you want to limit to specific months or channels
  -- WHERE mc.month >= '2024-01' AND mc.month <= '2024-12'
)
-- Calculate the implied churn count and dormant churn count attributed to each channel
-- based on the channel's share of the total user base.
SELECT
  acquisition_channel,
  -- Approximate total churn attributed to this channel based on its user base share
  -- This is a rough estimation: (churned_users_total * channel_share_of_base)
  -- Sum across all months
  SUM(
    churned_users * (total_users_acquired::NUMERIC / 
                     (SELECT SUM(total_users_acquired) FROM channel_totals))
  ) AS estimated_churned_count_attributed_to_channel,
  -- Approximate dormant churn attributed to this channel based on its user base share
  SUM(
    dormant_accounts_churned * (total_users_acquired::NUMERIC / 
                                (SELECT SUM(total_users_acquired) FROM channel_totals))
  ) AS estimated_dormant_churned_count_attributed_to_channel,
  -- Calculate the percentage of *estimated attributed churn* that was dormant for this channel
  ROUND(
    100.0 * SUM(
      dormant_accounts_churned * (total_users_acquired::NUMERIC / 
                                  (SELECT SUM(total_users_acquired) FROM channel_totals))
    ) / NULLIF(
      SUM(
        churned_users * (total_users_acquired::NUMERIC / 
                         (SELECT SUM(total_users_acquired) FROM channel_totals))
      ), 0
    ), 1
  ) AS estimated_pct_dormant_churn_for_channel
FROM churn_with_channel_totals
GROUP BY acquisition_channel
ORDER BY estimated_pct_dormant_churn_for_channel DESC;
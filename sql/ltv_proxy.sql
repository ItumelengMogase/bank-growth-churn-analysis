-- Corrected LTV proxy (channel-level attribution based on monthly data)
WITH monthly_channel_totals AS (
  -- Join transactions and user_acquisition on the 'month' column
  -- Sum up new users and total revenue for each channel-month combination
  SELECT
    ua.month,
    ua.acquisition_channel,
    SUM(ua.new_users) AS new_users_in_month,
    SUM(t.total_revenue) AS total_revenue_in_month -- Use total_revenue from transactions
  FROM raw.user_acquisition ua
  JOIN raw.transactions t ON ua.month = t.month
  GROUP BY ua.month, ua.acquisition_channel
),
channel_aggregates AS (
  -- Aggregate the monthly totals up to the channel level
  SELECT
    acquisition_channel,
    -- Total number of users acquired for this channel across all months
    SUM(new_users_in_month) AS total_users_acquired,
    -- Total revenue attributed to this channel based on its monthly acquisition periods
    SUM(total_revenue_in_month) AS total_revenue_attributed,
    -- Calculate the total attributed revenue divided by the total users acquired
    -- This gives a proxy for average revenue per user acquired for the channel
    -- Uses COALESCE and NULLIF to handle potential division by zero
    COALESCE(
      SUM(total_revenue_in_month)::numeric / NULLIF(SUM(new_users_in_month), 0), 0
    ) AS avg_revenue_per_acquired_user_proxy
  FROM monthly_channel_totals
  GROUP BY acquisition_channel
)
SELECT
  acquisition_channel,
  total_users_acquired,
  ROUND(total_revenue_attributed, 2) AS total_revenue_attributed,
  ROUND(avg_revenue_per_acquired_user_proxy, 2) AS avg_revenue_per_acquired_user_proxy,
  -- Calculate a 12-month LTV proxy by multiplying the monthly revenue proxy by 12
  ROUND(avg_revenue_per_acquired_user_proxy * 12, 2) AS ltv_12_month_proxy
FROM channel_aggregates
ORDER BY avg_revenue_per_acquired_user_proxy DESC;
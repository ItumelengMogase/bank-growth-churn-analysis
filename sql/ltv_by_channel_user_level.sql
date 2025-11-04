-- ltv_by_channel_aggregated_proxy.sql
-- Calculates a proxy for LTV by attributing total revenue to channels based on user acquisition.
-- This is a simplified proxy and has limitations compared to user-level analysis.

-- CTE 1: Calculate total revenue attributed to each month from transactions
WITH monthly_revenue AS (
  SELECT
    month,
    total_revenue -- Use the total_revenue column from raw.transactions
  FROM raw.transactions
),

-- CTE 2: Calculate total new users acquired for each channel across all months
channel_user_totals AS (
  SELECT
    acquisition_channel,
    SUM(new_users) AS total_users_acquired -- Sum of all new users for this channel
  FROM raw.user_acquisition
  GROUP BY acquisition_channel
),

-- CTE 3: Calculate total revenue across all months
total_revenue_overall AS (
  SELECT
    SUM(total_revenue) AS grand_total_revenue -- Sum of total_revenue from all months
  FROM monthly_revenue
),

-- CTE 4: Join revenue (monthly) with user acquisition (channel totals)
-- to calculate revenue attributed to each channel based on its share of total users acquired
channel_revenue_attr AS (
  SELECT
    ua.acquisition_channel,
    ua.total_users_acquired,
    -- Attribute total revenue to the channel proportionally based on its user share
    -- This assumes revenue is evenly distributed relative to user base size per channel
    (mr.grand_total_revenue * (ua.total_users_acquired::NUMERIC / 
       (SELECT SUM(total_users_acquired) FROM channel_user_totals))) AS attributed_revenue
  FROM channel_user_totals ua
  CROSS JOIN total_revenue_overall mr -- Join total revenue with each channel's user total
),

-- CTE 5: Calculate CAC per channel (as in cac_conversion_by_channel.sql)
cac_per_channel AS (
  SELECT
    acquisition_channel,
    ROUND(SUM(acquisition_cost)::NUMERIC / NULLIF(SUM(new_users), 0), 2) AS cac
  FROM raw.user_acquisition
  GROUP BY acquisition_channel
)

-- Final SELECT: Combine attributed revenue (LTV proxy), user counts, and CAC
SELECT
  cra.acquisition_channel,
  cra.total_users_acquired,
  -- Calculate LTV proxy: attributed revenue / total users acquired for the channel
  -- This gives an average revenue per user acquired via this channel over the period
  ROUND(cra.attributed_revenue / NULLIF(cra.total_users_acquired, 0), 2) AS ltv_12m_proxy, -- Renamed for clarity
  cpc.cac,
  -- Calculate LTV:CAC ratio
  ROUND(
    (cra.attributed_revenue / NULLIF(cra.total_users_acquired, 0)) / NULLIF(cpc.cac, 0), 2
  ) AS ltv_cac_ratio_12m_proxy -- Renamed for clarity
FROM channel_revenue_attr cra
JOIN cac_per_channel cpc ON cra.acquisition_channel = cpc.acquisition_channel
ORDER BY ltv_cac_ratio_12m_proxy DESC;
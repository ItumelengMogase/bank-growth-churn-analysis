/*
GESTALT PRINCIPLES APPLIED:
1. Proximity: Group related metrics
2. Similarity: Use consistent formats
3. Enclosure: Separate forecast from actual
4. Closure: Remove unnecessary borders (in viz layer)
5. Continuity: Align related data points
6. Connection: Link cause to effect

CLUTTER REMOVAL RULES:
- No trailing zeros on axis labels
- No diagonal text
- No 3D effects
- No pie charts (Knaflic: "Pie charts are evil")
- No more than 6 colors
*/

-- Clean data for presentation: Remove clutter BEFORE visualization
-- 03_eliminate_clutter.sql (uploaded)
CREATE OR REPLACE VIEW presentation.churn_clean AS
SELECT
    TO_CHAR(month, 'Mon') as month_label,
    ROUND(churned_users::NUMERIC / total_users_start * 100, 1) as churn_pct,
    churned_users as churned,
    total_users_start as user_base,
    CASE WHEN churned_users::NUMERIC / total_users_start * 100 > 6.0 THEN 'CRISIS' ELSE 'NORMAL' END as status,
    EXTRACT(MONTH FROM month) as month_num
FROM raw.churn
WHERE EXTRACT(YEAR FROM month) = 2024
ORDER BY month;

CREATE OR REPLACE VIEW presentation.channel_simple AS
SELECT
    CASE acquisition_channel
        WHEN 'Paid Search' THEN 'Paid Search'
        WHEN 'Social Media' THEN 'Social'
        ELSE acquisition_channel
    END as channel,
    ROUND(AVG(first_deposit_users::NUMERIC / new_users * 100), 0) as conv_rate,
    ROUND(SUM(acquisition_cost) / SUM(new_users), 0) as cac
FROM raw.user_acquisition
GROUP BY acquisition_channel
ORDER BY conv_rate DESC;

-- =====================================================
-- FOCUS ATTENTION: Preattentive Attributes
-- =====================================================

/*
KNAFLIC'S PREATTENTIVE ATTRIBUTES:
- Color: ONE accent color to draw attention
- Size: Bigger = more important
- Position: Top-left is seen first

OUR COLOR STRATEGY:
- Grey: Context data (everything else)
- Blue: Primary story (Referral channel)
- Red/Orange: Problem areas (Social Media, high churn)
- Green: Targets/goals
*/

-- 04_focus_attention.sql (uploaded)
CREATE OR REPLACE VIEW presentation.channel_with_emphasis AS
SELECT
    acquisition_channel,
    ROUND(AVG(first_deposit_users::NUMERIC / new_users * 100), 1) as conversion_rate,
    ROUND(SUM(acquisition_cost) / SUM(new_users), 0) as cac,
    CASE acquisition_channel
        WHEN 'Referral' THEN 'PRIMARY'
        WHEN 'Social Media' THEN 'PROBLEM'
        ELSE 'CONTEXT'
    END as visual_priority,
    CASE acquisition_channel
        WHEN 'Referral' THEN 1
        WHEN 'Social Media' THEN 2
        ELSE 3
    END as display_order
FROM raw.user_acquisition
GROUP BY acquisition_channel
ORDER BY display_order, conversion_rate DESC;

CREATE OR REPLACE VIEW presentation.churn_with_crisis AS
SELECT
    month,
    ROUND(churned_users::NUMERIC / total_users_start * 100, 1) as churn_rate,
    CASE WHEN month >= '2024-08-01' THEN 'CRISIS_PERIOD' ELSE 'NORMAL' END as period_type,
    CASE WHEN churned_users::NUMERIC / total_users_start * 100 > 6.0 THEN 'ABOVE_THRESHOLD' ELSE 'OK' END as threshold_status
FROM raw.churn
WHERE EXTRACT(YEAR FROM month) = 2024
ORDER BY month;

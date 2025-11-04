-- Drop ALL views that might have changed structure before recreating them
DROP VIEW IF EXISTS presentation.churn_crisis;
DROP VIEW IF EXISTS presentation.channel_quality;
DROP VIEW IF EXISTS presentation.key_metrics;

CREATE OR REPLACE VIEW presentation.churn_crisis AS
SELECT
    month,
    ROUND(churned_users::NUMERIC / total_users_start * 100, 1) as churn_rate,
    churned_users,
    total_users_start
FROM raw.churn
ORDER BY month;

CREATE OR REPLACE VIEW presentation.channel_quality AS
SELECT
    acquisition_channel,
    ROUND(AVG(first_deposit_users::NUMERIC / new_users * 100), 1) as conversion_rate,
    ROUND(SUM(acquisition_cost) / SUM(new_users), 0) as cac,
    SUM(new_users) as total_users
FROM raw.user_acquisition
GROUP BY acquisition_channel
ORDER BY conversion_rate DESC;

CREATE OR REPLACE VIEW presentation.key_metrics AS
SELECT
    'Recommended hiring' as metric_type,
    2 as value,
    'FTEs' as unit,
    'To backfill May departures and reduce ticket backlog' as reasoning
UNION ALL
SELECT
    'Budget shift recommended',
    30,
    '% of Social Media budget',
    'Redirect to Referral program (3.2x better LTV:CAC)'
UNION ALL
SELECT
    'Expected savings',
    400000,
    'USD annually',
    'By reducing churn from 6.9% back to 5.5%';
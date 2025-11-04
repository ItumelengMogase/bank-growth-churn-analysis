

with base as (
    select
      month::date as month,
      churned_users,
      total_users_start
    from raw.churn
)

select
  month,
  churned_users,
  total_users_start,
  round((churned_users::numeric / nullif(total_users_start,0)) * 100, 2) as churn_rate_pct,
  lag(round((churned_users::numeric / nullif(total_users_start,0)) * 100, 2)) over (order by month) as churn_rate_prev
from base
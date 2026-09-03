with fact_totals as (
  select
    order_date,
    sum(net_revenue) as net_revenue
  from {{ ref('fct_orders') }}
  group by 1
)

select
  m.metric_date,
  m.net_revenue as mart_net_revenue,
  f.net_revenue as fact_net_revenue
from {{ ref('mart_daily_commerce_kpi') }} m
join fact_totals f on m.metric_date = f.order_date
where m.net_revenue <> f.net_revenue


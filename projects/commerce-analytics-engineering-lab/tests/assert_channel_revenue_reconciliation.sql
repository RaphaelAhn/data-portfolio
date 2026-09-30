-- Channel-attributed revenue must add up to the daily commerce KPI, so no order is dropped or double-counted.
select k.metric_date, k.net_revenue, sum(c.attributed_net_revenue) as channel_revenue
from {{ ref('mart_daily_commerce_kpi') }} k
left join {{ ref('mart_channel_daily_performance') }} c using (metric_date)
group by 1, 2
having coalesce(sum(c.attributed_net_revenue), 0) <> k.net_revenue

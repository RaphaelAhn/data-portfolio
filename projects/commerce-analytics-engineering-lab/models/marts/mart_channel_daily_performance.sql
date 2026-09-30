with spend as (
  select
    s.spend_date as metric_date,
    c.platform as channel,
    sum(s.impressions) as impressions,
    sum(s.clicks) as clicks,
    sum(s.cost) as cost
  from {{ ref('stg_ad_spend') }} s
  join {{ ref('stg_campaigns') }} c using (campaign_id)
  group by 1, 2
),

orders as (
  select
    order_date as metric_date,
    channel,
    count(distinct case when is_recognized_order then order_id end) as attributed_orders,
    sum(net_revenue) as attributed_net_revenue
  from {{ ref('int_order_attribution') }}
  group by 1, 2
)

select
  coalesce(s.metric_date, o.metric_date) as metric_date,
  coalesce(s.channel, o.channel) as channel,
  coalesce(s.impressions, 0) as impressions,
  coalesce(s.clicks, 0) as clicks,
  cast(coalesce(s.cost, 0) as decimal(18, 2)) as cost,
  coalesce(o.attributed_orders, 0) as attributed_orders,
  cast(coalesce(o.attributed_net_revenue, 0) as decimal(18, 2)) as attributed_net_revenue,
  cast(coalesce(o.attributed_net_revenue, 0) / nullif(s.cost, 0) as decimal(18, 4)) as roas,
  cast(s.cost / nullif(o.attributed_orders, 0) as decimal(18, 2)) as cpa,
  cast(s.clicks / nullif(s.impressions, 0) as decimal(18, 4)) as ctr
from spend s
full outer join orders o
  on o.metric_date = s.metric_date
 and o.channel = s.channel

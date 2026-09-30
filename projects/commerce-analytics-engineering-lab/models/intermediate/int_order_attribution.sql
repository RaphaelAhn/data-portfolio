-- Last-click attribution: latest ad click at or before the order, within 7 days.
-- Orders without a qualifying click are attributed to 'organic'.
with qualifying_clicks as (
  select
    o.order_id,
    c.campaign_id,
    row_number() over (partition by o.order_id order by c.clicked_at desc) as click_rank
  from {{ ref('fct_orders') }} o
  join {{ ref('stg_ad_clicks') }} c
    on c.order_id = o.order_id
   and c.clicked_at <= o.ordered_at
   and c.clicked_at >= o.ordered_at - interval 7 day
)

select
  o.order_id,
  o.order_date,
  q.campaign_id,
  coalesce(cmp.platform, 'organic') as channel,
  o.is_recognized_order,
  o.net_revenue
from {{ ref('fct_orders') }} o
left join qualifying_clicks q
  on q.order_id = o.order_id
 and q.click_rank = 1
left join {{ ref('stg_campaigns') }} cmp
  on cmp.campaign_id = q.campaign_id

with item_totals as (
  select
    order_id,
    sum(item_net_amount) as item_net_amount
  from {{ ref('fct_order_items') }}
  group by 1
)

select
  o.order_id,
  o.ordered_net_amount,
  i.item_net_amount
from {{ ref('fct_orders') }} o
join item_totals i using (order_id)
where o.ordered_net_amount <> i.item_net_amount


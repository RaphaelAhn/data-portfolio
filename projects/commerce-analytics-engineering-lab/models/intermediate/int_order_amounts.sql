select
  o.order_id,
  o.customer_id,
  o.order_status,
  o.ordered_at,
  o.updated_at,
  cast(sum(i.quantity * i.list_price) as decimal(18, 2)) as gross_product_amount,
  cast(sum(i.discount_amount) as decimal(18, 2)) as discount_amount,
  cast(sum(i.item_net_amount) as decimal(18, 2)) as ordered_net_amount
from {{ ref('stg_orders') }} o
join {{ ref('stg_order_items') }} i using (order_id)
group by 1, 2, 3, 4, 5

select
  i.order_item_id,
  i.order_id,
  o.customer_id,
  i.product_id,
  cast(o.ordered_at as date) as order_date,
  o.order_status,
  i.quantity,
  i.list_price,
  i.discount_amount,
  i.item_net_amount
from {{ ref('stg_order_items') }} i
join {{ ref('stg_orders') }} o using (order_id)

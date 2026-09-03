select
  cast(order_item_id as varchar) as order_item_id,
  cast(order_id as varchar) as order_id,
  cast(product_id as varchar) as product_id,
  cast(quantity as integer) as quantity,
  cast(list_price as decimal(18, 2)) as list_price,
  cast(discount_amount as decimal(18, 2)) as discount_amount,
  cast(quantity * list_price - discount_amount as decimal(18, 2)) as item_net_amount
from {{ ref('raw_order_items') }}

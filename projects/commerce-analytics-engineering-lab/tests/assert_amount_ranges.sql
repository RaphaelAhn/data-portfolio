select *
from {{ ref('stg_order_items') }}
where quantity <= 0
   or list_price < 0
   or discount_amount < 0
   or discount_amount > quantity * list_price


select
  order_id,
  ordered_net_amount,
  completed_payment_amount
from {{ ref('fct_orders') }}
where is_recognized_order
  and ordered_net_amount <> completed_payment_amount


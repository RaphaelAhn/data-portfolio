select
  a.order_id,
  a.customer_id,
  cast(a.ordered_at as date) as order_date,
  a.ordered_at,
  a.updated_at,
  a.order_status,
  a.gross_product_amount,
  a.discount_amount,
  a.ordered_net_amount,
  r.completed_payment_amount,
  r.completed_refund_amount,
  case
    when a.order_status = 'completed' then r.net_revenue
    else cast(0 as decimal(18, 2))
  end as net_revenue,
  r.latest_refund_ingested_at,
  a.order_status = 'completed' and r.completed_payment_amount > 0 as is_recognized_order
from {{ ref('int_order_amounts') }} a
join {{ ref('int_payment_refund_reconciliation') }} r using (order_id)

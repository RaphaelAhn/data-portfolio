with completed_payments as (
  select
    order_id,
    cast(sum(paid_amount) as decimal(18, 2)) as completed_payment_amount
  from {{ ref('stg_payments') }}
  where payment_status = 'completed'
  group by 1
),

completed_refunds as (
  select
    p.order_id,
    cast(sum(r.refund_amount) as decimal(18, 2)) as completed_refund_amount,
    max(r.ingested_at) as latest_refund_ingested_at
  from {{ ref('stg_refunds') }} r
  join {{ ref('stg_payments') }} p using (payment_id)
  where r.refund_status = 'completed'
  group by 1
)

select
  o.order_id,
  coalesce(p.completed_payment_amount, 0) as completed_payment_amount,
  coalesce(r.completed_refund_amount, 0) as completed_refund_amount,
  cast(
    coalesce(p.completed_payment_amount, 0) - coalesce(r.completed_refund_amount, 0)
    as decimal(18, 2)
  ) as net_revenue,
  r.latest_refund_ingested_at
from {{ ref('stg_orders') }} o
left join completed_payments p using (order_id)
left join completed_refunds r using (order_id)


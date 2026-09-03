with typed as (
  select
    cast(payment_id as varchar) as payment_id,
    cast(order_id as varchar) as order_id,
    lower(cast(payment_status as varchar)) as payment_status,
    cast(paid_amount as decimal(18, 2)) as paid_amount,
    cast(paid_at as timestamp) as paid_at,
    cast(updated_at as timestamp) as updated_at
  from {{ ref('raw_payments') }}
)

select *
from typed
qualify row_number() over (
  partition by payment_id
  order by updated_at desc
) = 1

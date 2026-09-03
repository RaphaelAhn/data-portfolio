with typed as (
  select
    cast(refund_id as varchar) as refund_id,
    cast(payment_id as varchar) as payment_id,
    lower(cast(refund_status as varchar)) as refund_status,
    cast(refund_amount as decimal(18, 2)) as refund_amount,
    cast(refunded_at as timestamp) as refunded_at,
    cast(updated_at as timestamp) as updated_at,
    cast(ingested_at as timestamp) as ingested_at
  from {{ ref('raw_refunds') }}
)

select *
from typed
qualify row_number() over (
  partition by refund_id
  order by updated_at desc, ingested_at desc
) = 1

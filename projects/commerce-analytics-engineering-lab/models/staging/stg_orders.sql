with typed as (
  select
    cast(order_id as varchar) as order_id,
    cast(customer_id as varchar) as customer_id,
    lower(cast(order_status as varchar)) as order_status,
    cast(ordered_at as timestamp) as ordered_at,
    cast(updated_at as timestamp) as updated_at
  from {{ ref('raw_orders') }}
)

select *
from typed
qualify row_number() over (
  partition by order_id
  order by updated_at desc
) = 1

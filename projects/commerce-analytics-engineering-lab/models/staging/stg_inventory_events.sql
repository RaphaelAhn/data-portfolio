with typed as (
  select
    cast(event_id as varchar) as event_id,
    cast(product_id as varchar) as product_id,
    cast(quantity_delta as integer) as quantity_delta,
    lower(cast(reason as varchar)) as reason,
    cast(occurred_at as timestamp) as occurred_at,
    cast(ingested_at as timestamp) as ingested_at
  from {{ ref('raw_inventory_events') }}
)

select *
from typed
qualify row_number() over (
  partition by event_id
  order by ingested_at desc
) = 1


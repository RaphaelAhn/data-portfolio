select
  product_id,
  cast(occurred_at as date) as inventory_date,
  sum(quantity_delta) as daily_quantity_delta,
  max(ingested_at) as latest_ingested_at
from {{ ref('stg_inventory_events') }}
group by 1, 2


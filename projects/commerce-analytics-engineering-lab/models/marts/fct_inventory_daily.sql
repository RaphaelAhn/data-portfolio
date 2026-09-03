select
  product_id,
  inventory_date,
  daily_quantity_delta,
  sum(daily_quantity_delta) over (
    partition by product_id
    order by inventory_date
    rows between unbounded preceding and current row
  ) as ending_inventory_quantity,
  latest_ingested_at
from {{ ref('int_inventory_movements') }}


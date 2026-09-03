with latest as (
  select *
  from {{ ref('fct_inventory_daily') }}
  qualify row_number() over (
    partition by product_id
    order by inventory_date desc
  ) = 1
)

select
  l.product_id,
  p.category_id,
  p.product_name,
  l.inventory_date as latest_inventory_date,
  l.ending_inventory_quantity,
  l.ending_inventory_quantity <= 0 as is_stockout,
  l.latest_ingested_at
from latest l
join {{ ref('dim_product') }} p using (product_id)

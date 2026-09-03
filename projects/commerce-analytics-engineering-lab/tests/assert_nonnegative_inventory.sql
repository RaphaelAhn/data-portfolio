select *
from {{ ref('fct_inventory_daily') }}
where ending_inventory_quantity < 0


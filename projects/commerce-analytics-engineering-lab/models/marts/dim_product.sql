select
  product_id,
  category_id,
  product_name,
  valid_from,
  valid_to
from {{ ref('stg_products') }}


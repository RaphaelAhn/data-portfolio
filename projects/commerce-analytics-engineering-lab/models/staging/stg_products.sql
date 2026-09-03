select
  cast(product_id as varchar) as product_id,
  cast(category_id as varchar) as category_id,
  cast(product_name as varchar) as product_name,
  cast(valid_from as date) as valid_from,
  try_cast(valid_to as date) as valid_to
from {{ ref('raw_products') }}


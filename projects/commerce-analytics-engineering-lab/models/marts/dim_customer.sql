select
  customer_id,
  joined_at,
  customer_segment
from {{ ref('stg_customers') }}


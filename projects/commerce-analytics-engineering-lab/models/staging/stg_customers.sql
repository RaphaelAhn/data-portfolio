select
  cast(customer_id as varchar) as customer_id,
  cast(joined_at as date) as joined_at,
  cast(customer_segment as varchar) as customer_segment
from {{ ref('raw_customers') }}


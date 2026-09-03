select *
from {{ ref('fct_orders') }}
where order_status = 'cancelled'
  and net_revenue <> 0


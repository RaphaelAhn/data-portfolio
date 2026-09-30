-- O100: later Google click wins over earlier Meta click.
-- O103: click after the order and click older than 7 days are both ignored -> organic.
select *
from {{ ref('int_order_attribution') }}
where (order_id = 'O100' and channel <> 'google')
   or (order_id = 'O103' and channel <> 'organic')

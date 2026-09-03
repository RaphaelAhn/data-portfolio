-- R102 was ingested two days after its business event. The order-date mart must
-- be restated so O105 reflects the completed refund and yields 30,000 net revenue.
select *
from {{ ref('fct_orders') }}
where order_id = 'O105'
  and (completed_refund_amount <> 5000 or net_revenue <> 30000)


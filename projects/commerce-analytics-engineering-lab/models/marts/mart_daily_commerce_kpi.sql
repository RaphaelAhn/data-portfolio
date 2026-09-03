select
  order_date as metric_date,
  count(distinct case when is_recognized_order then order_id end) as completed_orders,
  cast(sum(case when is_recognized_order then gross_product_amount else 0 end) as decimal(18, 2)) as gross_product_amount,
  cast(sum(case when is_recognized_order then discount_amount else 0 end) as decimal(18, 2)) as discount_amount,
  cast(sum(case when is_recognized_order then completed_payment_amount else 0 end) as decimal(18, 2)) as completed_payment_amount,
  cast(sum(net_revenue) as decimal(18, 2)) as net_revenue,
  cast(
    sum(net_revenue) / nullif(count(distinct case when is_recognized_order then order_id end), 0)
    as decimal(18, 2)
  ) as average_order_value
from {{ ref('fct_orders') }}
group by 1

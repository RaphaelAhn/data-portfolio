select
  cast(click_id as varchar) as click_id,
  cast(order_id as varchar) as order_id,
  cast(campaign_id as varchar) as campaign_id,
  cast(clicked_at as timestamp) as clicked_at
from {{ ref('raw_ad_clicks') }}

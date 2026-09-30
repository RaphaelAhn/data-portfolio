select
  cast(campaign_id as varchar) as campaign_id,
  lower(cast(platform as varchar)) as platform,
  cast(campaign_name as varchar) as campaign_name
from {{ ref('raw_campaigns') }}

-- Ad platforms restate recent days; keep the latest report per campaign-day.
with typed as (
  select
    cast(campaign_id as varchar) as campaign_id,
    cast(spend_date as date) as spend_date,
    cast(impressions as bigint) as impressions,
    cast(clicks as bigint) as clicks,
    cast(cost as decimal(18, 2)) as cost,
    cast(reported_at as timestamp) as reported_at
  from {{ ref('raw_ad_spend') }}
)

select *
from typed
qualify row_number() over (
  partition by campaign_id, spend_date
  order by reported_at desc
) = 1

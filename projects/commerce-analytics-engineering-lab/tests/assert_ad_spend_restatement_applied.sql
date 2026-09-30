-- Meta restated 2026-08-01 spend from 30,000 to 27,000; only the latest report may count.
select *
from {{ ref('stg_ad_spend') }}
where campaign_id = 'CMP_META_01'
  and spend_date = date '2026-08-01'
  and cost <> 27000

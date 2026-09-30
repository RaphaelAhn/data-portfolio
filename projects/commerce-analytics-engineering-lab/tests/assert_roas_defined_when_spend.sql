-- Any day with spend must have a ROAS (0 when nothing converted); only zero-spend rows may be NULL.
select *
from {{ ref('mart_channel_daily_performance') }}
where (cost > 0 and roas is null)
   or (cost = 0 and roas is not null)

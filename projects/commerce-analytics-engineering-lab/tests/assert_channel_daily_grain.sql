select metric_date, channel, count(*) as row_count
from {{ ref('mart_channel_daily_performance') }}
group by 1, 2
having count(*) > 1

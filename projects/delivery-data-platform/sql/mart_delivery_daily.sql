-- Illustrative Trino-oriented SQL. Source relations are logical models, not deployed tables.
WITH orders AS (
    SELECT order_id, region_id, experiment_variant, event_time AS ordered_at
    FROM clean_order_events
    WHERE event_type = 'OrderCreated'
),
latest_dispatch AS (
    SELECT order_id, result, eta_minutes, event_time AS dispatched_at
    FROM (
        SELECT
            order_id,
            result,
            eta_minutes,
            event_time,
            row_number() OVER (PARTITION BY order_id ORDER BY event_time DESC, event_id DESC) AS rn
        FROM clean_dispatch_events
    )
    WHERE rn = 1
),
completed AS (
    SELECT order_id, event_time AS completed_at
    FROM clean_delivery_events
    WHERE event_type = 'DeliveryCompleted'
)
SELECT
    CAST(o.ordered_at AS DATE) AS order_date,
    o.region_id,
    o.experiment_variant,
    COUNT(*) AS created_orders,
    COUNT_IF(d.result = 'accepted') AS accepted_dispatch_orders,
    CAST(COUNT_IF(d.result = 'accepted') AS DOUBLE) / NULLIF(COUNT(*), 0) AS dispatch_success_rate,
    AVG(date_diff('second', o.ordered_at, d.dispatched_at)) AS avg_dispatch_seconds,
    AVG(date_diff('minute', o.ordered_at, c.completed_at) - d.eta_minutes) AS avg_eta_error_minutes
FROM orders o
LEFT JOIN latest_dispatch d ON o.order_id = d.order_id
LEFT JOIN completed c ON o.order_id = c.order_id
GROUP BY 1, 2, 3;

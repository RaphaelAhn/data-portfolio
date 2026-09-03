# Technical Guide: From Raw Commerce Events to Trusted Metrics

This guide explains the project for readers who are new to analytics engineering. It focuses on what each layer does, why it exists, and what would change in a production environment.

## 1. What an Analytics Engineer does

An analytics engineer turns raw operational records into data products that analysts, dashboards, and services can use consistently.

In this project, the operational records answer different questions:

- Orders describe customer intent and order status.
- Order items describe products, quantities, list prices, and discounts.
- Payments describe whether money was successfully collected.
- Refunds describe money returned after payment.
- Inventory events describe why stock increased or decreased.

No single source is sufficient to define revenue or inventory. The analytics layer therefore establishes a shared grain, business rules, tests, and a repeatable rebuild process.

## 2. Essential terms

### Grain

Grain means what one row represents. Before writing a join, the grain of both inputs must be known.

Examples:

- `fct_orders`: one row per `order_id`
- `fct_order_items`: one row per `order_item_id`
- `fct_inventory_daily`: one row per `product_id` and inventory movement date
- `mart_daily_commerce_kpi`: one row per order date

If two models with different grains are joined carelessly, amounts can be duplicated. For example, joining one order to three items and two payments can create six rows before aggregation.

### Fact and dimension

A fact records measurable activity, such as an order or inventory movement. A dimension contains descriptive attributes, such as a product name, category, or customer segment.

### Staging, intermediate, and mart

- **Staging** models clean one source at a time. They cast data types, normalize text values, and select the latest record.
- **Intermediate** models implement reusable business calculations without exposing a final reporting interface.
- **Mart** models publish stable grains and business-friendly metrics for analysts and downstream tools.

### Data contract

A data contract describes the meaning and reliability expectations of a data product. Useful fields include grain, column meaning, nullability, accepted values, update frequency, owner, and behavior during failure.

### Late-arriving data

Late-arriving data has a business event time earlier than its ingestion time. A refund can happen on Monday but reach the warehouse on Wednesday. If the warehouse only recalculates Wednesday, Monday's revenue remains wrong.

### Idempotency

An idempotent pipeline produces the same result when it receives the same input and runs more than once. This is important because production jobs are often retried after timeouts or partial failures.

## 3. Layer-by-layer walkthrough

### Step 1: Source fixtures

The `seeds/` directory contains deterministic CSV fixtures. They include normal and deliberately difficult cases:

- an order whose status changes from pending to completed;
- a payment whose status changes from requested to cancelled;
- a completed partial refund;
- a refund that arrives two days after its business event;
- a duplicated inventory event.

These fixtures are not production samples. Their purpose is to make transformation decisions executable and reviewable.

### Step 2: Staging models

`stg_orders.sql` casts identifiers and timestamps, normalizes status to lowercase, and uses a window function to keep the latest row per order.

```sql
qualify row_number() over (
  partition by order_id
  order by updated_at desc
) = 1
```

Read this from the inside out:

1. `partition by order_id` creates a separate group for each order.
2. `order by updated_at desc` places the newest update first.
3. `row_number()` labels the first row as 1.
4. `qualify ... = 1` keeps only that row.

Payments and refunds follow the same pattern. Refunds additionally use `ingested_at` because a business update can arrive late.

### Step 3: Ordered amounts

`int_order_amounts.sql` joins orders to order items and calculates three values:

```text
gross product amount = sum(quantity × list price)
discount amount      = sum(item discount)
ordered net amount   = sum(quantity × list price − discount)
```

These values represent what was ordered. They do not prove that payment completed.

### Step 4: Payment and refund reconciliation

`int_payment_refund_reconciliation.sql` sums only completed payments and completed refunds by order.

```sql
coalesce(completed_payment_amount, 0)
  - coalesce(completed_refund_amount, 0) as net_revenue
```

`COALESCE` replaces a missing amount with zero. This makes the subtraction explicit when an order has no completed refund.

### Step 5: Final order fact

`fct_orders.sql` brings ordered amounts and reconciled cash amounts together. Revenue is recognized only when the latest order status is completed.

The model exposes both components and the final metric. This is useful because a reviewer can inspect whether an unexpected net-revenue value came from order amount, payment, refund, or status.

### Step 6: Daily commerce KPI mart

`mart_daily_commerce_kpi.sql` groups the order fact by order date. All consumers reuse the same completed-order and net-revenue rules.

Average order value uses:

```sql
sum(net_revenue)
  / nullif(count(distinct completed_order_id), 0)
```

`NULLIF` turns a zero denominator into `NULL`, preventing division by zero. `NULL` communicates that the metric is undefined for a day with no completed orders.

### Step 7: Inventory movement and balance

Inventory events are first deduplicated by `event_id`. Daily movement is then calculated per product.

```sql
sum(quantity_delta) as daily_quantity_delta
```

A window sum converts movement into ending inventory:

```sql
sum(daily_quantity_delta) over (
  partition by product_id
  order by inventory_date
  rows between unbounded preceding and current row
)
```

This means “for the current product, add every movement from the first available date through this date.”

## 4. How dbt tests work

A dbt singular test is a SQL query that returns invalid rows. Zero returned rows means the test passes.

Example: reject negative net revenue.

```sql
select *
from {{ ref('fct_orders') }}
where net_revenue < 0
```

The project also uses schema tests:

- `not_null`: a required key or metric is present;
- `unique`: a declared single-column key does not repeat;
- `relationships`: a foreign key exists in its parent model;
- `accepted_values`: a status or reason belongs to the allowed set.

Business-specific tests reconcile totals between layers and verify the late-refund example.

## 5. Why the late-refund example matters

Order `O105` has a completed payment of 35,000. Refund `R102` later completes for 5,000. The correct net revenue becomes 30,000.

The refund is ingested two days after its business event. A production incremental pipeline should therefore:

1. find newly ingested or changed refunds using a watermark;
2. map each refund to its payment and order;
3. identify the original order date;
4. rebuild the affected order-date partition;
5. reconcile the rebuilt fact and daily mart;
6. record the affected dates, row counts, source freshness, and test results.

## 6. What the idempotency script proves

The Python script runs `dbt build`, reads five core tables, orders their rows deterministically, and hashes their serialized values. It repeats the process and compares both snapshots.

For the checked-in fixtures:

- both builds completed all 71 dbt items successfully;
- all five tables retained the same row counts;
- all five table hashes were identical.

This proves repeatability for the local fixtures. It does not prove safe concurrent writes, distributed transaction guarantees, or exactly-once streaming behavior.

## 7. Metric decisions that require business agreement

Technical correctness alone cannot decide every metric rule.

| Decision | Current prototype | Production question |
| --- | --- | --- |
| Business date | Date portion of order timestamp | Which timezone and cutoff define a day? |
| Completed order | Completed status with positive completed payment | Does a fully refunded order remain a completed order? |
| Net revenue | Completed payment minus completed refund | Are tax, shipping, points, coupons, and fees included? |
| Inventory | Cumulative product event quantity | Which location and stock status are represented? |
| Freshness | Local batch completion | What SLA and late-data window are required? |

## 8. Production architecture extension

```text
Oracle/MySQL commerce databases
    → CDC with Debezium or OGG
    → Kafka
    → stream normalization or landing tables
    → BigQuery raw and standardized layers
    → dbt incremental models
    → governed facts, dimensions, and metric marts
    → BI, API, database, file, or message consumers
```

The current repository implements only the local batch transformation layer. CDC, Kafka, Flink, BigQuery, and serving interfaces are architectural extensions and must not be presented as completed work.

## 9. Operational observability checklist

A production version should record:

- latest source `updated_at` and `ingested_at` by source;
- pipeline start, expected completion, actual completion, and delay;
- input, output, duplicate, and rejected row counts;
- missing parent keys and unexpected status values;
- dates and entities rebuilt because of late data;
- test pass and failure counts;
- reconciliation differences between facts and marts;
- current stockouts, negative balances, and unknown-product events.

## 10. Interview summary

> I modeled orders, payments, refunds, products, customers, and inventory in a layered dbt project. I reconciled completed payments and refunds at the order grain, published a single daily net-revenue definition, and added a regression test for a late-arriving refund. I executed all 71 dbt items twice and confirmed identical row counts and hashes for five core marts. The implementation is a local synthetic prototype; a production version would add incremental watermarks, deterministic CDC ordering, inventory snapshots, partition-aware reprocessing, BigQuery performance evidence, and operational observability.

# Commerce Analytics Engineering Lab

This synthetic-data portfolio project integrates order, payment, refund, product, customer, and inventory data into consistent analytics models. It also demonstrates data-quality controls and deterministic reprocessing.

> This project is a local prototype. It does not use CJ Olive Young data or systems, and it does not claim production experience, cloud-scale processing, real-time pipeline operation, or business impact.

## Problem Statement

Commerce metrics can diverge when teams interpret order status, payment status, partial refunds, and late-arriving updates differently. This project answers four practical questions with reproducible SQL models:

1. How should completed and cancelled orders be distinguished?
2. How should completed payments and partial refunds be reconciled?
3. How should a late-arriving refund update a historical order-date metric?
4. How can duplicate inventory events and invalid product references be detected?

## Data Flow

```text
CSV seeds
  └─ raw_orders / raw_order_items / raw_payments / raw_refunds
     raw_products / raw_customers / raw_inventory_events
          ↓
staging: type normalization, status standardization, latest-record selection,
         and inventory-event deduplication
          ↓
intermediate: order amounts, payment-refund reconciliation,
              and daily inventory movements
          ↓
marts: order and order-item facts, customer and product dimensions,
       daily KPIs, and current inventory health
```

## Models and Grain

| Model | Grain | Purpose |
| --- | --- | --- |
| `fct_orders` | One row per order | Combines item totals, completed payments, completed refunds, and net revenue |
| `fct_order_items` | One row per order item | Supports quantity and amount analysis by product and category |
| `dim_customer` | One row per customer | Provides signup date and an analytics-ready customer segment |
| `dim_product` | One row per product | Provides product and category attributes |
| `fct_inventory_daily` | One row per product and movement date | Calculates daily movement and cumulative closing inventory |
| `mart_daily_commerce_kpi` | One row per order date | Provides completed orders, gross merchandise value, discounts, payments, net revenue, and average order value |
| `mart_inventory_health` | One row per product | Provides latest inventory and out-of-stock status |

## Metric Definitions

| Metric | Definition | Exclusions and caveats |
| --- | --- | --- |
| Gross merchandise value | Sum of `quantity × listed price` for completed orders | Excludes cancelled orders |
| Discount amount | Sum of discounts allocated to completed order items | Tests reject negative discounts and discounts above gross item value |
| Completed payment amount | Payment amount whose latest status is `completed` | Excludes requested and cancelled payments |
| Net revenue | Completed payment amount − completed refund amount | Includes partial refunds and restates historical order-date metrics |
| Completed orders | Distinct completed orders with a completed payment | Removes duplicate status history |
| Average order value | Net revenue ÷ completed orders | Returns `null` when the denominator is zero |

Refund `R102` represents a late-arriving record loaded two days after the refund event. A full rerun restates order `O105` net revenue from 35,000 to 30,000 for its original order date. This simplified example demonstrates the recent-window reprocessing principle used in incremental pipelines.

## Data-Quality Controls

- Validate primary-key completeness and uniqueness.
- Validate referential integrity across order items, payments, refunds, inventory events, products, and orders.
- Validate allowed values for order, payment, refund, and inventory-reason statuses.
- Validate reasonable ranges for quantity, price, discount, net revenue, and inventory.
- Reconcile order-item totals with the order fact.
- Reconcile completed payment amounts with net order-item amounts.
- Confirm that a late-arriving completed refund is reflected in net revenue.
- Reconcile daily KPI net revenue with the order fact.
- Confirm that two runs with identical inputs produce identical mart results.

## Run Locally

Python 3.11 or later is recommended.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\verify_idempotency.py
```

The final command runs `dbt build` twice and confirms that row counts and SHA-256 hashes match for the core marts. The generated DuckDB database, logs, and dbt artifacts are stored under ignored local directories and are not committed to Git.

## Production Extension Plan

- Use `updated_at` from orders, payments, and refunds as incremental watermarks.
- Recalculate a recent time window to capture late-arriving refunds.
- Retain only the latest record for each `order_id`, `payment_id`, `refund_id`, and `event_id`.
- Reprocess only affected order-date partitions after a failure.
- Record run time, processed row counts, test results, and the latest source timestamp in operational logs.
- For BigQuery, select order-date partitioning and customer or product clustering only after measuring real query patterns.

## Scope and Limitations

- This is a local batch model built with synthetic data; it does not reproduce production traffic or data volume.
- CDC, Kafka, Flink, and API serving are outside the implementation scope.
- Data freshness is documented as a design consideration; no production SLA is claimed.
- Product validity dates are included, but a complete SCD Type 2 implementation is outside the current scope.

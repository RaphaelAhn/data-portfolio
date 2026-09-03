# Commerce Analytics Engineering Lab

A synthetic, local portfolio project that turns order, payment, refund, product, customer, and inventory records into consistent analytical models and governed commerce metrics.

> **Scope notice:** This project does not use CJ Olive Young data or systems. It does not claim production-scale processing, cloud operations, real-time pipeline experience, or realized business impact. The repository demonstrates modeling and validation choices on deterministic synthetic fixtures.

## Why this project exists

Commerce teams can calculate different versions of the same metric when order status, payment status, partial refunds, and late-arriving updates live in separate systems. This project creates one reusable transformation path for questions such as:

1. What qualifies as a completed order?
2. How should completed payments and partial refunds be reconciled?
3. How should a late refund restate the original order-date metric?
4. How can duplicate inventory events and invalid product references be detected?
5. Does a repeated pipeline run produce the same analytical outputs?

## Three portfolio examples

### 1. Order, payment, and refund reconciliation

The project builds one row per order in `fct_orders`. It combines ordered merchandise value, completed payments, completed refunds, and recognized net revenue.

```text
orders + order items + payments + refunds
    → typed and deduplicated staging models
    → order amount and payment/refund reconciliation models
    → fct_orders
    → mart_daily_commerce_kpi
```

The shared rule is:

```text
net revenue = completed payment amount - completed refund amount
```

Cancelled orders receive zero recognized revenue. Average order value uses `NULLIF` so a day with zero completed orders does not cause a divide-by-zero error.

### 2. Late-arriving refunds, quality tests, and idempotent rebuilds

Synthetic refund `R102` occurs on August 10 but arrives on August 12. Rebuilding the models restates order `O105` from 35,000 to 30,000 net revenue on its original order date.

The project validates primary keys, relationships, accepted statuses, amount ranges, order/payment reconciliation, late-refund behavior, daily KPI reconciliation, and non-negative inventory. `scripts/verify_idempotency.py` runs `dbt build` twice and compares row counts and SHA-256 hashes for five core marts.

### 3. Inventory events and stockout status

Receipt, sale, return, and adjustment events are deduplicated by `event_id`, aggregated by product and event date, and converted into a running ending-inventory balance. `mart_inventory_health` exposes the latest balance and stockout flag per product.

```text
inventory events
    → latest event per event_id
    → product-day movement
    → cumulative ending inventory
    → latest product inventory and stockout status
```

## Model layers and grain

| Model | Grain | Purpose |
| --- | --- | --- |
| `fct_orders` | One row per order | Reconciles merchandise, payment, refund, and net revenue |
| `fct_order_items` | One row per order item | Supports product and category analysis |
| `dim_customer` | One row per customer | Provides join-safe customer attributes |
| `dim_product` | One row per product | Provides product and category attributes |
| `fct_inventory_daily` | One row per product and movement date | Calculates daily movement and running ending inventory |
| `mart_daily_commerce_kpi` | One row per order date | Publishes completed orders, revenue components, and average order value |
| `mart_inventory_health` | One row per product | Publishes latest inventory and stockout status |

## Data flow

```text
CSV seeds
  └─ raw_orders / raw_order_items / raw_payments / raw_refunds
     raw_products / raw_customers / raw_inventory_events
          ↓
staging: types, normalized statuses, latest records, duplicate removal
          ↓
intermediate: order amounts, payment/refund reconciliation, inventory movement
          ↓
marts: facts, dimensions, daily commerce KPIs, inventory health
```

## Metric contract

| Metric | Definition | Exclusions and cautions |
| --- | --- | --- |
| Gross product amount | Sum of quantity × list price for recognized orders | Excludes cancelled orders |
| Discount amount | Sum of item-level discounts for recognized orders | Tests reject negative discounts and discounts above merchandise value |
| Completed payment amount | Latest payments whose status is `completed` | Excludes requested and cancelled payments |
| Net revenue | Completed payment amount − completed refund amount | Includes partial refunds and restates the order-date metric |
| Completed orders | Completed orders with a positive completed payment | Treatment of fully refunded orders requires a business decision |
| Average order value | Net revenue ÷ completed orders | Returns `NULL` when the denominator is zero |

## Verification evidence

The checked-in synthetic fixtures were built twice with dbt 1.9.8 and dbt-duckdb 1.9.6.

- 7 seeds, 17 models, and 47 data tests per build
- 71 total dbt items per build
- `PASS=71, WARN=0, ERROR=0, SKIP=0` on both builds
- Identical row counts and SHA-256 hashes for all five core marts across both runs

This evidence proves deterministic behavior for the current small fixtures. It does not prove production concurrency, distributed exactly-once processing, service-level objectives, or large-scale query performance.

## Documentation

- [Beginner-friendly technical guide](docs/TECHNICAL_GUIDE.md)
- [Evidence-based code review](docs/CODE_REVIEW.md)

## Run locally

Python 3.11 or newer is recommended.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\verify_idempotency.py
```

DuckDB files, dbt build artifacts, logs, virtual environments, and personal settings are excluded from version control.

## Production extension path

- Use source `updated_at` and `ingested_at` watermarks for incremental processing.
- Reprocess the order-date partitions affected by late refunds.
- Add a deterministic CDC sequence, LSN, or offset for tie-breaking.
- Record run time, row counts, rejected rows, test outcomes, and source freshness.
- Add an opening inventory snapshot and reconcile it periodically with event-derived balances.
- Measure actual query patterns before choosing BigQuery partitioning and clustering keys.
- Add explicit API, database, file, or message contracts for downstream consumers.

## Known limitations

- The project uses a tiny synthetic batch dataset.
- CDC, Kafka, Flink, BigQuery, and serving APIs are design extensions, not implemented features.
- Freshness is documented but no production SLA is measured.
- Product effective dates are present, but a complete SCD Type 2 transformation is not implemented.
- The detailed code review documents three Medium and three Low operational gaps.

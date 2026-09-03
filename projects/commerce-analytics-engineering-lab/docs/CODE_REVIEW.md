# Code Review

## Findings

The findings are ordered by severity. No Critical or High issues were found in the reviewed local prototype.

### Medium — Orders without items can disappear silently

- **Location:** `models/intermediate/int_order_amounts.sql:10-11`
- **Trigger:** an order arrives before its order items, order-item ingestion fails, or an empty order is present in the source.
- **Failure mode:** the inner join removes the order from `int_order_amounts`. Because `fct_orders` depends on that model, the order can also disappear from order counts and revenue without producing a failed relationship test.
- **Evidence:** current relationship tests verify that each order item references an order. They do not verify the reverse condition that every relevant order has at least one item.
- **Smallest correction:** preserve orders with a left join and expose missing items as an explicit error state, or add a singular test that returns orders with zero items. Do not silently finalize their monetary amounts as zero.
- **Confidence:** verified from the SQL path and test direction.

### Medium — Latest-record selection is nondeterministic when timestamps tie

- **Location:** `models/staging/stg_orders.sql:13-16`, `stg_payments.sql:14-17`, `stg_inventory_events.sql:14-17`
- **Trigger:** two records for the same business ID have the same `updated_at` or `ingested_at` but different values.
- **Failure mode:** `ROW_NUMBER()` has no unique final ordering key, so the selected record can depend on physical input order or execution behavior. Status, revenue, or inventory can change across runs or platforms.
- **Evidence:** the window order contains only a non-unique timestamp for these models. The fixtures contain no conflicting timestamp tie, so current tests do not exercise this path.
- **Smallest correction:** add a deterministic source sequence such as CDC LSN, Kafka offset, commit sequence, or ingestion sequence. If none exists, fail or quarantine conflicting ties.
- **Confidence:** verified from the window definitions; the production frequency is unknown.

### Medium — Inventory balance assumes complete history or an opening receipt

- **Location:** `models/marts/fct_inventory_daily.sql:5-9`
- **Trigger:** event ingestion begins after stock already exists, or historical events are truncated.
- **Failure mode:** the cumulative sum starts from zero. If the true opening stock is 500 and the first available event is a sale of 2, the model reports -2 instead of 498.
- **Evidence:** the fact uses only event deltas and has no opening snapshot input. Current fixtures begin each product with a receipt, but that assumption is not enforced by a contract or test.
- **Smallest correction:** introduce a dated opening-inventory snapshot and add later deltas after the snapshot boundary. Quarantine products without a valid starting balance.
- **Confidence:** strongly inferred; current synthetic inputs intentionally avoid the trigger.

### Low — Daily KPI reconciliation cannot detect a missing date

- **Location:** `tests/assert_daily_kpi_reconciliation.sql:13-15`
- **Trigger:** a date exists in the fact aggregate but disappears from the mart, or vice versa.
- **Failure mode:** the inner join removes the unmatched date, so the test can still return zero rows and pass.
- **Evidence:** the test compares amounts only for dates present on both sides.
- **Smallest correction:** use a full outer join and fail when either date is missing or coalesced values differ.
- **Confidence:** verified. The current mart groups directly from the fact, so no date is missing in the fixtures.

### Low — The idempotency script assumes a Windows executable name

- **Location:** `scripts/verify_idempotency.py:23-26`
- **Trigger:** the script runs in a Linux or macOS virtual environment.
- **Failure mode:** it looks specifically for `dbt.exe`, while non-Windows environments normally expose `dbt`.
- **Evidence:** the executable path is derived with `Path(sys.executable).with_name("dbt.exe")`.
- **Smallest correction:** resolve `dbt` with `shutil.which`, or use another verified platform-neutral invocation and fail with a clear message when unavailable.
- **Confidence:** verified by inspection. Windows execution passed; non-Windows execution was not available in this review.

### Low — Product-date uniqueness is not an executable schema contract

- **Location:** `models/schema.yml:111-116`
- **Trigger:** a future join or incremental change creates multiple rows for one product and inventory date.
- **Failure mode:** both columns remain non-null, so the current schema tests pass even though the declared fact grain is violated.
- **Evidence:** only individual not-null tests are defined for `product_id` and `inventory_date`.
- **Smallest correction:** add a unique-combination test for `(product_id, inventory_date)` using a singular test or a supported utility macro.
- **Confidence:** strongly inferred. The current upstream group-by produces a unique combination.

## Cleared surfaces

- Latest-state patterns are consistently used for orders, payments, refunds, and inventory events.
- Primary-key, relationship, accepted-value, and amount-range checks cover the main fixture paths.
- Cancelled orders are forced to zero recognized revenue.
- `NULLIF` prevents division by zero in average order value.
- Order-item totals, completed payments, order facts, and daily KPI totals are reconciled.
- The late-arriving refund has a durable regression test.
- Two consecutive builds produced identical rows and hashes for five core marts.

## Verification performed

- Runtime: dbt 1.9.8 with dbt-duckdb 1.9.6
- Build 1: `PASS=71, WARN=0, ERROR=0, SKIP=0`
- Build 2: `PASS=71, WARN=0, ERROR=0, SKIP=0`
- Idempotency: identical row counts and SHA-256 hashes for `fct_orders`, `fct_order_items`, `fct_inventory_daily`, `mart_daily_commerce_kpi`, and `mart_inventory_health`

## Strongest counterexample attempted

Passing tests do not prove source completeness. The reviewed join and reconciliation tests can still miss an order with no items and can miss a date that disappears from one side of the daily reconciliation. These are the strongest gaps in the current completion claim.

## Unreviewed or unavailable evidence

- Production data volume and query performance
- BigQuery partitioning and clustering behavior
- CDC ordering, replay, and out-of-order delivery
- Kafka or Flink delivery guarantees
- Concurrent writes and partial-failure recovery
- BI, API, database, file, or message consumer contracts
- Authentication, authorization, privacy, and retention controls

ROOT_CAUSE_ALIGNMENT: NOT_APPLICABLE — this is a portfolio code review, not a defect repair.

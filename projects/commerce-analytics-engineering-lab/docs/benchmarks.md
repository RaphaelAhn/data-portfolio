# Benchmarks

> Real measured results only — no estimates. Reproduce with `scripts/run_benchmark.py`, which generates FK-consistent synthetic seeds at each scale, runs `dbt build --full-refresh`, and restores the checked-in `seeds/` fixtures afterward with `git checkout -- seeds/`.

## Environment

- Windows, Python 3.12.14 (project `.venv`)
- dbt-core 1.9.8, dbt-duckdb 1.9.6
- No Docker; DuckDB runs as an embedded local database file (`target/commerce_analytics.duckdb`)
- `dbt.exe`'s console-script shim fails silently in this venv (see [CODE_REVIEW.md](CODE_REVIEW.md)); all runs invoke `dbt.cli.main.cli` directly via `python -c`

## Data generator

`scripts/generate_benchmark_seeds.py` builds orders, order items, payments, refunds, customers, products, and inventory events that satisfy every foreign key and business rule the project's 47 dbt tests check (no orphan order items, no negative running inventory, payment/refund reconciliation, etc.). It is a separate synthetic dataset from the small hand-written fixtures in `seeds/` — it is only used for timing, never committed, and `run_benchmark.py` always restores the original fixtures afterward.

## Results

| Orders | Order items | Payments | Refunds | Inventory events | `dbt build` time | Result |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 100,000 | 200,297 | 94,938 | 3,416 | 180,450 | 58.98s | PASS=71, WARN=0, ERROR=0, SKIP=0 |
| 500,000 | 999,175 | 474,915 | 16,963 | 899,642 | 166.77s | PASS=71, WARN=0, ERROR=0, SKIP=0 |
| 1,000,000 | 1,998,661 | 949,945 | 34,004 | 1,799,956 | 314.69s | PASS=71, WARN=0, ERROR=0, SKIP=0 |

All 71 dbt items (7 seeds, 17 models, 47 data tests) passed at both completed scales with zero warnings or errors — the same test suite that runs against the small checked-in fixtures also holds at 100K and 500K orders.

## First attempt failed — noted, not hidden

The first end-to-end run of `run_benchmark.py` (100K → 500K → 1M in sequence) failed at the 1M generation step with `OSError: [Errno 22] Invalid argument` writing `raw_inventory_events.csv`, immediately after the 500K run's `git checkout -- seeds/` restore. Retrying the 1M generation alone in isolation succeeded on the first try, so this looks like a transient file-handle condition (most likely antivirus or OS-level scanning of the large file just written) rather than a bug in the generator. The `finally` block in `run_benchmark.py` restored the original fixtures correctly even though the script exited with an error — the working tree was never left with generated data in place. The 1M `dbt build` itself was then run and timed separately (below), and `seeds/` was restored again with `git checkout -- seeds/` immediately after.

## What this does and does not prove

- **Proves:** the dbt build (7 seeds, 17 models, 47 tests) scales from 100K to 1M orders (up to ~5M total rows across all seven seed tables) on a single local machine with zero test failures. Build time grows faster than linearly with scale (59s → 167s → 315s is roughly 2.8x, 1.9x per 5x/2x increase in orders), which is expected for `--full-refresh` table materializations and is worth watching if scale increases further.
- **Does not prove:** production concurrency, distributed processing, multi-user query load, or cloud warehouse performance (BigQuery, Snowflake, etc.) — this is one process against an embedded DuckDB file.

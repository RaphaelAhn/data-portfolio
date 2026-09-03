from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "target" / "commerce_analytics.duckdb"
TABLES = (
    "fct_orders",
    "fct_order_items",
    "fct_inventory_daily",
    "mart_daily_commerce_kpi",
    "mart_inventory_health",
)


def run_build() -> None:
    dbt_executable = Path(sys.executable).with_name("dbt.exe")
    subprocess.run(
        [str(dbt_executable), "build", "--profiles-dir", str(ROOT)],
        cwd=ROOT,
        check=True,
    )


def snapshot() -> dict[str, dict[str, object]]:
    connection = duckdb.connect(str(DATABASE), read_only=True)
    try:
        result: dict[str, dict[str, object]] = {}
        for table in TABLES:
            rows = connection.execute(f"select * from {table} order by all").fetchall()
            payload = json.dumps(rows, default=str, ensure_ascii=False).encode("utf-8")
            result[table] = {
                "rows": len(rows),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        return result
    finally:
        connection.close()


def main() -> None:
    run_build()
    first = snapshot()
    run_build()
    second = snapshot()
    if first != second:
        print(json.dumps({"first": first, "second": second}, indent=2, ensure_ascii=False))
        raise SystemExit("Idempotency check failed: repeated builds changed the marts")

    print(json.dumps(second, indent=2, ensure_ascii=False))
    print("Idempotency check passed: two consecutive builds produced identical marts")


if __name__ == "__main__":
    main()

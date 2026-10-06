"""Independently recalculate published CSV and JSON metrics without SQL."""

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def audit(data_dir: Path, analysis_dir: Path) -> dict:
    source_names = ("order_lines", "shipment_lines", "return_lines", "inventory_snapshots")
    tables = {name: read_csv(data_dir / f"{name}.csv") for name in source_names}
    summary = json.loads((analysis_dir / "summary.json").read_text(encoding="utf-8"))
    published_rows = read_csv(analysis_dir / "daily_product_metrics.csv")
    as_of = summary["as_of"]
    orders = {row["order_line_id"]: row for row in tables["order_lines"]}
    shipments = {row["shipment_line_id"]: row for row in tables["shipment_lines"]}
    if len(orders) != len(tables["order_lines"]) or len(shipments) != len(tables["shipment_lines"]):
        raise AssertionError("duplicate source keys")

    fields = ("ordered_qty", "ordered_value_krw", "shipped_qty", "shipped_value_krw",
              "returned_qty", "returned_value_krw")
    by_day_product = defaultdict(lambda: {key: 0 for key in fields})
    visible_orders = {key: row for key, row in orders.items() if row["order_at"] <= as_of}
    for row in visible_orders.values():
        result = by_day_product[(row["order_at"][:10], row["product_id"])]
        result["ordered_qty"] += int(row["ordered_qty"])
        result["ordered_value_krw"] += int(row["ordered_qty"]) * int(row["unit_price_krw"])
    for row in tables["shipment_lines"]:
        order = visible_orders.get(row["order_line_id"])
        if order and row["shipped_at"] <= as_of:
            result = by_day_product[(order["order_at"][:10], order["product_id"])]
            result["shipped_qty"] += int(row["shipped_qty"])
            result["shipped_value_krw"] += int(row["shipped_qty"]) * int(order["unit_price_krw"])
    for row in tables["return_lines"]:
        shipment = shipments[row["shipment_line_id"]]
        order = visible_orders.get(shipment["order_line_id"])
        if order and row["recorded_at"] <= as_of:
            result = by_day_product[(order["order_at"][:10], order["product_id"])]
            result["returned_qty"] += int(row["returned_qty"])
            result["returned_value_krw"] += int(row["returned_qty"]) * int(order["unit_price_krw"])

    if len(published_rows) != len(by_day_product):
        raise AssertionError("daily metric row count mismatch")
    for row in published_rows:
        key = (row["order_date"], row["product_id"])
        expected = by_day_product[key]
        for field in fields:
            if int(row[field]) != expected[field]:
                raise AssertionError(f"{key}: {field} mismatch")
        net = expected["shipped_value_krw"] - expected["returned_value_krw"]
        if int(row["net_shipped_value_krw"]) != net:
            raise AssertionError(f"{key}: net value mismatch")
        if float(row["fulfillment_rate"]) != round(
            expected["shipped_qty"] / expected["ordered_qty"], 4
        ):
            raise AssertionError(f"{key}: fulfillment rate mismatch")

    totals = {field: sum(row[field] for row in by_day_product.values()) for field in fields}
    totals["net_shipped_value_krw"] = totals["shipped_value_krw"] - totals["returned_value_krw"]
    totals["order_line_count"] = len(visible_orders)
    for field, expected in totals.items():
        if summary[field] != expected:
            raise AssertionError(f"summary {field} mismatch")
    if summary["fulfillment_rate"] != round(totals["shipped_qty"] / totals["ordered_qty"], 4):
        raise AssertionError("summary fulfillment rate mismatch")

    files = [data_dir / f"{name}.csv" for name in source_names]
    files += [analysis_dir / "daily_product_metrics.csv", analysis_dir / "summary.json"]
    return {
        "status": "passed",
        "as_of": as_of,
        "daily_product_rows_checked": len(published_rows),
        "source_rows": {name: len(tables[name]) for name in source_names},
        "independent_totals": totals,
        "sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in files},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--analysis", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.input, args.analysis)
    (args.analysis / "audit.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({key: result[key] for key in ("status", "daily_product_rows_checked",
                                                      "source_rows")}, ensure_ascii=False))


if __name__ == "__main__":
    main()

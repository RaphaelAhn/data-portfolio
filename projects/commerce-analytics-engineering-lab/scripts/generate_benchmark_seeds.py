"""Generate FK-consistent synthetic commerce seeds at benchmark scale.

Writes CSVs matching the exact schema of the small checked-in fixtures in
seeds/, so dbt build can run against them unmodified. Used only for
performance benchmarking (docs/benchmarks.md) -- never overwrites the
checked-in seeds/ directly; scripts/run_benchmark.py handles the swap and
restores the original fixtures with `git checkout -- seeds/` afterward.
"""

from __future__ import annotations

import argparse
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

PRODUCTS = [
    ("P100", "SKINCARE", "Hydration Serum"),
    ("P200", "MAKEUP", "Lip Tint"),
    ("P300", "HAIR", "Repair Shampoo"),
    ("P400", "SKINCARE", "Vitamin C Toner"),
    ("P500", "MAKEUP", "Cushion Foundation"),
    ("P600", "HAIR", "Scalp Treatment"),
    ("P700", "FRAGRANCE", "Citrus Eau de Toilette"),
    ("P800", "SKINCARE", "Sunscreen SPF50"),
]

SEGMENTS = ["new", "returning", "vip"]
BASE_DATE = datetime(2026, 1, 1)


def write_csv(path: Path, header: list[str], rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def generate(order_count: int, outdir: Path, seed: int = 42) -> None:
    rng = random.Random(seed)
    customer_count = max(50, order_count // 8)

    # Customers
    customers = []
    for i in range(customer_count):
        joined = BASE_DATE - timedelta(days=rng.randint(0, 600))
        customers.append((f"C{i:07d}", joined.date().isoformat(), rng.choice(SEGMENTS)))
    write_csv(outdir / "raw_customers.csv", ["customer_id", "joined_at", "customer_segment"], customers)

    # Products (fixed small catalog; not scaled with order volume)
    products = [(pid, cat, name, "2026-01-01", "") for pid, cat, name in PRODUCTS]
    write_csv(outdir / "raw_products.csv", ["product_id", "category_id", "product_name", "valid_from", "valid_to"], products)

    orders = []
    order_items = []
    payments = []
    refunds = []
    inventory_events = []

    item_seq = 0
    refund_seq = 0
    event_seq = 0
    inventory_on_hand: dict[str, int] = {pid: 0 for pid, _, _ in PRODUCTS}

    # Opening receipts so running inventory never goes negative.
    receipt_qty = max(1000, order_count // 20)
    receipt_time = BASE_DATE - timedelta(days=1)
    for pid, _, _ in PRODUCTS:
        event_seq += 1
        inventory_events.append(
            (f"IE{event_seq:08d}", pid, receipt_qty, "receipt", receipt_time.isoformat(sep=" "), receipt_time.isoformat(sep=" "))
        )
        inventory_on_hand[pid] += receipt_qty

    for i in range(order_count):
        order_id = f"O{i:08d}"
        customer_id = f"C{rng.randrange(customer_count):07d}"
        ordered_at = BASE_DATE + timedelta(
            days=rng.randint(0, 240), seconds=rng.randint(0, 86_399)
        )
        status_roll = rng.random()
        if status_roll < 0.85:
            status = "completed"
        elif status_roll < 0.95:
            status = "cancelled"
        else:
            status = "pending"
        updated_at = ordered_at + timedelta(minutes=rng.randint(1, 30))
        orders.append((order_id, customer_id, status, ordered_at.isoformat(sep=" "), updated_at.isoformat(sep=" ")))

        item_count = rng.randint(1, 3)
        chosen_products = rng.sample(PRODUCTS, k=min(item_count, len(PRODUCTS)))
        order_amount = 0
        for pid, _, _ in chosen_products:
            item_seq += 1
            quantity = rng.randint(1, 3)
            list_price = rng.choice([12000, 15000, 18000, 20000, 25000, 32000])
            discount = rng.choice([0, 0, 0, 1000, 2000, 5000])
            order_items.append(
                (f"OI{item_seq:08d}", order_id, pid, quantity, list_price, discount)
            )
            order_amount += quantity * list_price - discount

            if status != "cancelled":
                event_seq += 1
                sale_time = updated_at + timedelta(minutes=1)
                inventory_events.append(
                    (f"IE{event_seq:08d}", pid, -quantity, "sale", sale_time.isoformat(sep=" "), sale_time.isoformat(sep=" "))
                )
                inventory_on_hand[pid] -= quantity

        if status in ("completed", "cancelled"):
            payment_status = "completed" if status == "completed" else "cancelled"
            paid_at = updated_at + timedelta(minutes=rng.randint(1, 5))
            payments.append(
                (f"PAY{i:08d}", order_id, payment_status, max(order_amount, 0), paid_at.isoformat(sep=" "), paid_at.isoformat(sep=" "))
            )

            if status == "completed" and rng.random() < 0.04:
                refund_seq += 1
                refund_amount = int(max(order_amount, 0) * rng.choice([0.3, 0.5, 1.0]))
                refunded_at = paid_at + timedelta(days=rng.randint(1, 5))
                ingested_at = refunded_at + timedelta(hours=rng.choice([0, 1, 24, 48]))
                refunds.append(
                    (
                        f"R{refund_seq:08d}",
                        f"PAY{i:08d}",
                        "completed",
                        refund_amount,
                        refunded_at.isoformat(sep=" "),
                        refunded_at.isoformat(sep=" "),
                        ingested_at.isoformat(sep=" "),
                    )
                )

    # Top up any product whose running balance would go negative (guards against
    # the RNG producing more sales than the opening receipt covers at large N).
    shortfall_time = BASE_DATE - timedelta(hours=12)
    for pid, balance in inventory_on_hand.items():
        if balance < 0:
            event_seq += 1
            inventory_events.append(
                (f"IE{event_seq:08d}", pid, abs(balance) + 100, "receipt", shortfall_time.isoformat(sep=" "), shortfall_time.isoformat(sep=" "))
            )

    write_csv(outdir / "raw_orders.csv", ["order_id", "customer_id", "order_status", "ordered_at", "updated_at"], orders)
    write_csv(
        outdir / "raw_order_items.csv",
        ["order_item_id", "order_id", "product_id", "quantity", "list_price", "discount_amount"],
        order_items,
    )
    write_csv(
        outdir / "raw_payments.csv",
        ["payment_id", "order_id", "payment_status", "paid_amount", "paid_at", "updated_at"],
        payments,
    )
    write_csv(
        outdir / "raw_refunds.csv",
        ["refund_id", "payment_id", "refund_status", "refund_amount", "refunded_at", "updated_at", "ingested_at"],
        refunds,
    )
    write_csv(
        outdir / "raw_inventory_events.csv",
        ["event_id", "product_id", "quantity_delta", "reason", "occurred_at", "ingested_at"],
        inventory_events,
    )

    print(
        f"Generated {order_count} orders -> {len(order_items)} items, "
        f"{len(payments)} payments, {len(refunds)} refunds, "
        f"{len(inventory_events)} inventory events (outdir={outdir})"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--orders", type=int, required=True, help="Number of orders to generate")
    parser.add_argument("--outdir", type=Path, required=True, help="Directory to write CSV seeds into")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for determinism")
    args = parser.parse_args()
    generate(args.orders, args.outdir, args.seed)


if __name__ == "__main__":
    main()

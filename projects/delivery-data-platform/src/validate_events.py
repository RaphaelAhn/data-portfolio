"""Validate minimal event-contract and lineage rules for the local fixture."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


ALLOWED_VARIANTS = {"control", "treatment"}


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    args = parser.parse_args()
    events = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line]
    errors: list[str] = []

    duplicate_ids = [event_id for event_id, count in Counter(e["event_id"] for e in events).items() if count > 1]
    if duplicate_ids:
        errors.append(f"duplicate event_id: {', '.join(duplicate_ids)}")

    orders = {e["order_id"]: e for e in events if e["event_type"] == "OrderCreated"}
    for order in orders.values():
        if order["experiment_variant"] not in ALLOWED_VARIANTS:
            errors.append(f"invalid experiment_variant for {order['order_id']}")

    for event in events:
        if event["event_type"] == "OrderCreated":
            continue
        order = orders.get(event["order_id"])
        if order is None:
            errors.append(f"orphan {event['event_type']} for {event['order_id']}")
        elif parse_time(event["event_time"]) < parse_time(order["event_time"]):
            errors.append(f"event before order creation: {event['event_id']}")

    if errors:
        print("Validation failed:", *errors, sep="\n- ")
        raise SystemExit(1)
    print(f"Validation passed: {len(events)} events, {len(orders)} orders")


if __name__ == "__main__":
    main()

"""Generate a deterministic, synthetic delivery-event fixture for local validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


EVENTS = [
    {"event_id": "ord-001", "event_type": "OrderCreated", "order_id": "O-1001", "event_time": "2026-01-01T12:00:00Z", "region_id": "R-SEOUL-01", "experiment_variant": "control"},
    {"event_id": "dsp-001", "event_type": "DispatchResult", "order_id": "O-1001", "dispatch_id": "D-1001-1", "rider_id": "rider-041", "result": "accepted", "eta_minutes": 26, "event_time": "2026-01-01T12:04:00Z"},
    {"event_id": "dlv-001", "event_type": "DeliveryCompleted", "order_id": "O-1001", "dispatch_id": "D-1001-1", "event_time": "2026-01-01T12:31:00Z"},
    {"event_id": "ord-002", "event_type": "OrderCreated", "order_id": "O-1002", "event_time": "2026-01-01T12:05:00Z", "region_id": "R-SEOUL-01", "experiment_variant": "treatment"},
    {"event_id": "dsp-002", "event_type": "DispatchResult", "order_id": "O-1002", "dispatch_id": "D-1002-1", "rider_id": "rider-018", "result": "accepted", "eta_minutes": 19, "event_time": "2026-01-01T12:08:00Z"},
    {"event_id": "dlv-002", "event_type": "DeliveryCompleted", "order_id": "O-1002", "dispatch_id": "D-1002-1", "event_time": "2026-01-01T12:25:00Z"},
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for event in EVENTS:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    print(f"Wrote {len(EVENTS)} synthetic events to {args.output}")


if __name__ == "__main__":
    main()

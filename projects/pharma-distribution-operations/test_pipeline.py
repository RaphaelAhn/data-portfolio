"""Independent checks for the synthetic distribution example."""

import copy
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pipeline  # noqa: E402
import audit as independent_audit  # noqa: E402


def small_tables():
    return {
        "order_lines": [
            {"order_line_id": "L1", "order_id": "O1", "product_id": "SYN-A",
             "order_at": "2026-09-01T09:00:00", "ordered_qty": 10, "unit_price_krw": 100},
            {"order_line_id": "L2", "order_id": "O1", "product_id": "SYN-B",
             "order_at": "2026-09-01T09:00:00", "ordered_qty": 5, "unit_price_krw": 200},
        ],
        "shipment_lines": [
            {"shipment_line_id": "S1", "order_line_id": "L1",
             "shipped_at": "2026-09-02T09:00:00", "shipped_qty": 8},
            {"shipment_line_id": "S2", "order_line_id": "L2",
             "shipped_at": "2026-09-02T09:00:00", "shipped_qty": 5},
        ],
        "return_lines": [
            {"return_line_id": "R1", "shipment_line_id": "S2",
             "returned_at": "2026-09-03T09:00:00",
             "recorded_at": "2026-09-04T09:00:00", "returned_qty": 1},
        ],
        "inventory_snapshots": [],
    }


class PipelineTests(unittest.TestCase):
    def test_hand_calculation_and_late_recording(self):
        tables = small_tables()
        _, before = pipeline.analyze(tables, "2026-09-03T23:59:59")
        rows, after = pipeline.analyze(tables, "2026-09-04T23:59:59")
        self.assertEqual((before["ordered_value_krw"], before["shipped_value_krw"],
                          before["returned_value_krw"], before["net_shipped_value_krw"]),
                         (2000, 1800, 0, 1800))
        self.assertEqual((after["returned_value_krw"], after["net_shipped_value_krw"],
                          after["fulfillment_rate"]), (200, 1600, 0.8667))
        self.assertEqual(len(rows), 2)

    def test_multiple_shipments_and_returns_do_not_multiply_order_amount(self):
        tables = small_tables()
        tables["order_lines"] = tables["order_lines"][:1]
        tables["shipment_lines"] = [
            {"shipment_line_id": "S1", "order_line_id": "L1",
             "shipped_at": "2026-09-02T09:00:00", "shipped_qty": 4},
            {"shipment_line_id": "S2", "order_line_id": "L1",
             "shipped_at": "2026-09-03T09:00:00", "shipped_qty": 6},
        ]
        tables["return_lines"] = [
            {"return_line_id": f"R{i}", "shipment_line_id": f"S{i}",
             "returned_at": "2026-09-04T09:00:00",
             "recorded_at": "2026-09-05T09:00:00", "returned_qty": 1}
            for i in (1, 2)
        ]
        _, summary = pipeline.analyze(tables, "2026-09-06T00:00:00")
        self.assertEqual((summary["ordered_value_krw"], summary["shipped_value_krw"],
                          summary["returned_value_krw"]), (1000, 1000, 200))

    def test_rejects_overship_overreturn_and_impossible_dates(self):
        original = small_tables()
        for change, expected in (
            (lambda t: t["shipment_lines"][0].update(shipped_qty=11), "shipment exceeds order"),
            (lambda t: t["return_lines"][0].update(returned_qty=6), "return exceeds shipment"),
            (lambda t: t["shipment_lines"][0].update(shipped_at="2026-08-31T09:00:00"),
             "shipment before order"),
            (lambda t: t["return_lines"][0].update(recorded_at="2026-09-02T09:00:00"),
             "invalid return dates"),
        ):
            with self.subTest(expected=expected):
                tables = copy.deepcopy(original)
                change(tables)
                with self.assertRaisesRegex(ValueError, expected):
                    pipeline.analyze(tables)

    def test_fixed_seed_csvs_are_reproducible_and_contain_only_allowed_columns(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            for location in (first, second):
                tables = pipeline.generate_tables()
                pipeline.write_tables(tables, Path(location))
                pipeline.read_tables(Path(location))
                self.assertGreater(len(tables["order_lines"]), 40)
                self.assertEqual(len(tables["inventory_snapshots"]), 8)
            for name in pipeline.COLUMNS:
                first_bytes = (Path(first) / f"{name}.csv").read_bytes()
                second_bytes = (Path(second) / f"{name}.csv").read_bytes()
                self.assertEqual(hashlib.sha256(first_bytes).digest(),
                                 hashlib.sha256(second_bytes).digest())
                self.assertNotIn(b"patient", first_bytes.lower())
                self.assertNotIn(b"prescription", first_bytes.lower())

    def test_independent_audit_rejects_changed_published_metric(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            data_dir = root / "data"
            analysis_dir = root / "analysis"
            tables = pipeline.generate_tables()
            pipeline.write_tables(tables, data_dir)
            rows, summary = pipeline.analyze(tables)
            pipeline.write_analysis(rows, summary, analysis_dir)
            self.assertEqual(independent_audit.audit(data_dir, analysis_dir)["status"], "passed")
            metric_path = analysis_dir / "daily_product_metrics.csv"
            text = metric_path.read_text(encoding="utf-8")
            metric_path.write_text(text.replace("10000", "10001", 1), encoding="utf-8")
            with self.assertRaisesRegex(AssertionError, "mismatch"):
                independent_audit.audit(data_dir, analysis_dir)


if __name__ == "__main__":
    unittest.main()

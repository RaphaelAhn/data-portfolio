import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from operations_pipeline import mask_pii, retrieve_policy, risk_and_route

class OperationsPipelineTest(unittest.TestCase):
    def test_masks_email_and_phone(self):
        masked = mask_pii("email a@example.com, phone 010-1234-5678")
        self.assertNotIn("a@example.com", masked); self.assertNotIn("010-1234-5678", masked)

    def test_expired_policy_is_not_retrieved(self):
        ticket = {"created_at": "2026-08-10T09:00:00+00:00", "issue_type": "배송", "masked_body": "배송이 지연"}
        policies = [{"policy_id": "old", "version": "1", "effective_from": "2025-01-01", "effective_to": "2026-01-01", "title": "배송", "body": "배송 지연"}, {"policy_id": "current", "version": "2", "effective_from": "2026-01-02", "effective_to": "9999-12-31", "title": "배송", "body": "배송 지연"}]
        policy, _ = retrieve_policy(ticket, policies); self.assertEqual("current", policy["policy_id"])

    def test_high_risk_ticket_routes_to_specialist(self):
        ticket = {"reopened": "false", "status": "closed", "created_at": "2026-08-10T10:00:00+00:00"}
        score, route, reasons = risk_and_route(ticket, 0.8, {"urgency": "high"})
        self.assertGreaterEqual(score, 4); self.assertEqual("specialist_review", route); self.assertIn("고위험 키워드/결제", reasons)

if __name__ == "__main__": unittest.main()

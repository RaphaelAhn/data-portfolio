"""Generate deterministic portfolio-only CS operations data."""
from __future__ import annotations

import csv
import json
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
random.seed(8102535)
AGENTS = [("A001", "배송"), ("A002", "배송"), ("A003", "환불"), ("A004", "결제"), ("A005", "계정"), ("A006", "일반")]
ISSUES = {
    "배송": ["배송이 지연되고 있습니다", "배송 상태가 멈췄습니다"],
    "환불": ["반품 후 환불 일정이 궁금합니다", "환불 금액이 아직 입금되지 않았습니다"],
    "결제": ["결제가 실패했습니다", "카드 결제가 승인되지 않습니다"],
    "계정": ["로그인이 되지 않습니다", "계정 접근을 확인해 주세요"],
}
POLICIES = [
    {"policy_id": "P-DEL-2026-01", "version": "2026.1", "effective_from": "2026-01-01", "effective_to": "9999-12-31", "title": "배송 지연 안내", "body": "배송 조회가 예정일을 초과한 경우 현재 물류 상태와 확인 절차를 안내합니다. 보상 또는 환불은 상담사가 정책 기준을 확인한 뒤 안내합니다."},
    {"policy_id": "P-REF-2026-01", "version": "2026.1", "effective_from": "2026-01-01", "effective_to": "9999-12-31", "title": "반품 및 환불", "body": "반품 접수와 검수 완료 여부를 확인한 뒤 환불 예정 절차를 안내합니다. 금액 또는 예외 보상은 자동으로 확정하지 않습니다."},
    {"policy_id": "P-PAY-2026-02", "version": "2026.2", "effective_from": "2026-02-01", "effective_to": "9999-12-31", "title": "결제 실패", "body": "결제 실패 시 결제수단과 오류 시점을 확인합니다. 카드 번호나 비밀번호 같은 민감정보를 요청하거나 저장하지 않습니다."},
    {"policy_id": "P-ACC-2026-01", "version": "2026.1", "effective_from": "2026-01-01", "effective_to": "9999-12-31", "title": "계정 접근", "body": "계정 접근 문제는 본인 확인 절차를 거쳐 지원합니다. 비밀번호나 인증번호를 상담 채널에서 요청하지 않습니다."},
]

def main() -> None:
    (ROOT / "policies.json").write_text(json.dumps(POLICIES, ensure_ascii=False, indent=2), encoding="utf-8")
    start = datetime(2026, 8, 1, tzinfo=UTC); tickets, assists = [], []
    for offset in range(21):
        day = start + timedelta(days=offset)
        for index in range(28 + (18 if offset in (18, 19) else 0)):
            issue = random.choices(list(ISSUES), weights=[42, 24, 22, 12])[0]
            agent_id, _ = random.choice(AGENTS); created = day + timedelta(hours=random.randrange(9, 19), minutes=random.randrange(60))
            body = random.choice(ISSUES[issue])
            if random.random() < 0.08: body += " 연락처는 customer@example.com 입니다."
            if random.random() < 0.05: body += " 즉시 보상해 주세요."
            ticket_id = f"T{offset + 1:02d}{index + 1:03d}"
            tickets.append({"ticket_id": ticket_id, "created_at": created.isoformat(), "channel": random.choice(["chat", "phone", "email"]), "issue_type": issue, "body": body, "agent_id": agent_id, "status": "open" if offset >= 19 and random.random() < 0.30 else "closed", "reopened": str(random.random() < 0.14).lower(), "handle_minutes": random.randint(5, 110)})
            assists.append({"ticket_id": ticket_id, "ai_draft_used": str(random.random() < 0.58).lower(), "review_outcome": random.choices(["approved", "edited", "rejected"], [68, 25, 7])[0], "latency_ms": random.randint(450, 2600), "estimated_cost_usd": round(random.uniform(0.001, 0.018), 4)})
    for filename, rows in (("synthetic_tickets.csv", tickets), ("synthetic_ai_assist.csv", assists)):
        with (ROOT / filename).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=rows[0]); writer.writeheader(); writer.writerows(rows)

if __name__ == "__main__": main()

"""Synthetic CS operations pipeline: quality checks, policy retrieval, routing, and reporting."""
from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA, OUTPUTS = ROOT / "data", ROOT / "outputs"
PII_PATTERNS = [re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"), re.compile(r"\b01[0-9]-?\d{3,4}-?\d{4}\b")]
HIGH_RISK_TERMS = ("보상", "법적", "개인정보", "비밀번호", "인증번호")

def mask_pii(text: str) -> str:
    for pattern in PII_PATTERNS: text = pattern.sub("[REDACTED]", text)
    return text

def tokenize(text: str) -> set[str]: return set(re.findall(r"[가-힣A-Za-z0-9]+", text.lower()))

def retrieve_policy(ticket: dict, policies: list[dict]) -> tuple[dict, float]:
    query = tokenize(ticket["issue_type"] + " " + ticket["masked_body"])
    eligible = [p for p in policies if p["effective_from"] <= ticket["created_at"][:10] <= p["effective_to"]]
    score, policy = max(((len(query & tokenize(p["title"] + " " + p["body"])) / max(1, len(query)), p) for p in eligible), key=lambda pair: pair[0])
    return policy, round(score, 3)

def classify_local(ticket: dict) -> dict:
    body = ticket["masked_body"]
    return {"issue_type": ticket["issue_type"], "urgency": "high" if any(term in body for term in HIGH_RISK_TERMS) or ticket["issue_type"] == "결제" else "normal", "summary": body[:90]}

def risk_and_route(ticket: dict, policy_score: float, classification: dict) -> tuple[int, str, list[str]]:
    reasons, risk = [], 0
    if ticket["reopened"] == "true": risk += 2; reasons.append("재문의")
    if ticket["status"] == "open": risk += 2; reasons.append("미처리")
    if classification["urgency"] == "high": risk += 4; reasons.append("고위험 키워드/결제")
    if policy_score < 0.10: risk += 3; reasons.append("정책 근거 부족")
    if ticket["status"] == "open" and (datetime.fromisoformat(ticket["created_at"]).hour - 9) % 24 >= 8: risk += 2; reasons.append("SLA 위험")
    return risk, "specialist_review" if risk >= 4 else "agent_approval", reasons

def read_csv(name: str) -> list[dict]:
    with (DATA / name).open(encoding="utf-8") as handle: return list(csv.DictReader(handle))

def validate(tickets: list[dict]) -> list[str]:
    errors, seen = [], set()
    for row in tickets:
        if row["ticket_id"] in seen: errors.append(f"duplicate ticket_id: {row['ticket_id']}")
        seen.add(row["ticket_id"])
        if int(row["handle_minutes"]) < 0: errors.append(f"negative handle_minutes: {row['ticket_id']}")
    return errors

def make_summary(tickets: list[dict], assists: list[dict], audits: list[dict]) -> dict:
    closed = [ticket for ticket in tickets if ticket["status"] == "closed"]
    by_day, by_issue = Counter(t["created_at"][:10] for t in tickets), Counter(t["issue_type"] for t in tickets)
    ordered_days, anomalies = sorted(by_day), []
    for position, day in enumerate(ordered_days):
        history = [by_day[prior] for prior in ordered_days[max(0, position - 7):position]]
        baseline = statistics.mean(history) if history else 0
        if len(history) >= 3 and by_day[day] > baseline * 1.25: anomalies.append({"date": day, "metric": "ticket_volume", "value": by_day[day], "baseline_mean": round(baseline, 1)})
    return {"portfolio_data_notice": "Synthetic data only; no actual CS performance is represented.", "ticket_count": len(tickets), "closed_ticket_count": len(closed), "average_handle_minutes": round(statistics.mean(int(t["handle_minutes"]) for t in closed), 1), "reopen_rate": round(sum(t["reopened"] == "true" for t in tickets) / len(tickets), 3), "tickets_by_issue": dict(by_issue), "review_routes": dict(Counter(a["route"] for a in audits)), "ai_review_outcomes": dict(Counter(a["review_outcome"] for a in assists)), "ai_assist_usage_rate": round(sum(a["ai_draft_used"] == "true" for a in assists) / len(assists), 3), "anomaly_candidates": anomalies}

def write_outputs(summary: dict, audits: list[dict]) -> None:
    OUTPUTS.mkdir(exist_ok=True); (OUTPUTS / "operations_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    fields = list(audits[0])
    for filename, rows in (("ai_assist_audit.csv", audits), ("review_queue.csv", [a for a in audits if a["route"] == "specialist_review"])):
        with (OUTPUTS / filename).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    lines = ["# CS 운영 일일 리포트", "", "> 가상 데이터 기반 포트폴리오 산출물이며 실제 운영 성과가 아닙니다.", "", "## 운영 요약", f"- 티켓 수: {summary['ticket_count']}", f"- 평균 처리 시간: {summary['average_handle_minutes']}분", f"- 재문의율: {summary['reopen_rate']:.1%}", f"- 전문 상담사 검수 큐: {summary['review_routes'].get('specialist_review', 0)}건", "", "## 조사 우선순위 후보"]
    for item in summary["anomaly_candidates"]: lines.append(f"- {item['date']} {item['metric']} {item['value']}건: 이전 일평균 {item['baseline_mean']}건 대비 증가. 원인 확정 전 채널·유형·시간대 점검 필요.")
    (OUTPUTS / "daily_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--use-openai", action="store_true"); args = parser.parse_args()
    classifier = classify_local
    if args.use_openai:
        from llm_adapter import classify_with_openai
        classifier = classify_with_openai
    tickets, assists = read_csv("synthetic_tickets.csv"), read_csv("synthetic_ai_assist.csv")
    if errors := validate(tickets): raise ValueError("Data quality checks failed: " + "; ".join(errors))
    policies = json.loads((DATA / "policies.json").read_text(encoding="utf-8")); audits = []
    for ticket in tickets:
        ticket["masked_body"] = mask_pii(ticket["body"]); policy, score = retrieve_policy(ticket, policies); classification = classifier(ticket); risk, route, reasons = risk_and_route(ticket, score, classification)
        audits.append({"ticket_id": ticket["ticket_id"], "issue_type": classification["issue_type"], "urgency": classification["urgency"], "policy_id": policy["policy_id"], "policy_version": policy["version"], "retrieval_score": score, "risk_score": risk, "route": route, "route_reasons": "|".join(reasons) or "normal", "masked_summary": classification["summary"]})
    write_outputs(make_summary(tickets, assists, audits), audits)

if __name__ == "__main__": main()

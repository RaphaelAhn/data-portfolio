# CS 운영 인텔리전스 공개 범위 결정

- Status: accepted
- Date: 2026-09-04
- Owners: Portfolio maintainer
- Scope: `projects/cs-operations-intelligence`
- Supersedes: none
- Superseded by: none

## Context

CS 운영과 AI 자동화 역량을 공개적으로 증명하되, 실제 고객·상담사·정책·API 비밀정보는 공개할 수 없음.

## Evidence

| Claim | Kind | Source and environment | Observed | Reference | Freshness / redaction |
| --- | --- | --- | --- | --- | --- |
| 기존 허브는 합성 데이터와 재현 가능한 분석 근거를 공개함 | fact | local repository | 2026-09-04 | `projects/commerce-analytics-engineering-lab/` | 실제 데이터 미포함 |
| 이 프로젝트는 외부 패키지 없이 실행 가능함 | runtime | local Python 3.12 | 2026-09-04 | `data/generate_synthetic_data.py`, `src/operations_pipeline.py` | 합성 데이터만 사용 |

## Decision

결정론적 데이터 생성기, SQL·Python 구현, 평가셋, 라우팅 정책과 테스트만 공개한다. 생성 CSV, 실행 출력, API 키, 실제 고객·운영 데이터는 커밋하지 않는다.

## Alternatives considered

- 별도 공개 저장소 — 기존 포트폴리오 허브의 기술 증거 구조와 중복되어 보류함.
- 실행 산출물 전체 커밋 — 재현 가능하고 매 실행 시 생성되므로 제외함.

## Consequences

- Positive: 채용 담당자가 코드와 안전성 설계를 재현·검토할 수 있음.
- Negative: 라이브 LLM 호출이나 실제 CS 효과를 증명하지 않음.
- Operational: 외부 API 연동은 환경 변수로만 허용하며, 실제 데이터 사용 전 보안·개인정보 검토가 필요함.

## Verification

- 데이터 생성, 파이프라인 실행, 단위 테스트 통과를 확인함.

## Revisit when

- 실제 공개 가능한 데이터셋, UI 데모 또는 검증된 LLM 평가 결과가 추가될 때.

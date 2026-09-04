# 딜리버리 데이터 플랫폼: 배차 품질·실험 분석을 위한 이벤트 처리 설계

주문, 배차, 라이더, 배달 완료 이벤트를 공통 키로 연결하고, 배차 품질과 정책 실험에 필요한 분석용 데이터 마트를 제공하는 **합성 데이터 기반 로컬 프로토타입**입니다.

> 이 사례는 특정 배달 서비스의 데이터·시스템·성과를 사용하거나 재현하지 않습니다. Kafka, Spark, Airflow, AWS 기반의 운영 아키텍처는 설계 범위이며, 이 저장소의 실행 코드는 표준 Python으로 이벤트 계약과 데이터 품질 규칙을 검증합니다. 실제 운영 규모, 실시간 SLA, 비용 절감, 비즈니스 성과를 주장하지 않습니다.

## 문제 정의

배달 운영 데이터는 주문 상태, 배차 시도, 라이더 위치, 배달 완료 이벤트가 서로 다른 시점에 도착하며, 중복 또는 지연 이벤트 때문에 팀마다 배차 성공률·ETA 오차·취소율을 다르게 계산하기 쉽습니다. 이 사례는 아래 질문에 답하는 데이터 기반을 설계합니다.

1. 주문부터 배차·완료까지의 이벤트를 어떤 키와 시간 기준으로 연결할 것인가?
2. 중복·지연·역순 이벤트가 발생했을 때 분석 지표의 정합성을 어떻게 지킬 것인가?
3. 배차 정책 A/B 테스트에서 노출과 결과를 재현 가능하게 어떻게 연결할 것인가?
4. 실시간 운영 지표와 배치 분석용 마트를 어떻게 분리해 관리할 것인가?

## 아키텍처

```text
Order / Dispatch / Rider / Delivery events
                    │
                    ▼
             Kafka topics (design)
                    │
                    ▼
 Spark Structured Streaming ──► Raw event storage
                    │                    │
                    ▼                    ▼
 Real-time operational view   Airflow batch orchestration
                    │                    │
                    └────────┬───────────┘
                             ▼
                  Clean / conformed layer
                             │
                             ▼
       Delivery marts in Trino / StarRocks (design)
                             │
               ┌─────────────┴─────────────┐
               ▼                           ▼
       Operations dashboard       A/B test analysis dataset
```

로컬 데모에서는 `src/generate_demo_events.py`가 JSONL 이벤트를 만들고, `src/validate_events.py`가 이벤트 계약·중복·참조 무결성·시간 순서 규칙을 검사합니다.

## 데이터 모델과 그레인

| 모델 | 그레인 | 용도 |
| --- | --- | --- |
| `raw_order_events` | 주문 상태 변경 이벤트 1건 | 주문 생성·취소 상태 추적 |
| `raw_dispatch_events` | 배차 시도 또는 결과 이벤트 1건 | 배차 시도·수락·실패 추적 |
| `raw_delivery_events` | 배달 완료 이벤트 1건 | 실제 배달 시간 및 ETA 오차 계산 |
| `fct_delivery_order` | 주문 1건 | 주문-배차-배달 결과를 연결한 핵심 사실 테이블 |
| `mart_delivery_daily` | 주문일·지역·실험군 1건 | 운영 대시보드 및 정책 실험 분석 |

상세한 키, event time, 지연 이벤트 처리 규칙은 [데이터 모델](docs/data-model.md)에 정리했습니다.

## 핵심 지표 정의

| 지표 | 정의 | 주의점 |
| --- | --- | --- |
| 배차 성공률 | 배차 결과가 `accepted`인 주문 ÷ 배차 대상 주문 | 취소 주문 및 중복 배차 이벤트 처리 기준을 명시해야 함 |
| 배차 소요 시간 | 첫 배차 시도 시각 − 주문 생성 시각 | event time 기준으로 계산 |
| ETA 오차 | 실제 배달 소요 시간 − 배차 시점의 ETA | 완료 이벤트가 없는 주문은 제외하고 별도 모니터링 |
| 취소율 | 취소 주문 ÷ 주문 생성 주문 | 취소 원인과 취소 시점을 별도 보존 |
| 라이더 가동률 | 가용 시간 중 배달 수행 시간의 비율 | 위치 이벤트가 없는 구간의 해석을 제한 |

## 실행 및 검증

Python 3.11 이상에서 외부 패키지 없이 실행할 수 있습니다.

```powershell
python src/generate_demo_events.py --output data/demo/delivery_events.jsonl
python src/validate_events.py --input data/demo/delivery_events.jsonl
```

생성된 파일은 `.gitignore`의 `data/` 규칙에 따라 커밋되지 않습니다. 검증기는 다음을 확인합니다.

- `event_id`의 유일성
- 주문 생성 전에 발생한 배차·완료 이벤트가 없는지
- 배차·배달 이벤트가 존재하는 주문을 참조하는지
- 완료 시각이 주문 생성 시각보다 빠르지 않은지
- 실험군 값이 허용된 계약을 따르는지

## 운영 설계

- [운영 및 데이터 품질 Runbook](docs/operations-runbook.md): 품질 검사, 지연 이벤트, 백필, 모니터링 및 장애 대응 원칙
- [실험 데이터 설계](docs/experiment-design.md): 노출·배정·결과 이벤트와 분석 안전장치
- [샘플 데이터 마트 SQL](sql/mart_delivery_daily.sql): Trino 호환 SQL을 목표로 작성한 마트 쿼리 예시

## 한계와 다음 단계

- 로컬 코드는 스트리밍 엔진·오케스트레이터·클라우드 인프라를 구동하지 않습니다.
- 합성 이벤트는 실제 주문량, 라이더 행동, 배차 알고리즘을 대표하지 않습니다.
- 다음 구현 단계는 Docker 기반 Kafka/Spark 개발 환경, Airflow DAG, dbt 테스트, 지연 이벤트 재처리 통합 테스트입니다.

# 데이터 모델 및 이벤트 계약

## 식별자와 시간 기준

| 필드 | 설명 | 규칙 |
| --- | --- | --- |
| `event_id` | 이벤트의 불변 식별자 | 전체 이벤트 스트림에서 유일해야 함 |
| `order_id` | 주문 식별자 | 모든 배차·완료 이벤트가 참조해야 함 |
| `dispatch_id` | 배차 시도 식별자 | 재배차는 새 `dispatch_id`를 사용 |
| `rider_id` | 라이더 식별자 | 분석용으로 가명화된 키를 사용 |
| `event_time` | 실제 비즈니스 발생 시각 | 지표 산출과 이벤트 순서 판단의 기준 |
| `ingested_at` | 플랫폼 수집 시각 | 지연 도착 감시와 재처리 범위 산정에 사용 |

`event_time`과 `ingested_at`을 분리합니다. 운영 시스템의 네트워크 지연이나 재시도로 인해 수집 순서가 실제 발생 순서와 다를 수 있으므로, 단순 수집 순서로 배차 소요 시간이나 ETA 오차를 계산하지 않습니다.

## 이벤트별 최소 계약

### OrderCreated

```json
{"event_id":"ord-001","event_type":"OrderCreated","order_id":"O-1001","event_time":"2026-01-01T12:00:00Z","region_id":"R-SEOUL-01","experiment_variant":"control"}
```

### DispatchResult

```json
{"event_id":"dsp-001","event_type":"DispatchResult","order_id":"O-1001","dispatch_id":"D-1001-1","rider_id":"rider-041","result":"accepted","eta_minutes":26,"event_time":"2026-01-01T12:04:00Z"}
```

### DeliveryCompleted

```json
{"event_id":"dlv-001","event_type":"DeliveryCompleted","order_id":"O-1001","dispatch_id":"D-1001-1","event_time":"2026-01-01T12:31:00Z"}
```

## 정합성 규칙

1. 같은 `event_id`가 두 번 적재되면 후속 처리에서 한 번만 반영합니다.
2. `DispatchResult`, `DeliveryCompleted`는 반드시 이미 생성된 `order_id`를 참조해야 합니다.
3. 완료 시각은 주문 생성 시각보다 빠를 수 없습니다.
4. 하나의 주문에는 여러 배차 시도가 가능하므로, 주문 수준 지표는 최종 유효 결과를 선택하는 규칙을 명시해야 합니다.
5. 취소·완료처럼 종결 상태가 변경되는 경우에는 최신 상태의 근거 이벤트와 변경 시각을 보존합니다.
6. 이벤트가 늦게 도착하면 해당 주문과 영향을 받는 일자·지역·실험군 마트를 재계산합니다.

## 마트의 계산 경계

`mart_delivery_daily`는 `order_date`, `region_id`, `experiment_variant` 단위로 계산합니다. 이 그레인은 지역 또는 실험군 간 비교에는 유용하지만, 라이더별 가동률 같은 세부 운영 분석에는 별도의 라이더-시간 단위 마트가 필요합니다.

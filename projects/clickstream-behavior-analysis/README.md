# 공개 클릭스트림 기반 사용자 탐색 행동 분석

공개 이커머스 클릭스트림을 세션 단위로 집계해, 사용자의 탐색 깊이와 상품 카테고리별 행동 차이를 기술 통계로 분석한 개인 프로젝트임.

[English version](README.en.md)

> **범위 고지:** 이 사례는 실제 기업의 운영 데이터나 성과가 아님. 원천 데이터에는 구매 완료·매출·장기 사용자 식별 정보가 없어 전환율, 리텐션, 매출 성과, 개별 고객 행동에 관한 결론을 주장하지 않음.

## Problem

한 세션에서 사용자가 얼마나 깊게 상품을 탐색하는지, 상품의 주 카테고리와 첫 클릭의 화면 위치에 따라 탐색 깊이가 어떻게 달라지는지를 확인하였음.

## Data and method

- UCI Machine Learning Repository의 *Clickstream Data for Online Shopping* 공개 데이터를 사용하였음.
- 2008년 4–8월 의류 쇼핑몰 클릭스트림 165,474건을 24,026개 세션 단위로 집계하였음.
- 세션 ID별 클릭 수와 최대 클릭 순서로 탐색 깊이를 정의하였음.
- 주 카테고리·첫 클릭의 화면 위치별 평균 탐색 깊이를 비교하였음.
- 세션을 `1회`, `2–3회`, `4–6회`, `7회 이상` 탐색 구간으로 분류하였음.

## Technical implementation

- SQL: 세션 ID, 클릭 순서, 상품 카테고리를 기준으로 같은 집계 로직을 작성하였음.
- Node.js: 원본 CSV를 입력으로 받아 세션 단위 결과와 요약 산출물을 재현하였음.
- Outputs: 탐색 깊이 분포, 카테고리별 평균 탐색 깊이, 포트폴리오용 해석·한계 문서를 생성하였음.

## Interpretation and limitations

결과는 집계 수준의 탐색 행동을 설명하는 데만 사용하였음. 구매·매출·실험군·장기 사용자 식별자가 없으므로, 비즈니스 전환 효과나 인과 관계를 판단할 수 없음.

## Source

- [UCI Clickstream Data for Online Shopping](https://archive.ics.uci.edu/dataset/553/clickstream%2Bdata%2Bfor%2Bonline%2Bshopping)

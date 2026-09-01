# Fraud Risk Scoring


An offline modeling prototype that uses public simulated transaction data to rank transactions for review under limited investigator capacity.


[한국어 버전](README.md)


> **Scope notice:** This is not customer data or production performance from a financial service. All results come from offline evaluation on public simulated data and do not demonstrate loss reduction, customer-experience outcomes, regulatory compliance, or online serving performance.


## Problem


Rather than automatically deciding every transaction, the prototype ranks transactions by risk for a **daily review queue of 100 cases**. Evaluation therefore considers not only overall classification performance but also the utility of the top 100 ranked cases.


## Validation design


- Split training and evaluation data in chronological order.
- Apply a **7-day label-delay gap** between training and final evaluation to reduce leakage risk.
- Final test set: 66,741 transactions and 614 simulated anomalous transactions.
- Baseline: Logistic Regression.
- Comparison model: HistGradientBoosting (HGB).


## Results


| Metric | Logistic Regression | HistGradientBoosting |
| --- | ---: | ---: |
| PR-AUC | 0.555 | 0.732 |
| Precision@100 | — | 63.7% |
| Recall@100 | — | 72.6% |


- **Precision@100**: the proportion of anomalous transactions among the 100 reviewed transactions.
- **Recall@100**: the proportion of all simulated anomalous transactions included in the top-100 review queue.


### Segment analysis


For the 50–99 transaction-amount range, the model captured 94 of 160 anomalous transactions, for a recall of 58.8%. The remaining 66 simulated anomalies were outside the top-100 review queue; this is interpreted as a priority segment for further feature engineering and threshold review.


## Portfolio material


- [Portfolio PDF — Korean](이상거래_리스크_스코어링_포트폴리오_6p.pdf)
- [Portfolio PDF — English](Fraud_Risk_Scoring_Portfolio_6p_EN.pdf)


## Reproducibility and data policy


This repository is a portfolio hub and does not contain raw data or executable source code, so the results cannot be rerun from this repository. After the code and reproducibility workflow are organized and verified, they will be published in a separate project repository and linked here.


Raw data, personal information, and private configuration values are not included.


## Limitations and next steps

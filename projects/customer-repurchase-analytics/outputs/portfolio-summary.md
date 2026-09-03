# Analysis Results

## Data and evaluation design

- Clean transaction lines: 397,884
- Unique customers: 4,338
- Training rows across three time-based snapshots: 8,972
- Customers in the final evaluation: 3,357
- 90-day repurchase rate in the final evaluation: 57.0%

## Prioritization performance

| Method | ROC-AUC | Customers reviewed | Precision@Top 10% | Recall@Top 10% | Repeat purchasers captured |
| --- | ---: | ---: | ---: | ---: | ---: |
| Recency baseline | 0.687 | 336 | 78.9% | 13.8% | 265 |
| Logistic regression with RFM, product diversity, and prior history | 0.735 | 336 | 95.5% | 16.8% | 321 |

## Interpretation

The top-10% metric represents an offline review queue under limited CRM capacity. It does **not** show that a message or incentive caused additional purchases. A production test should use a randomized holdout group and evaluate incremental repurchase rate, contribution margin, and unsubscribe rate.

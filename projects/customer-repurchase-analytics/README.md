# Customer Repurchase Prediction and CRM Prioritization

This offline analysis uses public e-commerce transactions to identify customers who are likely to purchase again within 90 days and to design a capacity-aware CRM review queue.

> **Scope notice:** This project does not use data from Olive Young or any other named company. All figures are offline results from the public UCI Online Retail dataset. They do not represent campaign lift, production performance, or realized business impact.

## Problem

Broad retention campaigns can spread CRM resources across customers with very different purchase patterns. This project asks: **which customers should be reviewed first when CRM capacity is limited?** The evaluation therefore measures both overall ranking quality and how many future repeat purchasers appear in the highest-scored 10% of customers.

## Data

- Source: [UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online-retail)
- Period: December 1, 2010–December 9, 2011
- Original data: 541,909 transaction lines from a UK-based online retailer
- Available fields: invoice, product, quantity, transaction time, unit price, customer ID, and country
- Cleaning: removed cancelled invoices, rows without a customer ID, and rows with non-positive quantity or unit price

The raw dataset is not committed to this repository. Dataset licensing and attribution follow the UCI source page.

## Decision design

| Item | Definition |
| --- | --- |
| Prediction unit | Customer ID |
| Final observation cutoff | September 8, 2011 |
| Target | At least one positive purchase during the next 90 days |
| Feature windows | Most recent 90 days plus the preceding 180 days |
| CRM review capacity | Top-scored 10% of customers |
| Baseline | Ranking customers by purchase recency alone |

## Method

1. **Transaction cleaning:** excluded cancellations and unidentified customers, then calculated line revenue as `Quantity × UnitPrice`.
2. **Customer features:** calculated recency, order frequency, item quantity, revenue, average order value, product diversity, and prior-period order history.
3. **Time-based validation:** combined training snapshots from June, July, and August 2011. Each snapshot used only information available before its cutoff and labeled purchases in the following 90 days.
4. **Modeling:** fitted an L2-regularized logistic regression on standardized customer features. Future transactions were never included in feature construction.
5. **Evaluation:** compared the model with the recency baseline using ROC-AUC, Precision@Top 10%, and Recall@Top 10%.

## Results

The fixed final evaluation included 3,357 customers, of whom 57.0% purchased again within 90 days.

| Method | ROC-AUC | Customers reviewed | Precision@Top 10% | Recall@Top 10% | Repeat purchasers captured |
| --- | ---: | ---: | ---: | ---: | ---: |
| Recency baseline | 0.687 | 336 | 78.9% | 13.8% | 265 |
| Logistic regression with RFM, product diversity, and prior history | 0.735 | 336 | 95.5% | 16.8% | 321 |

At the same review capacity, the model captured 56 more future repeat purchasers than the recency-only baseline. This is evidence of better offline prioritization, **not evidence that a campaign caused additional purchases**.

## CRM action hypothesis

The score is designed as an input to human review rather than an automatic messaging rule.

- High-score customers: review recent category, order value, and purchase cadence to select replenishment reminders, complementary products, or membership benefits.
- Mid-score customers: consider lower-cost reminders or content exposure.
- Low-score customers: avoid blanket discounts and use a separate reactivation test or customer-research track.

A production workflow would also enforce consent, inventory, margin, and contact-frequency constraints. Incremental repurchase rate, contribution margin, and unsubscribe rate should be evaluated with a randomized holdout group.

## Reproducibility

Install the dependencies in `requirements.txt`, download `Online Retail.xlsx` from UCI, and run the following command from this project directory:

```powershell
python src/analyze_repurchase.py --input ..\..\data\raw\online-retail\Online Retail.xlsx
```

The script writes a machine-readable summary and a portfolio-ready results table to `outputs/`.

## Limitations

- The dataset does not contain marketing exposure, browsing behavior, offline-store activity, margin, inventory, or messaging consent.
- A 90-day target can understate retention for customers with longer purchase cycles.
- Missing customer IDs and cancellation rules can affect the analytical population.
- Offline prediction quality does not establish campaign incrementality, deployment reliability, or production monitoring performance.

## Source

Chen, D. (2015). *Online Retail* [Dataset]. UCI Machine Learning Repository. [https://doi.org/10.24432/C5BW33](https://doi.org/10.24432/C5BW33)

# Technical Profile and Evidence

This page separates the tools named in the resume and cover letter from the evidence available in public portfolio work. It documents how a tool was used for an analytical question instead of presenting a technology list without context.

[한국어 버전](TECHNICAL_PROFILE.md)

> **Public-scope notice:** This page does not claim production performance or customer data. Skill levels reflect the submitted resume. Project results are limited to offline analysis of public or simulated data.

## Core tools

| Tool | Resume level | Project evidence | Public scope |
| --- | --- | --- | --- |
| SQL | Intermediate | Aggregated clickstream records by session ID, click order, and product category; defined exploration segments | Aggregation and descriptive analysis |
| Python | Intermediate | Used for time-based validation, baseline comparison, and error/segment analysis of simulated transactions | Offline prototype |
| Node.js | Used in project | Reproduced session-level results through a public-clickstream analysis script | Local analysis script |
| Excel | Advanced | Resume self-assessment | No linked artifact in this hub yet |
| Tableau / Power BI | Foundational | Resume self-assessment | No dashboard implementation artifact in this hub yet |
| Git | Foundational | Used to version analysis documentation and project materials | Public-repository scope |

## Analytical methods

- Session-level data modeling and aggregation
- Metric definition and segment comparison
- Chronological training/evaluation separation
- Baseline comparison and priority evaluation under limited review capacity
- Documentation of data scope, interpretation limits, and reproduction steps

## Project evidence

| Case study | Verifiable tools and methods | Interpretation scope |
| --- | --- | --- |
| [Public Clickstream User-Exploration Analysis](projects/clickstream-behavior-analysis/README.en.md) | SQL, Node.js, session aggregation, exploration-depth segments, descriptive analysis | Public clickstream analysis without purchase, revenue, or retention outcomes |
| [Customer Repurchase Prediction and CRM Prioritization](projects/customer-repurchase-analytics/) | Python, time-based validation, RFM and product-diversity features, baseline comparison, capacity-aware ranking | Offline analysis of public transaction data |
| [Fraud Risk Scoring](projects/fraud-risk-scoring/README.en.md) | Python, time-based validation, baseline comparison, prioritization queue, error/segment analysis | Offline prototype on simulated data |
| [Sales & Marketing Analytics + AI Copilot](projects/sales-marketing-analytics-ai-copilot/README.en.md) | Data-mart design, data-quality rules, SQL modeling, AI workflow design | Fictional case study using synthetic-data assumptions |

## Evidence standards

- No raw data, personal information, or private keys are published.
- A metric or outcome is used in the resume or portfolio only when it agrees with source code or an output document.
- Production customer impact, revenue/P&L impact, deployment, and advanced BI implementation are not claimed without evidence.
- The fraud-risk project has a discrepancy between resume and project-page dataset/evaluation figures; those values should be reconciled against the source analysis before further external use.

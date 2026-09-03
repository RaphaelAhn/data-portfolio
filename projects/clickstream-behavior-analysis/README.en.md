# Public Clickstream User-Exploration Analysis

An individual project that aggregates public e-commerce clickstream records at the session level to describe exploration depth and category-level behavior.

[한국어 버전](README.md)

> **Scope notice:** This is not a company's production dataset or operational result. The source has no completed-purchase, revenue, or long-term user-identity fields; it does not support claims about conversion, retention, revenue outcomes, or individual customer behavior.

## Problem

How deeply do users explore products within a session, and how does exploration depth differ by main product category and first-click screen position?

## Data and method

- Used the UCI Machine Learning Repository's *Clickstream Data for Online Shopping* public dataset.
- Aggregated 165,474 apparel-store clickstream records from April–August 2008 into 24,026 sessions.
- Defined exploration depth from clicks per session and maximum click order.
- Compared average exploration depth by main category and first-click screen position.
- Classified sessions into `1 click`, `2–3 clicks`, `4–6 clicks`, and `7+ clicks` segments.

## Technical implementation

- **SQL:** expressed the session aggregation with session ID, click order, and product category.
- **Node.js:** reproduced session-level outputs and summaries from the source CSV.
- **Outputs:** exploration-depth distribution, average exploration depth by category, and a portfolio interpretation/limitations document.

## Interpretation and limitations

The results describe aggregated exploration behavior only. Because purchase, revenue, experimental-group, and long-term user-identity fields are absent, the analysis cannot establish business conversion effects or causality.

## Source

- [UCI Clickstream Data for Online Shopping](https://archive.ics.uci.edu/dataset/553/clickstream%2Bdata%2Bfor%2Bonline%2Bshopping)

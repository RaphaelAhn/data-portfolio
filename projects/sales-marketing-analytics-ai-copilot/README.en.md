# Sales & Marketing Analytics + AI Copilot

A **fictional case study** showing how a Sales and Marketing data mart can support both decision workflows and a controlled AI sales assistant.

[한국어 버전](README.md)

> **Scope notice:** This is a portfolio demonstration. The company, customers, data, implementation details, and outcomes are illustrative; it does not represent production performance or a specific company's systems.

## Problem

When CRM, paid-media, web-behavior, opportunity, and revenue data live in separate systems, teams may know lead volume but cannot consistently decide which segments and campaigns deserve the next unit of sales and marketing capacity. Representatives also spend time switching between tools to research a lead and decide on a next action.

## Approach

### 1. Decision-ready data mart

The design connects customer and lead records through a common identity and defines the following analytical models.

| Model | Purpose |
| --- | --- |
| Customer / lead | Standardizes customer segments, acquisition channel, owner, and lifecycle status |
| Touchpoint | Records intent signals such as pricing-page views, demo requests, and content engagement |
| Opportunity / revenue | Connects sales stage, expected value, and net revenue to channels and campaigns |
| Daily growth mart | Aggregates leads, MQLs, SQLs, opportunities, and revenue by date, channel, and campaign |
| Lead-priority mart | Combines fit, purchase intent, recency, and expected value into an explainable score |

Data quality is evaluated with primary-key uniqueness, required fields, accepted lifecycle statuses, and referential integrity between leads, touchpoints, and opportunities.

### 2. Decision workflow

- **Growth Command Center:** target attainment, CAC, pipeline, and notable changes
- **Funnel & Response SLA:** stage conversion, backlog, and first-response time for high-value leads
- **Channel-to-Revenue:** channel and campaign comparison through SQL, opportunities, and net revenue—not just lead volume
- **Lead queue:** an explainable score to prioritize the leads that deserve review today

### 3. AI Sales Copilot boundary

The Copilot turns read-only, approved mart context into a concise brief with evidence and a draft next action. A deterministic rules-based model calculates priority; the LLM summarizes evidence and does not manufacture customer facts.

- Retrieve only the rows authorized for the requester
- Include sources, data-refresh time, and unknown information in every recommendation
- Require human confirmation before any CRM write or customer contact
- Measure groundedness, usefulness, adoption, and access-control failures separately

## Validation scope

This case does not claim business outcomes. A real implementation would measure research time, time to first contact for high-value leads, recommendation adoption, and MQL-to-SQL conversion against a baseline and comparison group. Channel mix, seasonality, and changes in sales capacity would also be considered.

## Technical evidence

A public implementation repository is planned to contain synthetic data, dbt SQL models, data tests, local reproduction instructions, and the Copilot's access, audit, and confirmation design. It will not contain raw customer data, private keys, or real performance data.

## Skills demonstrated

- Translating a business bottleneck into metrics, data models, and workflow design
- Designing SQL data marts and data-quality rules
- Connecting analysis to budget allocation, lead routing, and sales action
- Designing AI workflow assistance with access control, traceability, and human confirmation

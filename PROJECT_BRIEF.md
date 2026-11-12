# Project brief

**In development.** Fictional direct-to-consumer mattress retailer; no analysis results yet.

## Business objective

Analyze acquisition spend and customer journeys, identify conversion problems, reconcile purchases and revenue, and recommend prioritized experiments. The eventual audience is a growth or e-commerce team deciding where to focus measurement and experimentation.

## Questions to answer

- How does spend relate to measured acquisition and purchases by channel?
- Where do users leave the product, cart and checkout journey?
- Why do GA4 purchase events and Shopify orders or revenue differ?
- Which experiments are justified by validated quantitative and qualitative evidence?

## Milestones and acceptance criteria

1. **Local foundation:** folders, documentation, isolated Python, safety rules and verification. Completed and uploaded to private GitHub; the remote was empty, so no merge was needed.
2. **Measurement plan and synthetic data (user-facing Milestone 1):** implemented definitions, linked schemas, deterministic 90-day baseline, separate quality fixtures and automated checks. See docs/MEASUREMENT_PLAN.md and docs/SIMULATION_ASSUMPTIONS.md. No business analysis or live integration is implied.
3. **Local SQL analysis (user-facing Milestone 2):** implemented SQLite schemas, same-session funnels, daily financials, campaign acquisition, purchase-event reconciliation, visit classification, independent fixtures and a reviewed synthetic report. Real-data and causal conclusions are out of scope.
4. **Source connections and real-data quality:** planned; authorize each account separately, document permissions/extraction/freshness and repeat reconciliation against real source totals. No paid service activation without approval.
5. **Analysis and visualization:** build reproducible funnel and acquisition analyses and a Tableau dashboard with definitions and traceable evidence.
6. **Experiment recommendations:** rank hypotheses using evidence, expected impact, confidence and effort. Specify primary metric, guardrails, eligibility and test design; do not claim causal lift without a suitable experiment.
7. **Portfolio release:** reproduce outputs, validate AI contributions, review privacy and document limitations before publishing sanitized artifacts.

## Scope and constraints

The current milestone includes local synthetic generation, SQLite analysis and validation, not real data collection, real business conclusions, external account configuration, dashboards or experiments. Revenue definitions address refunds, cancellations, tax, shipping, discounts and currencies. Ad-platform attributed conversions can overlap and must not be added as unique orders. Attribution is not proof of incremental impact.

## Planned deliverables

A measurement plan, data dictionary, synthetic quality checks, SQLite purchase/revenue reconciliation, funnel/acquisition analysis and reviewed synthetic report are implemented. Real source mapping and analysis, cloud warehouse, dashboard and prioritized experiment backlog remain planned.

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
2. **Measurement plan and synthetic data:** define grain, keys, date windows, time zones, currencies, consent limitations, attribution and revenue rules; create labeled synthetic fixtures with known expected totals.
3. **Source connections:** authorize each account separately; document permissions, extraction method, freshness and limitations. No paid service activation without approval.
4. **Quality and reconciliation:** test uniqueness, completeness, joins and totals; quantify matched and unmatched records; explain residual differences before interpreting performance.
5. **Analysis and visualization:** build reproducible funnel and acquisition analyses and a Tableau dashboard with definitions and traceable evidence.
6. **Experiment recommendations:** rank hypotheses using evidence, expected impact, confidence and effort. Specify primary metric, guardrails, eligibility and test design; do not claim causal lift without a suitable experiment.
7. **Portfolio release:** reproduce outputs, validate AI contributions, review privacy and document limitations before publishing sanitized artifacts.

## Scope and constraints

Initial setup does not include data collection, analysis, external account configuration, dashboards or experiments. Revenue definitions must explicitly address refunds, cancellations, tax, shipping, discounts and currencies. Ad-platform attributed conversions can overlap and must not be added as unique orders. Attribution is not proof of incremental impact.

## Planned deliverables

A measurement dictionary, source mapping, data quality checks, purchase and revenue reconciliation, funnel analysis, acquisition analysis, dashboard, prioritized experiment backlog and validation log. These are planned outputs, not completed work.

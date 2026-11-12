# Validation requirements

Synthetic schema, reproducibility and arithmetic checks run through the automated test suite; see MILESTONE_1_VALIDATION.md for the original results and ../reports/MILESTONE_2_ANALYSIS.md for local SQL controls. Milestone 2 adds hand-calculated SQL fixtures, as-of/reprocessing regressions, full-run reproducibility and source-total reconciliation. No real data or business conclusions have been validated. Environment and synthetic checks do not validate real business conclusions.

Before analysis, document each table's grain, unique key, source, extraction time, time zone, currency and applicable date range. Check missing fields, duplicates, valid values, source totals and join cardinality; avoid inflated revenue from many-to-many joins.

For reconciliation, define which Shopify orders qualify and whether revenue is gross or net. Align refund timing, discounts, shipping, tax, cancellations and currencies. Match GA4 transaction IDs to eligible orders, report unmatched records in both directions, quantify differences and document tolerances before using the results. Do not assume browser events capture every order.

For journeys, define the population and denominator at each step, user versus session scope, event order, identity limitations and consent gaps. For acquisition, distinguish spend, platform-attributed revenue and reconciled orders. Define CAC, ROAS and conversion rate explicitly before calculating them.

## Validated AI workflow

1. Record the question, permitted inputs, assumptions and proposed method. Use synthetic or approved anonymized inputs.
2. Treat AI-generated code, SQL and prose as drafts. Inspect for incorrect joins, invented columns, leakage and unsupported claims.
3. Run code on known fixtures, compare key totals using an independent calculation, and trace statements back to saved evidence.
4. Record tool/model when used, checks performed, outcomes, reviewer and remaining uncertainty in a validation log.
5. Publish only reviewed, reproducible claims. Label observational associations and hypothetical experiments clearly.

Suggested future log fields: date, question, data version, code revision, AI contribution, independent check, expected/actual outcome, reviewer and limitations.

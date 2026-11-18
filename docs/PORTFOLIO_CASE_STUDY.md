# E-commerce growth analytics — synthetic portfolio case study

**Fictional DTC mattress retailer. Synthetic demonstration only; no findings about Puffy, real customers or measured commercial improvements. Dashboard final acceptance is pending.**

## Question and approach

Where do journeys lose potential buyers, how does acquisition performance vary, and what deserves investigation? I defined sessions, visitors, orders, revenue and attribution before analysis. A deterministic 90-day dataset makes the work reproducible without exposing customer information. Python generates and validates data; SQLite calculates results; equivalent GoogleSQL was executed in a BigQuery sandbox; three local Tableau dashboards present the reconciled baseline.

Seed 42 covers January 1–March 31, 2026 UTC, with refund observation through April 16 exclusive. There are 1,496 observed visitor identities, 2,700 sessions, 7,170 events, 377 orders and 79 partial refunds. Dataset fingerprint: `e486a1983c44d36bc6b57eddda6849feff49092ae3acea3b39d319e366f2e5da`.

## Calculated synthetic results

| Measure | Result |
|---|---:|
| Distinct converting sessions / sessions | 377 / 2,700 = 13.96% |
| Orders / purchasing visitor identities | 377 / 331 |
| Merchandise revenue before refunds | $345,007.20 |
| Refunds / net merchandise revenue | $14,084.25 / $330,922.95 |
| Paid media spend / paid-attributed net | $44,259.88 / $173,184.63 |
| Net attributed ROAS / first-observed paid CAC proxy | 3.91 / $245.89 |

Ordered funnel: 2,700 starts → 2,380 product views → 1,036 carts → 677 checkouts → 377 purchases. The largest absolute loss is product view to cart (1,344 sessions). Mobile conversion is 11.78% versus desktop 18.57%, but the generator deliberately sets device-specific probabilities. There are 195 campaign-days with spend and zero attributed orders; this is not proof of wasted spend.

## Decisions supported by this work

First validate tracking and price/delivery-information clarity before proposing a product-page experiment. Compare mobile and desktop within comparable source/visit cohorts before diagnosing friction. Investigate attribution sensitivity before changing budgets. These are learning priorities, not commercial recommendations justified by real-world evidence. Detailed alternatives and evidence requirements are in ../dashboard/DECISION_REPORT.md; one proposed test is in EXPERIMENT_PROTOCOL.md.

## Why the calculations are credible

Items and refunds are aggregated before joining orders. Campaign outcomes meet spend at campaign-day grain. Converting sessions stay distinct even when one session has multiple orders. Separate fixtures cover missing transaction IDs, duplicate purchases, late events, multiple items/refunds and skipped journeys. Independent hand calculations anchor expected results; counts and money reconcile with zero differences. The historical live BigQuery run passed 96/96 parity comparisons. AI-assisted work was reviewed through execution and independent fixtures rather than accepted as factual output.

## Limits and interview explanation

Perfect simulated identity, same-session attribution, simplified prices/refunds and missing landing pages limit interpretation. First observed purchasers are not necessarily new customers. No real-source connector or A/B experiment was implemented. BigQuery tables were temporary; local exports and the packaged workbook preserve the demonstration. See ../release/EVIDENCE_INDEX.md for current acceptance, historical results and reproducibility.

“I built a traceable analytics workflow, checked that joins could not multiply revenue or advertising costs, and verified it across SQLite and BigQuery. The dashboard turns those validated synthetic calculations into investigation questions. I distinguish reliable arithmetic from evidence that a business change would work.”

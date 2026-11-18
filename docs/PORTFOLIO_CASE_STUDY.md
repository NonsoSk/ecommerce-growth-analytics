# E-commerce growth analytics — synthetic portfolio case study

**Fictional DTC mattress retailer. Synthetic demonstration only; no findings about Puffy, real customers or measured commercial improvements. Dashboard acceptance completed November 18, 2026.**

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

## How I worked and why these choices matter

For a mattress retailer, a purchase can follow several visits and a large purchase price can make a small number of orders dominate daily results. Before suggesting changes to a page or an advertising budget, I wanted the basic counts and money to agree. The questions were: where does the ordered journey lose sessions, how do device/source cohorts differ, which campaign days receive attributed purchases, and which apparent problems need better measurement before action?

I used synthetic data so that the portfolio could be reproduced without customer records or connected commercial accounts. It includes repeat visits, abandoned journeys, mobile/desktop traffic, Google/Meta campaigns, direct/organic visits and partial refunds. Event occurrence and ingestion times are separate. Intentional tracking faults stay in separate fixtures, so demonstrations of duplicate or late-event handling do not contaminate the baseline dashboard.

Python coordinates generation, validation and exports; SQLite is the local SQL database. The equivalent GoogleSQL transformations were also executed in a BigQuery sandbox. I kept money in integer cents to avoid floating-point rounding in financial reconciliation. The same-session funnel requires each stage to follow its predecessor chronologically and counts an eligible session once at each stage. Ledger orders remain separate from tracked purchase events: a missing event should not erase a real order, and two orders in one session should not create two converting sessions.

The three dashboard datasets are independent: Overview has one row per day, Funnel one row per day/device/source/observed-visit cohort, and Acquisition one row per campaign-day. Joining advertising spend onto every event would repeat the same cost many times. I instead aggregate outcomes to the spend grain before combining them. Under filters, conversion and ROAS are recalculated from summed numerators and denominators rather than averaged percentages. This preserves the meaning of a metric when the selected population changes.

## What I would investigate next

These priorities demonstrate analytical reasoning, not decisions justified for a real retailer by simulated data.

1. **Product-page progression.** Only 43.53% of the 2,380 ordered product-view sessions progress to cart. The 1,344-session loss makes this a useful starting question, but comparison shopping, delayed purchases or missing events could explain a real-world loss. I would first audit events and inspect consented usability evidence. If unclear price, delivery or returns information is supported by real evidence, I would test clearer information near the purchase controls. Success would require improved completed purchasing, with revenue, refund and technical guardrails—not just extra cart clicks.
2. **Comparable mobile journeys.** Mobile has 216 purchases from 1,833 sessions (11.78%); desktop has 161 from 867 (18.57%). The generator deliberately varies device probabilities. I cannot infer a broken mobile experience. I would compare devices within similar source/visit cohorts, then inspect real tracking and technical diagnostics. A proposed fix should target an observed issue and be evaluated using controlled visitor-level purchase conversion and mature guardrails.
3. **Attribution before budget changes.** There are 195 campaign-days with spend and no attributed orders, yet the full paid-attributed net ROAS is 3.91. Sparse conversions and delayed or cross-device journeys can produce this pattern. I would compare defensible attribution windows and reconcile unmatched purchases before changing budgets. More stable attribution is a measurement improvement; proving advertising caused incremental purchases would require a separate lift or holdout design.

The [experiment protocol](EXPERIMENT_PROTOCOL.md) develops the first hypothesis. It proposes persistent 1:1 visitor assignment, a seven-day purchase outcome and a planning target of at least 3,842 eligible visitors per arm under explicitly illustrative assumptions. It specifies tracking checks, stopping rules and guardrails. No visitors were assigned, no treatment was launched and no outcome was measured. The real baseline, practical effect and sample-size requirements must be agreed before execution.

## Verification, challenges and my role

The project used AI assistance for drafting code, SQL, documentation and workbook XML. I provided the business scope, completed account sign-in myself and carried out Tableau interactions/screenshots where computer control was unavailable. Automated execution, independently hand-calculated fixtures and my supplied visual evidence were used to challenge outputs rather than treating generated answers as facts. I do not claim that I manually wrote every line or performed every automated check.

The independent SQL fixture includes four orders in three converting sessions, multiple items and partial refunds. It checks cases the baseline alone would not prove. Duplicate purchase events, missing transaction IDs and late-arriving records are preserved and audited; reprocessing is checked for double-counting. Spend and revenue reconcile with zero differences. The historical BigQuery run passed 96 comparisons against SQLite, including the quality cases.

Tableau XML generation initially produced an invalid data-source reference. The repair preserved all worksheets and corrected their source references; acceptance was withheld until the repaired views rendered. Computer-control timeouts were treated separately from workbook defects. User screenshots then verified combinations, empty results, resets and both directions of filter isolation. The final layout was adopted only after analytical equivalence checks and a source-only reproducible build; original drafts and the preceding release were preserved.

The relocated source TWBX was closed and reopened by me without reconnecting data or seeing warnings. The permanent release was subsequently sanitized and repackaged with the same extract bytes and equivalent workbook XML, plus matching CSVs for refresh. Automated checks verified all 1,637 rows and relative paths in that final package; the repackaged ZIP itself did not receive a separate agent GUI reopen. [Acceptance provenance](../release/ACCEPTANCE.md) records that distinction and the package hashes.

## What is complete and what remains optional

The synthetic portfolio scope is complete: measurement definitions, reproducible data, local SQL/Python analysis, historical BigQuery verification, local dashboards, quality evidence, a case study and a proposed experiment. Revenue and ROAS are not profit: cost of goods, fulfilment and other operating costs are not modeled. Attributed revenue is not causal lift, and the first-observed paid acquisition-cost proxy is not verified new-customer acquisition cost.

BigQuery verification occurred November 13, 2026; recorded sandbox expiration is November 19. Current cloud availability was not queried for release. Local data and the packaged workbook preserve the demonstration independently of those tables. Real-source connectors, landing-page instrumentation, longer attribution windows, real-data validation and execution of a properly designed experiment are optional future work, not hidden prerequisites or completed integrations. Screenshot previews are not bundled; the accepted workbook and evidence records are available.

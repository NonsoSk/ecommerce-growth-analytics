# E-commerce Growth Analytics

This project models a fictional direct-to-consumer mattress retailer. It contains no real customer data, findings about Puffy, measured revenue improvements or executed experiments.

An online retailer needs to understand where journeys stop, whether purchases and revenue agree across records, and how acquisition performance varies before deciding what to investigate. I built a reproducible Python/SQL workflow and three local Tableau dashboards to answer those questions with fictional data. The documented synthetic portfolio scope is complete; real-source ingestion and production operation remain future work.

## Start here

| Reviewer resource | What to look for |
|---|---|
| [Case study](docs/PORTFOLIO_CASE_STUDY.md) | Business question, approach, verified observations, recommendations and limitations |
| [Final Tableau workbook](release/SYNTHETIC_Growth_REVIEW.twbx) | Download the TWBX and open locally in Tableau; embedded data require no BigQuery connection |
| [Reproduction instructions](dashboard/README.md) | Python prerequisites, optional pinned Hyper tooling and a separate reproducible dashboard build |
| [Measurement plan](docs/MEASUREMENT_PLAN.md) and [data dictionary](docs/DATA_DICTIONARY.md) | Definitions, reporting grains, identifiers and timestamps |
| [Evidence index](release/EVIDENCE_INDEX.md) and [acceptance record](release/ACCEPTANCE.md) | Automated checks, user Tableau evidence and exact package provenance |
| [Proposed experiment](docs/EXPERIMENT_PROTOCOL.md) | Concrete design, explicitly unexecuted |

## Verified synthetic results

January 1–March 31, 2026 UTC; USD; refunds observed through April 16 exclusive.

| Measure | Calculated value |
|---|---:|
| Sessions / distinct converting sessions | 2,700 / 377 |
| Purchase conversion (converting sessions ÷ sessions) | 13.96% |
| Orders / purchasing visitor identities | 377 / 331 |
| Net merchandise revenue / merchandise refunds | $330,922.95 / $14,084.25 |
| Advertising spend / paid-attributed net revenue | $44,259.88 / $173,184.63 |
| Net attributed ROAS / first-observed paid CAC proxy | 3.91 / $245.89 |

The largest ordered-funnel loss is product view to cart: 2,380 views become 1,036 carts, a loss of 1,344 sessions. Mobile conversion is 11.78%, versus 18.57% on desktop. These are simulated patterns, not proof of customer friction or advertising effectiveness. See the [case study](docs/PORTFOLIO_CASE_STUDY.md) and [prioritized investigations](dashboard/DECISION_REPORT.md) for alternatives and evidence needed before acting. Revenue and return on ad spend (ROAS) are not profit; the acquisition-cost proxy does not establish genuinely new customers.

## Workflow and validation

1. Define the metrics and generate deterministic linked synthetic data with Python (seed 42).
2. Load explicit SQLite schemas, preserve raw records, reconcile purchases/refunds and run chronological funnel and campaign-day SQL.
3. Verify equivalent GoogleSQL in BigQuery: **96/96 comparisons passed on November 13, 2026**. Current cloud availability has not been checked; recorded demo-table expiration is November 19, 2026 UTC.
4. Export three independent dashboard datasets, keeping spend from multiplying across event rows, and build Overview, Funnel and Acquisition in Tableau Public locally.
5. Validate formulas and data automatically, then review actual Tableau filtering, reset, empty-case, isolation and relocated reopen evidence.

Recorded evidence includes 51 earlier regression tests, eight SQL/Hyper cases, 50 expression checks, 1,637 matched dashboard rows, three additional adoption-contract tests and a targeted report test. These were separate recorded runs, not a claim that the expanded suite was rerun as one batch. [PROGRESS.md](PROGRESS.md) records the sequence.

The final repackaged release was checked automatically. Tableau close/reopen evidence comes from the equivalent user-reopened source workbook: the exact extracts and layout were preserved, relative paths normalized, workstation fingerprints removed and matching CSVs restored. The final ZIP did **not** receive a separate agent GUI reopen. See [acceptance provenance](release/ACCEPTANCE.md).

## Dashboard previews

Genuine screenshots of the accepted source layout; no numbers or charts were retouched. [Provenance and full-size images](dashboard/screenshots/README.md).

![Synthetic Acquisition dashboard showing full-period paid spend of $44,259.88, attributed net revenue of $173,184.63 and four campaign comparisons](dashboard/screenshots/acquisition-full-period.png)

*Acquisition, January–March: attributed performance is descriptive, not causal or a measure of profit.*

<details>
<summary>Overview and Funnel previews</summary>

![January synthetic Overview with 930 sessions, 125 converting sessions, 13.44% conversion and $106,736.47 net merchandise revenue](dashboard/screenshots/overview-january.png)

*Overview uses January 1–31, so its totals differ from the full-period results above. The visible tooltip is part of the original capture.*

![Full-period synthetic Funnel with stages 2700, 2380, 1036, 677 and 377, plus device and source comparisons](dashboard/screenshots/funnel-full-period.png)

*Funnel, January–March: ordered same-session stages and comparison rates. The authoring interface and selected-mark tooltip remain visible.*

</details>

## Tools and repository map

| Tool / location | Role |
|---|---|
| Python · `src/`, `scripts/`, `tests/` | Deterministic generation, orchestration, reconciliation and independent fixtures |
| SQLite · `sql/` | Local relational analysis with explicit constraints and repeatable outputs |
| BigQuery · `bigquery/` | Equivalent GoogleSQL; historical 96/96 live parity, not current-availability assurance |
| Tableau Public · `dashboard/`, `release/` | Three local dashboards and the self-contained accepted workbook; never publicly published |
| Git / GitHub | Versioned code, documentation, synthetic exports and release evidence in this private repository |

I recommend investigating product-page clarity first, then comparing mobile journeys within similar cohorts, and reviewing attribution before changing budgets. These are proposed learning priorities, not proven interventions; the [case study](docs/PORTFOLIO_CASE_STUDY.md#what-i-would-investigate-next) sets out the evidence and success measures.

## Reproduce locally

Verified core environment: Python 3.14.8, SQLite 3.50.4, macOS ARM64. Core analysis uses the Python standard library; optional Tableau extract generation needs the separately pinned Hyper dependencies.

```sh
python3.14 -m venv .venv
.venv/bin/python scripts/run_analysis.py
```

Run from the repository root. The command runs tests, generates the default baseline if absent, validates it, builds SQLite analyses, exercises separate quality fixtures and exports CSVs/report under ignored `data/generated/analysis/`. Existing baseline data are verified rather than silently overwritten. See the [SQL pipeline guide](docs/SQL_PIPELINE.md) for cutoffs and expected behaviour.

To generate only the sample or run only tests:

```sh
.venv/bin/python scripts/generate_sample.py
.venv/bin/python -m unittest discover -s tests -v
```

For the accepted-layout rebuild, follow the [dashboard guide](dashboard/README.md). It outputs `dashboard/workbooks/SYNTHETIC_Growth_REBUILD.twbx` without overwriting the release. No ignored draft/template or cloud access is required. Hyper file bytes can vary across fresh builds; logical rows and canonical workbook structure are the reproducibility criteria.

## Scope and limitations

- Implemented: synthetic generator, data-quality fixtures, Python/SQLite pipeline, GoogleSQL migration workflow, historical live BigQuery parity, three accepted local Tableau dashboards and an unexecuted experiment protocol.
- Not implemented: GA4, Shopify, Google Ads, Meta Ads or Hotjar ingestion; placeholder settings are not connectors. No A/B test was run.
- Simulation assumes reliable visitor linking, simplified prices/refunds and same-session attribution. First observed purchases are not proven first-ever purchases. Direct traffic can include missing attribution or prior paid exposure; organic is not cost-free. Landing-page data are absent.
- Attribution describes assigned revenue; it does not establish incremental impact. Optional next work needs independently validated, authorized real data. See the [backlog](docs/FOLLOW_UP_BACKLOG.md).

## Repository and data safety

The final TWBX, a preceding-release backup, small synthetic illustrations and baseline dashboard CSVs are tracked. Full generated JSON/SQLite outputs, environments, credentials, original drafts and exploratory/failed workbook backups remain ignored. See [release evidence](release/EVIDENCE_INDEX.md) for hashes and contents.

Origin is `https://github.com/NonsoSk/ecommerce-growth-analytics.git`; repository privacy was reconfirmed November 19, 2026 before upload. Never force-push or commit private records or credentials. This private GitHub upload does not publish Tableau or activate any service.

[Project brief](PROJECT_BRIEF.md) · [Progress](PROGRESS.md) · [Integration status](docs/INTEGRATIONS.md) · [Simulation assumptions](docs/SIMULATION_ASSUMPTIONS.md)

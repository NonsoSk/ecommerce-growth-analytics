# Progress

## 2026-11-12 — initial local setup

**Setup-stage status (historical): local foundation verified and uploaded to private GitHub; authentication blocker resolved. See latest milestone below for current status.**

### Completed

- Inspected an empty working folder; no existing project files were overwritten.
- Found Git 2.54.0, Python 3.14.8 and Apple's Python 3.9.6.
- Initialized local Git on `main` and configured the requested origin after confirming there was no existing repository or remote.
- Set the user-provided Git author identity in this repository only; global configuration was not changed.
- Created `.venv` with Python 3.14.8. No Python version change or third-party analysis packages were needed for this milestone.
- Added source, SQL, notebook, test, documentation, report and sample-data folders with scope notes.
- Added the project brief, contributor instructions, integration plan, validation requirements, ignore rules and placeholder environment template.

### Verification results

`.venv/bin/python scripts/verify_environment.py` returned **PASS**:

- Python version: **3.14.8**.
- Running inside a virtual environment: **true**.
- Environment belongs to this project: **true**.
- Required folders present: **true**.
- Standard-library SQL smoke check: **passed**.

`.venv/bin/python -m pip check` reported **No broken requirements found**. Pip disabled its unwritable shared cache; this did not affect verification.

Ignore-rule checks confirmed exclusion of local environment files, virtual environments, private datasets, generated reports, credential folders and key files. The placeholder `.env.example` and sample README remain eligible for Git. Reviewed all 18 staged files: only setup documentation, code, ignore rules and placeholder configuration were present. A targeted secret-pattern scan found zero matches; both private and sample data folders contained zero datasets. `git diff --cached --check` passed. These checks supplement manual review and are not a guarantee against every possible secret format.

### Initial blockers and limitations (historical)

- GitHub remote inspection first encountered restricted network access; a permitted retry reached GitHub but requested authentication (`could not read Username`). Remote contents and history are unknown, and no reconciliation can be claimed.
- No accounts connected, paid services activated, data analyzed, findings produced or business results measured.
- No push has been performed. The local setup commit, once recorded, is not evidence of synchronization with GitHub; inspect the Git log for its identifier.

### Original next step (superseded below)

Resolve read access to the requested GitHub repository, fetch and inspect its history, and safely reconcile any existing files before a future authorized push. Then begin the measurement dictionary and synthetic data specification. External integrations and analysis remain future milestones.

## 2026-11-12 — GitHub authentication resolved and initial upload verified

- Verified authenticated GitHub account: `NonsoSk`. No authentication tokens were printed or stored in project files.
- Confirmed origin: `https://github.com/NonsoSk/ecommerce-growth-analytics.git` and repository visibility: **private**. Visibility was not changed.
- Inspected remote refs and fetched origin successfully. The remote had no branches or commits; no merge, overwrite or force-push was necessary.
- Reviewed all 18 tracked files and the sole initial commit before upload. No credentials, private datasets or environment files were found; the targeted secret-pattern scan found zero matches. No ignored files were tracked. `.env.example` contains placeholders only.
- Pushed the initial project, preserving the existing README, to `main` and configured upstream `origin/main`.
- Verified initial local and remote commit hashes matched: `e8ad1a4ba6225d3829ebfc1fd54eb8b253380172`.
- After that successful upload, updated README status and Git safety guidance, this progress log, and stale access notes in the brief and integration plan. The documentation commit follows the initial setup commit; its final synchronization is checked after pushing rather than embedding its own hash here.

### Current blockers and next step

No remaining blocker for initial setup or GitHub access. The project remains in development: no datasets, findings, measured business results or completed analytics integrations. No paid services were activated.

Next planned milestone: define the measurement dictionary and synthetic data specification. That work has not started in this upload task.

## 2026-11-12 — Milestone 1: measurement definitions and synthetic data

**Current status: in development. Measurement and synthetic-data milestone implemented and verified.** This is the user-facing Milestone 1, corresponding to the measurement/synthetic-data item after local foundation in the original brief. Earlier “not started” notes above describe the historical setup stage.

### What now works

- Documented purchase and funnel conversion, AOV, net merchandise revenue, revenue per session, paid-media CAC proxy and net ROAS, including grains, windows, exclusions and attribution limits.
- Added a field-level dictionary for seven requested tables plus a supporting campaign dimension. Event occurrence and ingestion timestamps are separate; money uses integer USD cents.
- Implemented deterministic standard-library generation with a fixed default seed and configurable size/start. Campaign and transaction identifiers link consistently; spend remains campaign-day grain.
- Added a strict baseline validator and nonmutating quality detector. Three separate hand-authored fixtures cover duplicate purchases, missing transaction IDs and late events.
- Added 14 automated tests, including independent money calculations and deliberate corruption cases. **All 14 passed** on Python 3.14.8. Identical inputs produced byte-identical files and matching manifest hashes. No dependencies were added.
- Default generated counts: customers **1,496**, sessions **2,700**, events **7,170**, orders **377**, order items **377**, refunds **79**, campaigns **4**, daily campaign spend **360**. These are synthetic counts only.
- Documented assumptions, expected fixture handling and actual control totals in `docs/MILESTONE_1_VALIDATION.md`. Kept bulk output ignored and included only one 12-row linked illustration plus four independent fixture events.
- Pre-commit review checked all 28 tracked/staged files: no credentials or private data found, no tracked ignored files, and no secret-pattern matches. Confirmed `.env`, `.venv`, private data and generated bulk files stay ignored. Git whitespace checks passed. The milestone commit is intended for the existing private `main` branch; final local/remote equality is verified after pushing.

### Reproduction

Generate baseline: `.venv/bin/python scripts/generate_sample.py`

Run tests: `.venv/bin/python -m unittest discover -s tests -v`

Optional generator settings: `--seed`, `--sessions`, `--start`. Default: seed 42, 2,700 sessions across 2026-01-01 through 2026-03-31. Refund observations extend beyond that session window. See `docs/SIMULATION_ASSUMPTIONS.md`.

### Limitations and remaining work

Synthetic probabilities demonstrate methods, not evidence about Puffy or real customers. No experiments, revenue improvements or real business findings are claimed. Perfect visitor linkage, simplified sequential journeys, same-session attribution and a limited order/refund lifecycle are intentional assumptions. First observed purchasers are not necessarily lifetime-new customers in a real dataset.

No BigQuery, Shopify, GA4, Google Ads, Meta Ads, Tableau or Hotjar connection was created. No paid services were activated. Production ingestion, quarantine/backfills, real-data reconciliation, dashboards and business analysis remain planned. Stop here for this milestone; no implementation blocker remains.

## 2026-11-12 — Milestone 2: reproducible local SQL analysis

**Current status: in development. Local SQLite analysis of synthetic data implemented and verified.** Earlier milestone status statements are historical. No external analytics connections, dashboards or experiments were created.

### Foundation review and implementation

- Read the project instructions, brief, progress, measurement plan, dictionary and generator/tests before changes. Preserved the generator and all simulated values.
- Clarified visitor identities versus purchasing visitors, orders versus converting sessions, and first observed versus first-ever purchases. Ledger conversion/revenue no longer ambiguously depends on event delivery; event-based ordered funnel purchases are reported separately.
- Documented same-session attribution, missing landing-page/source-medium fields, order-cohort refunds, incomplete observation and the absence of financial ingestion timestamps in `docs/MEASUREMENT_REVIEW.md`.
- Added explicit SQLite schemas, enforced financial relationships/amount checks, raw-event auditing, separate readable SQL analyses, campaign-day key unions, null ratio reasons and ignored CSV exports. Items/refunds are aggregated before joining; spend is never repeated across events.
- Added an independent hand-calculated fixture with multiple items, orders and partial refunds, repeat purchases, skipped/out-of-order journeys, zero-conversion spend days and missing spend. Exercised the original quality fixtures unchanged through isolated SQLite contexts.

### Actual verification results

- **29 tests passed**: 14 original generator tests and 15 SQL analysis tests, on Python 3.14.8 / SQLite 3.50.4. No dependencies were added.
- Full default pipeline repeated successfully with identical CSV/report/metadata hashes; raw baseline files stayed byte-identical and database row counts did not grow. Input hash mismatches fail before replacing validated outputs.
- Repeated the full pipeline twice again after the user's upgrade: all 29 tests passed each time. An explicit 12-part duplicate audit found zero duplicate visitor/session/event/order/transaction/item/refund keys, campaign-day keys, purchase transactions or derived order/session/campaign-day rows. Intentional duplicate test deliveries remain isolated in fixtures and are quarantined by the audit.
- All seven reconciliation differences are **zero**: session count, order count, merchandise revenue, refunds, net revenue, spend and paid-plus-unpaid net revenue.
- Baseline purchase reconciliation: **377 matched orders**, no excluded purchase deliveries; all **7,170** raw events accepted, zero late events and zero skipped/out-of-order sessions. This reflects a deliberately clean simulation, not real tracking completeness.
- Separate original quality fixtures: one accepted canonical purchase, one duplicate quarantined, one missing transaction ID quarantined and one late view included on restatement. Hand-calculated late processing changes funnel purchases from 1 to 2 once, with four ledger orders unchanged.
- Default cohort: 2026-01-01 inclusive to 2026-04-01 exclusive; observation cutoff 2026-04-16 exclusive, UTC/USD, seed 42, 2,700 sessions. All modeled refund windows are mature at this cutoff.
- Data SHA-256: `e486a1983c44d36bc6b57eddda6849feff49092ae3acea3b39d319e366f2e5da`. Input table and SQL fingerprints are recorded in generated run metadata.
- Pre-commit review covered all 48 tracked/staged files: zero secret-pattern matches, no private data files and no tracked ignored/environment/generated files. Only three small, explicitly synthetic JSON examples/fixtures are tracked. Confirmed the original generator and its tests are unchanged; Git whitespace checks passed.

### Computed simulation summary

1,496 observed visitors; 331 purchasing visitors; 377 orders across 377 converting sessions. Order conversion **13.96%**; pre-refund merchandise AOV **$915.14**; merchandise revenue **$345,007.20**; merchandise refunds **$14,084.25**; net merchandise revenue **$330,922.95**; revenue/session **$122.56**. Paid spend **$44,259.88**; same-session paid-attributed net revenue **$173,184.63**; 180 first-observed paid-attributed purchasers; net paid ROAS **3.91x**; paid-media CAC proxy **$245.89**.

These are synthetic outputs, not evidence about Puffy, real customers, causal lift or commercial improvements. The reviewed `reports/MILESTONE_2_ANALYSIS.md` contains calculated tables, limitations and three investigation ideas, each with evidence and alternative explanations.

### Reproduce and remaining scope

Run `.venv/bin/python scripts/run_analysis.py` for tests and the complete pipeline. Outputs stay ignored under `data/generated/analysis/`; the reviewed Markdown report is explicitly allowed in Git. See `docs/SQL_PIPELINE.md` for output grains, fixture arithmetic, null semantics and planned BigQuery migration.

Limitations: no landing pages, true lifetime customer history, complete financial ingestion history, cross-session attribution, real source data or production warehouse. BigQuery, Shopify, GA4, advertising platforms, Hotjar and Tableau remain disconnected. No paid service or A/B experiment was activated. Stop after this milestone; no implementation blocker remains. Commit/push and final local/remote verification follow the staged privacy review.

## 2026-11-12 — review corrections and Milestone 3 preparation

**Current status: in development. Review corrections completed; BigQuery migration prepared locally. Live BigQuery validation, execution and parity remain unverified.**

### Review corrections

- Corrected both the report renderer and reviewed report: direct is not assigned to a paid campaign under the current model and may include missing attribution or prior paid exposure. Organic does not imply zero acquisition cost.
- Renamed the displayed column to **Days with spend and zero attributed orders**.
- Confirmed conversion uses distinct buying sessions with order counts separate. Added an explicit assertion that two orders in one session yield one converting session and 100%, not 200%, daily conversion.
- Added a report-regeneration regression check and `docs/FOLLOW_UP_BACKLOG.md` for attribution sensitivity, comparable device/source/visit cohorts, landing-page tracking and independent real-data analysis. Simulation validation remains separate from business evidence.

### Migration preparation

- Checked current official Google Cloud documentation before implementing GoogleSQL/CLI-specific behavior; dated sources and operational caveats are linked in `docs/BIGQUERY_MIGRATION.md`.
- Added eight explicit raw schemas, native timestamp/date/integer-money CTE models, separate GoogleSQL report queries, summary/raw controls, a placeholder configuration and a standard-library workflow using the future `bq` CLI.
- Offline preparation creates deterministic ignored NDJSON, SQL, schema and SQLite-expectation artifacts for five isolated table groups, 40 exact demonstration table names and eight scenarios. There are 12 output/control queries per scenario, yielding 96 prepared comparisons.
- Future cloud stages require actual configuration and dataset ownership/location checks. Replacements are restricted to exact owned table names; no broad deletion, dataset creation, IAM or billing activation is implemented. Existing unlabelled/view/customer-managed-key targets are refused.
- Every query has a configurable maximum-bytes-billed value; execution is preceded by server dry-run support. New tables have explicit expiration. Per-query controls do not cover all storage, retained data, capacity, transfer or aggregate-run costs; these limits are documented.

### Checks actually run

- **42 local tests passed**: 14 generator, 15 SQLite, 12 offline migration/guard tests and one report-regeneration test. The migration tests use mocks for cloud calls; they do not validate Google's SQL engine or establish actual cloud parity.
- Repeated offline preparation produced identical artifacts, 40 unique destination names, no duplicate append behavior and unchanged raw baseline hashes. No Google Cloud requests were made by preparation.
- Local SQLite financial/count reconciliations remain at zero difference. Seed 42 and data fingerprint remain `e486a1983c44d36bc6b57eddda6849feff49092ae3acea3b39d319e366f2e5da`; no simulated values were changed.
- `gcloud` and `bq` were not found on PATH or checked installation paths. Google Python modules are absent; credential environment setting is unset and the default ADC file is absent. No credential contents or tokens were read or printed. This does not prove that no account/project exists elsewhere.
- Offline verification status is explicitly **not_verified_in_bigquery**. No server dry-run, cloud load, query execution or live BigQuery/SQLite result comparison has succeeded or been claimed. No billing, paid resources or Tableau dashboards were activated.
- Staged review covered 78 tracked/staged files: zero secret-pattern matches; no private data, credentials, local configuration, environments, generated bulk files or databases staged. New JSON files are explicit schemas or placeholder configuration. The original generator and data fixtures are unchanged; whitespace checks passed.

### Next input required

Supply the intended Google account/principal, actual Google Cloud project ID, approved dedicated dataset (proposed `ecommerce_growth_demo`) and exact dataset location. Install/authenticate the Google Cloud CLI locally. The execution principal needs BigQuery Job User on the job project and BigQuery Data Editor only on the dedicated dataset; an administrator must prepare/approve the dataset and ownership label. Confirm API/billing or sandbox constraints and the query-byte ceiling before separately authorizing a live run. Detailed commands, labels and permissions are in `docs/BIGQUERY_MIGRATION.md`.

Local reproduction: `.venv/bin/python scripts/run_analysis.py` then `.venv/bin/python scripts/bigquery_migrate.py prepare`. This milestone stops at preparation while cloud access is unavailable.

## 2026-11-13 — Milestone 3: live BigQuery sandbox migration verified

**Current status: in development. Synthetic cloud execution and all 96 parity comparisons passed. Earlier preparation-only statuses above are historical.**

### Access and scope

- Installed and verified the official Apple-silicon CLI outside the repository: gcloud 593.0.0 / bq 2.1.42. Project Python remains 3.14.8 with no new dependencies. User completed browser authentication; no tokens or credentials were printed or committed.
- Verified project `premium-silicon-514522-e8`, BigQuery API availability, and disabled billing/no linked account before loading and after execution. No trial, billing activation or IAM change was made.
- Created only the authorized `ecommerce_growth_demo` dataset in `US`, with `portfolio_project=ecommerce_growth_analytics` and seven-day default table expiration. Verified ownership on all 40 demonstration tables; no unrelated dataset was modified.

### Loads, validation and discrepancies

- Preflight upload: 2,312,867 NDJSON bytes, including 2,287,858 baseline bytes and 25,009 bytes of separate hand/quality fixtures. Forty explicit-schema batch loads completed once; baseline and fixture prefixes remain separate. BigQuery reports 735,612 logical bytes.
- Baseline: 12,563 rows; fixtures: 132 rows; total: 12,695. Eight baseline row counts match the manifest, with zero duplicate primary keys or duplicate order transaction IDs. Intentional duplicate purchase deliveries remain isolated in the fixture.
- Sanitized job metadata confirms exactly 40 load jobs and 180 successful query jobs across the interrupted attempt, isolated diagnostic and full rerun, with zero server-reported errors and 7,622,344 query bytes processed. No repeat load was submitted.
- All 96 distinct comparisons passed in a complete two-worker run, each preceded by a successful dry run with a 1,000,000,000-byte per-query ceiling. Counts and integer money agree exactly; nulls, result keys and floating ratios meet the measurement/parity contract.
- Seven source-to-output monetary/count reconciliation differences are zero. Baseline: 2,700 sessions, 377 converting sessions, 377 orders, $345,007.20 merchandise before refunds, $14,084.25 merchandise refunds, $330,922.95 net merchandise revenue and $44,259.88 media spend. Ordered funnel: 2,700 → 2,380 → 1,036 → 677 → 377.
- Hand-calculated cases, multiple orders/items/refunds, zero-conversion spend days, missing attribution, invalid funnel ordering, duplicate deliveries, missing IDs and late-event reprocessing all matched SQLite. The hand fixture correctly counts four orders across three converting sessions.
- The first four-worker attempt stopped after 81 passes due to a CLI error on `late_arrival/quality`. Available server job metadata showed no job failures; the isolated query and entire lower-concurrency rerun passed. Precise cause is unresolved. The interrupted status is retained locally; no expected values, SQL definitions or simulated data were changed to force agreement.
- Local suite: **45 tests passed**. Added receipt/remote-version guards to skip unchanged uploads and refuse automatic replacement of unverifiable nonempty tables; added bounded read-only concurrency and partial failure progress. No append loading or duplicate table copies were used.
- Seed 42 and original baseline fingerprint remain unchanged: `e486a1983c44d36bc6b57eddda6849feff49092ae3acea3b39d319e366f2e5da`. Detailed plan/result digests, row counts, quality audit and campaign tables are in `docs/BIGQUERY_VALIDATION.md`. Generated data, result files, metadata, load receipts and filled configuration remain ignored.

### Retention and limitations

Observed table expiration is 2026-11-19, between 22:43:31 and 22:49:50 UTC. Local sources and committed evidence outlive these temporary tables. The current sandbox's lifetime storage allowance is not restored by deletion; unchanged verified uploads are skipped. Query retries still consume compute allowance. Empty-file loads, remaining historical quota and production-scale behavior were not established. The bundled bq dependency warning did not prevent successful execution.

This validates a synthetic analytical method, not real business performance or causal impact. GA4, Shopify, Google Ads, Meta Ads, Hotjar and Tableau remain disconnected/not implemented. Next proposed milestone: a separately authorized dashboard built from validated outputs, with the measurement definitions and simulation caveats visible; independent real-data analysis remains a separate evidence requirement.

Reproduce (authenticated CLI on PATH, ignored local config present, demo tables not expired):

```sh
.venv/bin/python scripts/bigquery_migrate.py execute --config bigquery/config.local.json --acknowledge-cloud-actions --workers 2
.venv/bin/python -m unittest discover -s tests -v
```

For first loads or expired tables, follow the guarded load workflow and sandbox preflight in `docs/BIGQUERY_MIGRATION.md`; do not enable billing or extend retention automatically. Repository privacy and remote history were checked before this update; the branch had no remote divergence. Reviewed 11 changed files and scanned all 79 tracked files: zero targeted secret-pattern matches, zero tracked ignored/private/generated files, and no credential or local configuration files staged. Whitespace checks passed. The authorized commit/push is followed by a local-versus-remote hash check; the final hash is reported after upload rather than embedded in its own commit.

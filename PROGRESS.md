# Progress

## Current acceptance status — November 18, 2026

The synthetic portfolio dashboard is accepted. This summary supersedes historical pending notes below. Permanent workbook: `release/SYNTHETIC_Growth_REVIEW.twbx`; provenance and current hash: `release/ACCEPTANCE.md`. No further user acceptance action is required for the documented scope.

| Component | Completed work | Validation evidence | Known issue | Next action |
|---|---|---|---|---|
| Overview | Full/January totals and isolated date scope | SQL expectations and screenshots including final 5e5ba463 | Small authoring viewport may need scrolling | None required |
| Funnel | Ordered stages, cohorts, comparisons, reset/empty/isolation | User sequence plus screenshots; Google 12.98%, Meta 14.33% printed | Representative cases, not every combination | None required |
| Acquisition | Campaign-day metrics, reset/conflict/isolation | Final bc208b8b preserves January Google prospecting totals | CAC is first-observed proxy; attribution is not causal | None required |
| Portable release | Adopted reopened layout; exact extracts; restored CSVs; prior release backup | User close/reopen; canonical XML equivalence; 1,637 relocated rows | Repacked ZIP not separately GUI-opened; equivalence evidence documented | None required |
| Reproducible build | Committed accepted template; guarded analytical contract | Source-only build stages; 8 SQL/Hyper cases; 50 expressions; 3 new targeted tests | Hyper binary bytes may vary | Use documented rebuild command when needed |
| Analysis/documentation | Synthetic case study, protocol, dated cloud evidence | Existing independent tests; 1 report-review test | No real-source ingestion or executed experiment; current cloud state unqueried | Optional future work only |


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

## 2026-11-14 — Tableau dashboard copy generated; visual acceptance pending

The user screenshot confirms the repaired revenue probe displays $330,922.95. Built a separate `dashboard/workbooks/SYNTHETIC_Growth_DASHBOARDS.twb` with 29 calculated/comparison sheets, three dashboard layouts, synthetic labels, observation/attribution notes and scoped parameter controls. The original draft and backup remain byte-identical (SHA-256 `9bf07d7c6ad13cbc6ca8bcdf0461b63c0d51bc0beab8d5ee4e0810e8d7b37397`). No original data or historical work was replaced.

Diagnosed and fixed generated-format issues: invalid formatting attributes, missing worksheet window cards and missing dashboard view references. Tableau then required extracts (error 3C242D89), so installed official Hyper API 0.0.26479, cffi 2.1.1 and pycparser 3.12 into a separate ignored Python 3.14.8 tooling environment. Compatible ARM64 binary wheels were checked before installation; project `.venv` remains unchanged. Hyper runs locally with telemetry disabled. The sandbox initially blocked its required Unix socket; authorized local execution succeeded. No cloud upload, public publishing or paid activation occurred.

Actual validation: 51 local tests pass; baseline aggregate rows are 90 Overview / 1,187 Funnel / 360 Acquisition, all exactly equal to durable local Hyper extracts. Eight full/filtered SQL-to-Hyper comparisons have zero count/money differences. Fifty generated-workbook calculation/filter-predicate comparisons pass in Hyper SQL with explicit real-division semantics. These checks are not Tableau UI interaction tests. Extracts are content-addressed and never appended. Dataset observation/identity/attribution assumptions remain unchanged.

Tableau Public 2026.3 application `log_6.txt` records DOM loading `ok` at 00:42:46.654 and workbook loading `ok` at 00:42:47.082 on November 14. No query/calculation/extract syntax errors were found in that log at inspection. Full rendering and interactive filter acceptance are still unverified because computer controls remain attached to the original Tableau process. The workbook is **in development, not complete**. Next: inspect the three generated dashboard tabs and representative filters listed in `dashboard/README.md`. Work remains local and uncommitted under the current instruction; no push performed.

## Dashboard acceptance status — updated 2026-11-15

**Overall milestone PENDING final acceptance.** This table is the current status; dated entries below retain historical failures and superseded next actions. Use `dashboard/workbooks/SYNTHETIC_Growth_REVIEW.twbx`. The single remaining checklist is `dashboard/INTERACTION_CHECKS.md`.

| Component | Completed work | Validation evidence | Known issue | Next action |
|---|---|---|---|---|
| Preservation | Original draft, backups, CSVs and extracts preserved | Earlier hash checks; no workbook modifications in current review | None identified | Preserve originals |
| Overview | Seven KPIs, January/full period, corrected period note | Screenshots match SQL; agent rechecked all January KPIs on Nov 15 | None in reviewed states | Only reverse isolation and portable runtime check |
| Funnel | Baseline, January/full selected cohort, April empty and reset | User screenshots match stages, losses, printed conversion labels and quality count | Full-period Google 12.98% / Meta 14.33% now screenshot-verified | No further label evidence needed |
| Acquisition | Baseline, January campaign, conflicting empty case and reset | All six totals and all 16 campaign labels match SQL; empty screenshot shows 0 marks | None in reviewed states | Only reverse isolation and portable runtime check |
| Filter isolation | Acquisition selectors do not affect Overview/Funnel | Nov 15 agent navigated from conflicting Acquisition to correct January Overview/Funnel | Reverse-direction output screenshots match; confirmation Funnel selectors remained active is pending | Final checklist A |
| Automated checks | SQL reconciliation, formula predicates, package/data checks | Eight SQL checks, 50 expression checks, 51 tests, 1,637 relocated rows (previous runs) | Automated checks are not Tableau interactions | Retain separately; no unnecessary reruns |
| Layout | All 29 sheets render across screenshots; corrected notes viewed | No visible warning or unexpected blank chart | Scrolling needed in authoring viewport; two channel labels omitted | Inspect portable views and two tooltips |
| Computer control | Attachment/navigation work; Acquisition isolation completed | Actual UI observations Nov 15 | Dropdown click selects container without opening choices | User completes single consolidated remaining batch |
| Portable package | Seven-entry package; separate byte-identical copy prepared | SHA256 182481c1f06f29417e7231ea9fa5d9fe52b1289cb3dd8a7934dd8b79b1f93c3c; no workstation absolute paths; folder contains only TWBX | Relocated close/reopen confirmed by user with screenshots; reopened package differs from committed release | Resolve final artifact identity; see latest checklist |



The generated `.twb` was backed up before replacing six text-table comparison marks with bars. No dataset values or KPI formulas were changed. Portable package: `dashboard/workbooks/SYNTHETIC_Growth_PORTABLE.twbx`. Rebuild using `.venv/bin/python scripts/package_tableau_dashboard.py`; relocation validation uses the isolated Hyper environment and `scripts/validate_portable_tableau.py`. The package is a local deliverable candidate, not a completed dashboard milestone. Tableau’s official packaged-workbook guidance was reviewed: https://help.tableau.com/current/pro/desktop/en-us/save_savework_packagedworkbooks.htm .


### Invalid-data-source investigation and isolated repair candidate

Preserved original draft, backup, all three CSVs and all three Hyper extracts by SHA-256. Saved an additional content-addressed `FAILED_*.twb` backup of the generated workbook before repair. The failed generated TWB and portable TWBX remain unchanged. Preservation hashes are in ignored `dashboard/workbooks/repair_preservation.json`.

Inspection of the affected worksheet and all 29 peers found each source list begins with `Parameters`, whose datasource explicitly has `hasconnection=false`, followed by the actual analytical source. The working probe begins with its connected analytical datasource. All named analytical sources exist; worksheet dependency columns and column instances resolve; CSV and Hyper paths exist; named connection and relation references match; metadata object IDs match their logical object; extract relations map to `[Extract].[Extract]`. This rules out those structural/path defects but does not prove every aspect of Tableau's internal model is valid.

Leading causal hypothesis: the connectionless parameter source is being selected as the worksheet's primary source. The generator now puts the analytical source first and writes **only** `SYNTHETIC_Growth_REPAIRED.twb`. A canonical XML comparison proves the 29 source-list reorderings are the sole changes from the failed workbook. All 29 worksheets and three dashboards are retained; no warnings are suppressed and no affected sheet is deleted. Actual cause remains **not yet confirmed by a rendered A/B comparison**; source ordering is a narrowly isolated repair candidate, not a claimed successful fix.

`log_8.txt` records repaired DOM load `ok` at 12:06:18.742 and workbook load `ok` at 12:06:19.466 on Nov 14. These events prove opening only; the earlier failure also passed loading. Computer controls still attach to the original draft process, so repaired warnings, dashboard totals and filter behavior remain unobserved. The 29-sheet reference/path audit passed and preservation hashes match. Passing SQL/data/expression checks are separate evidence and **do not override failed Tableau validation**.

Next required visual evidence: in the repaired workbook, inspect Session starts (expected 2,700 unfiltered) and all three dashboards for warnings. Only after worksheet validity passes, test the SQL-derived combinations, resets and empty cases in `dashboard/INTERACTION_CHECKS.md`. Close/reopen and renewed portability acceptance also remain pending. All work remains local; no commit, push or publication.

Repair-candidate automated recheck: all 50 expression comparisons passed; 51 local tests passed again. This remains independent of the failed/unverified Tableau runtime acceptance.


### Latest validation attempt — 2026-11-14

User reports only `SYNTHETIC_Growth_REPAIRED` is open. Fresh native-control attachment timed out and reset the control runtime; one retry returned `Computer Use server error -10005: timeoutReached`. App inventory independently confirms Tableau is running, but no workbook UI state or screenshot was returned. No additional worksheet/filter interaction was executed. Available repaired-workbook logs yielded no new detailed worksheet error; their silence is not proof of successful rendering. Previous passing automated data/expression tests remain historical evidence, not new runtime results. Tableau validation remains failed pending confirmation of the repair. No workbook, CSV or extract was changed during this attempt. Next required input is a screenshot of the current repaired workbook, including any warning, to determine whether source validity is fixed before requesting further filter tests.


### Repaired Overview screenshot review — 2026-11-14

Reviewed attachment `codex-clipboard-b15a1ff4-7879-4813-b5ff-228580557989.png`. No datasource warning, error dialog or missing-data placeholder is visible. Six readable Overview KPIs match the full-period SQL values. Start 01/01/2026 and end 31/03/2026 controls are visible, but their operation is not tested. Currency has dollar signs/two decimals, conversion has two percentage decimals, and sessions has a thousands separator. Synthetic heading and reporting-period/cutoff note are present.

The open Show Me panel and horizontal viewport leave the rightmost Orders card unreadable and truncate part of the explanatory note. This is an observed visibility/layout limitation, not proof the sheet is absent or its value wrong. Long visible KPI titles wrap without apparent lost text. The Sessions mark is blue-highlighted; the screenshot alone does not establish whether this is selection state or saved styling. Funnel and Acquisition tabs exist, but their contents and all 29 worksheet validity remain unverified. A KPI-only Overview is expected; absence of charts on this view is not itself missing content.

The control-service timeout remains separate from workbook validation. No new tool interaction, filter test or close/reopen test passed merely because this screenshot was supplied. Next checks: unobscured Orders card, Funnel's previously failing Session starts, Acquisition totals/charts, actual filter combinations/reset/empty cases, and repaired portable package close/reopen. No workbook/data files were changed in this screenshot-review turn.


### Four-screenshot acceptance review and separate note correction

Reviewed attachments `b001c190` (January Overview), `78b15b5a` (full Overview), `964ceb4b` (Acquisition), and `77648404` (Funnel), using fresh SQLite queries. Full values and readable campaign/device/source labels are recorded in `dashboard/SCREENSHOT_REVIEW.md`. Every readable metric matches SQL. The screenshot evidence resolves the reported baseline Session starts failure; it does not prove all filters work.

Created `SYNTHETIC_Growth_REVIEW.twb` by changing only the three available-period notes in REPAIRED, verified by XML comparison. No analytical content was rebuilt or removed. Packaged REVIEW into `SYNTHETIC_Growth_REVIEW.twbx` with relative local-data paths and no workstation fingerprint attributes. Original and previous candidate workbooks remain unchanged. The new package is the exact remaining-acceptance filename.

PASS: baseline dashboard render states, January Overview state, all readable numerical labels, 50 automated expression checks on REVIEW, seven-entry archive integrity and relocated CSV/Hyper row equality. FIXED BUT VISUALLY PENDING: available-period wording. PENDING: Funnel/Acquisition combinations, reset actions, empty cases, filter isolation, omitted label tooltips and actual REVIEW package opening/closing/reopening. Control attachment timed out; no UI interactions are claimed. No publishing, external accounts, paid services, commit or push.

Final local checks for this review: 51 tests passed again; original/data preservation hashes match; Git whitespace checks passed. No further Tableau interaction was possible.

## 2026-11-14 — post-restart interaction evidence

- PASS: attached to the exact REVIEW TWBX; Overview visibly showed 2,700 sessions, 377 converting sessions, 13.96%, $330,922.95 net, $14,084.25 refunds and $44,259.88 spend, without a visible warning. Orders were outside the right viewport; do not count this as a new check of that mark. Corrected available-data/selected-period note is visible.
- PASS (visible marks only): changed Funnel end date to January 31; 930 starts, 819 views, 357 carts, 225 checkouts and losses 111/462/132/100 match a fresh run of the existing SQLite transformations. Rightmost purchase and lower quality mark were outside the viewport.
- PASS (visible marks only): selected April 1–30; visible Funnel metrics/comparisons became empty, and Acquisition inherited the dates with visible KPIs/charts empty. Fresh SQLite confirms zero qualifying rows in all three sources. No stale values or infinity shown.
- PASS (visible marks only): reset Acquisition dates to January 1–March 31; visible spend $44,259.88, attributed net $173,184.63, 203 orders and 3.91 ROAS returned. Date input initially retained March 30; explicit accessible value plus Return corrected it and results were visually checked.
- BLOCKED automation: dropdown clicks selected dashboard containers without opening choices; keyboard attempts did not change them. Presentation toggle changed its accessibility flag without changing the visible authoring layout. This is an interaction limitation, not evidence of a workbook calculation error. No further repetitive retries.
- PENDING: Funnel/Acquisition selector combinations, selector resets/isolation, contradictory campaign empty case, offscreen marks/tooltips, and opening/closing/reopening a relocated copy in Tableau. User-reported post-reboot opening plus observed data is fresh-session evidence, not the relocated acceptance check.
- No workbook/data/code was rebuilt or saved, and nothing was published. Current unsaved UI dates are January 1–March 31 with all selectors still All. Overall milestone remains PENDING. Next manual batch: January/mobile/google/returning_visit; fresh SQLite gives 87 → 79 → 24 → 15 → 9, losses 8/55/9/6 and 10.34%.

### Additional Funnel screenshot — full-period combination

PASS: user screenshot `codex-clipboard-f431d8b7-f361-437f-9813-ae0a3d241517.png` visibly selects January 1–March 31, mobile / google / returning_visit. Fresh execution of existing SQLite dashboard transformations confirms every displayed value: stages 242 → 216 → 71 → 47 → 23; losses 26 / 145 / 24 / 24; both comparison bars 9.50%; skipped/out-of-order 0. No visible warning or missing chart. This verifies that rendered combination state, not the requested January-only case or reset/isolation. Next action: change only the end date to January 31 and verify 87 → 79 → 24 → 15 → 9, losses 8 / 55 / 9 / 6, 10.34%, skipped 0. No workbook or data changes.

### January Funnel combination — screenshot verified

PASS: screenshot `codex-clipboard-ca1eea01-c483-429c-8391-344619e27733.png` shows January 1–31, mobile / google / returning_visit. All visible results match the previously executed SQLite expectations: stages 87 → 79 → 24 → 15 → 9; losses 8 / 55 / 9 / 6; both conversion charts 10.34%; skipped/out-of-order 0. No visible warning or missing chart. This is actual Tableau rendered-filter evidence, separate from automated expression checks. Next: verify this selected cohort becomes empty for April, then reset dates and all three selectors and verify full-period totals. Acquisition combinations, filter isolation and relocated close/reopen remain pending; milestone not complete.

### Funnel empty-result and reset — screenshot verified

PASS: `codex-clipboard-801e50f9-68f1-4bed-a2bf-28cd855f6d31.png` shows April 1–30 with mobile/google/returning_visit retained. All five stage marks, four loss marks, both comparison charts and the quality count are empty, consistent with zero qualifying SQL rows; no stale numbers or misleading 0% remain.

PASS: `codex-clipboard-26422e16-0611-4d57-90c7-fb0a0b1e9dde.png` shows January 1–March 31 and all three selectors reset to All. Stages 2,700 → 2,380 → 1,036 → 677 → 377, losses 320/1,344/359/300, skipped 0, device labels 18.57%/11.78% and printed channel labels 14.63%/14.24% match SQL. Both comparison charts return, with no visible warning. Google/Meta numeric labels remain unprinted, not separately verified by tooltip. Blue cart mark is selection highlighting. These screenshots verify actual rendered empty/reset states; automated expression checks remain separately documented.

Next short batch: Acquisition January 1–31, paid source google, campaign syn_google_prospecting; expect $3,722.01 spend, $15,363.94 attributed net, 18 orders, 4.13 ROAS, $248.13 first-observed paid CAC proxy and 16 days with spend and zero attributed orders. Acquisition interaction cases, cross-dashboard filter isolation and relocated Tableau close/reopen remain pending. No workbook/data modification or publication.

### Acquisition January combination — screenshot verified

PASS: `codex-clipboard-b3d7fbb5-2496-4c4f-9c0d-80fe416f90ed.png` visibly selects January 1–31, paid source google and campaign syn_google_prospecting. All six displayed metrics match existing SQL expectations: spend $3,722.01; paid-attributed net revenue $15,363.94; 18 attributed orders; net ROAS 4.13; first-observed paid CAC proxy $248.13; 16 days with spend and zero attributed orders. All four single-campaign charts render and their printed values match the KPIs. Correct available-period/selected-period note and attribution limitations are visible. No visible warning. This is rendered Tableau combination evidence, distinct from automated formula validation.

Next: keep January/google and select syn_meta_prospecting to verify contradictory-filter empty results, then reset dates to January 1–March 31 and both Acquisition selectors to All. Cross-dashboard filter isolation and relocated close/reopen remain pending. Workbook milestone remains incomplete; original workbook and data unchanged.

### 2026-11-15 — Acquisition full reset screenshot verified

PASS: `codex-clipboard-8e0afe03-f798-420c-8831-04f871d2c6bf.png` shows January 1–March 31 and both Acquisition selectors All. All six totals match SQL: $44,259.88 spend, $173,184.63 attributed net, 203 orders, 3.91 ROAS, $245.89 first-observed paid CAC proxy and 195 days with spend and zero attributed orders. All four campaigns return on each chart; all 16 numerical labels are now readable and match previously computed SQL expectations. In campaign order Google prospecting / Google retargeting / Meta prospecting / Meta retargeting: spend $11,356.56 / $11,670.38 / $10,091.24 / $11,141.70; net $42,447.72 / $50,380.26 / $33,420.01 / $46,936.64; ROAS 3.74 / 4.32 / 3.31 / 4.21; CAC proxy $270.39 / $216.12 / $288.32 / $227.38. No visible warning or missing chart. The header is above the scrolled viewport.

PENDING: no screenshot or explicit result supplied yet for January/google/syn_meta_prospecting contradictory-filter empty case. Do not infer it passed from the reset screenshot. Cross-dashboard filter isolation and relocated Tableau close/reopen remain pending. Next short manual batch requests just the contradictory case. Original files preserved; no publication or milestone completion claim.

### 2026-11-15 — conflicting empty case and isolation consolidation

PASS: screenshot `codex-clipboard-d2d2babb-6a87-4a65-9f24-def1730a18a5.png` shows January 1–31, google and syn_meta_prospecting. All visible KPI/chart marks are empty, status shows 0 marks, and no warning appears. This matches the zero-row contradictory predicate.

PASS: native control attached to REVIEW and confirmed those selectors. Without changing them or dates, agent navigated to Overview: 930 sessions, 125 converting sessions, 13.44%, 125 orders, $106,736.47 net, $4,498.03 refunds, $15,148.71 spend. Funnel selectors remained All: 930 → 819 → 357 → 225 → 125; losses 111/462/132/100. Acquisition selectors therefore did not restrict the observed Overview/Funnel metrics. Dropdown control still selected its container instead of exposing choices; no repeated retries. Left UI on January Funnel with All selectors; Acquisition retains google/meta conflict. No save/publish.

Prepared a byte-identical portable test copy at `/private/tmp/ecommerce-growth-portability-20261115/SYNTHETIC_Growth_REVIEW.twbx`; folder contains no adjacent CSVs/extracts. Seven archive entries and no workstation absolute paths reconfirmed. Actual relocated Tableau opening/closing/reopening remains pending. Consolidated only outstanding checks in `dashboard/INTERACTION_CHECKS.md`: reverse isolation, two missing channel label values, and relocated runtime. Existing combination/empty/reset tests need no repetition.

### 2026-11-18 — final batch output screenshots received

PASS (displayed results): Overview screenshot `codex-clipboard-2bfd2de2-c3b8-462d-83fe-0b382385fe36.png` shows January 1–31 with all seven expected values: 930 sessions, 125 converting sessions, 13.44%, 125 orders, $106,736.47 net, $4,498.03 refunds and $15,148.71 spend. Correct synthetic heading and available-period note are readable. Acquisition screenshot `codex-clipboard-133d6cc5-6c27-4cc4-89b7-e7c9acfa1108.png` shows January/google/syn_google_prospecting with $3,722.01 spend, $15,363.94 attributed net, 18 orders, 4.13 ROAS, $248.13 CAC proxy and 16 zero-order spend days. All four campaign charts and printed labels match. No visible warning or missing content in either view.

Reverse isolation remains pending only the user's confirmation that mobile/google/returning_visit stayed selected on Funnel while these two screenshots were captured; the screenshots cannot show another tab's selector state. No need to repeat these captures if that sequence was followed. Remaining final-batch evidence: full-period Google/Meta Funnel tooltip values and relocated package close/reopen confirmation with three post-reopen dashboard screenshots. No workbook/data changes, publication or completion claim.

## 2026-11-18 — essential local release cleanup

Implemented a sanitized committed Tableau template, removing build dependencies on ignored original/probe files. Build and finalization write separate BUILD/REBUILD candidates; repeated finalization accepts already-correct notes and is byte-identical. The Hyper interpreter fix uses absolute() rather than resolve() to retain virtual-environment identity; it was included in the successful build, not an untested post-build change.

Recorded validation: 51 tests passed; isolated staged-source export generated its own baseline/extracts, passed eight SQL/Hyper cases and 50 expression checks, built 29 worksheets/three dashboards and validated seven archive entries plus all 1,637 relocated rows. Finalization repeatability passed. Canonical rebuilt workbook XML equals REVIEW. All 63 executable/SQL/template/schema/dependency/fixture files match the successful source snapshot; hashes are in release/TESTED_SOURCE_MANIFEST.json. See release/BUILD_VALIDATION.md for exact source identity, resolved interpreter/socket failures and limitations. No successful build was restarted during final cleanup.

Created a concise synthetic portfolio case study, prioritized hypothesis narrative and concrete UNEXECUTED experiment protocol. Reconciled current README/brief/report generator/dashboard guide/integration status; historical BigQuery verification is distinct from current availability. No cloud access or reload occurred. Created permanent release/SYNTHETIC_Growth_REVIEW.twbx, byte-identical to the existing reviewed package (SHA256 182481c1f06f29417e7231ea9fa5d9fe52b1289cb3dd8a7934dd8b79b1f93c3c). Eleven preserved workbook/extract artifact hashes remain unchanged.

Tableau acceptance remains PENDING: (1) confirm Funnel mobile/google/returning_visit stayed selected for the supplied isolation screenshots, (2) full-period Google/Meta channel tooltip values, (3) relocated Tableau close/reopen sequence and three post-reopen views without reconnecting data. Existing passed combination/empty/reset checks need no repetition. The current release candidate is permanent; the earlier temporary copy is only a portability test location.

Local commit follows staged privacy/artifact review. No push or publication is authorized in this release task. The original working draft, failed candidates, environment, exploratory preview, lock/recovery files, private configuration and bulk generated data remain excluded.

Final local release review: 38 staged files before the CSV attribute rule; targeted credential-pattern scan found zero matches, no prohibited private/environment/recovery artifact paths were staged, and all 63 staged tested-source hashes matched the successful snapshot. Packaged XML/CSV members were also inspected; embedded Hyper data had already passed full row equality. CSV CRLF record endings are preserved byte-for-byte with a path-specific .gitattributes whitespace rule rather than altering validated data hashes. This targeted scan is a guardrail, not an exhaustive guarantee against every secret format. No code changes or rebuild were needed in this cleanup.

### 2026-11-18 — relocated runtime evidence received; exact release identity unresolved

User explicitly confirms closing/reopening the same relocated TWBX without reconnecting data or warnings. Reviewed screenshots: 90ac97da shows full-period Overview sessions 2,700, converting sessions 377, 13.96%, net $330,922.95, refunds $14,084.25, spend $44,259.88; Orders is outside this viewport (earlier screenshot passed). 783c07e8 shows all Funnel stages 2,700/2,380/1,036/677/377, losses 320/1,344/359/300, skipped 0, devices 18.57%/11.78% and channels direct 14.63%, Google 12.98%, Meta 14.33%, organic 14.24%. c14fd0a1 shows all six Acquisition totals and all 16 campaign labels matching existing SQL evidence. No visible warning or unexpected blank chart. Reopen/label evidence passes for the user's relocated version; no repeated tests needed.

Read-only package comparison found the relocated file now SHA256 7fd815642dfe6dfa524a91ccfcf747dcde7d1457c2365a461159cc1482bf5959, four members, altered layouts; committed release remains 182481c1f06f29417e7231ea9fa5d9fe52b1289cb3dd8a7934dd8b79b1f93c3c, seven members. All three Hyper extracts are byte-identical, top-level calculation formulas unchanged, 29 worksheet names/three dashboards retained, no absolute connection paths in either package. Tableau dependency formula occurrence counts changed, not top-level metric formulas. Neither workbook was modified.

Remaining: earlier reverse-isolation sequence confirmation and choice of final artifact (retain original release or adopt reopened layout-edited copy with preserved original/provenance). Acceptance documentation updated locally; conditional acceptance commit not made because not all requirements are satisfied. No push/publication, cloud operation, rebuild or metric change.

### 2026-11-18 — final isolation accepted and reopened layout adopted

User explicitly confirms January 1–31, Acquisition google/syn_google_prospecting, then Funnel mobile/google/returning_visit retained while capturing Overview and Acquisition. Screenshots 5e5ba463 and bc208b8b match SQL: Overview 930/125/13.44%/125, net $106,736.47, refunds $4,498.03, spend $15,148.71; Acquisition $3,722.01/$15,363.94/18/4.13/$248.13/16. This completes reverse isolation without repeating already-passed tests. Prior post-reopen evidence and explicit no-reconnect/no-warning confirmation satisfy runtime acceptance for the adopted layout.

Preserved preceding release under release/backups, retained exact accepted extracts and sanitized/packaged the user-edited layout with matching CSVs. The source-only adopted-layout build passed eight SQL/Hyper cases, 50 expression checks and all 1,637 relocated rows. All 29 analytical sheet contracts match. Canonical XML matches the accepted source after only path/fingerprint transformations. Three new contract regression tests and one report-review test pass; repeated finalization is byte-identical. See release/ACCEPTANCE.md for exact hashes/source version, resolved metadata-comparison stop and the distinction between user runtime evidence and automated package checks. No original draft or user-relocated source changed.

README, brief, report renderer/report, dashboard guide, case study, checklist and evidence index now agree: documented synthetic portfolio acceptance completed, no real commercial findings or executed experiments, cloud verification historical. Nothing pushed or published. Local commit follows review; only optional enhancements remain.

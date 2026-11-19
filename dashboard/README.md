# Exploring the analysis in Tableau

I organised the analysis into three views so I could move from the overall results to the journey and then to campaign performance. **Overview** shows sessions, converting sessions, orders and reconciled money. **Funnel** follows the ordered journey and compares devices, sources and observed visit cohorts. **Acquisition** compares campaign-day spend with assigned orders and revenue.

The workbook contains 29 worksheets and uses synthetic data only. The documented acceptance checks are complete; the [interaction checklist](INTERACTION_CHECKS.md) separates actual Tableau evidence from automated expression checks. Use [the final self-contained workbook](../release/SYNTHETIC_Growth_REVIEW.twbx): download the TWBX and open it locally in Tableau Public. The accepted source used Tableau 2026.3 on macOS. Default dates are January 1–March 31 and selectors are All; data should be available without reconnecting a source. Do not use Save to Tableau Public to open it locally.

The accepted user-edited layout is preserved. The preceding release is backed up under release/backups, and original drafts remain untouched. The final ZIP was validated automatically; the equivalent relocated source workbook supplied the actual close/reopen evidence. See [adoption provenance](../release/ACCEPTANCE.md).

## Data and calculations

Only seed-42 baseline data are included; intentional quality fixtures are excluded. Overview is day grain (90 rows); Funnel is day/device/channel/observed-visit grain (1,187 rows); Acquisition is campaign-day grain (360 rows). Sources are independent, without cross-source joins. Money remains integer USD cents until display. Ratios are sums of numerators divided by sums of denominators, null for zero denominators; spend-dependent measures also guard missing coverage.

Dates select January 1–March 31, 2026 UTC inclusively. Refund observation ends April 16 exclusive; refunds are assigned to the originating session cohort. Funnels require same-session chronological progression. CAC is a first-observed paid purchaser proxy, not lifetime-new customer CAC. Attribution is same-session, not causal. Direct can include missing attribution/prior paid exposure; organic is not cost-free. Full definitions are in ../docs/MEASUREMENT_PLAN.md.

## Clean-checkout build (no cloud or Tableau account)

Verified environment: Python 3.14.8, macOS ARM64. Install a compatible Python first if unavailable; do not silently substitute an unverified interpreter. Core analysis needs no third-party dependencies. Optional Hyper wheels and pins are in requirements-hyper.txt.

```sh
python3.14 -m venv .venv
.venv/bin/python -m venv .venv-hyper
.venv-hyper/bin/python -m pip install --only-binary=:all: -r dashboard/requirements-hyper.txt
.venv/bin/python scripts/build_dashboard_release.py --hyper-python .venv-hyper/bin/python
```

The command generates the baseline if absent, verifies its fingerprint, exports aggregates, creates/validates Hyper files, builds from the committed sanitized template, applies the accepted layout after checking formulas and filter scope, validates 50 expressions and packages/relocates the data. Output: `dashboard/workbooks/SYNTHETIC_Growth_REBUILD.twbx`. It never overwrites REVIEW or the release candidate. No ignored draft/probe is required. Repeated finalization is idempotent. Generated workbook connections may be absolute locally; packaged TWBX connections are relative. Hyper binary bytes can vary between fresh creations; compare logical rows and canonical workbook XML, not arbitrary Hyper file hashes across builds.

The template in templates/workbook.twb retains only workbook format settings, an Orders worksheet scaffold and card settings from the user-verified probe. Connections, source dependencies, other sheets and workstation fingerprints were removed. The generator replaces worksheet dependencies with explicit sources and preserves analytical-source-first ordering. Template provenance is documented here; no claim of full official XSD conformance is made.

## Evidence and limits

Previously recorded: 51 local tests; 1,637 CSV/Hyper rows identical; eight SQL checks; 50 expression comparisons. Historical build evidence is in [BUILD_VALIDATION.md](../release/BUILD_VALIDATION.md); the adopted-layout build is in [ACCEPTANCE.md](../release/ACCEPTANCE.md). [Evidence index](../release/EVIDENCE_INDEX.md) separates historical cloud results, automated checks and actual UI evidence. Rebuilding is not a claim of new Tableau visual acceptance. Keep the reviewed candidate until any rebuilt replacement is separately accepted.

No external source ingestion, public publication, paid service, real finding or experiment result is included.

The finalizer now uses `templates/accepted_workbook.twb`, sanitized from the user-reopened layout. It checks calculation formulas, worksheet source references, filters, shelf definitions and mark encodings against regenerated analyses before rebinding data paths. Tableau-inferred count types and parameter display metadata are retained from the accepted template. The older minimal template remains the generator scaffold. Rebuilds reproduce the accepted layout and logical data; ZIP/Hyper bytes need not be identical. They do not replace the permanent release automatically.

# Integration plan

**BigQuery synthetic demonstration verified; real source integrations remain planned and disconnected.** The authenticated BigQuery sandbox run passed 96/96 SQLite comparisons. Billing was disabled at the historical verification; current cloud state has not been rechecked. No paid service or trial was activated. See [validation evidence](BIGQUERY_VALIDATION.md). GitHub repository access is verified separately below.

| Tool | Intended role | Validation before use |
| --- | --- | --- |
| Python / SQL | Local analysis and transformations | Reproduce results with fixtures and checks |
| BigQuery | Verified synthetic demo warehouse | US demo dataset, owned tables, 96/96 parity; seven-day expiration and billing disabled at the recorded verification. Current availability is unverified. Real-data/production operation remains planned |
| GA4 | Events and journey steps | Event definitions, consent gaps, transaction IDs, export coverage |
| Shopify | Orders and revenue reference | Order lifecycle, refunds, tax, shipping, discounts, time zone |
| Google Ads | Spend and attributed conversions | Account currency, dates, attribution window and conversion actions |
| Meta Ads | Spend and attributed conversions | Account currency, dates, attribution window and overlap |
| Tableau Public | Implemented local synthetic dashboards using CSV/Hyper extracts | Documented acceptance completed November 18; user runtime evidence and automated package validation are distinguished in [ACCEPTANCE.md](../release/ACCEPTANCE.md). No Tableau cloud publication or BigQuery live connection |
| Hotjar | Qualitative behavior evidence | Consent, masking, sampling and privacy; no identifiable recordings in Git |
| AI-assisted development | Used for code, SQL, prose and workbook XML drafting/repair | Reviewed through independent fixtures, execution and user Tableau evidence; no automated production AI integration |

Connect sources gradually with least-privilege access. Document field mappings, grain, extraction timestamps, refresh cadence and limitations. Prefer approved synthetic data until source access and data handling are agreed.

## GitHub access — resolved 2026-11-12

The initial authentication blocker is resolved. GitHub CLI verified the active account as `NonsoSk` and the repository as private. Origin is `https://github.com/NonsoSk/ecommerce-growth-analytics.git`. Remote inspection and fetch found no branches or commits; no existing remote files needed reconciliation.

The reviewed initial setup was pushed to `main`, with upstream `origin/main`. Its local and remote commit hashes matched after upload. Keep the repository private, inspect future remote changes before pushing, and never force-push. This source-control connection does not establish any analytics integration.

Current GitHub status: the accepted private release and reviewer documentation were uploaded on November 19, 2026. The current commit is visible in Git history; initial-setup details above are historical. No analytics source connection follows from this GitHub upload.

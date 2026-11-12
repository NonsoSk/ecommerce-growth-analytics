# Integration plan

**All external services are planned and disconnected.** No credentials have been supplied, accounts configured or paid services activated.

| Tool | Intended role | Validation before use |
| --- | --- | --- |
| Python / SQL | Local analysis and transformations | Reproduce results with fixtures and checks |
| BigQuery | Warehouse | Approve project, region, access and cost controls before setup |
| GA4 | Events and journey steps | Event definitions, consent gaps, transaction IDs, export coverage |
| Shopify | Orders and revenue reference | Order lifecycle, refunds, tax, shipping, discounts, time zone |
| Google Ads | Spend and attributed conversions | Account currency, dates, attribution window and conversion actions |
| Meta Ads | Spend and attributed conversions | Account currency, dates, attribution window and overlap |
| Tableau | Dashboard | Reconcile displayed totals to validated queries; review sharing |
| Hotjar | Qualitative behavior evidence | Consent, masking, sampling and privacy; no identifiable recordings in Git |
| AI workflow (provider undecided) | Assist code, exploration and explanation | Independently verify every result and record review |

Connect sources gradually with least-privilege access. Document field mappings, grain, extraction timestamps, refresh cadence and limitations. Prefer approved synthetic data until source access and data handling are agreed.

## GitHub access blocker

The initial unauthenticated read of repository refs failed because GitHub requested a username. This does not establish whether the repository is private, missing or populated. The remote URL is configured locally, but no remote files have been fetched.

When access is available, inspect `git remote -v`, fetch origin, then inspect its default branch and history. If populated, compare files and reconcile on a separate branch or temporary checkout; if histories are unrelated, preserve the local setup commit and apply reviewed changes onto the remote history. Resolve overlaps manually. Never force-push or assume the remote is empty.

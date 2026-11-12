# Milestone 1 validation record

Date: **2026-11-12**. Status: **synthetic milestone verified; project in development**.

## Inputs and execution

- Python: existing `.venv`, Python 3.14.8; standard library only, no added dependencies.
- Generator: `scripts/generate_sample.py`, schema/generator version 1, seed 42, 2,700 sessions.
- Session cohort: 2026-01-01 inclusive to 2026-04-01 exclusive; refund observation cutoff 2026-04-16 exclusive, UTC, USD.
- Generated baseline successfully and ran `.venv/bin/python -m unittest discover -s tests -v`: **14 tests passed**.
- Determinism check generated independent directories, compared every JSON file byte for byte, and verified SHA-256 hashes against the manifest. Different seed and sizes 1, 137 and 900 also passed their relevant checks.

## Baseline counts

| Table | Rows |
| --- | ---: |
| campaigns | 4 |
| customers (visitor identities, not all buyers) | 1,496 |
| sessions | 2,700 |
| events | 7,170 |
| orders | 377 |
| order_items | 377 |
| refunds | 79 |
| ad_spend_daily | 360 |

Separate fixtures: **3 cases / 4 event rows**. Committed illustration: **12 linked rows** (one per table except five events). Neither is added to baseline counts.

## Arithmetic controls (integer cents, synthetic only)

| Control | Expected / actual |
| --- | ---: |
| Gross merchandise | 35,330,800 |
| Discounts | 830,080 |
| Merchandise after discounts, before refunds | 34,500,720 |
| Total original payment including tax | 37,260,710 |
| Merchandise refunds | 1,408,425 |
| Merchandise after discounts and refunds | 33,092,295 |
| Campaign-day spend | 4,425,988 |

These are reproducibility controls, not business findings. Unit-price × quantity minus discounts was independently compared with original paid totals minus charges. Campaign-day aggregation retained the same spend total; the tests do not join spend onto event rows.

## Coverage and limits

Passed checks cover unique keys in every table, linked customer/session/order/item/refund/campaign records, event order and ingestion chronology, transaction matching, monetary arithmetic, cumulative refunds, default traffic/journey variety, illustrative sample consistency, exact quality-fixture detection and zero baseline issue detections. Corruption tests show invalid keys, amounts and chronology are rejected, rather than merely checking that generated output accepts itself.

AI-assisted code and documentation were executed and reviewed against the measurement contract. The independent checks are arithmetic recomputation, deliberate corruption cases, hand-authored quality fixtures and byte/hash comparisons. No private inputs or external analysis services were used. These checks do not prove real-world tracking completeness, causal effects or production readiness. A human portfolio review remains appropriate before presenting analytical conclusions.

Pre-commit review covered all 28 tracked/staged files: no secret-pattern matches, tracked ignored files or private data files were found. Both committed JSON examples are small, explicitly synthetic, and use fictional identifiers; fixture case names are issue labels, not personal names. Ignore checks confirmed that bulk generated output, `.venv`, `.env` and private datasets remain excluded. Manual content review supplements the targeted scan; it is not a universal secret-detection guarantee. `git diff --cached --check` passed. GitHub synchronization is checked after push; obtain the revision from Git rather than embedding a self-referential commit hash here.

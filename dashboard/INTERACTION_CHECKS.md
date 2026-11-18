# Tableau acceptance checklist — completed November 18, 2026

Synthetic demonstration only. Final workbook: `../release/SYNTHETIC_Growth_REVIEW.twbx`. No outstanding user acceptance actions. Dated screenshot identifiers and observations remain in PROGRESS.md; adoption/build provenance is in release/ACCEPTANCE.md.

| Check | Status | Evidence |
|---|---|---|
| Three dashboards, 29 worksheets, baseline totals and charts | PASS | Reviewed Overview/Funnel/Acquisition screenshots; SQL reference totals |
| January Overview including orders, refunds and spend | PASS | 930 sessions; 125 converting sessions; 13.44%; 125 orders; $106,736.47 net; $4,498.03 refunds; $15,148.71 spend |
| Funnel combinations | PASS | January mobile/google/returning_visit: 87/79/24/15/9, losses 8/55/9/6, conversion 10.34%; full-period combination also reviewed |
| Funnel empty and reset | PASS | April cohort empty without stale values; reset restores 2,700/2,380/1,036/677/377 |
| Acquisition combination | PASS | January google/syn_google_prospecting: $3,722.01 spend, $15,363.94 net, 18 orders, 4.13 ROAS, $248.13 first-observed paid CAC proxy, 16 zero-order spend days |
| Acquisition conflicting empty and reset | PASS | google/syn_meta_prospecting: no marks; All/full-period restores six totals and four campaigns |
| Acquisition filters isolated from Overview/Funnel | PASS | Agent-observed navigation November 15; January Overview/Funnel unaffected |
| Funnel filters isolated from Overview/Acquisition | PASS | November 18 explicit user sequence confirmation plus 5e5ba463 and bc208b8b screenshots; January values above retained while Funnel mobile/google/returning_visit remains active |
| All Funnel channel labels | PASS | Reopened screenshot 783c07e8: direct 14.63%, google 12.98%, meta 14.33%, organic 14.24% |
| Relocated local close/reopen | PASS | User explicitly closed/reopened the same relocated TWBX without reconnecting or warnings; three post-reopen views 90ac97da / 783c07e8 / c14fd0a1 |
| Accepted-layout analytical equivalence | PASS, automated | Same formulas, 29 worksheet sources/filter/shelf/mark contracts; identical accepted extracts; final package 1,637 rows match CSVs |
| Build reproduction | PASS, automated | Source-only adopted-layout build; 8 SQL/Hyper cases, 50 expression checks, canonical layout equality |

Dates intentionally apply across dashboards. Funnel selectors affect only Funnel; Acquisition selectors affect only Acquisition; Overview uses dates only. Empty selections render blank marks rather than fabricated zero ratios. These are representative acceptance cases, not exhaustive proof of every possible filter state.

Runtime evidence concerns the user-reopened layout. Final packaging removed workstation fingerprint attributes, normalized relative paths and restored matching baseline CSVs. Canonical XML after those transformations matches the reopened workbook, and its exact extract bytes are retained. The final ZIP itself was structurally/data validated, not separately opened by the agent in Tableau. See release/ACCEPTANCE.md. No publication or real commercial result is implied.

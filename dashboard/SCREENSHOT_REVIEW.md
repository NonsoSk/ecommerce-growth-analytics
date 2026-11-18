# Four-screenshot review — synthetic demonstration

Reviewed the four user attachments on 2026-11-14 against newly executed SQLite baseline queries. No business findings or causal effects are inferred. Screenshots establish visible rendered states, not every interaction or future reload.

## Overview: screenshots 1 (January) and 2 (full period)

| Metric | January screenshot / SQL | Full-period screenshot / SQL | Result |
|---|---:|---:|---|
| Sessions | 930 | 2,700 | PASS |
| Converting sessions | 125 | 377 | PASS |
| Purchase conversion | 13.44% | 13.96% | PASS, rounded ratio of sums |
| Orders | 125 | 377 | PASS |
| Net merchandise revenue | $106,736.47 | $330,922.95 | PASS |
| Merchandise refunds | $4,498.03 | $14,084.25 | PASS |
| Advertising spend | $15,148.71 | $44,259.88 | PASS |

Both date controls and all seven KPI sheets are visible. Currency/percentage formats are correct. No warning, blank KPI or missing worksheet is visible. Long titles wrap legibly. The blue refund background is a visible selection/highlight state, not evidence of an arithmetic error. January and full-period date-filter result states are visually established; the screenshots do not demonstrate the precise reset action or all other combinations.

**Confirmed wording defect:** the static Jan 1–Mar 31 note could be mistaken for the selected period in January. Corrected only that note in a separate REVIEW copy to: “Available data: Jan 1–Mar 31, 2026 UTC. Selected period: date controls below.” The original/repaired workbook, CSVs and extracts are preserved. Exact XML comparison confirms only three dashboard notes changed; all 29 sheets, controls, formulas and layouts are retained.

## Acquisition: screenshot 3

Full-period / All-source / All-campaign values match SQL: spend **$44,259.88**, paid-attributed net **$173,184.63**, orders **203**, net attributed ROAS **3.91**, first-observed paid CAC proxy **$245.89**, days with spend and zero attributed orders **195**. All four campaign charts contain four bars. All four controls are present. No visible datasource warning, blank chart or missing sheet.

SQL control totals by campaign (not every bar's exact value is printed in the screenshot):

| Campaign | Spend USD | Net attributed USD | ROAS | CAC proxy USD |
|---|---:|---:|---:|---:|
| syn_google_prospecting | 11,356.56 | 42,447.72 | 3.74 | 270.39 |
| syn_google_retargeting | 11,670.38 | 50,380.26 | 4.32 | 216.12 |
| syn_meta_prospecting | 10,091.24 | 33,420.01 | 3.31 | 288.32 |
| syn_meta_retargeting | 11,141.70 | 46,936.64 | 4.21 | 227.38 |

Readable bar labels **$11,670.38, $11,141.70, $50,380.26, $46,936.64, 4.32, 4.21 and $270.39** all match. Some other numeric labels are automatically omitted in this compact view; their exact values are SQL-validated but not visually verified by these images. This is not a blank/missing chart. Titles and campaign names are readable; screenshot is scrolled below the dashboard heading/notes, so those elements are outside the capture, not proven missing.

## Funnel: screenshot 4

All five stages match SQL: **2,700 → 2,380 → 1,036 → 677 → 377**. All four losses match: **320, 1,344, 359, 300**. Skipped/out-of-order sessions **0** matches. The formerly invalid Session starts worksheet now renders **2,700** with no visible warning, supporting the isolated source-order repair for the reported failure.

Both comparison charts render. Device labels **desktop 18.57%** and **mobile 11.78%** match. Source labels **direct 14.63%** and **organic 14.24%** match. Google **12.98%** and Meta **14.33%** are SQL expectations, but their numbers are not printed in this screenshot; exact visual checks remain pending. All five controls are present. Titles wrap; no confirmed clipped visible title. Dashboard heading/notes are above the scrolled viewport. No blank chart or missing sheet is visible.

## Acceptance boundary

Across the screenshots, all 29 dashboard worksheet zones show content. This establishes three baseline dashboard rendered states and January Overview. It does not prove each worksheet's full domain, every filter, filter isolation, empty-result behavior, reset actions, or a successful close/reopen cycle. The control service again timed out on fresh attachment (`-10005: timeoutReached`); this is independent of workbook correctness.

Use **SYNTHETIC_Growth_REVIEW.twbx** for the remaining checks. This is a fresh package of the source-order repair plus note clarification, not the older PORTABLE package built from the failed workbook. Its seven entries and relative data paths passed archive checks; all 1,637 rows matched after unpacking into an unrelated temporary directory. Fifty expression/predicate checks passed on the REVIEW TWB. Actual Tableau opening/closing/reopening of this new package and its new note rendering are still pending. Do not mark the milestone complete.

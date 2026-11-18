# Final Tableau acceptance batch — 2026-11-15

Synthetic demonstration only. Overall acceptance is pending. Use SYNTHETIC_Growth_REVIEW.twbx. Complete A and B, then send evidence together. Do not repeat earlier standalone baseline, combination, empty or reset tests: they already pass. Acquisition-to-Overview/Funnel isolation was completed by the agent on November 15.

## A. Remaining direction of filter isolation

**November 18 update:** both requested Overview/Acquisition screenshots received and their values pass. Do not recapture them if you kept Funnel mobile/google/returning_visit selected; just confirm that sequence. Section B evidence remains outstanding.

Keep January 1–31, 2026 throughout this section. Dates are intentionally shared.

1. On Acquisition choose paid source `google`, campaign `syn_google_prospecting`. This establishes the previously verified reference state; no new screenshot needed yet.
2. On Funnel select device `mobile`, source `google`, cohort `returning_visit`. Confirm 87 → 79 → 24 → 15 → 9. These selectors must affect only Funnel.
3. Without changing dates or selectors, visit Overview and Acquisition. Capture each view. Overview must still show 930 sessions, 125 converting sessions, 13.44%, 125 orders, $106,736.47 net, $4,498.03 refunds and $15,148.71 spend. Acquisition must retain google/prospecting controls and $3,722.01 spend, $15,363.94 attributed net, 18 orders, 4.13 ROAS, $248.13 CAC proxy and 16 zero-order spend days. Tell me you left the Funnel selectors active while capturing both screenshots. These two screenshots plus that sequence confirmation test reverse isolation; no extra Funnel screenshot is required.

## B. Portable close/reopen and remaining labels

The agent already copied the package, without rebuilding it, to:

`/private/tmp/ecommerce-growth-portability-20261115/SYNTHETIC_Growth_REVIEW.twbx`

This directory contains only that TWBX, no adjacent CSV or Hyper files. SHA256: `182481c1f06f29417e7231ea9fa5d9fe52b1289cb3dd8a7934dd8b79b1f93c3c`. All data are embedded with relative paths. The original repository copy and original draft remain untouched.

1. Close the current REVIEW workbook using File > Close. If there are unsaved layout edits you want to keep, preserve them first using local File > Save As under a different filename; do not overwrite the original draft or the prepared test package. Do not use Save to Tableau Public. Filter-only test changes need not be saved.
2. In Finder press Shift–Command–G and enter `/private/tmp/ecommerce-growth-portability-20261115`. Open its REVIEW TWBX. It should open with local data, without a missing-file/source warning, login requirement or cloud connection. Default dates should be January 1–March 31 and selectors All. Report any different defaults; do not silently treat them as passed.
3. Visit all three dashboards and check the full-period reference table below. This is a runtime test from the relocated package, not a repeat of earlier calculation testing. Scroll as needed so all sheets and notes can be seen.
4. On full-period Funnel, hover the **google** and **meta** bars in the channel comparison. Expected conversion: google **12.98%** (105 / 809), meta **14.33%** (98 / 684). Capture the two tooltips, or report their exact text if the tooltip disappears during capture. Other labels already have sufficient evidence.
5. Close this relocated workbook, reopen the **same file from that folder**, and revisit all three dashboards. No missing-data warning should appear, and the same totals and sheets must remain. Capture one screenshot per dashboard after this second opening, including controls and full results where possible. Confirm explicitly that you closed/reopened the relocated file and did not reconnect a source. No other filter tests need repeating.

| Reopened view | Expected full-period results |
|---|---|
| Overview | Sessions 2,700; converting sessions 377; conversion 13.96%; orders 377; net $330,922.95; refunds $14,084.25; spend $44,259.88 |
| Funnel | Stages 2,700 → 2,380 → 1,036 → 677 → 377; losses 320 / 1,344 / 359 / 300; skipped 0; two comparison charts |
| Acquisition | Spend $44,259.88; attributed net $173,184.63; orders 203; ROAS 3.91; first-observed paid CAC proxy $245.89; zero-order spend days 195; all four campaigns on all four charts |

Send together: two isolation screenshots, two tooltip values/screenshots, three post-reopen dashboard screenshots, and the brief sequence confirmations. If any step fails, include the exact error and stop that operation; do not reconnect files or alter formulas just to make it pass. These are the only outstanding acceptance checks. After evidence review, documentation can be finalized or specific defects identified. Everything stays local; no publication or paid service.

> Historical investigation record. Pending/failure statements describe the dated stage below, not the final release. See [current acceptance](../release/ACCEPTANCE.md) for resolved status. Retained to explain the repair and evidence trail.

# Tableau XML compatibility probe — not validated

Synthetic demonstration data only. In development. Local work only.

The original `dashboard/SYNTHETIC_Growth_DRAFT.twb` is byte-for-byte identical to its backup at `dashboard/workbooks/backups/SYNTHETIC_Growth_DRAFT_9bf07d7c6ad1.twb`.

A separate `dashboard/workbooks/SYNTHETIC_XML_PROBE.twb` copies the working Orders worksheet and adds a calculated Net Merchandise Revenue USD sheet: `SUM([net_revenue_cents]) / 100.0`. No KPI value is hard-coded. The baseline overview CSV contains 90 rows and totals 33,092,295 cents ($330,922.95).

The probe is well-formed XML, but has NOT opened successfully. Tableau Public 2026.3.0 attempted to load it on November 13, 2026 at 21:46:48 local time. Its workbook DOM loader terminated with error D2E8DA72 (decimal 3538475634): “Errors occurred while trying to load the workbook ... The load was not able to complete successfully.” Detailed error contents are masked in the log. Computer controls remain attached to the original draft and do not expose the second process's error dialog. The next action is to obtain that dialog's detailed error text before making further changes. This does not establish that all programmatic editing is incompatible.

Reviewed official schema documentation: https://github.com/tableau/tableau-document-schemas . The official 2026.3 XSD downloaded to a temporary location did not compile standalone with xmllint because its imported user/XML namespace definitions were unresolved. Therefore no XSD-validation success is claimed. Tableau's documentation also distinguishes syntax validation from successful workbook loading.

No remaining dashboards were generated from this unverified probe. No public publication, account changes or paid services occurred. The original CSV connections and original workbook remain unchanged. The original uses a temporary Hyper extract path; durability of an eventual generated workbook must be verified separately.

## Repair verification — November 13, 2026

The generator inserted the datasource calculated column after `extract`, immediately before `layout`. The official 2026.3 XSD `DataSource-CT` sequence places `Columns-G` before `Extract-G`, then `Layout-G`. The original working workbook follows that ordering. This was an invalid sibling order, not an invalid datasource parent or a duplicate datasource column. In the inspected pre-repair copy the added column was at line 287; line 318 was near the end of the datasource, so reported error positions should not be assumed to identify the originating node exactly.

Corrected `scripts/test_tableau_xml.py` to insert after the last existing datasource column, before the extract. Also preserved the original `xmlns:user` declaration. Checks before reopening confirmed unique datasource column names, exactly one revenue worksheet/window, all columns preceding extract, and original/backup byte equality. No original workbook, backup or CSV was rewritten. Only the probe was regenerated.

Tableau's new `log_2.txt` records `end-workbook-dom-loader.load-workbook-dom` with `rk=ok` at 22:44:36.295 and `end-workspace.load-workbook` with `rk=ok` at 22:44:36.980. These are actual application load results, not merely XML parsing. The control interface continues to expose the original draft's process, so the new worksheet display has NOT been visually verified. Expected baseline amount remains $330,922.95, computed from the CSV rather than hard-coded into the workbook. Expansion remains gated on that visual check. No complete XSD-validation claim is made.

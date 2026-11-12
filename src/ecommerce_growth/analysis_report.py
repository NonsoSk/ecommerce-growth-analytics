"""Render actual computed SQL outputs; never insert claimed commercial outcomes."""
from collections import Counter


def money(cents):
    return 'N/A' if cents is None else f'${cents / 100:,.2f}'


def rate(numerator, denominator):
    return 'N/A' if not denominator else f'{numerator / denominator:.2%}'


def table(headers, rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |'] +
                     ['| '+' | '.join(str(v) for v in row)+' |' for row in rows])


def render(metadata, outputs, controls, fixtures):
    s=metadata['summary']; f=outputs['funnel'][0]
    campaigns=outputs['campaign_summary']
    spend=sum(r['spend_cents'] or 0 for r in campaigns)
    paid_net=sum(r['net_revenue_cents'] for r in campaigns)
    paid_new=sum(r['first_observed_purchasers'] for r in campaigns)
    missing=sum(r['missing_spend_days'] for r in campaigns)
    quality=Counter(r['reason'] for r in outputs['quality'])
    reconciled=Counter(r['status'] for r in outputs['reconciliation'])
    steps=[('Session → product',f['session_starts'],f['product_views']),('Product → cart',f['product_views'],f['carts']),('Cart → checkout',f['carts'],f['checkouts']),('Checkout → purchase',f['checkouts'],f['purchases'])]
    largest=max(steps,key=lambda r:r[1]-r[2])
    devices={r['segment']:r for r in outputs['funnel_segments'] if r['dimension']=='device'}
    rows=[('Eligible sessions',s['sessions']),('Observed visitors (includes nonbuyers)',s['visitors']),
          ('Purchasing visitors',s['purchasing_visitors']),('First observed purchasers',s['first_observed_purchasers']),
          ('Converting sessions (order ledger)',s['converting_sessions']),('Paid orders',s['orders']),
          ('Order-based purchase conversion',rate(s['converting_sessions'],s['sessions'])),
          ('Merchandise revenue after discounts, before refunds',money(s['merchandise_cents'])),
          ('Merchandise refunds',money(s['refunds_cents'])),('Net merchandise revenue',money(s['net_revenue_cents'])),
          ('Pre-refund merchandise AOV',money(s['merchandise_cents']/s['orders'] if s['orders'] else None)),
          ('Net revenue per session',money(s['net_revenue_cents']/s['sessions'] if s['sessions'] else None)),
          ('Paid media spend',money(spend)),('Same-session paid-attributed net revenue',money(paid_net)),
          ('Paid-attributed first observed purchasers',paid_new),
          ('Net paid ROAS',f'{paid_net/spend:.2f}x' if spend and not missing else 'N/A'),
          ('Observed paid-media CAC proxy',money(spend/paid_new if paid_new and not missing else None)),
          ('Sessions with immature refund windows',s['refund_immature_sessions'])]
    sections=[
        '# Milestone 2 — SYNTHETIC-DATA ANALYSIS',
        '**In development. Fictional simulation only; not findings about Puffy or real customers. No causal effects, commercial improvements or successful experiments are claimed.**',
        '## Reproduction and provenance',
        'Run `.venv/bin/python scripts/run_analysis.py` from the repository root. It verifies or generates the baseline, loads a fresh constrained SQLite database, exports CSVs, exercises quality fixtures, renders this report to the ignored output folder and runs the complete test suite. The committed report is a reviewed copy; reruns do not overwrite it.',
        f"Seed **{metadata['seed']}**; configured sessions **{metadata['configured_sessions']}**; schema/generator version **{metadata['generator_version']}**. UTC cohort **[{metadata['start_date']}, {metadata['end_date_exclusive']})**; exclusive observation cutoff **{metadata['cutoff']}**. Currency: USD. SQLite **{metadata['sqlite_version']}**; Python **{metadata['python_version']}**.",
        f"Canonical data SHA-256: `{metadata['data_fingerprint']}`. This hashes sorted table names and their original row order using the generator's canonical JSON serialization. Per-table input hashes and SQL hashes are recorded in ignored `data/generated/analysis/run_metadata.json`.",
        'Generated CSVs and SQLite database are under `data/generated/analysis/`. Blank ratio cells mean null, not zero. Cohort dates without sessions remain in daily output; future dates are explicitly marked not_yet_observed. See [SQL pipeline documentation](../docs/SQL_PIPELINE.md) for all export grains and caveats.',
        '## Calculated summary',table(['Metric','Value'],rows),
        'Orders are counted independently of purchase-event delivery. The strict funnel below requires a valid linked purchase event. Their totals agree in the clean baseline; missing tracking would create a visible discrepancy, not erase ledger revenue.',
        '## Ordered, same-session funnel',
        table(['Transition','Sessions at prior step','Sessions at next step','Loss count','Step conversion'],[(n,a,b,a-b,rate(b,a)) for n,a,b in steps]),
        f"Skipped/out-of-order sessions: **{f['skipped_or_out_of_order_sessions']}**. Repeated steps count once; chronology and the session_start prefix are required. No cross-session stitching is performed.",
        '## Funnel by available dimensions',
        table(['Dimension','Segment','Sessions','Views','Carts','Checkouts','Purchases','View → cart','Session → purchase'],[(r['dimension'],r['segment'],r['sessions'],r['product_views'],r['carts'],r['checkouts'],r['purchases'],rate(r['carts'],r['product_views']),rate(r['purchases'],r['sessions'])) for r in outputs['funnel_segments']]),
        'Landing page is absent from the source schema. No landing-page analysis or invented page labels are included. Source here means channel; source/medium and click IDs are also absent.',
        '## Campaign totals — same-session attribution',
        table(['Campaign','Spend','Orders','Net revenue','First observed buyers','Net ROAS','CAC proxy','Paid days / no orders'],[(r['campaign_id'],money(r['spend_cents']),r['attributed_orders'],money(r['net_revenue_cents']),r['first_observed_purchasers'],'N/A' if r['net_roas'] is None else f"{r['net_roas']:.2f}x",money(r['observed_paid_cac_cents']),r['paid_days_without_orders']) for r in campaigns]),
        'These are ratios of summed values, not averages of daily ratios. CAC includes media cost only, uses first-observed purchasers, and is not lifetime or fully loaded CAC. Missing-spend days suppress campaign aggregate ratios. Spend-only and conversion-only keys are retained; no spend is assigned to individual events or devices.',
        '## Activity not attributed to paid campaigns',
        table(['Channel','Sessions','Orders','Net revenue','First observed buyers'],[(r['channel'],r['sessions'],r['orders'],money(r['net_revenue_cents']),r['first_observed_purchasers']) for r in outputs['unattributed']]),
        'Organic and direct are known unpaid channels, not necessarily tracking failures. Paid CAC/ROAS are not applicable to them. Direct orders stay direct rather than inheriting an earlier paid session.',
        '## First observed versus returning visits',
        table(['Visit type','Sessions','Distinct visitors','Purchasing visitors','Orders','First observed purchasers','Conversion'],[(r['visit_type'],r['sessions'],r['distinct_visitors'],r['purchasing_visitors'],r['orders'],r['first_observed_purchasers'],rate(r['converting_sessions'],r['sessions'])) for r in outputs['visitors']]),
        'Visitors can appear in both rows over time; distinct-visitor counts across these rows are not additive. First visit and first purchase are different events. No pre-simulation history exists, so first observed never proves first-ever.',
        '## Data quality and reconciliation',
        ('Automated suite: **{run} tests, {failures} failures, {errors} errors**.'.format(**metadata['tests']) if metadata.get('tests') else 'Automated suite not run by this invocation.') + ' Independent hand-calculated fixtures supplement source-total and baseline checks.',
        table(['Baseline event disposition','Rows'],sorted(quality.items())),
        table(['Purchase/order reconciliation status','Rows'],sorted(reconciled.items())),
        table(['Control (cents for money)','Source','SQL','Difference'],[(k,v['source'],v['sql'],v['difference']) for k,v in controls.items()]),
        f"Baseline late events: **{sum(r['late_arrival'] for r in outputs['quality'])}**. The baseline is deliberately clean; zero detections do not imply real tracking would be complete. Event payloads contain no revenue amount, so transaction matching validates purchase coverage, while money is independently reconciled from items, charges and refunds.",
        '### Separate quality-fixture results',
        table(['Case','Raw event','Reason','Disposition'],[(r['case'],r['event_id'],r['reason'],r['disposition']) for r in fixtures]),
        'Raw records are retained. Duplicate delivery is quarantined, missing IDs are quarantined, and late valid records restate the occurrence cohort. The independent SQL fixture proves late reprocessing changes ordered purchases from 1 to 2 after arrival, then stays at 2 on repeated execution; its four ledger orders are unchanged. Its two orders in one session, multiple items and cumulative partial refunds reconcile to 35,000 cents before refunds, 2,500 cents refunds and 32,500 cents net. Separate tests cover skipped steps and spend-only/conversion-only keys.',
        '## Observations to investigate — not recommendations of proven impact',
        f"1. **Journey loss:** the largest absolute step loss is {largest[0]}: {largest[1]:,} prior-step sessions, {largest[2]:,} next-step sessions, a loss of {largest[1]-largest[2]:,} ({rate(largest[1]-largest[2],largest[1])}). Limitation: progression probabilities are hard-coded and journeys stop at the first failed step. Alternatives include ordinary browsing intent or missing event instrumentation in a future real dataset. Next investigation: validate step coverage and segment product intent before proposing a product-page experiment.",
    ]
    if 'mobile' in devices and 'desktop' in devices:
        m,d=devices['mobile'],devices['desktop']
        sections.append(f"2. **Device difference:** mobile has {m['purchases']}/{m['sessions']} ordered purchases per session ({rate(m['purchases'],m['sessions'])}); desktop has {d['purchases']}/{d['sessions']} ({rate(d['purchases'],d['sessions'])}). Limitation: the generator explicitly sets different mobile and desktop progression probabilities. Channel mix and chance are alternative explanations for the exact realized gap; this is not proof of a mobile usability defect. Next investigation: compare like-for-like source and repeat-visit cohorts, then validate instrumentation before any usability hypothesis.")
    if campaigns:
        sections.append(f"3. **Acquisition needs cautious interpretation:** {sum(r['paid_days_without_orders'] for r in campaigns)} campaign-days incurred positive spend without an attributed order, out of {len(outputs['campaign_daily'])} campaign-day keys. Limitation: spend and traffic are independently simulated; this cannot establish waste or incrementality. Alternatives include small daily samples and purchases in later direct sessions under the same-session attribution rule. Next investigation: review cohort maturity and attribution sensitivity; do not move budgets based on this simulation.")
    sections += ['## Limits and next scope',
        'The full default refund window is mature only under the invented maximum 14-day delay plus ingestion allowance. Earlier cutoffs are provisional; unfinished sessions are excluded, future event arrivals are deferred, and refunds are included only when available. Orders/spend are static snapshots without ingestion timestamps, so this is not a historical warehouse backtest. Failed payments, cancellations, full returns, true lifetime customer history, landing pages, real consent loss and production-scale validation remain absent.',
        'BigQuery remains the planned cloud warehouse. No BigQuery, GA4, Shopify, Google Ads, Meta Ads, Hotjar or Tableau integration is implemented. No dashboard, A/B experiment or paid service was activated. See docs/SQL_PIPELINE.md for migration considerations and docs/MEASUREMENT_REVIEW.md for definition corrections.']
    return '\n\n'.join(sections)+'\n'

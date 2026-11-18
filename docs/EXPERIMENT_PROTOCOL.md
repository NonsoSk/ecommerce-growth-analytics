# Proposed product-page information experiment — NOT EXECUTED

**Synthetic portfolio design only. No assignment, exposure, experiment data, statistical result or revenue improvement exists.** Do not launch from these simulated patterns. Before launch, independently reconcile authorized real tracking, inspect usability evidence and approve an actual intervention.

## Hypothesis and treatment

Hypothesis: placing clear total price, delivery timing and returns terms beside the purchase controls improves completed purchasing among eligible product-page visitors. Control retains the existing page; treatment changes only this information presentation. Content must be accurate and equivalent in commercial terms. This is a proposed interface change, not an existing product implementation.

## Population and assignment

Eligible: consented, non-bot adult-market visitors reaching an eligible mattress product page, with a stable first-party experiment identifier; exclude employees, QA and conflicting experiments before assignment. Randomize that visitor identifier 1:1 at first eligibility, persist assignment for the study, and analyse intention-to-treat. Cross-device identity limitations must be measured; do not pretend the synthetic customer ID solves real identity. Count each assigned visitor once, including nonbuyers. Predefine fraud/test-order exclusions independent of treatment and report exclusions by arm.

Primary metric: fraction of assigned eligible visitors with at least one eligible paid order within seven days of assignment. This is visitor-level experimental conversion, intentionally distinct from the dashboard's descriptive session conversion. Secondary: ordered add-to-cart progression; no success claim based solely on this proxy. Guardrails: net merchandise revenue per assigned visitor, merchandise refund share, checkout errors and page-load latency. Observe refunds for 30 days after order (a design assumption to confirm against actual return policy); report immature outcomes separately.

## Sample-size and duration plan

Illustrative planning assumptions, NOT estimates from this session-level simulation: 10% baseline visitor conversion, minimum detectable absolute increase 2 percentage points (10% to 12%), two-sided alpha 0.05, 80% power, equal allocation. The usual normal-approximation formula is:

`n per arm = ((1.96*sqrt(2*pbar*(1-pbar)) + 0.8416*sqrt(p0*(1-p0)+p1*(1-p1))) / (p1-p0))**2`, where pbar=0.11.

This gives approximately 3,841 visitors per arm; plan at least 3,842 per arm (7,684 total) and recompute with real independently measured baseline and agreed practical effect before launch. Enrol for at least two full weekly cycles and until target enrolment is reached, with a predeclared maximum of six weeks. If target is not reached, report underpowered/inconclusive rather than changing the effect threshold after seeing results. Wait seven days for primary outcomes and the full refund window before the final guardrail decision. No sequential significance peeking or optional stopping.

## Analysis and decision rules

Before unblinding outcomes, check assignment/exposure logs, sample-ratio mismatch (chi-square diagnostic threshold p<0.001), duplicates, contamination, missing outcomes and revenue reconciliation. A material tracking/randomization fault pauses interpretation. Do not exclude users because their behaviour looks inconvenient.

Report visitor counts, conversions, absolute/relative difference and a two-sided 95% interval; use a two-proportion test for the single primary endpoint. Report visitor-level bootstrap uncertainty for skewed net revenue. Segments are exploratory and cannot rescue a failed primary result. Pre-register guardrail noninferiority margins with stakeholders before launch; illustrative proposal: no more than 5% relative net-revenue-per-visitor loss, 1 percentage-point refund-share increase, 0.5 percentage-point checkout-error increase, or 200ms p75 latency increase. Confirm feasibility and power for these guardrails; inadequate precision is unresolved, not a pass.

A rollout recommendation requires a positive primary interval excluding zero, an estimated effect meeting the agreed practical target, mature guardrails within agreed margins and valid instrumentation. Otherwise report inconclusive/harmful/no meaningful benefit as supported; never infer success from synthetic data. A human product owner approves any real rollout. All accounts, live traffic changes and actual execution require separate authorization.

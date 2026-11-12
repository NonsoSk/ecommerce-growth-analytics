# Simulation assumptions and reproducibility

**SYNTHETIC ONLY. Not evidence about Puffy or any real customers.** No real data was used to set probabilities, prices or spend. There is no successful experiment or simulated uplift claim.

- Standard library `random.Random(seed)` isolates the random stream. Default seed is 42, size is 2,700 sessions and first date is 2026-01-01. The window is always 90 UTC days. Reproducibility is verified on the existing Python 3.14 environment; revalidate byte hashes after interpreter or generator changes.
- Session days are evenly allocated by index; start times are random within the first 85,001 seconds of each day, leaving room for the full journey. With fewer than 90 sessions, some days have no traffic, while spend still covers every day. Session IDs need not sort chronologically; timestamps do.
- The first session creates a visitor; each later session has 55% probability of creating a new visitor, otherwise it selects an existing visitor uniformly. Some visitors never buy, some return and some buy repeatedly. Identity is perfectly linked across visits, unlike real consent/cookie-limited data. First observed does not establish lifetime-new status.
- Channels are independently sampled: Google 30%, Meta 25%, organic 25%, direct 20%. Paid traffic picks prospecting or retargeting uniformly within its channel. Audience names do not enforce real eligibility or retargeting logic. No ad API is involved.
- Devices: mobile 68%, desktop 32%. Conditional progression: session → product 88%; product → cart 40% mobile / 52% desktop; cart → checkout 65%; checkout → purchase 50% mobile / 65% desktop. All are deliberately invented knobs. Channel-specific differences arise from random mix, not calibrated platform effectiveness.
- Each reached step occurs one minute after the previous step. Journeys terminate after the first failed transition; no step skipping, navigation loops, cross-session cart recovery, multiple tabs or purchases per session. Arrival is five seconds after occurrence. This clean baseline is intentionally simpler than real event data.
- One mattress item line per order; unit prices are $599, $899 or $1,199 with equal probability. Quantity is one (95%) or two (5%). A 10% line discount applies with 25% probability. Tax is a fictional flat 8%, truncated to integer cents; shipping is zero. This is an arithmetic convention, not tax guidance.
- Paid orders have an 18% chance of one partial merchandise refund, equal to 10%, 20% or 30% of discounted merchandise value with equal probability. Refund occurs 1–14 days after purchase, with five-minute ingestion delay. Tax refund is floor(8% × merchandise refund). No cancellations, full returns, chargebacks, failed payments or inventory constraints.
- Each of four campaigns has daily spend sampled uniformly as integer cents from 5,000 to 20,000 inclusive, independent of traffic and purchases. There is no budget optimization or revenue-to-spend feedback.
- Reporting uses a 90-day session cohort and an observation cutoff 105 days after start. Refund rows may extend outside the 90-day traffic window; they are retained so late-cohort refunds are not systematically dropped.
- Size changes can change the entire realization, not just append rows. Small sizes/seeds may have no purchases or refunds; tests verify structural validity, not forced outcomes. Default data are checked for all requested journey patterns.

## Reproduce from repository root

Generate the ignored baseline (replaces only the generator’s named files in its dedicated output directory):

```sh
.venv/bin/python scripts/generate_sample.py
```

Optional configuration: `--seed 7 --sessions 900 --start 2026-02-01`. Output stays under `data/generated/baseline/`; changing the start still generates 90 days.

Run all automated checks:

```sh
.venv/bin/python -m unittest discover -s tests -v
```

No dependencies were added. JSON was chosen because the standard library preserves nulls and integer monetary values without an additional package. Bulk output is ignored. The committed `data/sample/illustrative_journey.json` is a small linked excerpt, not an analysis dataset; regenerate the full baseline for calculations. The independent event fixtures live in `tests/fixtures/` and must never be appended to baseline data.

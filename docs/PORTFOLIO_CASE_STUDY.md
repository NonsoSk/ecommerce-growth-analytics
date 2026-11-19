# Investigating customer journeys and advertising performance for an online mattress retailer

I created this project to investigate how visitors move through an online store, where their journeys stop, and how purchases relate to advertising spend. I used a fictional direct-to-consumer mattress retailer, meaning a retailer that sells directly to customers through its own store.

The data is entirely synthetic. I generated it for this analysis; it does not describe real customers or the performance of a real retailer. The results helped me examine how an analysis should be structured and checked before its recommendations could be considered for a real business.

## Contents

- [The problem I wanted to investigate](#the-problem-i-wanted-to-investigate)
- [Where the data came from](#where-the-data-came-from)
- [How I prepared and checked the data](#how-i-prepared-and-checked-the-data)
- [How I measured performance](#how-i-measured-performance)
- [The dashboards and what I found](#the-dashboards-and-what-i-found)
- [My recommendations](#my-recommendations)
- [The experiment I proposed](#the-experiment-i-proposed)
- [Challenges and lessons from the work](#challenges-and-lessons-from-the-work)
- [What is complete and what I would improve](#what-is-complete-and-what-i-would-improve)

## The problem I wanted to investigate

For an online retailer, bringing visitors to the store is only part of the work. Visitors may look at a product, add it to their cart, begin checkout and leave before buying. Some may return later. At the same time, advertising platforms, website events and order records can describe the same purchase differently. If these differences are overlooked, the business could act on a misleading conversion rate or count the same revenue more than once.

I wanted to understand the journey and check the underlying numbers before recommending changes. The questions I set out to answer were:

1. Where is the largest loss between the steps leading to a purchase?
2. How does conversion differ by device, traffic source and observed visit history?
3. Do purchase events agree with the order records, and how do refunds affect revenue?
4. How much spend and revenue are assigned to each paid campaign?
5. Which issues deserve further investigation, and what evidence would be needed before taking action?

These questions could help a retailer decide whether to investigate product information, a mobile interaction or its tracking setup. They do not assume that every abandoned visit is a problem or that a campaign caused every purchase assigned to it.

## Where the data came from

I used Python to generate a repeatable 90-day dataset covering **January 1–March 31, 2026**. All dates use UTC and all monetary values use USD. Refunds are observed up to **April 16, 2026, exclusive**: records at or after that cutoff are outside the analysis.

Using synthetic data allowed me to create linked visits, orders, refunds and advertising records without collecting personal information or connecting real store accounts. A fixed random seed of 42 makes the simulated choices repeatable. It is a reproducibility setting, not evidence that the behaviour is realistic.

| Table | What it contains | Baseline rows |
|---|---|---:|
| Customers | Fictional observed visitor identities, including people who never buy | 1,496 |
| Sessions | Individual visits, with device, traffic source and optional campaign | 2,700 |
| Events | Recorded steps within those visits | 7,170 |
| Orders | Purchase records linked to a visitor and session | 377 |
| Order items | Merchandise lines with prices, quantities and discounts | 377 |
| Refunds | Partial merchandise refunds linked to items and orders | 79 |
| Campaigns | Fictional Google and Meta campaigns | 4 |
| Daily advertising spend | One campaign's spend on one date | 360 |

Customer IDs link visits and orders. Session IDs connect events to visits, while transaction IDs connect purchase events to orders. Refunds link back to the relevant item and order. Campaign IDs connect paid visits with campaign-day spend.

The table called `customers` needs particular care: its rows represent observed visitor identities, not just buyers. There are **331 purchasing identities**, compared with 1,496 identities overall. I also cannot establish that a person's first purchase in this dataset is their first-ever purchase.

The simulation includes repeat visits, abandoned journeys, mobile and desktop traffic, Google and Meta campaigns, organic and direct visits, purchases and partial refunds. It simplifies identity matching, prices and returns, and deliberately uses different device probabilities. It has no landing-page field. I kept those limitations visible rather than inventing data to complete a chart. The [data dictionary](DATA_DICTIONARY.md) and [simulation assumptions](SIMULATION_ASSUMPTIONS.md) explain the relationships and restrictions in more detail.

## How I prepared and checked the data

I started with the [measurement plan](MEASUREMENT_PLAN.md), so that the meaning of a purchase, converting session and refund was settled before writing the analysis. Python then generated the inputs and checked unique identifiers, links between tables, event timing and financial arithmetic.

I used SQL in SQLite, a local relational database, to analyse the data. Explicit table definitions constrain the types and relationships that are allowed. The pipeline verifies input hashes, which act as file fingerprints, before loading them. Reruns create validated replacement outputs rather than appending the same records again. The raw baseline remains unchanged.

One important decision was to total order items and refunds separately before joining them to orders. Otherwise, an order with several items and several refunds could appear in several joined rows, multiplying its money. I applied the same principle to advertising: campaign outcomes are grouped by campaign and date before meeting spend at that level.

I also created separate quality-test fixtures. These are deliberately small examples with known answers, including duplicate purchase events, missing transaction IDs, late events, multiple items, multiple partial refunds and out-of-order journey steps. They stay outside the dashboard baseline. Invalid or unavailable records receive an explicit reason rather than disappearing from the audit, and late-event reprocessing is checked for double-counting.

For an independent example, the hand-calculated fixture has **four orders in three converting sessions**. Its merchandise amount is 35,000 cents, refunds are 2,500 cents and net merchandise revenue is 32,500 cents. This checks a case that the baseline, where each buying session contains one order, would not prove on its own.

I then compared equivalent SQL in BigQuery with the SQLite results. The live synthetic-data run passed **96 of 96 comparisons on November 13, 2026**. That is historical verification, not a claim that the cloud tables are available today. Their recorded expiration is November 19, 2026; I have not rechecked current availability. The local exports and workbook do not depend on those cloud tables.

## How I measured performance

I kept visitors, sessions and orders separate throughout the work. A visitor can return several times, and a session can contain more than one order. Purchase conversion therefore uses **distinct sessions with at least one eligible order divided by all eligible sessions**, rather than orders divided by sessions.

I stored money in integer cents during processing and converted it to dollars for display. Net merchandise revenue means merchandise after discounts, less merchandise refunds. It excludes tax and shipping and is not profit: cost of goods, fulfilment and operating costs are not modeled.

For the ordered funnel, a session must reach each stage after the previous one: product view, add to cart, checkout and purchase. Each eligible session counts once per stage. This is a same-session journey; it does not reconstruct a purchase that happens after several visits. Skipped or out-of-order journeys are reported separately.

For advertising, I used the campaign attached to the purchasing session. This is **attribution**: a rule for assigning an outcome to a source. It does not prove that the advertisement caused the purchase. Direct traffic has no paid campaign assignment under this rule, but it can still include missing attribution or earlier paid exposure. Organic traffic is not necessarily free to acquire.

The dashboard has three separate datasets. Overview has one row per day; Funnel has one row per day, device, source and observed visit cohort; Acquisition has one row per campaign-day. Keeping them separate prevents campaign spend from being repeated across individual events. When filters change, ratios are calculated from the selected totals, not by averaging daily percentages.

## The dashboards and what I found

I organised the Tableau workbook into three views: Overview, Funnel and Acquisition. Each view answers a different part of the business question. The [genuine screenshots](../dashboard/screenshots/README.md) show the accepted source layout; the [final workbook](../release/SYNTHETIC_Growth_REVIEW.twbx) contains its local data.

### Overview: how much traffic converted, and how much revenue remained?

I first used reconciled session and order records to establish the overall position. The full-period results are:

| Measure | Result |
|---|---:|
| Sessions | 2,700 |
| Distinct converting sessions | 377 |
| Purchase conversion | 13.96% |
| Orders | 377 |
| Purchasing visitor identities | 331 |
| Merchandise revenue before refunds | $345,007.20 |
| Merchandise refunds | $14,084.25 |
| Net merchandise revenue | $330,922.95 |
| Advertising spend | $44,259.88 |

The conversion calculation is `377 ÷ 2,700 × 100 = 13.96%`. The fact that there are also 377 orders is a feature of this baseline, not a reason to treat orders and converting sessions as the same measure.

For revenue, `$345,007.20 − $14,084.25 = $330,922.95`. This shows why I kept refunds in the analysis rather than reporting the original merchandise amount alone. Dashboard refunds are assigned to the originating session cohort, so a January selection includes the modeled refunds associated with January purchases within the observation cutoff. It is not a statement that all those refunds occurred during January.

These figures establish a reconciled starting point. They do not show whether the fictional retailer is profitable or whether its conversion rate would be good for a real business. My next step in a real setting would be to reconcile the same definitions with actual order and payment records before comparing performance or setting targets.

### Funnel: where do the ordered journeys stop?

To answer this, I counted sessions that progressed chronologically through each step.

| Stage | Sessions reaching it | Loss from the preceding stage |
|---|---:|---:|
| Session start | 2,700 | — |
| Product view | 2,380 | 320 |
| Add to cart | 1,036 | 1,344 |
| Checkout | 677 | 359 |
| Ordered purchase | 377 | 300 |

The largest absolute loss is between product view and cart: **1,344 sessions**. Of the 2,380 sessions that viewed a product in sequence, 1,036 reached the cart, giving **43.53% progression**.

This makes product-page progression a useful question to investigate. It does not establish that the page is confusing. In real data, comparison shopping, a later visit or missing tracking could also explain the difference. In this project, the generator determines the transition probabilities. I would therefore validate events and review consented usability evidence before proposing a page change.

I also compared devices. Mobile recorded **216 purchases from 1,833 sessions (11.78%)**, while desktop recorded **161 from 867 (18.57%)**. The gap is visible, but it is not proof of mobile friction. Different traffic sources, visit history and intent can affect an aggregate rate; device probabilities are also deliberately different in the simulation. My next investigation would compare mobile and desktop within similar source and observed-visit cohorts, followed by real technical and usability checks if suitable data became available.

### Acquisition: how does assigned revenue compare with spend?

I grouped orders and refund-adjusted revenue by the campaign and day of the purchasing session, then joined those totals to campaign-day spend.

| Paid acquisition measure | Result |
|---|---:|
| Advertising spend | $44,259.88 |
| Paid-attributed net merchandise revenue | $173,184.63 |
| Paid-attributed orders | 203 |
| Net attributed return on ad spend | 3.91 |
| First-observed paid customer acquisition cost proxy | $245.89 |
| Campaign-days with spend and zero attributed orders | 195 of 360 |

Return on ad spend, or **ROAS**, divides assigned revenue by advertising spend. Here, `$173,184.63 ÷ $44,259.88 ≈ 3.91`: about $3.91 in assigned net merchandise revenue for each advertising dollar. This is not $3.91 of profit, and it does not prove incremental advertising impact.

The customer acquisition cost, or **CAC**, measure is explicitly a proxy. It divides spend by first-observed purchasers assigned to paid campaigns. I cannot verify that these people are genuinely new customers because the dataset has no lifetime purchase history.

The 195 campaign-days with spend and no assigned orders deserve attention, but they do not establish wasted spend. Daily conversions can be sparse, and same-session attribution can miss later purchases. Before recommending a budget change, I would investigate unmatched purchases and compare defensible attribution windows. A causal advertising decision would need a separate lift or holdout study.

## My recommendations

Based on these findings, I recommend the following order of investigation. These are proposals to gather evidence, not changes whose effectiveness has been demonstrated.

| Priority | Evidence behind it | Next action and evidence needed | How I would measure success |
|---|---|---|---|
| 1. Investigate product-page progression | 1,344 sessions are lost between ordered product view and cart | Audit event sequencing, then examine real usability evidence for price, delivery or returns-information problems | Completed purchasing as the main outcome; cart progression as supporting evidence; revenue, refunds and technical performance as guardrails |
| 2. Compare similar mobile and desktop visits | Conversion is 11.78% on mobile and 18.57% on desktop | Compare source/visit cohorts and validate tracking before inspecting a specific mobile issue | Within-cohort conversion and journey progression; controlled testing of any proposed fix |
| 3. Review attribution before reallocating spend | 195 campaign-days have spend and no attributed orders | Reconcile real orders and spend, investigate unassigned activity and compare justified attribution windows | Reliable transaction matching and stable conclusions across assumptions; a separate controlled study for causal impact |

I put measurement checks before intervention because an apparent business problem can also be a data problem. None of these recommendations justifies changing a real retailer's website or budget using this synthetic dataset alone.

## The experiment I proposed

I developed the first investigation into a [proposed product-page information experiment](EXPERIMENT_PROTOCOL.md). It has **not been executed**. The hypothesis is that clearer total price, delivery timing and returns terms beside the purchase controls would improve completed purchasing among eligible product-page visitors.

The proposal assigns eligible, consented visitors to the current presentation or the revised presentation in a 1:1 split, keeping each visitor in the same group throughout the study. The primary outcome is the share of assigned visitors who place at least one eligible paid order within seven days. This is visitor-level experimental conversion, intentionally different from the descriptive session conversion in the dashboard.

The plan also checks net merchandise revenue per visitor, refunds, checkout errors and page-load time so that an apparent conversion improvement does not hide unwanted effects. It requires validated assignment and exposure logs, checks for an unexpected imbalance between groups and a predefined observation period.

For illustration, the sample-size calculation assumes 10% baseline conversion and a detectable increase to 12%, with a two-sided 5% significance level and 80% power. It plans at least **3,842 visitors per group**. Those assumptions are not estimates from this session-level simulation and must be recalculated using real baseline evidence. A rollout recommendation would require a positive, practically meaningful primary result, valid measurement and mature guardrails within agreed limits. There is no experiment result or sales improvement to report.

## Challenges and lessons from the work

The work made the distinction between correct arithmetic and a justified conclusion especially clear. Revenue can reconcile exactly while attribution remains uncertain. A lower device conversion rate can be correctly calculated without explaining why it is lower. That is why I kept calculation checks, interpretation and proposed action separate.

Tableau workbook generation also required more than checking whether its XML could be parsed. An early copy had an invalid data-source reference. The repair retained the worksheets, and acceptance stayed pending until the dashboards rendered and the relevant interactions had evidence. Computer-control timeouts were recorded separately from workbook errors.

I reviewed the dashboards through the available controls and supplied screenshots/manual interaction results where automation could not complete the checks. The evidence covers full and January totals, selected device/source/cohort combinations, empty results, resets and filter isolation between dashboards. Automated checks separately cover eight SQL/Hyper cases, 50 expressions and 1,637 matching dashboard rows. These are different forms of evidence, not interchangeable checks.

I closed and reopened the same relocated source workbook without reconnecting a data source or seeing warnings. The permanent release was later sanitized and repackaged with its exact extracts and equivalent workbook XML, with relative paths and matching CSVs restored. That final ZIP passed automated package/data validation; it did **not** receive a separate agent GUI reopen. The [acceptance record](../release/ACCEPTANCE.md) preserves this precise distinction.

AI assistance supported code, SQL, prose and workbook XML drafting and repair. My role included defining the scope, reviewing the interpretation and providing the manual Tableau evidence; automated execution and independent hand-calculated fixtures checked the implementation. I do not claim to have manually written every line or performed every automated operation.

## What is complete and what I would improve

The completed project includes the measurement definitions, repeatable synthetic dataset, local SQL/Python pipeline, historical BigQuery comparison, three accepted local dashboards, quality evidence and an unexecuted experiment protocol. The [README](../README.md) provides the entry point; the [dashboard guide](../dashboard/README.md) explains how to open the included workbook or build a separate copy. Original work and the preceding-release backup are preserved.

GA4, Shopify, Google Ads, Meta Ads and Hotjar ingestion remain unimplemented. Future work could add appropriately authorized real data, landing-page tracking, longer attribution windows and stronger identity/observation controls. Any real intervention would need fresh measurement validation and a properly designed experiment.

The practical lesson I take from this project is to make the numbers traceable before acting on them. I can explain how a session became a converting session, how refunds changed revenue and how spend met campaign outcomes without multiplying costs. I can also explain where those calculations stop short of evidence about real customer behaviour or a change that would work.

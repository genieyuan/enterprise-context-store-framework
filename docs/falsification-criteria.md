# Falsification Criteria

# Falsification criteria

- **Version:** v1
- **Date:** 2026-08-17
- **Covers:** ADR-0001 … ADR-0015, [framework doc-v4](phase-1-framework.md)

> **Why falsification and not acceptance.** Acceptance criteria ask *"did it work?"* — and
> almost any small pilot will appear to work while telling you very little. These ask *"what
> observation would prove this decision wrong?"* Criteria written **before** a run cannot be
> rationalised after it, which is the entire value.
>
> Most of this is not new work. Every ADR already carries a *"What would make us revisit
> this"* section. This document turns that prose into an **observation, a measure, and a
> threshold**.

## How to read the Home column

A candidate validation instance is a **family context store** — iMessage instead of Slack,
household calendar and photos instead of ERP and warehouse.

**Home is a strong falsifier and a weak confirmer.** If topic segmentation cannot separate
"school run logistics" from "holiday planning" across a family's messages, it certainly will
not handle a workspace — that is a real kill signal, cheaply obtained. But a clean run tells
you the mechanism is not broken, **not** that the design is validated, because the parts that
make the enterprise case hard are precisely the parts a family does not exercise.

| Mark | Meaning |
|---|---|
| ✅ | Home tests this well |
| ◐ | Home tests it partially, or needs more elapsed time than a short run allows |
| ❌ | Home **cannot** test this — do not read a green result as evidence |

---

## The criteria

| ADR | Claim | Falsified if… | Measure | Home |
|---|---|---|---|---|
| **0002** Tech-agnostic framework | The framework can be implemented without naming products, and survives tech churn | Implementation repeatedly stalls on decisions the framework should have made but didn't | Count of "the framework doesn't say" blockers per week of build | ✅ |
| **0003** Measure by declared assumptions | Assumption count — especially corrected — is a usable quality signal | Assumption count tracks output length or model verbosity more than actual context gaps; **or** agents silently don't declare at all | (a) Correlation of assumption count with output tokens, task held constant. (b) **Injected-gap test**: withhold a fact you know is needed; does the assumption appear? (c) Declaration rate across agents | ✅ |
| **0004** Preserve originals | Translation is lossy in ways that matter; originals must be kept | Agents perform indistinguishably on nuance-bearing content given translation vs original | A/B same sentiment-heavy content, translated vs original, compare agent judgement | ✅ |
| **0005** Agents only, no human UI | A human interface is unnecessary because humans go through agents | You repeatedly bypass the agent to inspect the store directly | Count of direct-inspection events during build and operation | ✅ |
| **0006** Record ACLs, enforce later | Recording at ingest makes later enforcement possible without re-ingest | Sources cannot supply visibility metadata, so most items record "unknown" | % of ingested items with a known visibility class | ◐ |
| **0008** Value × Volatility | Two independent axes; volatility answers eviction and freshness | The axes are collinear — volatility adds nothing beyond value; **or** ingest-time volatility is uncorrelated with observed decay | (a) Correlation between the two axes across topics — high correlation kills the second axis. (b) Ingest volatility vs observed reuse decay | ◐ |
| **0009** Topics as the unit | Topic-grain rating survives volume; topic identity is stable | Report rate per topic exceeds a trust threshold; **or** the same input segments differently across runs | (a) Reports per topic per week. (b) **Stability test**: segment the same corpus twice, measure assignment agreement | ✅ |
| **0010** Retain all rater scores | Raters genuinely disagree in ways role explains | Inter-rater variance is negligible — a mean would have lost nothing | Variance across raters per topic; does role predict score? | ❌ |
| **0011** One report, free text | Free text beats categories because the taxonomy is unobserved | Reports arrive with empty or useless reasons | % of reports whose reason is non-informative | ✅ |
| **0012** Type entities, typed relations | Aggregated typed relations produce useful business structure; hubs are harmless | Relation vocabulary fragments, surfaced relations are trivially true, relation direction is wrong, provenance is absent, temporal validity is wrong, or errors do not propagate | (a) Label fragmentation and human usefulness. (b) Direction accuracy. (c) Provenance and temporal-validity coverage. (d) Error propagation from source to aggregate | ❌ |
| **0013** Enriches systems of record | Three-layer composition works; routing relations let agents compose | Agents fail to use authoritative routes; instance references cannot be resolved; or the store keeps duplicating authoritative facts to be useful | Route-use and route-resolution rates; unresolved instance-reference rate; duplicate-fact pressure in task traces | ◐ |
| **0014** Two-level, agent-native | Coverage beats ranking for agents; negative space changes agent behaviour | Agents behave identically with and without negative space; coverage-optimised sets do not beat top-k at equal budget; graph/vector invariant or citation paths fail; retries are nondeterministic | (a) A/B negative space. (b) A/B coverage vs ranked. (c) Graph returns scopes/routes/IDs while vector returns permitted evidence. (d) Citation-path accuracy and deterministic retry rate | ✅ |
| **0015** Bootstrap from schema | ERP/warehouse schema gives a usable conceptual baseline | Schema entities are transactional, not conceptual; type/schema binding is poor; or conversation candidates bypass human validation | Schema/conversation overlap; type-binding quality; human-gate pass/reject behavior for conversation-derived candidates | ❌ |

---

## Run these first

Ordered by *"what would most change the design if it failed"*, not by ease.

**1. Negative space A/B (ADR-0014).** The most important test in this document, because
[ADR-0003](adr/0003-measure-context-quality-by-declared-assumptions.md) depends on it. If
telling an agent *"I found nothing about X"* does not change what it does, then negative space
is decoration, the assumption loop has no input, and the measurement the whole design rests on
collapses. Cheap to run, and it invalidates two ADRs at once if it fails.

**2. Injected-gap test (ADR-0003).** Withhold a fact you know is needed and see whether the
assumption surfaces. Direct, immediate, needs no infrastructure beyond a working retrieval
path. Home is ideal because you have ground truth.

**3. Segmentation stability (ADR-0009).** Segment the same corpus twice and measure agreement.
Cheap, deterministic, and topic identity instability would undermine participant routing,
accumulated scores and the report loop simultaneously.

**4. Is the framework implementable (ADR-0002)?** Building anything at all is the test. Every
"the framework doesn't say" moment is a real finding about phase 1's completeness.

---

## Decisions with no real falsifier

is either trivially true or unexamined. Three came out that way, and the honest answer is that
they are a different kind of decision rather than a weak one.

**[ADR-0001](adr/0001-record-architecture-decisions.md) and
[ADR-0007](adr/0007-two-sources-of-truth.md) are process conventions, not claims about the
world.** "Record decisions as ADRs" and "Obsidian for personal, git for collaboration" cannot
be falsified by observation because they do not predict anything. They can only be judged by
whether people follow them. The nearest measurable proxy is **drift** — decisions that happened
are still being followed.

**[ADR-0006](adr/0006-record-source-acls-without-enforcing.md) is a bet, not a hypothesis.**
The claim is that recording ACLs now will be useful later. That cannot be falsified until
"later" arrives. The measure in the table tests something weaker but real — whether the
recording is even *possible* at ingest. If most items record "unknown", the bet is void
regardless of whether it was wise.

## The gap with nothing to falsify

**How external signals earn value has no ADR, and therefore no falsifier.**

Customer feedback attaches to topics, but nothing states how it accrues value — open question
1, open by explicit decision. There is no claim here to disprove, which means this table cannot
tell you whether that half of the system works.

It is left as an empty row on purpose. It is the last gap between doc-v4 and the framework
passing its own definition of done, and it should be uncomfortable to look at.

| ADR | Claim | Falsified if… | Measure | Home |
|---|---|---|---|---|
| *(none)* | *how external signals earn value* | — | — | — |

## Research candidates with no accepted falsifier yet

The following are research inputs and candidate projections only. They are not accepted ADR claims,
do not create ADR-0016 or later, and do not promote Episode projections or Topic facets beyond the
approved Topic canonical unit.

| Candidate | Why it is recorded | Current boundary |
|---|---|---|
| Logs as an additional bootstrap source | Adds observable operational evidence to schema bootstrap | Candidate input; not an accepted source-of-truth change |
| Operational and decision evidence as richer Topic facets | Preserves Topic as the canonical unit while testing richer evidence | Candidate facet shape; not accepted architecture |
| OperationalEpisode / DecisionEpisode projections | Supports future episode-oriented retrieval experiments | Candidate projection only; no accepted canonical unit |
| Proactive delta monitoring | Makes change detection a consuming-agent concern | Candidate consumer behavior; notification remains outside the store |
| Minimum decision-context capture contract | Gives future capture work a bounded field set | Candidate contract; no Phase 1 acceptance claim |

## What this document is not

- **Not a test plan.** No fixtures, no harness, no thresholds tuned to a real dataset. Numeric
  thresholds are deliberately absent because none can be justified before a first run
- **Not acceptance criteria.** Nothing here says the design is right. Everything here says how
  it could be shown wrong
- **Not evidence.** No test below has been run

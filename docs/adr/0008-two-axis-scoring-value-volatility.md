
# ADR-0008: Score context on two axes — Value × Volatility — with reasons

- **Status:** Accepted
- **Date:** 2026-08-17
- **Supersedes:** —

## Context

The store needs a way to decide what to retrieve eagerly, what to keep, and what to evict.
[ADR-0003](0003-measure-context-quality-by-declared-assumptions.md) gives a measure of how
well the store *served a request*, but that is a per-request signal — it does not tell you
what a given piece of context is worth in general.

A single "importance" scalar is the obvious approach and is insufficient: it cannot
distinguish a durable fact about how the company prices things from a highly valuable
statement that was true last quarter and is now misleading.

similar problem with its A8 assessment: two independent 1–10 scores — Urgent × Important —
each with a short reason, routed as a quadrant, with 5 deliberately below threshold and
boundary cases sampled for extra calibration.

## Decision

**Every topic carries two independent 1–10 scores, each with a short reason.**

| Axis | Question |
|---|---|
| **Value** | How much does having this improve an agent's output? |
| **Volatility** | How fast does this go stale? |

Routed as a quadrant:

| | Value 6–10 | Value 1–5 |
|---|---|---|
| **Volatility 1–5** | Core context — index heavily, retrieve eagerly | Cheap to retain, background |
| **Volatility 6–10** | Serve with freshness metadata; re-verify before relying on it | Evict |

Three rules carried over from A8 verbatim in spirit:

- **5 is below threshold.** No fence-sitting
- **Boundary cases (4–6) get extra calibration sampling** — where the model is least reliable
- **Every score carries a reason, including low ones**, so the rejected set is auditable and
  not merely invisible

**Scoring is two-step:** capture raw with no privileged sources → assign an initial score at
ingest → refresh continuously from reuse, recall, and reference by other topics.

**Urgency is not a third axis in v1.** Deferred, not rejected.

## Options considered

### Option A — Value × Volatility  ✅ *chosen*

- **Upside:** Volatility answers a question a single scalar cannot — *what do we evict, and
  what must carry a freshness warning*. Stale context is worse than absent context because it
  is confidently wrong. Both axes are query-independent, so they can be stored rather than
  recomputed per request
- **Cost:** Two numbers to produce and maintain instead of one
- **Risk:** Volatility is hard to assess at ingest; a message's shelf life is often only
  obvious later. The refresh step is what makes this survivable

### Option B — Single importance scalar

- **Upside:** Simplest possible thing
- **Why not chosen:** Cannot separate "valuable and durable" from "valuable but expiring",
  so it cannot drive eviction or freshness warnings

### Option C — Urgent × Important, copied from Life Capture

- **Upside:** Proven shape, already reasoned through, familiar to the decision-maker
- **Why not chosen:** Urgency exists because Life Capture decides whether to interrupt a
  person. This store notifies nobody ([ADR-0005](0005-serve-agents-only.md)), so an urgency
  score would have no consumer. Decision-maker's own assessment: *"i think the urgency still
  apply. but i agree it is hard for agent to assess at the enterprise level"*

### Option D — Score only from observed usage, nothing at ingest

- **Upside:** No guessing; every score is evidence-based
- **Why not chosen:** Cold-start trap. Unscored context is not retrieved, so it is never used,
  so usage-based weighting can never bootstrap

## Consequences

**What gets easier:** Eviction and retention become policy rather than judgement calls.
Freshness warnings become mechanical. Reasons attached to scores make the model's judgement
auditable, so a wrong score is a correctable event rather than an inexplicable one.

**What gets harder:** Volatility must be estimated at ingest, when it is least knowable, and
the estimate will often be wrong. The refresh step carries that weight.

**What we're now committed to:** Reasons stored alongside every score, for low scores too.
Boundary-case sampling as a first-class part of the calibration loop, not an afterthought.

**What would make us revisit this:** Volatility estimates proving so unreliable at ingest that
they mislead more than they help — in which case volatility becomes a purely observed property
(measured decay in reuse) rather than an assessed one. Worth measuring early in phase 2.

## References

- [Phase 1 framework](../phase-1-framework.md) §5

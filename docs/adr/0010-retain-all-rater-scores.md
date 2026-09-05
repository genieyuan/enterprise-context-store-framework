
# ADR-0010: Retain every rater's score; collapse only at retrieval

- **Status:** Accepted
- **Date:** 2026-08-17
- **Supersedes:** —

## Context

A topic is routed to every participant, and each scores it independently
([ADR-0009](0009-topics-as-the-unit-of-context.md)). So a topic typically carries several
Value × Volatility scores that disagree.

The conventional move is to collapse them at write time — store a mean, or a median, and
throw the individual scores away. It keeps the data model simple and gives every downstream
consumer one number to sort by.

It is also irreversible, and it destroys the most interesting thing in the data.

## Decision

**Store every rater's score, reason, and role. Never collapse at write time.**

**Collapse happens at retrieval, relative to the consuming context.** An agent working a
marketing task should weight marketing participants' scores more heavily than IT's; an agent
working an infrastructure task should do the opposite. The consumer's frame determines the
collapse, so the collapse cannot be precomputed.

**Disagreement is retained as signal.** A topic where participants scored 9, 8 and 8 is a
different object from one scored 9, 5 and 2, even though the means are close. The second is
contested or role-dependent, and an agent should be able to know that.

## Options considered

### Option A — Retain all, collapse at retrieval  ✅ *chosen*

- **Upside:** No information destroyed. Role-relative weighting becomes possible, which a
  single stored number forecloses. Disagreement — genuinely useful metadata — survives.
  Consistent with [ADR-0004](0004-preserve-originals-translate-at-consumption.md): preserve
  the original, derive at consumption
- **Cost:** Storage grows with rater count. Retrieval does more work. No single number to sort
  by without deciding *for whom*
- **Risk:** The collapse function becomes a real component with real failure modes, rather
  than a stored integer

### Option B — Collapse to a mean at write time

- **Upside:** Simplest data model; one number everywhere
- **Why not chosen:** Irreversible, and it erases exactly the disagreement that carries
  meaning. Decision-maker: *"different people will have different ways to measure it. While it
  is important for IT, might not be the same for marketing."* A mean asserts a consensus that
  does not exist

### Option C — Store a mean plus a variance

- **Upside:** Cheap disagreement signal without keeping every rater
- **Why not chosen:** Variance says *that* they disagreed, never *who* disagreed or *which
  way* — so role-relative weighting is still impossible. Half the cost, most of the loss

## Consequences

**What gets easier:** Retrieval can serve different consumers different answers from the same
underlying data, honestly. Contested context can be flagged as contested. Rater-level history
supports later work on calibration and drift.

**What gets harder:** There is no universal "importance of this topic" — every answer needs a
frame. That is more truthful and less convenient, and consumers will ask for the single
number anyway.

**What we're now committed to:** Rater identity and role captured with every score, which
carries a privacy dimension that must be revisited alongside the deferred security work
([ADR-0006](0006-record-source-acls-without-enforcing.md)). Individual scores are attributable,
and people rate differently when they know that.

**What would make us revisit this:** Retrieval-time collapse proving too slow at scale. The
fix is a cache of precomputed collapses per common consumer frame — **not** discarding the
underlying scores, which would be the one irreversible move.

## References

- [Phase 1 framework](../phase-1-framework.md) §5
- Open question §7.5 — the collapse function itself is unspecified

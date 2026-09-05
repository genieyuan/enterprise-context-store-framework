
# ADR-0002: Phase 1 delivers a technology-agnostic framework, not an implementation

- **Status:** Accepted
- **Date:** 2026-08-17
- **Supersedes:** —

## Context

The Enterprise Context Store needs to capture signals, store them, and serve them to agents.
There is strong pull toward building immediately — the connectors are well understood and a
working prototype would be satisfying.

The binding constraint is that the underlying technology is moving faster than any
architecture built on top of it. Embedding models, retrieval strategies, agent protocols and
storage engines all have useful lifetimes measured in months. An architecture that names its
components inherits their obsolescence.

There is also no market pressure forcing a build: there is no target market yet, no
customer, and no deadline. That is unusual and worth spending.

## Decision

**Phase 1 produces a framework document and no implementation.** Phase 2 implements that
framework against specific technology, and is expected to be re-implemented against
different technology over time.

The phase 1 framework must describe the system **without naming any product, vendor, model,
database, protocol, or library.**

**Definition of done:** the framework can describe end to end how one internal signal and one
external signal travel from capture, through storage, to consumption by an agent — including
how weight and score are assigned — without naming a product. If it cannot survive that
walkthrough, it is not finished. Phase 2 does not begin before it is met.

## Options considered

### Option A — Framework first, implementation in phase 2  ✅ *chosen*

- **Upside:** Survives technology churn. The expensive thinking is done once. Forces
  articulation of what the system *is* rather than what it's assembled from
- **Cost:** No running code, so no empirical feedback. Delays discovery of ideas that sound
  coherent but don't survive contact with real data
- **Risk:** A framework with no finish line drifts indefinitely — mitigated by the explicit
  definition of done above

### Option B — Prototype first, extract the framework afterwards

- **Upside:** Fast empirical feedback. Reveals problems no amount of writing would
- **Cost:** The framework ends up shaped by whatever the prototype's stack made easy, which
  is exactly the coupling this decision exists to avoid
- **Why not chosen:** With no market pressure, the usual justification for prototype-first
  doesn't apply

### Option C — Build both in parallel

- **Upside:** Feedback without coupling, in theory
- **Why not chosen:** For a team this size it means neither gets finished

## Consequences

**What gets easier:** Re-platforming. When the storage or retrieval layer needs replacing —
easier too: a claim about behaviour can be argued without arguing about a vendor.

**What gets harder:** No empirical validation in phase 1. Some of this framework is going to
be wrong in ways only running code reveals, and we will not find out for a while.

**What we're now committed to:** The repository stays docs-first in the near term. `src/`
remains empty until phase 2 — that's a signal of correctness, not neglect.

**What would make us revisit this:** A concrete customer or deadline appearing; or the
framework passing its definition of done, at which point this ADR has served its purpose and
phase 2 begins.

## References

  the framework, no implementation. phase 2 is implementation using specific tech (it can be
  different techs over time as the tech evolve so fast)"*
- [Phase 1 framework](../phase-1-framework.md) §2

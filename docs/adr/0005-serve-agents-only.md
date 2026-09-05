
# ADR-0005: Serve agents only; no human-facing interface

- **Status:** Accepted
- **Date:** 2026-08-17
- **Supersedes:** —

## Context

Context stores are usually built with two consumers in mind: agents calling an API, and
humans using a search interface. Serving both means every design choice gets made twice —
once for token efficiency and machine parsing, once for readability and browsing.

Those two sets of requirements conflict more than they overlap. Human interfaces want
pagination, snippets, highlighting, ranked lists and progressive disclosure. Agents want
dense, complete, structured payloads with provenance, and no presentation at all.

## Decision

**The only consumer is an agent.** There is no human-facing search, browse, or dashboard.

A human who needs context goes **through an agent**, which retrieves and assembles it for
them. The output format is whatever is most efficient for an agent to consume — not what
reads nicely to a person.

## Options considered

### Option A — Agent-only  ✅ *chosen*

- **Upside:** One consumer, one contract, one format. No UI to build or maintain. Every
  request flows through an agent, so every request produces the declared assumptions that
  [ADR-0003](0003-measure-context-quality-by-declared-assumptions.md) depends on
- **Cost:** No way for a human to inspect the store directly. Debugging and trust-building
  are harder — "why did it return that?" requires tooling that doesn't exist yet
- **Risk:** Early-phase opacity. If the store returns something odd, diagnosis means going
  through an agent

### Option B — Agent API plus a human search UI

- **Upside:** Humans can inspect, verify and build confidence directly
- **Cost:** Two contracts to maintain; UI work competing with core work; and human queries
  bypass the assumption loop, so a chunk of usage produces no learning signal
- **Why not chosen:** The cost is immediate and the benefit is mostly reassurance

### Option C — Agent-only, plus a thin internal debug view

- **Upside:** Keeps one product contract while making diagnosis tractable
- **Why not chosen for phase 1:** Phase 1 builds nothing at all. Worth reconsidering at the
  start of phase 2 as an internal tool rather than a product surface

## Consequences

**What gets easier:** The serve contract is designed for exactly one consumer and can be
optimised without compromise — dense payloads, structured provenance, staleness metadata, no
presentation concerns. All usage flows through the agent path, so the learning loop sees
everything.

**What gets harder:** Human inspection. Nobody can look directly at what the store holds,
which will be uncomfortable early and will make trust slower to build.

**What we're now committed to:** No presentation logic in the store. Any human-readable
rendering — including translation, per
[ADR-0004](0004-preserve-originals-translate-at-consumption.md) — belongs to the consuming
agent, not to the store.

**What would make us revisit this:** Debugging in phase 2 proving impractical without direct
inspection. The likely answer is an internal debug tool (Option C), not a product surface —
the distinction matters, because a debug view that becomes a product re-introduces the second
contract this decision exists to avoid.

## References

  be just agent, no human. if Human needs the info, they can access through an agent and it
  will assemble it. The output format should be whatever is easier for Agent"*
- [Phase 1 framework](../phase-1-framework.md) §3.3


# ADR-0011: Corrections are a single report action with a free-text reason

- **Status:** Accepted
- **Date:** 2026-08-17
- **Supersedes:** —

## Context

[ADR-0009](0009-topics-as-the-unit-of-context.md) makes topic segmentation load-bearing *and*
user-visible: a misfiled topic appears in someone's queue, and a queue that regularly contains
things people don't recognise is a queue they stop opening. Segmentation will be wrong early,
so a correction path is not optional.

The obvious design is a structured one — separate actions for *I wasn't part of this*, *this
doesn't belong together*, *this should be split*, *these should be merged* — because each
implies a different repair, and structured input can drive automated repair.

The problem is that this taxonomy is invented rather than observed. Nobody has yet run this
system, so nobody knows which failures actually occur or in what proportion. A category set
designed in advance will be wrong in the usual way: the common case won't have a button, and
half the buttons will go unused.

## Decision

**One report action, with a required free-text reason.**

No categories. Whatever the person means — *this doesn't belong*, *I don't recognise this*,
*this is two different things* — goes in the text box in their own words.

**"I don't remember this" is not by itself grounds for removal.** The expectation is that the
person checks the source before reporting. The card therefore **must link back to the source
thread**, not merely quote it — if we are asking people to go and check, that has to be one
tap or they will report instead, because reporting is cheaper.

**Reports are evidence, not automatic repair.** In v1 they accumulate against the topic and
inform the next segmentation pass. The graph does not self-heal from a single report.

actions are recorded as events and reversed by compensation, never by mutation.

**The taxonomy will be derived, not designed.** Once there is a body of real reports, the
categories that actually occur can be extracted and structured. That is a v2 decision informed
by data, not a v1 decision informed by imagination.

## Options considered

### Option A — One report, free-text reason  ✅ *chosen*

- **Upside:** Cannot be wrong about a taxonomy we haven't observed. Lowest friction, so it
  gets used. The prose is richer than any category — it says *why*, not just *which bucket*.
  Consistent with the framework's own no-predefined-schema stance
- **Cost:** Cannot mechanically drive repair; a human or model must read it. Analysis is
  needed before the reports become actionable in bulk
- **Risk:** Free text is easy to leave empty-ish ("wrong"). Mitigated by requiring the field —
  Life Capture A9's *"overrides strongly prompt for a reason"*

### Option B — Structured categories (not mine / doesn't belong / split / merge)

- **Upside:** Machine-actionable. Routing could be adjusted automatically from *not mine*
- **Why not chosen:** The categories are guesses. Decision-maker also rejected the premise of
  the *not mine* button outright: *"while they cannot remember, they should go back to their
  slack, this is not an excuse."* A button that legitimises not-remembering encourages the
  behaviour it should discourage

### Option C — Structured categories plus free text

- **Upside:** Best of both, in theory
- **Why not chosen:** Still bakes in an unobserved taxonomy, and people pick the first
  plausible category and skip the text. The structure crowds out the prose that is currently
  the more valuable half

## Consequences

**What gets easier:** Shipping. There is no category design to argue about, and the mechanism
cannot be wrong about a distinction that doesn't exist yet. Reports carry reasoning, which is
the same gold-signal class as a corrected assumption in
[ADR-0003](0003-measure-context-quality-by-declared-assumptions.md) — expensive to fake,
because faking it means doing the work.

**What gets harder:** No automated repair loop in v1. Reports must be read before they change
anything, so the graph improves in batches rather than continuously. The *not mine* versus
*genuinely misfiled* distinction still exists — it has moved from a button into prose, where a
model must infer it. That is a deliberate trade: less friction now, inference cost later.

**What we're now committed to:** A source deep-link on every card, since the decision to
reject "I don't remember" as sufficient grounds depends on checking being trivial. Append-only
retrofitting undo onto mutations means the history needed to reverse them was never recorded.

**What would make us revisit this:** A body of reports showing a small number of dominant,
cleanly separable failure modes — at which point structuring the top two or three is worth it,
with free text retained for everything else.

## References

- Life Capture A9 — *"overrides strongly prompt for a reason"*, *"Every action supports Undo
  and is idempotent"*
- [Phase 1 framework](../phase-1-framework.md) §5
- Open question §7.2 supersedes into this ADR; §7.3 (cross-thread continuity) remains open

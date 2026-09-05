
# ADR-0001: Record architecture decisions in this repo

- **Status:** Accepted
- **Date:** 2026-08-15
- **Supersedes:** —

## Context

This repository will accumulate design decisions about the Enterprise Context Store —
storage model, retrieval strategy, tenancy boundaries, embedding choices, freshness
guarantees. Most of those are expensive to reverse once code depends on them.

The failure mode we're guarding against is well known: six months in, someone asks "why is
it built this way?" and nobody remembers. The reasoning existed — it just lived in a chat
thread, a call, or one person's head. Without it, the team either re-litigates settled
questions or, worse, treats an accidental choice as sacred because nobody knows it was
accidental.

We are a small team. Any process heavier than "write it down" will not survive contact
with a busy week.

## Decision

We will record every decision that is expensive to reverse as an Architecture Decision
Record in `docs/02-design/adr/`, using the format described by Michael Nygard.

- One file per decision, numbered sequentially: `NNNN-short-slug.md`.
- Copy [`TEMPLATE.md`](TEMPLATE.md) to start.
- The pull request discussion is the decision process; merging is the decision being made.
- **Merged ADRs are immutable.** To change a decision, write a new ADR that supersedes the
  old one, and edit the old one's status line to point at its replacement.

"Expensive to reverse" is the bar. Choosing a variable name is not an ADR. Choosing a
vector database is.

## Options considered

### Option A — ADRs in the repo  ✅ *chosen*

  we already use. Diffable, searchable, and there when someone clones the repo.
- **Cost:** Someone has to write the thing. Roughly 20 minutes per decision.

### Option B — Decisions in a wiki or Notion

- **Upside:** Nicer editing, easier for non-technical contributors.
- **Why not chosen:** The decision and the code it constrains belong in the same history.

### Option C — Do nothing; rely on PR descriptions and memory

- **Upside:** Zero overhead.
- **Why not chosen:** This is the status quo that produces the "why is it like this?"
  problem. PR descriptions are not findable six months later, and memory is not a record.

## Consequences

**What gets easier:** Onboarding — a new contributor can read `docs/02-design/adr/` in
order and understand how we got here. Reopening a decision becomes a legitimate, low-drama
act: you write ADR-0012 superseding ADR-0004.

**What gets harder:** Every significant decision now costs ~20 minutes of writing. That is
the point; if a decision isn't worth 20 minutes, it probably wasn't significant.

**What we're now committed to:** Keeping the numbering sequential, and never editing a
merged ADR's substance. The wrong turns stay visible — knowing what we rejected, and why,
is most of the value.

**What would make us revisit this:** If we hit ~30 ADRs and can no longer find things, we
add an index. If the team grows past ~8 people, we may need a lighter fast-lane for
reversible decisions.

## References

- Michael Nygard, *Documenting Architecture Decisions* (2011) — the original format.
- [`CONTRIBUTING.md`](../../../CONTRIBUTING.md) — how ADRs fit the PR workflow.


# ADR-0007: Obsidian is the source of truth for personal work; git for collaboration

- **Status:** Accepted
- **Date:** 2026-08-17
- **Supersedes:** — (scopes [ADR-0001](0001-record-architecture-decisions.md); does not replace it)

## Context

Work on this project starts as thinking — notes, drafts, links across unrelated projects —
argue with, or build on it.

and a single place everyone agrees is current.

Trying to serve both from one system fails in a predictable direction. Git-only means
collaborators cannot see the truth they are supposed to be working against, and every
contribution needs manually merging back — a two-way sync that will drift the first busy week.

[ADR-0001](0001-record-architecture-decisions.md) asserted that the PR discussion is the
decision process and merging is the decision being made. That remains right for collaborative
artefacts, but it never addressed where thinking lives beforehand.

## Decision

**Two sources of truth, scoped by audience.**

| Content | Truth | Why |
|---|---|---|

**The promotion flow:**

```
   ▲                                            │
   └──────── rejected / changed ────────────────┘
             take the status back and rework
```

- Work is drafted in Obsidian
- It is promoted to git **as a pull request** — including the repository owner's own changes.
  Nobody pushes to `main` directly
- Once merged, the git copy is canonical for that artefact
- If a proposal is not accepted, its status returns to Obsidian and is reworked there

**There is no obligation to sync git back into Obsidian.** A merged contribution is already
derivative, never authoritative.

## Options considered

### Option A — Two truths scoped by audience  ✅ *chosen*

- **Upside:** Each system does what it is good at. Removes the two-way sync problem entirely:
  collaborative content is canonical in git, so nothing needs merging back. Thinking stays
  frictionless
- **Cost:** Two places to look. Requires discipline about which mode a document is in
  copy as *unpromoted* rather than *drifted* — divergence is a signal to publish, not an error

### Option B — Git as the single source of truth

- **Upside:** One place, unambiguous
  written down at all — which is precisely the context-loss this project exists to solve


- **Upside:** One authoritative home for the owner
- **Why not chosen:** Collaborators cannot see the truth they are working against, and every
  contribution requires a manual merge back into a system they have no access to. That
  round-trip is the part that breaks first

## Consequences

**What gets easier:** Collaborators work against git and their merged work is immediately
authoritative — no merge-back queue, no drift backlog. Thinking has a home with no ceremony.

**What gets harder:** Two places to look, and a judgement call each time about which mode a
document is in. Tooling that can only reach one of them is only half useful — see below.

**What we're now committed to:**

- `main` is protected by convention: **all changes arrive by PR, the owner's included**
- Any tool or agent expected to work on personal-truth content **must be able to read the
  inherits that grant. This is an operational constraint, not a preference

**What would make us revisit this:** The team growing past a couple of people, at which point
genuine bottleneck for collaborators who keep needing content that hasn't been promoted.

## References

- Decision-maker, verbatim: *"Obsidian is my truth. Git is the truth for collaboration"* and
  *"will go through a PR. as i mentioned. Obsidian is the source of truth of my works. if it
  is not accepted by other parties, then we will take the status and work on it again."*
- [ADR-0001](0001-record-architecture-decisions.md) — scoped, not superseded

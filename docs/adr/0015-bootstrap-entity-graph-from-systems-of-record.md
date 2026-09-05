
# ADR-0015: Bootstrap the entity graph from ERP and warehouse schema; enrich from conversation

- **Status:** Accepted
- **Date:** 2026-08-17
- **Refines:** [ADR-0012](0012-type-level-entities-and-typed-relations.md) — which established
  type-level entities and derived relations, but not where the initial entity set comes from

## Context

[ADR-0012](0012-type-level-entities-and-typed-relations.md) left two problems open, and they
turn out to be the same problem.

**Cold start.** Deriving every entity from conversation means the graph begins empty and
noisy. Early relations are extracted with no vocabulary to anchor them, so `customers`,
`clients` and `accounts` arrive as three entities for one concept.

**Binding.** [ADR-0013](0013-context-store-enriches-systems-of-record.md) puts the context
store alongside systems of record. If `customers` in the store and the `Customer` dimension in
the warehouse are independently derived, something has to join them — and any mapping layer is
brittle, drifts, and starts to look like the ontology the
[prior-art survey](../../01-research/2026-08-17-context-graph-prior-art.md) found kills these
projects.

ADR-0012 also recorded a consequence honestly: a derived type-level layer **is** an ontology,
just an unwritten one, so the survey's decay warning still applied to us.

## Decision

**Bootstrap the entity and relation baseline by scanning the schemas and relationships already
present in the warehouse and ERP.** Simple and solid: the entities the business actually
operates on, and the relations its systems already encode.

**Then enrich from conversation.** Each dialogue can add relations between existing entities,
and can introduce entities the systems of record have no concept of — a new initiative, an
emerging process, a concern that has no table.

**Human validation gates entity creation.** New entities derived from conversation require
human confirmation before entering the baseline. *The mechanism is not yet designed — this is
an explicit placeholder, see open questions.*

### Why this resolves both problems at once

**Binding disappears for the baseline.** An entity derived *from* the `Customer` dimension
**is** that dimension. There is nothing to map, because it never diverged. Only
conversation-introduced entities need binding, and those are precisely the ones with no
counterpart to bind to.

**The ontology decay problem moves to its rightful owner.** The ERP schema is maintained by
whoever maintains the ERP, and it is ground truth by definition — the business runs on it. We
inherit a live, maintained ontology instead of authoring one that decays. This directly
addresses the consequence recorded in ADR-0012.

**Vocabulary gets an anchor.** Conversation-derived relations attach to entities that already
have canonical names, which reduces the fragmentation risk ADR-0012 flagged.

## Options considered

### Option A — Bootstrap from schema, enrich from conversation, human-gated creation  ✅ *chosen*

- **Upside:** Solves cold start and binding together. Inherits a maintained ontology at zero
  authoring cost. Anchors relation vocabulary. Starts from what the business demonstrably
  operates on rather than what it happens to talk about
- **Cost:** Requires schema access to ERP and warehouse before anything works. Human validation
  is an unbuilt mechanism and a workflow dependency
- **Risk:** ERP schemas encode *transactional* structure, which is not always the structure
  people reason in. The baseline may be technically correct and conceptually foreign

### Option B — Derive everything from conversation

- **Upside:** No dependency on external systems; entities reflect how people actually talk
- **Why not chosen:** Cold start, no vocabulary anchor, and an unsolved binding problem to the
  systems of record

### Option C — Predefined entity taxonomy authored for the domain

- **Upside:** Clean, consistent, controllable
- **Why not chosen:** This is the ontology tax the survey found to be a leading cause of
  failure — decaying from the day it ships, and unknowable before the data exists

### Option D — Bootstrap from schema, no human gate on new entities

- **Upside:** Fully automatic; no workflow dependency
- **Why not chosen:** Entity creation is the highest-leverage and least reversible act in the
  graph. An entity wrongly created accretes relations and topics around it and is expensive to
  unpick later

## Consequences

**What gets easier:** The graph starts useful rather than empty. Entities bind to systems of
record by construction. The maintained-ontology problem is largely someone else's.

**What gets harder:** Phase 2 needs read access to ERP and warehouse schemas before any of it
works, which is an organisational dependency as much as a technical one. And a human approval
step now sits in the ingestion path — if nobody performs it, entity creation stalls and the
graph silently stops growing.

**What we're now committed to:** Schema access as a precondition. A distinction, maintained
throughout, between **baseline entities** (from systems of record, bound, authoritative) and
**derived entities** (from conversation, human-gated, unbound). And a human validation
mechanism that does not yet exist.

**What would make us revisit this:** ERP schemas proving conceptually unusable — encoding
transactional structure people never reason in. The fallback is to use the schema as a
*vocabulary hint* for conversation-derived extraction rather than as the baseline itself.

## References

- Decision-maker: *"to start, we can scan the warehouse and ERP relationship to form a
  baseline. a simple and solid one. Then for each conversation, dialogue, we should be able to
  derive more relationship between different entity. However, we certainly should have a way
  for human to put in their validation for entity creation"*
- Open question: the human validation mechanism — [framework §7](../phase-1-framework.md)


# ADR-0012: Topics carry type-level entities; links are typed relations aggregated across topics

- **Status:** Accepted
- **Date:** 2026-08-17
- **Refines:** [ADR-0009](0009-topics-as-the-unit-of-context.md) — which established topics as
  the unit and said "link related topics", without specifying what a link *is*. This ADR
  specifies it. Not a reversal

## Context

[ADR-0009](0009-topics-as-the-unit-of-context.md) left the linking mechanism unspecified.
Left as-is, the only available signal is semantic similarity between topics, which produces
**co-occurrence edges** — and the
[prior-art survey](../../01-research/2026-08-17-context-graph-prior-art.md) found those
reported consistently as cheap and low-value.

The survey also found that **every architecture that works has an entity layer.** GraphRAG,
LightRAG, HippoRAG and PathRAG all build on entities;
[DyG-RAG](https://arxiv.org/abs/2507.13396) — our closest analogue, since its Dynamic Event
Units accrete over time much as our topics do — links its units by *shared entities plus
temporal proximity*, not by similarity.

But the goal here is not theirs. Those systems answer instance-level factual questions:
*which customer complained about the thing Alice shipped in Q2*. What we want is the shape of
the business — how customers, suppliers and processes actually relate inside this
organisation, learned from its own conversations.

## Decision

**Each topic carries multiple related entities, and entities are types, not instances.**

`customers`, `suppliers`, `pricing`, `onboarding` — **not** customer A and customer B.

**The graph derives how entities relate.** Relations are not predefined. They are extracted
per topic and **aggregated across topics**, so a relation gains weight from recurrence.

**Topics do not link to each other directly. They link through typed entity relations.** The
question *"what does a link between two topics mean?"* is answered: it means those topics
contribute evidence to the same entity relation.

**The graph's output is a learned map of business relationships and processes** — not an index
for factual lookup.

### The hub problem, and why relations rather than nodes

Type-level entities are **low-cardinality and high-frequency**. `customers` may appear in most
topics. If topics linked because they *share* an entity, that entity would become a hub
connected to nearly everything, and a link through it would carry almost no information. This
is the standard reason the field uses instance-level entities: they are selective, and type
entities are not.

**The value therefore lives in the typed relation, aggregated, not in the shared node.**

Not: *"these two topics both mention customers."*
But: *"across 40 topics, `customers` → `complain about` → `onboarding`."*

The edge carries the business fact; the node is only an anchor. Traversal follows relations,
never co-mentions, so hub-ness becomes harmless — high degree on `customers` is expected and
uninformative by itself, while a specific relation with weight is the finding.

## Options considered

### Option A — Type-level entities, typed relations aggregated across topics  ✅ *chosen*

- **Upside:** Gives edges something real to key on. Produces business-structure insight
  directly — the relation *is* the finding. Avoids instance-level entity resolution, which the
  survey identifies as GraphRAG's acknowledged weak point. Low node count keeps the graph small
- **Cost:** Relation extraction per topic is an LLM task, with the usual cost and error modes.
  Aggregation needs weighting and a confidence notion
- **Risk:** Relation vocabulary drifts — `complain about` and `raise issues with` may be
  extracted as different relations for the same fact, fragmenting the evidence

### Option B — Instance-level entities, as in the prior art

- **Upside:** Selective, well-trodden, supports multi-hop factual QA, and every reference
  implementation works this way
- **Why not chosen:** Answers a question we are not asking. Also drags in entity resolution
  across sources, which [ADR-0009](0009-topics-as-the-unit-of-context.md) keeps out of scope
  and which the survey flags as a known weak point

### Option C — No entity layer; link topics by semantic similarity

- **Upside:** Cheapest; nothing to extract
- **Why not chosen:** Produces co-occurrence edges. The survey found no successful architecture
  doing this, and reports such edges as low-value

### Option D — Predefined entity types and relation vocabulary

- **Upside:** No drift; consistent extraction; machine-checkable
- **Why not chosen:** This is the ontology the survey found kills projects — decaying from the
  day it ships, and unknowable before the data exists. Deriving it is the documented survivor
  strategy

## Consequences

**What gets easier:** Topic links become meaningful and explainable — *"these topics are
connected because they both evidence customers→onboarding"* is inspectable in a way that a
similarity score is not. The graph answers the question in
[ADR-0009](0009-topics-as-the-unit-of-context.md)'s own terms: it now produces business
structure, not just organised conversation.

**What gets harder:** Two LLM extraction steps at ingest rather than one — topics *and* the
entity relations within them. Relation aggregation needs a weighting and confidence model that
does not yet exist.

**What we're now committed to:** Relation vocabulary control **without** a predefined
ontology — some normalisation so `complain about` and `raise issues with` converge, derived
rather than declared. This is the direct analogue of the entity-resolution problem we avoided,
displaced onto relations, and it should be watched.

Also committed: a derived type-level layer **is** an ontology, just an unwritten one. The
survey's decay warning still applies. **Re-derivation must be designed, not assumed** — the
layer has to be rebuildable from preserved originals, per
[ADR-0004](0004-preserve-originals-translate-at-consumption.md).

**What would make us revisit this:** Relation extraction proving too noisy to aggregate
usefully — in which case the fallback is entity co-occurrence with relations demoted to an
advisory label, which is Option C with better provenance. Or a genuine need for instance-level
questions appearing, which would mean adding a second entity layer rather than replacing this
one.

## References

- [Context graph prior art](../../01-research/2026-08-17-context-graph-prior-art.md) §3, §6
- Decision-maker, verbatim: *"each topic should have multiple entity related. The graph should
  decide how the entities are related. in this case, we are not talking about customer A and
  customer B as two entities, we are talking about customers and suppliers are two entities."*

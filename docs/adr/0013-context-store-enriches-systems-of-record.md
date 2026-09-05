
# ADR-0013: The context store enriches systems of record and never asserts what they own

- **Status:** Accepted
- **Date:** 2026-08-17
- **Supersedes:** —

## Context

The context store is not the only place an agent gets information, and treating it as though
it were produces two failure modes: a shadow data warehouse that drifts from the real one, and
a conflict-resolution problem that should never have existed.

An enterprise already has systems of record — ERP, operational databases, applications, data
warehouse / lake / lakehouse. They hold **facts**: customer records, order status, inventory,
the sales hierarchy. They have schemas, referential integrity, and owners.

What they cannot supply is why the facts look the way they do. An ERP reports that order
volume in a segment fell 20%. It has no way to know that three weeks ago, in a Slack thread,
someone decided to deprioritise that segment. An agent reading the number without that context
reaches a confident and wrong conclusion.

**That gap is the entire reason this project exists.**

## Decision

**Three layers, with the context store as the interpretive layer over the other two.**

| Layer | Holds | Owner |
|---|---|---|
| **Systems of record** — ERP, apps, DB, warehouse/lake | Facts. Instances. Order status, customer records, inventory | The business's existing systems |
| **Context store — graph** | Type-level entities and their relations, including **which system is authoritative for which fact** | This project |
| **Context store — content** | The human layer: discussions, decisions, meeting outcomes, directions, ideas | This project |

**The store never asserts a fact a system of record owns.** Not order status, not inventory,
not customer details. If it has a schema and a system of record, it is not context store
material.

**Instead, the graph records which system is authoritative for which entity**, so the agent
can route. `order status → is held by → ERP system A` is a relation like any other.

**There is therefore no precedence rule and no conflict resolution**, because the two layers
never assert the same thing. The store supplies *where to look* and *why it happened*; the
system of record supplies *what is true*.

### The worked example

An agent asks why an order was cancelled.

1. The graph says order records live in ERP system A → the agent retrieves the status there
2. The store surfaces a meeting two days ago between the customer and a sales rep
3. The agent retrieves that meeting's detail and finds the words the sales rep used
4. The agent now holds both the fact and its cause

Neither layer could produce that answer alone, and neither had to overrule the other.

## Options considered

### Option A — Three layers; the store enriches and routes, never asserts  ✅ *chosen*

- **Upside:** No duplication, so no drift. No conflict-resolution policy needed. The store
  stays small and stays about the thing nothing else captures. Routing information is exactly
  what an agent needs and nothing else holds it
- **Cost:** The store must know which systems exist and what they own — a real dependency on
  the enterprise's landscape
- **Risk:** If the routing relations are wrong or stale, agents are sent to the wrong place,
  which is worse than sending them nowhere

### Option B — Context store as a superset, ingesting operational data too

- **Upside:** One place to ask; no routing needed
- **Why not chosen:** Produces a worse copy of the ERP that drifts, and inherits every
  freshness and correctness obligation the source already meets. This is where "context layer"
  projects commonly end up

### Option C — Two independent layers, with a precedence rule on conflict

- **Upside:** Simple to state — systems of record win on facts, the store wins on intent
- **Why not chosen:** The premise is wrong. The conflict only arises if the store asserts facts
  it should never have asserted. Decision-maker, on a proposed ERP-vs-Slack conflict: *"I dont
  think this example make sense… the context store should not answer those question"*

## Consequences

**What gets easier:** The store's scope has a checkable boundary. Retrieval composes across
layers instead of competing with them. A whole class of conflict-resolution design disappears.

**What gets harder:** The store now needs a view of the enterprise's system landscape — what
exists and what each owns. That is a dependency on something outside itself, and it can go
stale.

**What we're now committed to:** *Authoritative-for* is a first-class relation in the graph,
maintained like any other. The store must be able to say **"I don't hold that, ask system X"**
as a normal response, which makes it part of the retrieval contract in
[ADR-0014](0014-two-level-agent-native-retrieval.md), not an error case.

**What would make us revisit this:** An enterprise with no usable systems of record, where the
store would have to hold operational facts to be useful at all. That is a different product
and should be recognised as one rather than absorbed.

## References

- [ADR-0012](0012-type-level-entities-and-typed-relations.md) — the type/instance split now
  has a structural reason: instance identity already has an owner
- [Phase 1 framework](../phase-1-framework.md) §3

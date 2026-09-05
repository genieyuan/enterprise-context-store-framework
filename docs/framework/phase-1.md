# ECS Phase 1 Framework

This document defines the normative, technology-agnostic Phase 1 framework. It is a design contract, not an implementation or deployment guide.

# Enterprise Context Store — Phase 1 Framework

- **Version:** doc-v4 — positions the store as the interpretive layer over systems of record
  (§3.0), and specifies retrieval as an agent-native contract (§3.3). doc-v3 described the
  store as if it were the agent's only source, and described serving as if a human read it
- **Date:** 2026-08-17
  Primary source: [2026-08-12 founding discussion](../01-research/2026-08-12-founding-discussion-context-store.md)

> Navigation: [reference architecture](reference-architecture.md) · [falsification criteria](falsification-criteria.md) · [annotated research set](../01-research/2026-08-19-context-graph-reference-set.md)

## Security tier — read this first

**Tier: none. Phase 1 handles no data.** This phase produces a framework document, not a
running system. Exposure is zero because nothing is deployed and nothing is ingested.

Phase 2 will handle enterprise-internal communications and is expected to be **Tier 2 —
internal confidential, single-tenant**. Its threat model is deliberately **not** in scope
here, with one exception carried forward as a hard constraint: see
[ADR-0006](adr/0006-record-source-acls-without-enforcing.md).

---

## 1. The problem

Enterprises want to adopt AI. AI that has not been given an enterprise's context can only
work from public knowledge, so it produces generic output that fails on delivery. The gap
is not model capability. It is that almost nothing inside an enterprise is in a form an AI
can read, and nobody knows which parts it should have been given.

From the founding discussion (00:04:42):

> 在很多情况下，我们看到 AI 的表现不好，是因为根本没有给它 AI 应该要知道的东西
>
> *In many cases AI performs badly simply because it was never given the things it needed
> to know.*

### The paradox this project has to answer

The discussion kept hitting the same wall (00:06:21, 00:16:58, 00:18:21): if the system
knows what context is missing, it already has that context — so why is a human needed at
all? And if it doesn't know, how can it ever ask?

**The resolution is that the system never detects absence. It observes what it invented.**
An agent doing real work has to make assumptions to finish. Those assumptions are gaps that
have already revealed themselves. You don't need to know what's missing in advance; you
need to know what got made up. This is much cheaper to know, and *"is this assumption
right?"* is a far easier question to put to a domain expert than *"what context should you
have given me?"*

This single move is what makes the rest of the system tractable. See
[ADR-0003](adr/0003-measure-context-quality-by-declared-assumptions.md).

## 2. What phase 1 is

**Phase 1 delivers a framework. It delivers no implementation.**

Phase 2 implements it against specific technology — and that technology is expected to
change repeatedly, because the field moves faster than any architecture built on top of it.
The framework must therefore describe the system **without naming a single product,
vendor, model, database, or protocol**. See
[ADR-0002](adr/0002-phase-1-is-a-technology-agnostic-framework.md).

### Definition of done

The framework is complete when it can describe, end to end, how **one internal signal** and
**one external signal** travel from capture, through storage, to consumption by an agent —
including how weight and score are assigned along the way — **without naming a product.**

If it cannot survive that walkthrough, it is not yet a framework. This is the exit
condition; phase 2 does not begin before it is met.

## 3. Shape of the system

### 3.0 Where the store sits — three layers

**The context store is not the only place an agent gets information, and it must not behave as
though it were.** See [ADR-0013](adr/0013-context-store-enriches-systems-of-record.md).

```
        ┌──────────────────────────────────────────────────────────┐
        │  AGENT                                                   │
        └───┬──────────────────────────┬───────────────────────────┘
            │ 1. what relates to what  │ 3. the facts themselves
            │    who owns which fact   │
   ┌────────▼─────────┐       ┌────────▼──────────────────────────┐
   │  CONTEXT STORE   │       │  SYSTEMS OF RECORD                │
   │  ┌────────────┐  │       │  ERP · apps · operational DB      │
   │  │   graph    │  │       │  warehouse / lake / lakehouse     │
   │  │ entities + │  │       │                                   │
   │  │ relations  │──┼──────▶│  facts · instances · order status │
   │  └─────┬──────┘  │ routes│  customer records · inventory     │
   │  ┌─────▼──────┐  │  to   └───────────────────────────────────┘
   │  │  content   │  │
   │  │ topics —   │  │  2. why the facts look like that
   │  │ the human  │  │     discussions · decisions · meetings
   │  │   layer    │  │     directions · ideas
   │  └────────────┘  │
   └──────────────────┘
```

An ERP reports that order volume in a segment fell 20%. It cannot know that three weeks ago,
in a Slack thread, someone decided to deprioritise that segment. An agent reading the number
without that context reaches a confident and wrong conclusion. **Closing that gap is the whole
purpose of this system.**

Two rules follow:

- **The store never asserts a fact a system of record owns.** If it has a schema and a system
  of record, it is not context store material
- **The graph records which system is authoritative for which fact**, so the agent can route.
  `order status → is held by → ERP system A` is a relation like any other

There is therefore **no precedence rule and no conflict resolution** — the layers never assert
the same thing.

**Worked example — why was this order cancelled?**

1. Graph: order records live in ERP system A → the agent retrieves the status there
2. Store: surfaces a meeting two days ago between the customer and a sales rep
3. Agent: retrieves that meeting's detail, finds the words the sales rep used
4. Agent: now holds both the fact and its cause

Neither layer could produce that answer alone, and neither had to overrule the other.

### The lifecycle stages inside the store

The canonical lifecycle is **Capture → Compile → Serve → Continuous Learning**, with
Governance & Trust cross-cutting. The store is the system being built; Compile is its
interpretive stage, not a separate storage stage.

```
   CAPTURE                  COMPILE                    SERVE
   ────────                 ───────                    ─────
   internal signals  ──┐                          ┌──▶ agent sends task
   (work happening)    │    ┌──────────────┐      │    + token budget
                       ├───▶│  raw, as-is  │──────┤
   external signals  ──┘    │  + derived   │      └──▶ found  + NOT-found
   (customer voice)         │    layers    │           + provenance
                            └──────┬───────┘           + staleness
                                   │
                            ┌──────▼───────┐
                            │ recurring    │  reweights by reuse/recall
                            │ self-learn   │  tags valuable assets
                            └──────────────┘  consumes corrected assumptions
```

### 3.1 Capture

**Only what humans have already produced.** The store does not conduct interviews, does not
run elicitation, and does not manufacture knowledge that does not yet exist. That capability
is attractive and is recorded as a future phase — it is not phase 1.

Two reference signal types, deliberately different in shape:

| | Internal | External |
|---|---|---|
| **Example** | Slack public channels (or email) | Customer feedback from a social feed |
| **Represents** | the inside view — what the business says about itself | the outside view — what customers experience |
| **Character** | conversational, high volume, implicit | unstructured, sentiment-bearing, adversarial to summarise |

The pairing is the point. Together they support a question neither answers alone: **does
what we say internally match what customers actually experience?** External signals must be
labelled as external — clearly and structurally, not by convention.

**Nothing is privileged at capture.** No preference, no weighting. Everything arrives flat.

### 3.2 Compile

**The store is a context graph whose nodes are topics, not a pile of documents.**

Ingestion runs over an interval — the delta from a source across a window (24h, or shorter;
the interval is a tuning parameter, not a fixed property). For each batch:

1. Segment the raw conversation into **topics**
2. Attach each segment to an **existing topic** where one fits; otherwise create a new one
3. Extract the **type-level entities** each topic concerns, and the **typed relations**
   between them
4. **Aggregate those relations across topics**, so a relation gains weight from recurrence

Topics are durable and accrete over time: a discussion resumed three weeks later lands on the
same node. This is what makes the store queryable by *subject* rather than by *document*, and
it is also the unit at which humans rate context — see §5.

#### Entities and links

**Entities are types, not instances** — `customers`, `suppliers`, `pricing`, `onboarding`;
not customer A and customer B. See
[ADR-0012](adr/0012-type-level-entities-and-typed-relations.md). Instance identity already has
an owner — the systems of record (§3.0) — so duplicating it would produce a worse copy that
drifts.

**The entity baseline is bootstrapped from ERP and warehouse schema**, then enriched from
conversation. See [ADR-0015](adr/0015-bootstrap-entity-graph-from-systems-of-record.md).

This solves two problems at once. Binding disappears for baseline entities: one derived *from*
the `Customer` dimension **is** that dimension, so there is nothing to map. And the ontology
decay problem moves to its rightful owner — the ERP schema is maintained by whoever maintains
the ERP, and the business demonstrably runs on it, so we inherit a live ontology instead of
authoring one that rots.

Conversation adds relations between existing entities, and can introduce entities the systems
of record have no concept of — a new initiative, an emerging process, a concern with no table.
**New entities from conversation are human-gated**; the validation mechanism is an open
question (§7).

**Topics do not link to each other directly. They link through typed entity relations.** Two
topics are connected because they contribute evidence to the same relation.

The value is in the **aggregated relation**, not the shared node. Not *"these two topics both
mention customers"* — type entities are high-frequency, so shared-entity links would connect
almost everything to almost everything and mean nothing. Instead: *"across 40 topics,
`customers` → `complain about` → `onboarding`."* The edge carries the business fact; the node
is only an anchor.

**So the graph's output is a learned map of business relationships and processes**, derived
from the organisation's own conversations — not an index for instance-level factual lookup.

Relation vocabulary is **derived, not declared**. No predefined ontology: the
[prior-art survey](../01-research/2026-08-17-context-graph-prior-art.md) found predefined
schemas to be a leading cause of enterprise knowledge-graph failure, decaying from the day
they ship and unknowable before the data exists.

**This is not entity resolution, which stays deferred.** Topics cluster *content* and entities
are *types*; entity resolution would reconcile *identities* across sources (is `@han` in Slack
the same person as that account on the feed). Type-level entities need no such reconciliation
— that is much of why they were chosen. Instance-level identity remains out of scope per §6.

No ontology and no fixed schema is imposed on what a topic *is*. Different enterprises
genuinely differ, and any taxonomy invented now will be wrong for most of them. Topics emerge
from the content.

Three hard constraints:

- **Topic structure is a derived layer over preserved raw content**, never a replacement for
  it. Re-segmentation must always be possible from the originals — the clustering *will* be
  wrong early, and that has to be recoverable

- **Originals are never destroyed.** Translation, summarisation, chunking and extraction all
  produce *derived* artefacts linked to a preserved source. See
  [ADR-0004](adr/0004-preserve-originals-translate-at-consumption.md).
- **Source access-control metadata is recorded at ingest**, even though phase 1 enforces
  nothing. See [ADR-0006](adr/0006-record-source-acls-without-enforcing.md).

**Skills and prompts are stored context**, held in the same store and tagged as a distinct
type. They are not a separate system.

### 3.3 Serve

**The consumer is an agent. There is no human interface.** A human who needs context goes
through an agent, which assembles it for them. See [ADR-0005](adr/0005-serve-agents-only.md).

Serving is **on request**. The store does not invoke anything, at any stage.

#### Two-level retrieval

See [ADR-0014](adr/0014-two-level-agent-native-retrieval.md).

**Level 1 — the graph scopes.** Resolves the task into relations, and into which systems own
the relevant facts. Returns *scopes and routing*, **never content**.

**Level 2 — the vector index selects.** Within each scope, selects content under a budget.
Returns content, provenance, and gaps.

The graph never hands text to the agent. That is what avoids the precision dilution documented
in the [prior-art survey](../01-research/2026-08-17-context-graph-prior-art.md) — graph
retrieval scores highest factual correctness but *lowest context relevance* because traversal
drags in extraneous material. Scoping instead of answering removes the problem rather than
mitigating it.

Because relations are aggregated across topics, the graph already knows which topics evidence
a relation. Level 2 is therefore not finding them from scratch — it is **selecting among a
known candidate set under budget**, and recovering near-misses the relation extraction failed
to attach. That makes the vector index a recall safety net over an imperfect extraction step.

**The two levels are a dependency order, not a pipeline.** Within each level everything fans
out: relations traverse concurrently, scopes search concurrently.

**Entry does not require natural language.** An agent that already knows the entities or
relations it needs says so and skips resolution. And not every task is relational — direct
topic lookup is available without traversal, chosen per request rather than by blanket policy.

#### The response contract

This store is built for agents, not people, and the contract reflects that.

| Not this | This | Why |
|---|---|---|
| Query string | **Task + token budget** + optional structured intent | The agent already has structure; making it write a sentence discards it |
| Ranked list | **Budget-filling set optimised for coverage**, redundancy penalised | An agent doesn't read top-down and stop. Two near-identical top hits are worth less than one hit plus one different fact |
| What was found | What was found **and what was sought and not found** | See below |
| Prose | **Structured** provenance, collapsed score, staleness per item | The agent decides machine-side whether to rely or flag |
| One call | Optional cheap **coverage probe** before a budgeted fetch | Lets the agent budget before spending tokens |

**Negative space is part of the response, not an error.** The response states what was sought
and not found, and — per §3.0 — what the store does not hold at all, plus which system owns it
instead.

This is not a convenience. §5 measures the store by the assumptions an agent declares. For an
agent to declare *"I assumed the child is 4"*, retrieval must have told it nothing about age
was found. **A ranked list structurally cannot express absence**, so without negative space the
measurement the whole design rests on has nothing to feed on.

**Retrieval is deterministic for identical inputs.** Agents retry. If the same task yields
different context across attempts, a changed assumption could mean the world changed or that
retrieval jittered — and the correction signal becomes noise. Humans tolerate search jitter; a
measurement loop cannot.

Ordering within the returned set uses three inputs, not one: **vector relevance × collapsed
value score** (§5, weighted to the consuming agent's frame) **× freshness**.

## 4. Trigger design

"Trigger" conflates two different things. Separating them settles the question.

**Ingest-time processing** — a signal lands and the store normalises, links, extracts, tags
and updates its view. Internal, asynchronous, and mandatory. Read-time efficiency is bought
with write-time work; there is no version of this where ingest is lazy and serving is fast.
This is not a trigger, it is the pipeline.

**Outbound triggering** — a signal lands and the store goes and invokes something. **The
store must never do this.** Instead it emits an append-only change feed that consumers may
subscribe to.

Rationale:

- The store stays passive, which is the phase 1 requirement
- Triggering becomes possible later by adding a *consumer*, not by changing the store
- The judgement of *when something matters enough to act* differs per consumer and per
  enterprise. Putting it in the store means per-customer branches in the core
- The write path's availability stops depending on consumers being alive

If triggering is ever added, it must be asynchronous. Signals arrive in bursts; a meaningful
trigger is almost never "one message arrived" but "enough has changed here to matter", which
requires debouncing and aggregation over a window.

**On the serve path:** if a signal landed moments ago and is not yet processed, serve the
materialised view and **return staleness as metadata**. Never block a read on ingest
completion — that is how "serve efficiently" quietly becomes "serve slowly under load".

## 5. The learning loop

### What "right" means

Defining "good" is the problem the founding discussion never resolved (00:00:52). The
framework sidesteps it the same way the paradox was sidestepped.

**The store is measured on whether the agent had to assume less, and whether what it did
assume held up.** Not on the quality of the final artefact.

This matters because it separates failure modes. A poor output with *no* assumptions is an
agent problem. A poor output with *many corrected* assumptions is a store problem. Without
that split you cannot tell which half to fix, and you will spend months tuning the wrong one.

The gold signal is the **corrected** assumption: a human spent effort to say "no, actually".
That is expensive to fake, unambiguous, and tells you both that the gap was real and what
should have been there.

### Two-axis scoring

Every topic carries **two independent 1–10 scores, each with a short reason**. The axes are
adapted from the Life Capture Swipe Card System's Urgent × Important assessment (A8).

| Axis | Question | Why this axis |
|---|---|---|
| **Value** | How much does having this improve an agent's output? | The thing we actually care about |
| **Volatility** | How fast does this go stale? | Stale context is not merely useless — it is *confidently wrong*, which is worse than absent |

Routed as a quadrant:

| | Value 6–10 | Value 1–5 |
|---|---|---|
| **Volatility 1–5** (durable) | Core context — index heavily, retrieve eagerly | Cheap to retain, keep in background |
| **Volatility 6–10** (perishable) | Serve, but always with freshness metadata; re-verify before relying on it | Evict — retention cost exceeds value |

Three rules carried over from A8 because they are the parts that make it work:

- **A score of exactly 5 is below threshold.** No fence-sitting
- **Boundary cases (4–6) get extra calibration sampling** — that is where the model is least
  reliable and where correction is worth most
- **Every score carries a reason, including for low scores.** A7 requires explaining why
  attention *is or is not* warranted, which makes the *rejected* set auditable rather than
  invisible. This is unusual and worth the cost

**Urgency is deliberately not a third axis in v1.** It exists in Life Capture because that
system decides whether to interrupt a person; this store notifies nobody (ADR-0005), so the
number would have no consumer. Held open as a candidate third axis once there is a real
reader to calibrate against — deferred, not rejected.

### Scoring is two-step

1. **Capture raw.** No privileged sources, no weighting
2. **Apply an initial score** at ingest — model-assigned Value × Volatility with reasons
3. **Refresh continuously** from how often the topic is actually reused, recalled, and
   referenced by other topics

The initial score matters more than it looks: without one, nothing is retrievable, so nothing
can become used, so usage-based weighting can never bootstrap. The initial score is a prior
that evidence corrects — not a verdict.

### Human rating: topic-grain, participant-routed

**The unit of human rating is a topic, not a message.** A topic is routed to the queue of
**every person who participated in it**, and each of them scores it independently.

This is what makes the daily pass survive enterprise volume. A workspace producing thousands
of messages a day yields perhaps 50–100 topics, and an individual only sees the ones they were
could be.

**Participation is binary.** Anyone in the discussion may score it. How much they wrote is
irrelevant — someone who replied "agreed" was still in the room, and volume-weighting would be
a tuning knob that invites gaming.

### All rater scores are retained; collapse happens at retrieval

**Never collapse multiple raters into a single number at write time.** Store every rater's
score, reason, and role.

Disagreement is signal, not noise. Something critical to IT may be irrelevant to marketing,
and both scores are correct within their frame. A mean would destroy exactly that
information, and it is unrecoverable once discarded.

The collapse happens **at retrieval, relative to the consuming context** — an agent working a
marketing task should weigh marketing participants' scores more heavily than IT's. This is the
same principle as [ADR-0004](adr/0004-preserve-originals-translate-at-consumption.md):
preserve the original, derive at consumption. See
[ADR-0010](adr/0010-retain-all-rater-scores.md).

### External signals: no human rating in v1

Nobody rates external signals for now — participant-routing has nothing to route on, since
nobody was in the conversation.

The intended value signal for external is **pattern, not judgement**: how many *distinct*
customers raise a given topic. Because external signals attach to the same topic nodes as
internal ones, breadth-of-customer-noise and internal human scores accumulate against a shared
subject — which is what makes the pairing answer *does what we say internally match what
customers experience?*

**This is an open question, not a settled design** — see §7.

### Correcting the graph

Segmentation will be wrong early, and a queue that regularly contains things people don't
recognise is a queue they stop opening. So correction is part of the rating surface, not a
follow-on feature. See [ADR-0011](adr/0011-report-with-free-text-reason.md).

**One report action, with a required free-text reason.** No categories — whatever the person
means goes in their own words. The taxonomy will be *derived* from real reports later, not
designed now from imagination. This is the same stance the store takes on its own schema: you
cannot categorise failures you have not yet observed.

**"I don't remember this" is not by itself grounds for removal.** The person is expected to
check the source first. That obligation only holds if checking is trivial, so **every card
must link back to the source thread**, not merely quote it — otherwise reporting is cheaper
than verifying and people will report.

**Reports are evidence, not automatic repair.** They accumulate against the topic and inform
the next segmentation pass. The graph does not self-heal from a single report — one person
saying "not mine" is strong evidence about their own participation and weak evidence about
whether the classification is wrong for everyone else.

events and reversed by compensation, never by mutation. Taken from Life Capture A9 — *"every
action supports Undo and is idempotent"* — and it must exist from the start, because
retrofitting undo onto mutations means the history needed to reverse them was never recorded.

### No autonomy gate in this iteration

Not adopted for v1. Revisit when the loop has produced enough correction data to measure
agreement at all.

## 6. Explicitly out of scope for phase 1

Recorded here so that "we didn't think of it" is never confused with "we decided against it
for now".

| Out of scope | Status |
|---|---|
| Any implementation | Phase 2 |
| Outbound triggering / event-driven action | Deferred; change feed designed for, not built |
| Prompting a human to fill a gap | Future phase — the target behaviour is described in §1 |
| Interview-based elicitation (digital-human interview, expert extraction) | Future phase |
| Entity resolution, identity linking across sources | Deferred; ingest as-is, recalibrate later |
| Human-facing search or dashboard | Rejected — see ADR-0005 |
| Market positioning, pricing, go-to-market | No market awareness yet; deliberately unaddressed |
| Skill Hub as a product, e-commerce agents, 智慧店长 | Adjacent product ideas from the founding discussion; not this system |
| Social/economic consequences of AI adoption | Context for why this matters; not repo scope |

## 7. Open questions

1. **How external signals earn value.** No human rates them (§5). The intended signal is
   *pattern* — how many distinct customers raise a topic — but the mechanism is undesigned.
   Open by explicit decision, not oversight
2. **How reports become repairs.** ADR-0011 settles the *reporting* mechanism — one action,
   free-text reason. What consumes those reports, and how many it takes before the next
   segmentation pass acts on one, is undesigned
3. **Cross-thread topic continuity.** A discussion that resumes weeks later, or spills across
   channels, should land on the same topic. That is the hardest part of §3.2 and the part
   most likely to be wrong in v2
4. **Coverage when people skip their queue.** Some fraction won't rate. A topic rated by
   nobody is not the same as one scored low, and the model must not confuse them
5. **The retrieval-time collapse function.** §5 says scores collapse relative to the
   consuming context. *How* — role match, participation overlap, learned affinity — is
   unspecified
6. **What the self-learning routine recalibrates** — topic boundaries, scores, source
   weighting, eviction? "Reuse-driven" is the direction, not the mechanism
7. **Serve latency budget** — unspecified. Agent-in-the-loop tolerances differ by orders of
   magnitude from human-interactive ones
8. **Whether "assumption" is machine-checkable** — the loop depends on agents reliably
   declaring assumptions. What happens when they silently don't?
9. **Canonical language for derived artefacts** — originals are preserved (ADR-0004), but the
   working language of the derived layer is unspecified
10. **Urgency as a third axis** — deferred, not rejected (§5)
11. **Relation vocabulary drift.** [ADR-0012](adr/0012-type-level-entities-and-typed-relations.md)
    derives relations rather than declaring them, so `complain about` and `raise issues with`
    may be extracted separately for the same fact, fragmenting the evidence that aggregation
    depends on. This is the entity-resolution problem displaced onto relations
12. **The human validation mechanism for new entities.** [ADR-0015](adr/0015-bootstrap-entity-graph-from-systems-of-record.md)
    gates conversation-derived entity creation behind human confirmation and explicitly does
    not design it. If nobody performs the step, entity creation stalls and the graph silently
    stops growing
13. **Coverage selection under budget.** [ADR-0014](adr/0014-two-level-agent-native-retrieval.md)
    replaces ranking with set-level coverage optimisation. That needs a redundancy notion that
    does not yet exist, and standard IR metrics do not measure it
14. **Keeping the authoritative-for relations current.** §3.0 has the graph route agents to the
    right system. Stale routing sends them to the wrong place, which is worse than sending them
    nowhere

### Deliberately deferred, not open

- **Cost bounds.** Ingest cost is not modelled, by decision: validate the concept and the
  framework first, then optimise with engineering techniques. Recorded here because the
  survey's numbers are large — indexing one dataset with the original GraphRAG pipeline ran to
  roughly $33k in LLM calls, and our topic layer is structurally the same object that the
  field's cost-driven refactor removed. Deferred with eyes open, not overlooked

## 7b. How we would know we are wrong

Each ADR carries a *"What would make us revisit this"* section. Those are aggregated and
operationalised — observation, measure, and whether a home-scale validation instance can test
them at all — in [falsification-criteria.md](falsification-criteria.md).

Two findings from writing it are worth carrying here:

- **ADR-0001, ADR-0007 and ADR-0006 have no real falsifier.** The first two are process
  conventions rather than claims about the world; the third is a bet that cannot resolve until
  later. Named as such rather than left looking like tested design
- **The external-signal gap has nothing to falsify at all**, because no ADR makes a claim about
  it. That is the same hole as open question 1, seen from the other side

## 8. Decisions carried by ADR

| ADR | Decision |
|---|---|
| [0002](adr/0002-phase-1-is-a-technology-agnostic-framework.md) | Phase 1 is a technology-agnostic framework, not an implementation |
| [0003](adr/0003-measure-context-quality-by-declared-assumptions.md) | Measure context quality by declared assumptions |
| [0004](adr/0004-preserve-originals-translate-at-consumption.md) | Preserve originals; translate only at consumption |
| [0005](adr/0005-serve-agents-only.md) | Serve agents only; no human interface |
| [0006](adr/0006-record-source-acls-without-enforcing.md) | Record source ACLs at ingest without enforcing them |
| [0007](adr/0007-two-sources-of-truth.md) | Obsidian is truth for personal work; git for collaboration |
| [0008](adr/0008-two-axis-scoring-value-volatility.md) | Score context on two axes: Value × Volatility, with reasons |
| [0009](adr/0009-topics-as-the-unit-of-context.md) | Topics are the unit of context; the store is a linked topic graph |
| [0010](adr/0010-retain-all-rater-scores.md) | Retain every rater's score; collapse only at retrieval |
| [0011](adr/0011-report-with-free-text-reason.md) | Corrections are a single report action with a free-text reason |
| [0012](adr/0012-type-level-entities-and-typed-relations.md) | Topics carry type-level entities; links are typed relations aggregated across topics |
| [0013](adr/0013-context-store-enriches-systems-of-record.md) | The context store enriches systems of record and never asserts what they own |
| [0014](adr/0014-two-level-agent-native-retrieval.md) | Two-level retrieval — graph scopes, vector selects — with an agent-native contract |
| [0015](adr/0015-bootstrap-entity-graph-from-systems-of-record.md) | Bootstrap the entity graph from ERP and warehouse schema; enrich from conversation |

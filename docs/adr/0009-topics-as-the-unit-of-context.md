
# ADR-0009: Topics are the unit of context; the store is a linked topic graph

- **Status:** Accepted
- **Date:** 2026-08-17
- **Supersedes:** —

## Context

Two problems that looked separate turned out to share one answer.

**Scale.** Human rating is part of the scoring loop ([ADR-0008](0008-two-axis-scoring-value-volatility.md)),
modelled on Life Capture's ten-minute daily pass. But Life Capture is one person rating their
own low-volume captures. A Slack workspace produces thousands of messages a day. No daily pass
survives that at message grain, and if nobody rates, human judgement is dead weight in the
scoring vector.

**Retrieval.** An agent asking "what do we know about X" wants a *subject*, not a ranked list
of message fragments that each mention X. A document-shaped store answers the second question
well and the first badly.

## Decision

**Topics are the unit of context. The store is a graph of linked topics, not a pile of
documents.**

Ingestion runs over an interval — the delta from a source across a window (24h, or shorter;
the interval is a tuning parameter, not a fixed property). For each batch:

1. **Segment** the raw conversation into topics
2. **Attach** each segment to an existing topic where one fits; otherwise create a new one
3. **Link** related topics to each other

Topics are durable and accrete: a discussion resumed three weeks later lands on the same node.

**Human rating happens at topic grain**, and a topic is routed to the queue of **every person
who participated in it**. Each scores it independently.

**Participation is binary.** Anyone in the discussion may score it; how much they wrote is
irrelevant.

**No ontology is imposed on what a topic is.** Topics emerge from content. Different
enterprises genuinely differ, and any taxonomy invented now will be wrong for most of them.

**Topic structure is a derived layer over preserved raw content**, per
[ADR-0004](0004-preserve-originals-translate-at-consumption.md). Re-segmentation must always
be possible from the originals.

**This is not entity resolution**, which remains out of scope. Topics cluster *content*;
entity resolution reconciles *identities* across sources. The first makes the store useful;
the second is not yet needed.

## Options considered

### Option A — Topic graph, participant-routed rating  ✅ *chosen*

- **Upside:** Collapses thousands of messages into perhaps 50–100 topics a day, and each
  person sees only what they were in — a 5–15 item queue, genuinely a ten-minute pass. Puts
  judgement where the knowledge is: the people in the room. Routing one topic to several
  participants yields multi-rater data for free. And it makes the store queryable by subject
- **Cost:** Segmentation is a model task that will be wrong sometimes, visibly, in users'
  queues
- **Risk:** Cross-thread continuity — a discussion resuming weeks later, or spilling across
  channels — is the hard part and the most likely thing to be wrong

### Option B — Thread as topic, no clustering

- **Upside:** Zero inference, fully debuggable, never surprises anyone
- **Why not chosen:** Misses exactly the cross-thread and cross-channel discussions that carry
  the most context. Considered as a v1 simplification and rejected by the decision-maker:
  *"This is where some of the intelligence needs to come in."*

### Option C — Message-grain storage and rating

- **Upside:** No segmentation to get wrong
- **Why not chosen:** Rating does not survive the volume, and retrieval returns fragments
  rather than subjects

## Consequences

**What gets easier:** Human rating becomes tractable at enterprise volume. Retrieval is by
subject. Internal and external signals attach to the *same* topic nodes, so internal
discussion and customer feedback accumulate against a shared subject — which is what makes the
pairing answer *does what we say internally match what customers experience?*

**What gets harder:** Segmentation quality becomes load-bearing and user-visible. A misfiled
topic shows up in someone's queue and costs trust directly. Ingestion is no longer a
pass-through; it involves a model, with the cost and failure modes that implies.

**What we're now committed to:** Preserved originals sufficient to re-segment from scratch,
because early clustering *will* be wrong and that must be recoverable. Participation must be
derivable from every internal source, since it is what routing depends on.

**What would make us revisit this:** Segmentation proving unreliable enough that users stop
trusting their queues — the fallback is Option B (thread as topic) with clustering as an
advisory overlay rather than the primary structure.

## References

- [Phase 1 framework](../phase-1-framework.md) §3.2, §5
- Open questions §7.2, §7.3, §7.4 — segmentation correction, cross-thread continuity,
  and coverage when people skip their queue

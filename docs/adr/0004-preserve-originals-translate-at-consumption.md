
# ADR-0004: Preserve originals; translate only at consumption

- **Status:** Accepted
- **Date:** 2026-08-17
- **Supersedes:** —

## Context

The store must be language-agnostic. There is no target market, and the founding discussion
happened in Mandarin purely by circumstance — so no language gets to be privileged by
accident.

Internally, a single working language keeps retrieval and processing simple. The question is
**where** the conversion happens.

This matters far more than it first appears because of what the external signal is:
**customer feedback**. Translation flattens idiom, register, sarcasm and intensity. A furious
Chinese complaint and a mildly disappointed one can both land as the same polite English
sentence. Customer feedback *pattern detection* is precisely the thing that nuance carries —
so normalising at ingest would destroy the signal we chose that source to capture.

Translation is lossy and irreversible. You cannot un-translate.

## Decision

**Originals are stored, always, and never discarded.** Translation, summarisation, chunking
and extraction produce **derived artefacts linked back to a preserved source**.

**Translation happens at consumption**, not at ingest.

This generalises beyond language: any lossy transformation is a derived layer over a
preserved original, never a replacement for it.

## Options considered

### Option A — Store original, derive at consumption  ✅ *chosen*

- **Upside:** No signal is ever lost. Re-derivable when translation quality improves — and it
  will. Agents can choose to work in the source language when nuance matters
- **Cost:** More storage, and consumers must handle mixed-language content
- **Risk:** Latency if translation is fully on-demand — mitigated by caching derived artefacts

### Option B — Normalise to one language at ingest

- **Upside:** Simplest retrieval; everything downstream is monolingual
- **Cost:** Destroys the original, permanently
- **Why not chosen:** Irreversible, and it destroys exactly the signal the external source
  exists to capture. Every future translation-quality improvement would be unusable on
  historical data

### Option C — Store both, cross-lingual retrieval throughout

- **Upside:** Query in any language, retrieve in any language
- **Why not chosen:** Materially harder for phase 2, with no established need. Option A does
  not preclude it later

## Consequences

**What gets easier:** Re-deriving everything when models improve. Auditing — you can always
show what was actually said. Adding languages, which needs no migration.

**What gets harder:** Consumers face mixed-language content and must decide when to ask for a
translation. Storage grows with each derived layer.

**What we're now committed to:** Immutable originals with derived layers linked to them.
Every transformation records what produced it. This shape must exist from the first line of
phase 2 — bolting it on later means the originals were already lost.

**What would make us revisit this:** Storage cost becoming material at scale — though even
then the answer is likely tiered storage for originals, not deletion.

## References

  — *"original, then translation in consumption"*
- [Phase 1 framework](../phase-1-framework.md) §3.2

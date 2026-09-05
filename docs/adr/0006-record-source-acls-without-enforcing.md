
# ADR-0006: Record source access-control metadata at ingest without enforcing it

- **Status:** Accepted
- **Date:** 2026-08-17
- **Supersedes:** —

## Context

Security is deliberately deferred. Phase 1 exists to establish what the context store needs
to be and whether the approach works at all; security components come afterwards. Phase 1
ingests **public channels only**, so there is no immediate exposure.

That deferral is sound with one exception, which is why this ADR exists separately from the
general deferral.

**Access-control context is only knowable at the moment of ingest.** Whether a Slack message
information the *source system* holds. Once the content is in the store without that
metadata, it cannot be recovered by inspecting the store. The only way to get it back is to
re-ingest everything from the source, assuming the source still exists, still has the
history, and still exposes the same permissions.

So the general "defer security" decision is cheap, but this one specific piece of it is not:
it is cheap **now** and impossible **later**.

## Decision

**Record each item's source access-control metadata at ingest. Enforce nothing in phase 1.**

identifier for the containing scope, and the timestamp at which that visibility was
observed. Store it alongside the item as immutable provenance.

Phase 1 performs **no** access checks at serve time. This is recording only.

## Options considered

### Option A — Record ACLs, enforce nothing  ✅ *chosen*

- **Upside:** Preserves the option to add enforcement later without re-ingesting. Costs a few
  fields in a schema. No enforcement complexity now
- **Cost:** Slightly more to capture and store; a small ongoing discipline in every connector
- **Risk:** Recorded-but-unenforced metadata can create false confidence that access control
  exists. It does not, and phase 1 documentation must say so plainly

### Option B — Defer ACL capture entirely along with everything else security-related

- **Upside:** Simplest possible connectors
- **Why not chosen:** Requires a full re-ingest to add security later. Sources may have
  rotated, aged out, or changed their permission model by then — some of that history is
  simply unrecoverable

### Option C — Full ACL enforcement in phase 1

- **Upside:** Secure from day one
- **Why not chosen:** Contradicts the phase 1 scope. Enforcement is a substantial subsystem
  and phase 1 is a framework, not an implementation

## Consequences

**What gets easier:** Adding real access control in a later phase becomes a serve-time
change, not a data migration. Audit questions — "where did this come from and who could see
it?" — remain answerable.

**What gets harder:** Every connector must obtain visibility metadata, which for some sources
is a separate API call. Some sources may not expose it at all, and those cases must be
recorded as *unknown* rather than silently assumed public.

**What we're now committed to:** Provenance including visibility is part of the ingest
contract from the first connector. And to being explicit, in the framework and in the
README, that **recording is not enforcing** — phase 1 has no access control.

**What would make us revisit this:** A source that cannot supply visibility metadata at all,
forcing a decision about whether to ingest it and how to mark it.

## References

  just ingest the public channels. Security is a completely separate topic which we need to
  discuss further in future phases."*
- [Phase 1 framework](../phase-1-framework.md) — Security tier, §3.2

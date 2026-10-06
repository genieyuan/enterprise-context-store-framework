# ADR-0016: Compile publishes the graph; Serve assembles request packages

## Status

Accepted — 2026-09-05

## Decision

Compile publishes atomic, evidence-backed `ContextClaim` and `EdgeClaim` objects into a
versioned Enterprise Context Graph (ECG). Every semantic relationship is backed by an EdgeClaim;
Topic and DecisionCase remain projections. Graph publications and their objects are durable,
append-only and versioned. Each claim carries evidence, provenance, valid-time and
transaction-time, authority state, contradiction state/links, version and supersession lineage.

Serve reads pinned graph/object/evidence/policy/derivation versions and assembles a temporary,
authorized, task-scoped ContextPackage. It records a durable ContextDeliveryReceipt containing
authorization, budget, omissions and the pinned versions. Package possession never grants
authority. Revoked packages are not served again, while governed history and audit stubs remain.

Compile never owns a durable ContextPackage, retrieval ranking/budgeting, authorization
enforcement, or operational facts owned by systems of record. Such facts are represented as
routing pointers. Visibility/ACL metadata is preserved per evidence item and any package-level
classification is derived by Serve under a stamped policy version.

## Compatibility and superseded wording

Existing ADR meanings remain unchanged. The former wording that Compile builds or owns durable
ContextPackages is superseded: legacy package fields map to ECG claims, EdgeClaims, projections,
manifests, or Serve receipts. Historical documents and quotations remain unchanged and are not
normative evidence of current ownership.

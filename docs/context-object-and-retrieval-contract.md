# Context Object and Retrieval Contract

> **Publication scope:** technology-neutral framework, not a deployed runtime. The Phase 1
> public-channel-only scope and recording-only ACL boundary remain unchanged. References to
> current authorization, revocation, encryption, or privacy enforcement specify obligations for
> future implementations; they do not claim those mechanisms are implemented or authorize
> private/restricted ingestion. Existing accepted ADRs are not silently superseded.

The [Compile/Serve boundary](adr/0016-compile-publishes-ecg-serve-assembles-packages.md)
assigns durable ECG claim publication to Compile and task-package assembly to Serve.

## Normative semantic spine

This section preserves the approved ECS semantic model. Source observations are represented by
`EvidenceEvent`. Atomic governed assertions are `ContextClaim`; consequential addressable
relationships are `EdgeClaim`, never naked graph edges. `DecisionCase` is a versioned decision
projection containing alternatives, criteria, evidence, assumptions, approvals, actions,
outcomes, and revisions. `EvaluationEvent` records subjective evaluation and `OutcomeEvent`
records objective results; neither silently rewrites canonical history.

The flow is:

`EvidenceEvent → ContextClaim / EdgeClaim → Topic or DecisionCase → ContextPackage + ContextDeliveryReceipt → EvaluationEvent / OutcomeEvent`

`ContextPackage` is temporary, bounded, and assembled for a task under current authorization.
`ContextDeliveryReceipt` is the durable delivery/use record: it records the exact delivered
object and representation versions, policy decision, derivation/ranking versions, budget or
truncation, safe omission categories, and links to resulting answer, decision, or action.
Retrieval receipts are external links to a `DecisionCase`, not intrinsic semantic nodes.

`PrincipalRef` identifies the requesting or receiving principal. A scoped
`AuthorityGrantRef` records the applicable authority boundary. Authorization is evaluated for
the current delivery and is not inferred from possession of context, a prior receipt, or model
confidence. Revocation affects future delivery; historical records remain governed by their
retention and access policy. Indexes and projections are rebuildable and cannot become a second
source of truth.

Evidence sufficiency is separate from action eligibility. A human validation request is workflow
state, not evidence. Source systems remain authoritative for their original records.

## Derived operational guidance

`RetrievalPlan` is derived orchestration, not a canonical storage primitive. A plan may gather
claims and `EdgeClaim` paths, traverse `DecisionCase` history, apply current authorization,
classify results, and assemble a bounded package before writing a receipt. Derived profiles,
ranking views, execution traces, and indexes cannot grant authority or change the semantic
meaning of canonical objects.

The approved base importance classes are `CRITICAL=5`, `IMPORTANT=3`, and `SUPPORTING=1`.
Evidence credits are `FACT=1.0`, `ASSUMPTION=0.4`, and `UNKNOWN=0.0`. Diagnostic coverage bands
use boundaries `0.65` and `0.85`; coverage alone is never sufficient for action. Critical or
authorization gaps, non-leakage constraints, and policy overrides take precedence. A runtime
model cannot invent or change weights, thresholds, budgets, risk rules, profiles, or authority
without a pinned approved bundle or profile.

An Evidence Capsule is always minimal. In regulated use, full evidence remains with the governed
source system or records custodian. ECS retains an encrypted, access-controlled reference that
can resolve to the individual source record, together with its integrity fingerprint and
provenance metadata. Resolving it requires current source authorization; context access does
not grant source-record access. If the source is unavailable, preserve that limitation rather
than fabricate evidence.

## Open questions

Numeric-default suitability questions remain open and non-normative. The final ECS/action-policy
boundary, terminal-outcome precedence, tenant/base-semantic boundary, detailed onboarding
policy beyond approved guidance, and commercial or pricing claims also remain open. None is
resolved by this document or by research evidence.

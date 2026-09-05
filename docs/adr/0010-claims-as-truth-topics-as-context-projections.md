
# ADR-0010: Claims as truth; Topics as context projections

**Status:** Accepted

EvidenceEvent, ContextClaim and EdgeClaim form the canonical truth-bearing spine. Topic remains
the durable agent-facing unit of context, retrieval, graph organization and conversation
continuity, but is a versioned projection over atomic evidence-bearing claims, never the atomic
truth record. This supersedes the narrow wording of ADR-0009 while preserving its delivery role.

`reference-architecture.md`, `context-object-and-retrieval-contract.md`, and the approved ECS
Semantic Projection and Claim Interchange contract. The CIC envelope is normative; vendor stores

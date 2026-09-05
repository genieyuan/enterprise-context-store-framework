# Compile Stage

**Phase 1 / public-channel / security-deferred boundary:** this is a public architecture document. It does not authorize ingestion of private or restricted channels, and security enforcement is deferred to a future phase.

Compile is the publication boundary: it deterministically turns landed evidence into atomic
`ContextClaim` and `EdgeClaim` objects and publishes them into a versioned Enterprise Context
Graph. Claims retain supporting and contradicting evidence, provenance, valid/transaction time,
authority and contradiction state, object version, and supersession links. Derived Topics,
DecisionCases, indexes and weights may be rebuilt from those canonical objects.

Compile does not write a durable ContextPackage, rank or budget retrieval, enforce authorization,
or assert operational facts owned by a system of record. It emits a routing pointer for those
facts. Serve creates the temporary request-scoped ContextPackage and durable
ContextDeliveryReceipt.
# Enterprise Context Store — Compile Stage: Gate 1 Final Design

**implementation: none**  
**Lifecycle disposition:** Gate 1 closes with this artifact. No Gate 2 and no implementation.



**implementation: none**
**Lifecycle:** Capture → **Compile** → Serve → Continuous Learning, with **Governance & Trust** cross-cutting (2026-09-02 amendment, Gate 1 closed — this document does not reopen it).

---

## 0. Round 1 findings disposition

Concise map from each binding Round 1 finding to the exact revised section(s) that close it. Full closure narrative for each finding is inline in the referenced sections; §29 is the consolidated disposition ledger with per-finding pass/fail evidence.

| Finding | Round 1 defect (summary) | Closed in | How |
|---|---|---|---|
| **F2** | Tombstone "reconstructable history" contradicted §13.2/FV5 releasing references for GC; quarantine vs. terminal tombstone conflated | **§11**, **§13.2**, **§15**, **§22 (FV11–FV12)** | Four lifecycle states are now distinct and non-contradictory: Restricted (temporary quarantine), Withdrawn (governance soft withdrawal, evidence/history **retained**), Deleted (governance hard erasure, removal obligation **propagated**), Superseded (append-only lineage). Reference/hold retention and reconstructability are stated per state; a deletion/restoration validation sequence proves no deleted content survives via lineage. |
| **F3** | Package `visibility_class` collapsed; per-evidence visibility not preserved; no derivation rule | **§9** (Evidence Reference + package `visibility_derivation`), **§18**, **§22 (FV13)** | Each Evidence Reference now carries its recorded source visibility/ACL metadata; the package label is a **derived** value stamped with the Governance-owned policy-version reference. Enforcement stays out of Compile. A mixed-visibility case proves no downgrade/loss through aggregation, supersession, correction, withdrawal, or deletion. |
| **F4** | Manifest proved presence, not reproducible lineage; NF2/NF10 too weak | **§9** (Compiler Manifest), **§19**, **§23 (NF2, NF10)**, **§22 (FV14)** | Manifest now binds the exact ordered input snapshot with content digests, prior-state lineage, produced outputs, governing policy versions, and integrity digests, with a defined `manifest_identity` and a stated **replay-equivalence criterion** (permitted nondeterministic variance enumerated). Validation checks identity/integrity, not a non-null pointer. |
| **F6** | Unresolved decisions mixed with Phase 2 choices; walkthroughs assumed unresolved mechanics | **§26** (reclassified a/b/c/d with owners/bounds), **§21.1** (conditional branch), **§14.1** | Every open item is classified as (a) blocking owner decision, (b) framework invariant with mechanism delegated, (c) Phase 2 implementation choice, or (d) parked separate scope. Owners named for (a); invariant/validation bound named for (b). Walkthrough steps depending on unresolved mechanics are marked as explicit conditional branches, not demonstrated behavior. |
| **F7** | Several validation cases not falsifiable; missing cases | **§22** (FV1–FV14), **§23** (NF1–NF12) | Each Gate 1 criterion now has an unambiguous logical pass/fail condition or is explicitly labeled a non-blocking health signal; production numeric SLOs are labeled Phase 2. Added: mixed-visibility (FV13), manifest-integrity/replay (FV14), full internal/external agent-consumption (FV11 covers deletion path; consumption proven by §21 + NF11), governance deletion/restoration propagation (FV11–FV12). |

Non-blocking editorial correction (page-one author attribution): **closed** — see the page-one block above.

---

## 1. Security tier, exposure, threat model — read this first (AC6)

**Tier for this document: none.** It is a framework, produces no running system, and processes no data.

**Tier this document designs *for*: Tier 2 — internal confidential, single-tenant, enterprise-controlled trust boundary.** Compile is the stage that performs semantic interpretation over enterprise-sensitive signals once implemented (Compile draft §11: "compilation should be local or air-gapped… must occur within an enterprise-controlled trust boundary"). That threat model is **not designed here** — this is a Phase 1 logical architecture, per ADR-0002.

**Explicitly not in scope:** authentication, authorization enforcement, encryption, network boundaries, deployment topology, and any decision about *which* trust boundary (local / private-cloud / on-prem / sovereign / air-gapped) an enterprise should choose. Compile **inherits** ADR-0006 as-is: source ACL/visibility metadata is recorded at Capture and carried through Compile's evidence references (now per-evidence, §9, F3), but Compile **enforces nothing**. Any component in this design that appears to make an access decision is a bug in the design.

---

## 2. Purpose

Compile turns source-faithful, landed signals — Capture's output, not yet semantically interpreted — into **Context Packages**: linked, evolving, governed, reproducible units of enterprise why/how knowledge that Serve hands to agents. Compile is where interpretation *starts*; Capture is explicitly forbidden from doing it (Capture blueprint §1: "does not assign enterprise truth, resolve contradictions, apply ontologies, compile context").

Compile does not decide anything an agent or a human will act on. It builds the evidence-backed map an agent consults before acting, and it is honest about what it doesn't know.

---

## 3. Vocabulary — one fixed mapping

The accepted ADR baseline (2026-08-17) and the 2026-09-03 Compile draft use different words for adjacent ideas. This document fixes the mapping once, here, and uses it consistently below.

| ADR-baseline term | 2026-09-03 draft term | This design uses | Notes |
|---|---|---|---|
| Topic (ADR-0009) | Subject (evidence-aggregation layer) | **Topic** | Same construct: the unit content clusters around |
| Type-level entity + typed relation (ADR-0012) | (unnamed structural layer) | **Entity / Relation** | Sits alongside topics, aggregates across them |
| — | Context Package | **Context Package** | The linked, evolving, versioned unit Serve consumes; built from one or more topics plus the entity/relation evidence they carry |
| — | Context Store | **Context Store** | The whole of Compile's durable output — all Context Packages, topics, and the entity/relation graph together |
| Assumption, declared (ADR-0003) | Assumption/hypothesis (§5.8) | **Assumption claim** | A claim kind with no (or explicitly flagged) supporting evidence |
| Report (ADR-0011) | — | **Correction report** | Free-text, one action, append-only |
| Tombstone (Preserve amendment) | Tombstone (draft §15) | **Restricted** (temporary quarantine) + **Withdrawn** (governance soft withdrawal) | The single word "tombstone" was doing two incompatible jobs; split here to close F2 (§11, §15) |

Two logical layers above Capture's landed evidence, per Compile draft §5.3, now concrete:

```
Landed Evidence (from Capture)
        │  segment by interval, attach/create
        ▼
   TOPICS  ───extract───▶  ENTITIES & RELATIONS (type-level, aggregated across topics)
        │                              │
        └──────────────┬───────────────┘
                        ▼
              CONTEXT PACKAGES (linked, versioned, evidence-bound)
                        │
                        ▼
                 CONTEXT STORE  ───▶  Serve
```

---

## 4. Scope

### 4.1 In scope

- Converting landed signals into topics, then into entity/relation structure, then into Context Packages.
- Evidence binding: every claim in a package cites what supports and what contradicts it.
- Append-only knowledge evolution, correction, and (governance-gated) restriction, soft withdrawal, hard erasure, and restoration.
- Attaching and retaining human evaluations, including Value×Volatility scores, at topic/package grain.
- Bootstrapping the entity/relation baseline from systems-of-record structure (schema, not operational data) and enriching from conversation, human-gated.
- Compilation triggers and recompilation.
- Protecting evidence linked to a retained package from Capture's landing-expiry GC.
- Carrying per-evidence visibility/ACL provenance and stamping any package-level classification with the Governance policy version that derived it (recording only; enforcement out of scope — F3, §9, §18).
- Producing a reproducible compiler manifest with checkable identity and integrity, and a defined replay-equivalence criterion (F4, §9, §19).
- Supplying Continuous Learning with attributable evaluation/outcome lineage.
- Exposing facts, interpretations, assumptions, contradictions and gaps as **distinct, labeled** things, and exposing them intact through Serve to the consuming agent (F1, §21).

### 4.2 Non-goals

Carried forward verbatim in substance from Compile draft §2 and the wish list's confirmed requirements — Compile does **not** own:

- Operational facts or transactions held by systems of record (ADR-0013).
- Retrieval mechanics — ranking, budget-filling, coverage, collapse-at-retrieval, the two-level graph/vector contract. That is Serve's job (ADR-0014). Compile's obligation stops at producing a structure Serve *can* retrieve over. The §21 walkthroughs trace data **through** Serve's read interface to the agent but design none of Serve's internals (F1).
- The operational forecast number, or any operational output.
- A universal, human-designed package schema — Compile fixes a **minimum contract** (§9); internal representation, topology, splitting, merging and traversal are AI-designer choices (compile draft §5.1–5.3).
- Implementation technology or deployment pattern.
- Autonomous agent decision-making policy.
- Access-control enforcement (ADR-0006 — recording only, and the *authoring* of that recording happens in Capture; Compile carries and derives, never enforces).

---

## 5. Inputs and outputs

### 5.1 Inputs (from Capture, per the Capture blueprint's Minimum Capture Envelope)

- The complete landed source record plus Envelope (source system id, ECS capture id, capture timestamp, source-system metadata **including per-record visibility class / ACL provenance**, the source record itself). Compile carries the per-record visibility metadata forward onto each Evidence Reference unchanged (F3, §9).
- Landing/change notifications, including linked source edit chains (v1→v2…) or, where source identity is unavailable, **explicit best-effort/ambiguous correlation** — Compile must carry that ambiguity forward, never silently resolve it into false-confident lineage.
- Structural sources: ERP/warehouse schema, entity-relationship models, ontology/catalog versions (never operational records, status, or transactions — those are excluded at Capture and remain excluded here).
- Discovery-window and retention policy from Governance & Trust, which bounds how long unreferenced raw evidence survives before GC.
- Governance policy versions Compile must stamp but not author: the **visibility-derivation policy** (F3), the **governance ruleset** (restriction/erasure/restoration), and the **retention policy**. Compile records the version it applied; it does not define the policy.

### 5.2 Outputs

- **To Serve:** the Context Store — topics, the entity/relation graph (with aggregate relation weight, F1), and versioned Context Packages with bound evidence, per-evidence visibility metadata, scores (uncollapsed), evaluations, and compiler manifests with checkable identity. Serve reads this; Compile does not rank, collapse, or budget it (ADR-0014 stays out of scope).
- **To Continuous Learning:** attributable evaluation/outcome lineage (package version → use → assumptions → proposal → human modification/decision → outcome), per Compile draft §9, without claiming causal proof.
- **Back to Capture (indirect):** nothing. Compile does not write to Capture's landing area other than the retention holds it issues via the Evidence Reference Ledger (§13.2). A missing system-of-record fact discovered during compilation is surfaced as a **governance/data-stewardship gap**, not written anywhere by Compile (ADR-0013, Capture blueprint §2.4).

---

## 6. Architectural principles

Carried forward from Compile draft §5, reconciled with the ADR baseline:

1. **AI-built for AI consumption.** Package topology and internal representation are an AI-designer's job; this document specifies requirements and a minimum contract, not a schema (compile draft §5.1).
2. **Dynamic package formation**, not a hard-coded taxonomy.
3. **Two logical layers above landing** — topics, then packages — per §3.
4. **Append-only evolution.** Nothing is silently overwritten; new signals or evaluations append timestamped states that reinforce, weaken, contradict, correct, or supersede. The **only** exception is governance-authorized hard erasure (§15.2), scoped as narrowly as the Preserve amendment allows.
5. **Evidence and provenance are mandatory**, not optional metadata — see §16's binding invariant and the manifest identity contract (§19).
7. **Official practice and observed practice are both retained**, and divergence between them is exposed, not silently resolved either direction (§5.7).
8. **Facts, interpretations and assumptions are distinguishable types**, not flattened prose (§5.8), and this typing is schema-checkable (NF1, F6 item 8).
9. **No package-completeness claim.** Missing evidence is not evidence of absence (§5.9).
10. **Multiple causal explanations survive**; correlation is never laundered into causation (§5.10).
11. **Topics are the unit of context, entities are types not instances, relations are derived and aggregated** — ADR-0009, ADR-0012, unchanged.
12. **The entity graph is bootstrapped from structure, enriched from conversation, human-gated on creation** — ADR-0015, unchanged.
13. **Compile never asserts what a system of record owns** — ADR-0013, unchanged; Compile's structural entities may derive *from* ERP/warehouse schema, but Compile never ingests or asserts ERP operational state. When an operational fact is needed, Compile emits a routing pointer, not a value (§9 `routing-pointer`, §21).
14. **Visibility metadata is preserved, never manufactured or downgraded.** Compile carries each evidence item's recorded visibility and derives any package label only through a stamped Governance policy version; it never invents, relaxes, or loses a restriction (F3, §18).

---

## 7. Logical components

| Component | Responsibility | Explicitly not responsible for |
|---|---|---|
| **Intake Listener** | Consumes Capture's landing/change notifications; resolves them to a discovery-window batch | Deciding what to capture, or how |
| **Topic Resolver** | Segments a batch into topics; attaches to an existing topic or creates one; carries participant refs (internal) or pattern refs (external) | Ranking topics for retrieval; the continuity-matching mechanism itself (delegated, §26 item 4) |
| **Entity & Relation Extractor** | Extracts type-level entities and relations per topic; aggregates relation weight across topics; applies vocabulary normalization (best-effort, not a fixed ontology) | Resolving instance identity (out of scope, ADR-0009) |
| **Schema Bootstrap Adapter** | Reads structural sources (ERP/warehouse schema, ontology/catalog versions) landed by Capture; seeds the baseline entity set | Reading ERP operational records — structurally forbidden |
| **Package Compiler** | Builds/updates Context Packages from topics + entity/relation evidence; produces Claims with supporting/contradicting evidence; writes the Compiler Manifest (with identity/integrity, §19) for every compilation run; derives package visibility via the stamped Governance policy (§18) | Choosing package granularity beyond the minimum contract (AI-designer territory); enforcing visibility |
| **Evidence Reference Ledger** | Tracks which raw evidence items are referenced by which live packages; issues/releases holds; the GC-protection mechanism; retains references for Restricted/Withdrawn packages (§13.2, F2) | Performing GC itself — that remains Capture/landing-area machinery, informed by the Ledger |
| **Governance Interface** | Routes hold requests, restriction flags, and confidentiality/removal concerns to Governance & Trust; executes only governance-issued restriction/withdrawal/erasure/restoration decisions; propagates an erasure obligation across evidence, claims, packages, manifests, projections, audit stubs (§15.2) | Making the restriction/removal/restoration decision itself |
| **Trigger & Recompilation Controller** | Evaluates event-driven, time/batch, manual, and boundary-crossing triggers; schedules recompilation | Blocking Serve reads on recompilation (forbidden, §12); concluding truth or resolving disagreement |
| **Continuous Learning Feed** | Assembles attributable evaluation/outcome lineage for pull by Continuous Learning | Retraining or globally rewriting compiler behaviour from one response (forbidden, compile draft §8) |

---

## 8. Logical interface contracts

Named operations, not a protocol. No transport, format, or vendor implied.

**Capture → Compile**
- `notifyLanded(sourceRecordRef, envelope, correlation: {status: linked|ambiguous, priorVersionRef?})` — triggers intake. `envelope` carries per-record `visibility_class`/ACL provenance (F3).
- `notifyStructuralSource(schemaRef, catalogVersion)` — triggers Schema Bootstrap Adapter.

- `submitCorrectionReport(topicOrPackageId, reporterId, reasonText)` — ADR-0011: one action, required free text, no categories. Accepted as new evidence; never an in-place repair (§15.1, F5).
- `undo(evaluationOrReportId, actorId)` — compensating event, never a mutation.

**Compile → Serve** (Compile exposes; Serve alone scopes/ranks/collapses — F1 boundary)
- `getPackage(packageId, asOf?)` — returns a package at current or historical state; includes claims, evidence refs (not raw content — Serve/agent resolves those against Capture's landing area), **per-evidence visibility metadata and the derived package classification with its policy-version stamp** (F3), **relation weights referenced by the package's claims** (F1), scores (uncollapsed, per-rater), evaluations, `compiler_manifest_ref` with `manifest_identity` (F4), reproducibility field, and `known_gaps[]` (negative space). Restricted/Withdrawn/Deleted packages are **not** returned to Serve as servable content (§11); a Deleted package resolves only to its non-content audit stub.
- `getTopicGraph(scopeHint?)` — returns topic/entity/relation structure **including aggregate relation weight and contributing-topic refs** for Serve's Level-1 graph scoping (ADR-0014); Compile supplies the structure and the weights, Serve does the scoping and selection.
- `notifyPackageChanged(packageId, newVersion)` — passive change feed, consistent with the framework's "no outbound triggering" stance (§4 of phase-1-framework): notification, not an invocation of anything downstream.

> **What Serve does with this (out of scope, stated only to fix the F1 boundary):** Serve scopes the topic graph, selects packages, collapses the retained per-rater score set relative to the consuming context (ADR-0010), fills a token budget, and returns found/not-found negative space to the agent (ADR-0014). Compile designs none of that; §21 shows the data crossing this line intact, not how Serve transforms it.

**Compile → Governance & Trust**
- `requestHold(evidenceRefOrPackageId, reason)`
- `raiseConcern(packageId, evaluationRef, concernType: confidentiality|removal|other)`

**Compile → Continuous Learning**
- `pullEvaluationEvidence(since)` — returns the attributable lineage described in §17.

---

## 9. Minimum Context Package Contract (logical data model)

This is the floor every implementation must satisfy — analogous in spirit to Capture's Minimum Envelope. It is **not** the universal package schema the compile draft rules out (§4.2); topology, splitting/merging, indexing and traversal remain open (§26 item 5).

**Context Package**
- `package_id` — durable identity across versions.
- `version` — monotonic within the package's lineage.
- `state` — see §11 (Proposed | Active | Contested | Restricted | Withdrawn | Deleted | Superseded).
- `supersedes` / `superseded_by` — lineage pointers.
- `topic_refs[]` — the topic(s) this package draws evidence from.
- `entity_relation_refs[]` — the aggregated typed relation(s) this package's structure derives from, **each carrying `aggregate_weight` and `contributing_topic_refs[]`** so relation weight is a first-class package output (F1).
- `claims[]` — see below.
- `known_gaps[]` — explicit missing-evidence markers (§16), distinct from contradiction; surfaced to Serve as negative space (F1).
- `scores[]` — per-participant Value×Volatility records, each `{rater_id, role, value, volatility, reason, timestamp}`; **never collapsed here** (ADR-0010) — collapse is Serve's job (§17).
- `evaluations[]` — append-only human evaluation records (§8).
- `reports[]` — append-only correction reports (ADR-0011), each with undo status.
- `compiler_manifest_ref` — see below. **Required, non-null, and its `manifest_identity`/integrity digests must be well-formed** (F4; NF2).
- `reproducibility` — `{status: reproducible | non-reproducible, reason?}`. **Required.** `reproducible` means it satisfies the replay-equivalence criterion (§19).
- `governance` — `{visibility_derivation: {derived_class, policy_version_ref}, hold_refs[], restriction_state}`. The package-level class is a **derived** value, always accompanied by the Governance policy version that derived it; the per-item source visibility lives on each Evidence Reference below (F3).
- `created_at`, `last_compiled_at`, `last_reaffirmed_at`.

**Claim** (nested/linked within a package)
- `claim_id`, revision chain (append-only, supersession pointers — never in-place edits).
- `statement` — a derived artifact, itself linked back to originals per ADR-0004.
- `kind` — one of: fact-observation | attributed-interpretation | ai-inferred-interpretation | assumption/hypothesis | causal-explanation | routing-pointer (a pointer to the system of record that owns the actual fact, per ADR-0013; carries the SoR identity, never the operational value).
- `epistemic_basis` — one of the §5.10 taxonomy: temporal-sequence | observed-association | human-attributed-cause | ai-inferred-cause | repeated-pattern | stronger-causal-evidence | competing/unresolved.
- `supporting_evidence[]`, `contradicting_evidence[]` — Evidence References. **A claim with neither must be typed `assumption/hypothesis` and marked unsupported; there is no other way to have zero evidence.** This is schema-checkable at 100% (NF1, F6 item 8).
- `contradicts[]` — links to other claim_ids representing an unresolved alternative. No precedence assigned by Compile, ever. The presence of a live `contradicts[]` pair is what defines a package's Contested state (§11, F5).
- `compiler_manifest_ref`, `reproducibility` — same shape as package-level, since a package can be reproducible overall while one claim inside it isn't (e.g., one claim's evidence expired).

**Evidence Reference**
- `evidence_ref_id`, `capture_id`, `source_system_id`, `source_version`.
- `visibility_class`, `acl_provenance` — **the per-item recorded visibility/ACL metadata, carried verbatim from Capture's Envelope (F3). Never re-derived, downgraded, or dropped here.** This is what makes a mixed-visibility package representable (FV13).
- `content_digest` — a technology-neutral digest of the exact referenced content version, used for manifest input identity and replay (F4, §19).
- `role` — supporting | contradicting | inconclusive (relative to a specific claim).
- `linkage_confidence` — deterministic | best-effort-ambiguous (carried from Capture's correlation field, §5.1).
- `hold_status` — referenced-by-live-package | referenced-by-restricted | referenced-by-withdrawn | governance-hold | none (drives GC eligibility, §13.2, F2).

**Compiler Manifest** (F4 — proves reproducible lineage, not mere presence)
- `manifest_id`, `manifest_version`.
- `manifest_identity` — a content digest over the identity-defining tuple: `(compiler_identity_version, ruleset_version, ordered_input_digest, policy_version_set)`. Two runs asserting the same computation must produce the same `manifest_identity`; this is the key replay checks against.
- `compiler_identity_version` — technology-agnostic "which compiler configuration produced this."
- `ruleset_version` — segmentation parameters, extraction ruleset, scoring-model version.
- `policy_version_set` — `{visibility_derivation_policy_version, governance_ruleset_version, retention_policy_version}` (the governing policies in force at this run, F3/F2).
- `input_evidence_snapshot[]` — the **exact, ordered** inputs read, each `{evidence_ref_id, source_system_id, source_version, content_digest}`. Replaces the opaque `input_evidence_set_ref`.
- `ordered_input_digest` — digest over `input_evidence_snapshot[]` in order (order is part of identity when the compiler is order-sensitive; disclosed under `nondeterminism_disclosure` when not).
- `prior_state_ref` — `{superseded_package_version, superseded_package_digest}` — the lineage this run advances (null for a first version).
- `produced_outputs[]` — `{package_id, version, package_digest, claim_ids[]}` — what this run produced.
- `output_digest` — digest over `produced_outputs[]`.
- `manifest_digest` — integrity digest over the whole manifest (tamper-evidence).
- `timestamp`.
- `nondeterminism_disclosure` — the enumerated set of output fields permitted to vary across an otherwise-identical replay (e.g., "extraction step uses a sampling-based interpreter; free-text `statement` phrasing may vary; claim ordering may vary"). Anything **not** in this set must replay byte-identical or the package is a reproducibility defect (§19, NF10).

**Topic**
- `topic_id`, `created_at`, `last_active_at`, `window_metadata` (the ingestion interval that produced/updated it).
- `entity_relation_evidence[]` (per-topic, pre-aggregation).
- `participant_refs[]` (internal) or `external_pattern_refs[]` (external — distinct-source count, time window; **no participant identity**, since nobody rates external signals, §14.5).
- `linked_evidence[]`.
- `continuity_lineage[]` — append-only record of reattach/merge events so cross-thread continuity, however it is later mechanized, leaves an unbroken evidence trail (F6 item 4 bound; §14.1).

**Entity / Relation**
- `entity_id`, `label`, `origin` (baseline-from-schema | conversation-derived).
- If conversation-derived: `validation_state` (pending-human-gate | confirmed | rejected) — ADR-0015's placeholder, given a concrete home in §14.3. A `pending-human-gate` entity is **never** a first-class graph node (FV10).
- Relation record: `(entity_a, relation_label, entity_b, aggregate_weight, contributing_topic_refs[])` — `aggregate_weight` is Compile's output; ranking over it is Serve's (F1, §14.2).

---

## 10. Workflow

```text
Capture landing/change notification
        │
        ▼
Intake Listener — resolve discovery-window batch, honour correlation/ambiguity + per-record visibility flags
        │
        ▼
Topic Resolver — segment; attach to existing topic or create new (continuity branch, §14.1)
        │
        ├──▶ Entity & Relation Extractor — per-topic entities/relations
        │            │
        │            ▼
        │    Aggregate relation weight across topics
        │            │
        └────────────┴──▶ Package Compiler
                                │  builds/updates Context Package(s):
                                │   - claims with supporting + contradicting evidence
                                │   - known_gaps where evidence is absent
                                │   - per-evidence visibility carried; package class derived + policy-stamped
                                │   - compiler manifest (identity + integrity) for this run
                                │   - reproducibility assessment against replay criterion
                                ▼
                        Context Store (versioned)
                                │
                    ┌───────────┼────────────────┐
                    ▼           ▼                ▼
              Surface        (getPackage/     Feed (evaluation/
              (evaluations,   getTopicGraph    outcome lineage)
              corrections)    → AGENT, §21)
                    │
                    ▼
        new evaluation/report → accepted as evidence → Trigger & Recompilation Controller
        → schedules a new Package Compiler run → new version, supersedes prior (never in-place)
```

This is a **dependency order, not a strict pipeline** — the Entity & Relation Extractor and Topic Resolver operate per-batch and fan out across topics concurrently, consistent with ADR-0014's fan-out principle applied one layer earlier.

---

## 11. State model

**Context Package state machine** (F2 — four distinct governance states, no longer conflating quarantine with terminal tombstone; F5 — determinate contested transitions):

```
              (compiler run, min. evidence/coverage
               threshold — AI-designer defined, §13.1)
   Proposed ─────────────────────────────────▶ Active
                                                  │  ▲
             live contradicts[] pair exists       │  │ contradiction no longer present in the
             in the compiled evidence set         ▼  │ compiled evidence set (superseding evidence
                                                Contested │ arrived) — never by fiat/vote/seniority
                                                  │  │
                                                  ▼  │  (auto-quarantine on raise; references RETAINED)
                                              Restricted ── restore (governance) ──▶ Active/Contested
                                                  │
                              Governance decision (receiveDecision)
                       ┌──────────────────────────┼────────────────────────────┐
                       ▼                           ▼                            ▼
                 restore →                   Withdrawn (soft:              Deleted (hard erasure:
                 Active/Contested            served: NO; history &         removal obligation propagated;
                                             evidence RETAINED &           only a non-content audit stub
                                             reconstructable;              remains; nothing recoverable
                                             references RETAINED)          via lineage) — governance-only
                                                  │
                                          restore (governance) ──▶ Active/Contested

   Any Active/Contested state, upon a new compiled version → prior version becomes
   Superseded (append-only lineage; history retained; queryable "as of" its own
   timestamps). References release only if no live/Restricted/Withdrawn package and
   no governance hold still protect the evidence (§13.2).
```


|---|---|---|---|
| Proposed → Active | Compiler run meets promotion threshold | Package Compiler (AI-designer sets threshold within §13.1 bounds) | Threshold tuning cannot suppress `contradicting_evidence[]` |
| Active → Contested | A live `contradicts[]` pair exists in the compiled evidence set | Package Compiler (deterministic on evidence state) — **not** a human "declaring" disagreement | Contested is entered whenever contradiction exists; it is a fact of the evidence, not a judgment |
| Contested → Active | The contradiction is no longer present because superseding evidence removed one side | Package Compiler (deterministic on evidence state) | Never exited by fiat, vote, seniority, or a single report; requires an evidence trail (F5) |
| Active/Contested → Restricted | A confidentiality/removal concern is raised | Governance Interface (quarantine is **automatic** on raise; references **retained**) | Auto-quarantine pulls the package from Serve without any deletion; nothing is released yet |
| Restricted → Active/Contested | Governance restore decision | Governance & Trust exclusively | Restoration is clean because references were retained |
| Restricted → Withdrawn | Governance soft-withdrawal decision | Governance & Trust exclusively | Evidence, history, references **retained**; package not served (§15.2) |
| Restricted/Withdrawn → Deleted | Governance hard-erasure decision | Governance & Trust exclusively | Erasure obligation propagates; only a non-content audit stub survives (§15.2) |
| Withdrawn → Active/Contested | Governance restore decision | Governance & Trust exclusively | Restoration is clean because references were retained |
| Any Active/Contested → Superseded | New compiled version | Package Compiler, always append-only | Prior version stays retrievable "as of" its timestamps |

**Four distinct events behind "a correction happened"** (F5 — separated so one report has a defined, bounded effect):


**Bounds that hold regardless of any AI-designer threshold (F5):**
- One report can never be silently treated as truth — it is evidence (event 1), requires a run (event 3), and the run may not delete the contradicting claim.
- A disagreement can never disappear without a superseding-evidence trail (event 4).
- The repair *threshold* (how much/what evidence a run needs before it supersedes) is an AI-designer choice (§26 item 3, class b) **only inside** these bounds.

**Claim** and **Evidence Reference** follow the same append-only/supersession discipline; there is no independent state machine beyond "current vs. superseded" plus the governance-erasure exception (§15.2).

---

## 12. Triggers and recompilation

Carried from Compile draft §6, unchanged in substance, with the F5 event separation made explicit:

- **Event-driven** — a new signal lands affecting a topic/relation.
- **Time-based/batch** — the same interval-window mechanic as ADR-0009's ingestion window.
- **Manual** — an operator or governance action.
- **Boundary-crossing** — a package reaches a change/parameter threshold (AI-designer defined).
- **Human evaluation/correction** — a submitted evaluation or report is **accepted as new evidence** (event 1, §11) and **schedules recompilation** (event 2); it **does not itself rewrite anything** — the next compiler run consumes it (events 3/4). This is the F5 fix: the trigger and the state effect are separate, sequenced, and bounded.
- **Agent-exposed gap** — Serve reports back that an agent's request exposed missing knowledge (this is the "assumption declared" loop, ADR-0003, arriving from downstream).

**Hard invariant (from the framework's §4, extended one stage):** recompilation must never block a Serve read. No Serve read path may be gated on a recompilation lock. If a signal has landed but not yet been compiled, Serve reads the last compiled version and receives staleness metadata. This is NF4 (§23) — stated as a structural invariant (pass/fail: does any read path depend on a compile completing?), with production latency numbers deferred to Phase 2 (§26 item 10).

Compilation must be possible online and offline (compile draft §6) — this document takes no position on what "offline" means technically; it is a requirement on the design, not an implementation instruction.

---

## 13. Evidence selection, promotion and retention

### 13.1 Favourable and unfavourable evidence selection/promotion

**Promotion must not selectively favour confirming evidence.** This is a named trap (§20): an AI compiler under pressure to produce a clean package will tend to promote supporting evidence and quietly under-represent contradicting evidence. The Package Compiler contract requires:

- Every claim's `contradicting_evidence[]` field exists and is populated whenever contradicting evidence was found — omission is a defect, not a simplification.
- Inconclusive evidence (`role: inconclusive`) is retained and linked, not discarded for being ambiguous.
- A claim's `epistemic_basis` must reflect the *weakest* honest characterization the evidence supports — e.g., an observed association must not be silently promoted to attributed-cause because it is more useful-sounding.

Promotion from Proposed → Active packages is a **coverage/threshold** decision (AI-designer territory, §26 item 5) but the requirement above is a framework invariant regardless of how promotion thresholds are tuned, and no threshold may suppress contradiction or force a Contested exit (§11, F5).

### 13.2 Evidence references, holds, retention and GC implications (F2 — reconciled with §15)

The working rule, carried from compile draft §10, made concrete via the Evidence Reference Ledger and now **consistent** with the tombstone/withdrawal semantics:

> A retained Context Package protects its linked raw evidence past Capture's discovery-window landing expiry. Append-only references or retention flags keep it alive; GC removes evidence only when **no** live/Restricted/Withdrawn package references it and **no** governance hold protects it.

Reference retention/release by state — this is the exact table that closes the F2 contradiction (Round 1 §13.2 released references on Tombstone, which destroyed the "reconstructable history" §15 promised):

| Package state | Evidence references | Governance holds | GC-eligible? | What is reconstructable |
|---|---|---|---|---|
| Active / Contested | `referenced-by-live-package` — **retained** | as issued | No | Full package + evidence |
| Restricted (quarantine) | `referenced-by-restricted` — **retained** | retained | No | Full package + evidence (not served) |
| **Withdrawn (soft)** | `referenced-by-withdrawn` — **retained** | retained | No | **Full history + evidence, internally reconstructable; not served** |
| Superseded | released **only if** no live/Restricted/Withdrawn package and no hold still reference the item | independent of state | Only when unreferenced **and** unheld | Package version retained; a superseded package may legitimately become non-reproducible (`evidence-expired`, §19) if its evidence was orphaned and GC'd |
| **Deleted (hard erasure)** | released as part of erasure; erasure obligation **propagated** (§15.2) | released except the audit-stub record | Erased content is destroyed, not GC-deferred | **Only the non-content audit stub** — nothing of the deleted content is recoverable via lineage metadata (FV11) |

- `hold_status = governance-hold` is independent of package state and can outlive package supersession (e.g., a legal hold on evidence whose package has since moved on).
- **This is Compile's obligation, not Capture's** — Capture defines the discovery window; Compile is what tells Capture's landing area "don't expire this yet" via the Ledger. Withdrawn is the concrete fix for F2: soft withdrawal **retains** references precisely so its history stays reconstructable, contradicting the Round 1 behavior that released them.

---

## 14. Topic, entity and graph resolution

### 14.1 Topic segmentation and continuity (F6 item 4 — invariant kept, mechanism delegated, walkthrough branch marked)

Per ADR-0009: segment the interval-window delta, attach to an existing topic where the content fits, otherwise create one. Cross-thread/cross-channel continuity — a discussion resuming weeks later — is **not solved here** (framework open question §7.3).

**Classification (F6):** this is class **(b)** — a *framework invariant* with the matching mechanism delegated to the future AI designer. The invariant, which any mechanism must satisfy: reattachment (or a later human merge) must leave `continuity_lineage[]` an **unbroken evidence trail**; no reattach may silently drop or rewrite prior evidence. The invariant is validated by FV1; the *matching algorithm* is AI-designer territory (§26 item 5). Walkthrough §21.1 marks its reattach step as an explicit **conditional branch** so continuity is never presented as demonstrated behavior (F6).

### 14.2 Entity and relation extraction

Per ADR-0012: entities are types (`customers`, `pricing`), never instances; relations are derived per topic and aggregated across topics so a relation gains weight from recurrence. Compile must avoid the "hub problem" — value lives in the typed, aggregated relation, never in a shared high-frequency node. Traversal (Serve's concern) follows relations, not co-mentions; Compile's obligation here is to **produce** relations with `aggregate_weight` and `contributing_topic_refs[]`, and to expose that weight through `getTopicGraph`/`getPackage` (F1) — not to rank them for retrieval.

### 14.3 Bootstrap from structure, human-gated enrichment

Per ADR-0015: the Schema Bootstrap Adapter seeds the baseline entity/relation set from ERP/warehouse **structural** sources (schema, entity-relationship model, ontology/catalog version) landed by Capture — never operational records. Baseline entities are bound to their source dimension by construction; nothing to map.


### 14.4 Vocabulary drift

Per ADR-0012's own carried-forward risk: `complain about` and `raise issues with` may fragment the same fact into separate relations. This design does not solve normalization (AI-designer territory) but requires the Extractor to record enough (raw extracted label plus any applied normalization) that a later re-derivation pass can retroactively merge fragmented relations without losing history — consistent with append-only evolution.

### 14.5 Internal vs. external topics


---

## 15. Restriction, soft withdrawal, hard erasure and restoration — without accidental history rewrite (F2)

Round 1 collapsed "tombstone" into two incompatible meanings. This section defines **four** distinct governance-lifecycle mechanisms, matched to the Preserve amendment's sequence ("restriction, official decision, then deletion or restoration"), and states for each exactly what is retained or released and what remains reconstructable. Ordinary correction (§15.1) is separate again and always available.

### 15.1 Ordinary correction (soft, Compile-internal, always available — no governance)

A correction report or factual-correction evaluation is **accepted as new evidence** (event 1) and **schedules recompilation** (event 2). It **never mutates** the prior claim or package. The next compiler run produces a new version that **supersedes** the old (event 3). Both versions remain independently retrievable "as of" their own timestamps. This is the normal path and requires no Governance involvement — it is how the graph self-corrects over time. ADR-0011 is explicit that a single report is *evidence*, not automatic repair; it takes a compiler run to act on it, bounded by §11's F5 invariants.

### 15.2 Governance lifecycle — the four mechanisms


1. **Restriction (temporary quarantine).** On concern raised (`raiseConcern`), Compile **automatically** moves the package to `Restricted` and pulls it from Serve. **Nothing is released:** references stay `referenced-by-restricted`, holds retained, evidence intact, history intact. This is the reversible holding step *before* any official decision. Reconstructable: everything.
2. **Restoration.** Governance decides `restore`. The package returns to `Active`/`Contested`. Because Restriction (and Withdrawal, below) retained all references, restoration is clean — no evidence had to be re-fetched or reconstructed. Reconstructable: everything, unchanged.
3. **Soft withdrawal (governance-approved, history retained).** Governance decides `withdraw`. The package moves to `Withdrawn`: it **stops serving**, but its **evidence, references, and full history are retained and internally reconstructable**. A `superseded_by`-style marker records "removed-from-service, not removed-from-record." This is the durable "we no longer serve this, but we did not erase it" state. Reconstructable: full history and evidence, internally. **This is the concrete fix for F2** — the Round 1 draft released references on tombstone, which is what made history unreconstructable; Withdrawn does not release them.

**Propagation rule (erasure):** an erasure that leaves the content recoverable through any lineage path — a manifest input snapshot, a superseding version's evidence pointer, a projection, an audit stub that embeds content — is a design defect (FV11). The audit stub is the *only* surviving artifact and it is non-content by construction.

Compile itself never invents a restriction, withdrawal, erasure, or restoration criterion. A component that removes on its own judgment is a design violation (FV6, §22).

---

## 16. Contradiction, uncertainty, staleness, ambiguity and missing-evidence semantics

| Phenomenon | Representation | Non-negotiable rule |
|---|---|---|
| **Contradiction** | Two claims, each with its own evidence, linked via `contradicts[]`; a live pair defines Contested state (§11) | Compile never picks a winner. No precedence, no vote, no seniority weighting (§5.6). Contested is exited only by superseding evidence, never by fiat (F5) |
| **Uncertainty** | `epistemic_basis` taxonomy on every interpretive/causal claim | The weakest honest basis is used, never inflated |
| **Staleness** | Derived from the bound Volatility score(s) plus elapsed time since `last_reaffirmed_at` | Staleness is metadata attached to a claim/package, never silently used to suppress it |
| **Ambiguity** | `linkage_confidence: best-effort-ambiguous` on an Evidence Reference, carried from Capture | Ambiguous lineage is never presented as deterministic |
| **Missing evidence** | `known_gaps[]` on a package, distinct from a `contradicting_evidence` entry; surfaced to Serve as negative space (F1) | **Missing evidence is not proof of absence** (§5.9) — Compile must not fabricate a value, and must not silently drop the topic because it has a gap |
| **Visibility** | Per-evidence `visibility_class`/`acl_provenance`; derived, policy-stamped package class (F3) | Never downgraded, manufactured, or lost through aggregation/supersession/correction/withdrawal/erasure (FV13) |

This table operationalizes compile draft §5.8–§5.10 into fields any implementation must expose.

---

## 17. Scoring interfaces — the Compile/Serve boundary

Compile owns:

- Assigning the **initial** Value×Volatility score with reason, at ingest into Compile, for internal signals (two-step per ADR-0008: capture raw with no privileged sources → initial model-assigned score with reason).
- **Retaining every rater's score, reason, and role** — internal human raters plus the initial model score — **never collapsing them** (ADR-0010). This is a hard invariant, not an optimization; see NF6, §23.
- Refreshing scores continuously via the Continuous Learning Feed as reuse/recall data returns from Serve.
- Recording the raw external pattern signal (distinct-source count over a window) as evidence on the topic — **not** as a score, because no rating mechanism for external signals exists (§14.5; open owner decision §26 item 1).

Serve owns (out of scope here, referenced only for the F1 boundary):

- Collapsing the retained multi-rater score set **at retrieval, relative to the consuming context** (ADR-0010) — e.g., weighting marketing raters higher for a marketing task.
- Ranking, coverage optimization, and the negative-space contract (ADR-0014).

Compile's obligation to Serve is to expose the **uncollapsed** score set with full attribution and the relation weights — collapsing or ranking earlier would foreclose Serve's per-consumer behavior and violate ADR-0010/0014. The §21 walkthroughs show this uncollapsed set and weight crossing the boundary to the agent intact (F1).

---

## 18. Governance & Trust boundary (F3 — visibility derivation named)

Governance & Trust owns, and Compile consumes without redefining:

- The discovery-window and retention policy Capture enforces and Compile's Evidence Reference Ledger respects.
- ACL/visibility **recording standards** and the **visibility-derivation policy** by which a package-level classification is computed from its bound evidence. Compile carries per-evidence `visibility_class`/`acl_provenance` (F3) and derives the package `visibility_derivation.derived_class` **only** by applying this Governance-owned policy, stamping `policy_version_ref`. Compile does not choose the rule and enforces nothing (ADR-0006). If the policy is absent or ambiguous, Compile records the most restrictive bound of the constituent evidence and flags a governance gap — it never downgrades (FV13).
- Consent for any elicitation-sourced signal (Capture's concern; Compile treats elicited signals identically to any other captured signal per the common-pipeline principle).
- The restriction/withdrawal/erasure/restoration decision (§15) — Compile requests, quarantines, and executes; it never decides.
- The enterprise-controlled trust boundary and deployment risk choice (Compile draft §11) — entirely outside this document's technology-agnostic scope.
- The security tier and threat model for Phase 2 (§1) — not designed here.


---

## 19. Reproducibility and the compiler manifest (F4 — identity, integrity, replay equivalence)

**Every Claim and every Context Package binds a `compiler_manifest_ref` and a `reproducibility` field. This is not optional and not deferred — it is the mechanism that makes "governed, reproducible" in this design's charter checkable at all.** Round 1's manifest proved only *presence*; this section defines the *lineage* it must prove.

**Manifest identity.** `manifest_identity` is a content digest over `(compiler_identity_version, ruleset_version, ordered_input_digest, policy_version_set)`. It answers "which exact inputs and versions were read, under which compiler/ruleset/governance-policy identities" as a single comparable key. Two runs claiming the same computation must yield the same `manifest_identity`.

**Manifest integrity.** `ordered_input_digest`, `output_digest`, and `manifest_digest` make the manifest tamper-evident and let a verifier confirm the recorded inputs and outputs are exactly those that were read/produced (via each Evidence Reference `content_digest` and each `package_digest`). `prior_state_ref` binds what state this run superseded, so lineage is a chain, not a set of islands.

**Replay-equivalence criterion.** A replay of a package/claim is **equivalent** iff:
1. its `manifest_identity` matches (same compiler/ruleset/policy versions and same ordered inputs by digest), **and**
2. every `input_evidence_snapshot[].content_digest` still resolves to un-GC'd, un-erased evidence, **and**
3. the recomputed `output_digest` matches the recorded one **after masking exactly the fields enumerated in `nondeterminism_disclosure`** (the permitted variance — e.g., sampling-driven `statement` phrasing or claim ordering).

Any variance **outside** the disclosed set means the package is **not** reproducible — a manifest-completeness defect, not a documentation nuance (NF10). `reproducibility.status = reproducible` asserts this criterion is met.

`reproducibility.status = non-reproducible` must carry an enumerated `reason`, at minimum one of:

- `evidence-expired` — a bound evidence item has since been GC'd (should not happen while a package is live/Restricted/Withdrawn, per §13.2, but a Superseded package can legitimately hit this).
- `compiler-version-retired` — the manifest references a compiler configuration no longer available to replay.
- `inherent-nondeterminism` — a compilation step is disclosed as non-deterministic beyond the maskable set (e.g., a sampling interpreter whose output structure varies) even with identical inputs.
- `governance-redaction-applied` — evidence was restricted/withdrawn/erased by Governance since compilation.
- `ephemeral-external-source` — an external signal's source may no longer be retrievable at replay time (platform-side deletion/edit) — the anticipated common case for social-feed evidence, called out explicitly because it will otherwise be discovered the hard way.
- `policy-version-retired` — a governing policy version in `policy_version_set` is no longer available to reproduce the derivation.
- `unknown` — reproducibility could not be determined; this must itself be treated as a defect to investigate, not a safe default.

A package or claim reporting `reproducible` that does not satisfy the replay-equivalence criterion is a design defect (NF10, §23), audited at 100% for the schema-checkable parts (identity/integrity well-formedness) and by replay sample for the equality parts (FV14).

---

## 20. Failure modes and common architectural traps

Extends compile draft §15 with lifecycle-boundary-specific traps found while reconciling this design against the ADR baseline and the Round 1 findings:

1. Treating Context Packages as document summaries without evidence lineage.
2. Hard-coding a human-designed package taxonomy before testing AI consumption.
3. Silently rewriting packages instead of appending revision history.
4. Flattening disagreement or competing causal explanations into one clean narrative.
5. Treating majority opinion or seniority as factual truth.
6. Optimizing for swipe/evaluation approval while business outcomes do not improve.
7. Treating correlation as causation.
8. Treating missing evidence as false.
9. Letting official documentation erase observed practice, or vice versa.
10. Turning Compile into a shadow system of record.
11. Allowing packages to authorize actions.
12. Deleting raw evidence still referenced by a retained (including Restricted/Withdrawn) package.
13. Retaining orphan evidence indefinitely with no live reference and no policy hold.
14. Designing proactive-agent behaviour inside Compile.
15. Treating future outcome knowledge as available at the decision time being reconstructed.
16. **Collapsing rater scores inside Compile instead of leaving collapse to Serve** — silently reintroduces the single-scalar failure ADR-0008/0010 exist to prevent.
17. **Letting entity creation silently stall** because nobody performs the human validation gate (ADR-0015) — the graph stops growing with no visible alarm.
18. **Treating a correction report as automatic repair** — ADR-0011 is explicit that reports are evidence, requiring a compiler run to act on them; a report is not a mutation.
19. **Importing Serve's two-level agent-native retrieval logic into Compile** — scoping/ranking/budget-filling/collapse belong downstream; Compile produces structure, not answers.
20. **Selectively promoting confirming evidence** while under-populating `contradicting_evidence[]` (§13.1) — the most likely place an AI compiler quietly cheats toward a cleaner-looking package.
21. **Assigning an urgency score with no consumer** — carried forward from ADR-0008's rejection of urgency as a v1 axis.
22. **Releasing evidence references on soft withdrawal** — the exact Round 1 F2 contradiction; soft withdrawal must retain references so history stays reconstructable (§13.2, §15.2).
23. **Collapsing mixed-visibility evidence to a single package label without a stamped policy version, or downgrading a restriction on aggregation** (F3, §18).
24. **Treating a non-null manifest pointer as proof of reproducibility** — identity, integrity, and replay-equivalence must be checkable (F4, §19).
25. **Exiting a Contested state without a superseding-evidence trail**, or letting one report be treated as truth (F5, §11).
26. **Presenting an unresolved mechanic (cross-thread continuity, external scoring) as demonstrated behavior** in a walkthrough (F6, §21, §26).

---

## 21. End-to-end walkthroughs (F1 — extended through agent receipt)


### 21.1 Internal signal — a pricing exception (through the agent)

1. Capture lands new Slack messages (S2 onboarding path) in a thread about a pricing exception for a customer, each envelope carrying its per-record `visibility_class` (internal-confidential) and participants Account Owner, Sales Ops, Finance.
2. Intake Listener resolves the batch. **Conditional branch (cross-thread continuity, §14.1, class b — mechanism delegated):** *If* the Topic Resolver recognizes continuity, it attaches to the existing topic "pricing exception — Customer X," dormant three weeks, and appends a `continuity_lineage[]` entry. *If it does not*, a new topic is created and a later human split/merge signal (§14.1) reconciles them. **Either branch preserves unbroken evidence lineage;** continuity is not presented here as a solved mechanism.
3. Entity & Relation Extractor finds entities `customers`, `pricing`, `discount-policy`; the relation `pricing-exception → granted-for → customers` gains weight, aggregating with evidence from 12 other topics. Its `aggregate_weight` and `contributing_topic_refs[]` are recorded on the relation and referenced by the package (this weight is Compile output, F1 — Compile does not rank it).
4. Package Compiler produces two claims on package "Pricing Exception — Customer X" v(n+1):
   - **Claim A** (`attributed-interpretation`, `human-attributed-cause`): "Sales granted a temporary pricing exception pending Finance sign-off." `supporting_evidence` = the Slack thread; each Evidence Reference carries its `visibility_class` and `content_digest`.
   - **Claim B** (`assumption/hypothesis`): "Exception expires end of quarter." No supporting evidence found — typed as an assumption, not asserted as fact. This is exactly the gap ADR-0003's measurement loop depends on downstream.
5. Compiler manifest recorded with `manifest_identity`, `input_evidence_snapshot` (ordered, digested), `policy_version_set`, `produced_outputs` and digests; `reproducibility = reproducible` (deterministic segmentation, stable evidence set, satisfies the §19 criterion). Package `governance.visibility_derivation = {derived_class: internal-confidential, policy_version_ref: <Governance policy vN>}`.
7. Account Owner submits a `factual-correction` evaluation: "Expiry is 2026-09-30, per the exception memo." Per §11's F5 events: **accepted as new evidence** (no mutation), **recompile scheduled**.
8. Recompile: v(n+2) supersedes v(n+1) (event 3). Claim B is superseded by a new `fact-observation` claim citing the memo. Finance scores Volatility high ("must reverify before quarter close") while Account Owner scores it low — **both retained, uncollapsed** (ADR-0010). No `contradicts[]` pair exists, so the package is `Active`, not `Contested`.
9. **Agent receipt (the F1 exit condition).** A support-ops agent's task triggers Serve. Serve calls `getPackage("Pricing Exception — Customer X")` and `getTopicGraph`. The agent receives, unchanged from Compile: the two claims with their kinds and `epistemic_basis`; the relation `pricing-exception → granted-for → customers` with its `aggregate_weight`; the **complete uncollapsed score set** `[{Finance, volatility:high, reason}, {Account Owner, volatility:low, reason}, {model, initial, reason}]`; the manifest ref with `manifest_identity` and `reproducibility=reproducible`; the derived visibility class with its policy stamp; and any `known_gaps[]` (here, none on this claim). **Serve** — not Compile — collapses the score set for this consuming context and does the ranking/budget-filling (ADR-0014); those internals are out of scope and not shown.
10. **System-of-record routing (ADR-0013).** The agent needs the *current operational* discount record. Compile does not hold it; the package exposes a `routing-pointer` claim naming the CRM/ERP that owns it. The agent follows the pointer to the SoR for the live value; Compile asserted the why/how, never the operational fact.
11. **Trap check:** if the exception was never actually entered into the CRM/ERP as a real discount record, Compile flags this as a governance/data-stewardship gap (§5.2, ADR-0013) — surfaced as negative space, not filled by Compile.

### 21.2 External signal — customer onboarding friction (through the agent)

1. Capture lands a batch of public social-feed posts mentioning onboarding confusion, tagged external, `visibility_class = public`, no participant identity.
2. Topic Resolver attaches this to the **same** topic node as an existing internal topic, "onboarding — customer friction," previously raised by CS in Slack — because both concern the same subject (§14.5). (Same-subject attachment is structural, not the unresolved cross-thread-continuity mechanic.)
4. Entity & Relation Extractor strengthens `customers → complain-about → onboarding`, aggregating internal and external evidence against the same relation; the relation's `aggregate_weight` rises and its `contributing_topic_refs[]` now span both sources (F1 output).
5. Package Compiler produces two claims:
   - **Claim A** (`observed-association`): "External customers report friction at onboarding step 3." `supporting_evidence` = the social-feed posts (visibility public, `content_digest` recorded; reproducibility risk flagged, step 7).
   - **Claim B** (`fact-observation`): "The official onboarding runbook does not list step 3 as optional." `supporting_evidence` = the runbook (structural/document source).
   - These are linked via `contradicts[]` (official-vs-observed divergence, §5.7) — Compile does not decide which is "right." The live pair puts the package in **Contested** (§11); it can leave Contested only if superseding evidence removes one side (F5).
7. Reproducibility on Claim A is marked `non-reproducible`, `reason: ephemeral-external-source` — the social posts may be edited or removed by the platform before any replay attempt. The manifest still records their `content_digest` so the claim's *stated* provenance is checkable even when the source becomes unretrievable.
9. **Downstream (out of scope, stated for the boundary):** a proactive support-ops agent may later propose a runbook update for human approval — that workflow is explicitly outside Compile (Compile draft §12). Compile's job ended at exposing the unresolved, weighted, provenance-bearing divergence to the agent.

---

## 22. Functional validation cases (F7 — each with an unambiguous logical pass/fail)

| ID | Case | Pass/fail condition (Phase 1 logical conformance) |
|---|---|---|
| FV1 | A topic dormant 3+ weeks receives a new signal (either continuity branch, §14.1) | **Pass:** the resulting structure preserves unbroken `continuity_lineage[]` across the gap with no duplicated or dropped evidence, whether reattached or later human-merged. **Fail:** any evidence lineage break or silent duplicate. (Validates the invariant, not a specific matching mechanism.) |
| FV2 | Two authorized signals assert opposite claims about the same subject, each with valid evidence | **Pass:** two linked `contradicts[]` claims; package enters Contested; neither is marked authoritative. **Fail:** any precedence assigned, or Contested not entered. |
| FV3 | A human submits a factual correction | **Pass:** correction is accepted as new evidence (no mutation), a run produces a superseding version, both versions independently retrievable "as of" their time, correction attributable — exactly the four F5 events in order. **Fail:** any in-place mutation, or a version change not produced by a compiler run. |
| FV4 | A subject has zero evidence for an attribute an agent would need | **Pass:** an explicit `known_gaps[]` marker appears and reaches the agent as negative space; no fabricated value; topic not silently dropped. **Fail:** any fabricated value or silent drop. |
| FV5 | A live package references evidence nearing Capture's landing expiry | **Pass:** evidence is not purged while referenced by any live/Restricted/Withdrawn package or governance hold; release happens only per the §13.2 table. **Fail:** any purge while still referenced/held. |
| FV7 | Three participants score the same topic/package with materially different scores | **Pass:** all three stored independently, attributable, uncollapsed, and delivered uncollapsed to Serve. **Fail:** any collapse at the Compile layer. |
| FV8 | An external-source claim exists alongside internal human-rated claims | **Pass:** external provenance and **explicitly labeled** unrated status remain visible through every package version and reach the agent. **Fail:** unrated status lost or silently rendered as zero. |
| FV9 | A package's manifest references evidence since removed or a retired compiler/policy version | **Pass:** `reproducibility.status = non-reproducible` with an enumerated §19 reason. **Fail:** it still claims `reproducible`. |
| FV10 | A conversation-derived candidate entity refers to the same concept as an existing baseline entity | **Pass:** `validation_state = pending-human-gate`; entity does **not** enter the aggregated graph as a first-class node until `entity-validation: confirm`. **Fail:** any pre-gate graph entry. |
| FV12 | **(F2)** Governance authorizes soft withdrawal, then later restoration | **Pass:** on withdrawal the package stops serving but evidence/references/history are retained and internally reconstructable; on restore it returns to Active/Contested with no re-fetch needed. **Fail:** any reference released on withdrawal, or history unreconstructable after withdrawal. |
| FV13 | **(F3)** A package binds evidence items of differing visibility classes | **Pass:** each Evidence Reference retains its own `visibility_class`/`acl_provenance`; the package `visibility_derivation.derived_class` is the policy-derived label with a `policy_version_ref`, never below the most-restrictive constituent; no restriction lost through aggregation, supersession, correction, withdrawal, or erasure. **Fail:** any per-item visibility dropped or any downgrade. |
| FV14 | **(F4)** A package flagged `reproducible` is replayed | **Pass:** `manifest_identity` matches, all `content_digest`s resolve, and the recomputed `output_digest` matches after masking exactly `nondeterminism_disclosure`; manifest/input/output integrity digests verify. **Fail:** any variance outside the disclosed set, or any integrity-digest mismatch (a manifest-completeness defect). |

## 23. Non-functional validation cases and measurable success criteria (F7 — falsifiable or explicitly labeled a health signal)

| ID | Criterion | Pass/fail measure |
|---|---|---|
| NF1 | Provenance/assumption-typing completeness | **100%, schema-checkable (not sampled):** every claim in an Active/Contested package has ≥1 Evidence Reference OR is typed `assumption/hypothesis` with declared zero evidence. Any exception fails. (Closes F6 item 8 for the Compile layer; agent-side assumption declaration is out of scope, §26 item 8.) |
| NF2 | Manifest identity/integrity coverage | **100%, schema audit:** every claim/package carries a non-null `compiler_manifest_ref` whose `manifest_identity`, `ordered_input_digest`, `output_digest`, and `manifest_digest` are present and well-formed. A non-null-but-opaque pointer fails (F4). |
| NF3 | Append-only compliance | **Zero** in-place mutations of prior records outside supersession, soft withdrawal, and governance hard erasure — diff audit of history logs. |
| NF4 | Recompilation never blocks Serve reads | **Structural invariant, pass/fail:** no Serve read path is gated on a recompilation lock; a landed-but-uncompiled signal yields last-compiled + staleness metadata. Production latency numbers (workload, baseline, percentile, allowable regression) are a Phase 2 SLO (§26 item 10), not this gate. |
| NF6 | Rater disagreement retained | **Pass/fail:** nonzero, inspectable variance is preserved wherever raters materially disagree; a single collapsed number surfacing at the Compile layer fails outright. |
| NF7 | Discovery-window/GC correctness | **Zero** evidence purged while referenced by any live/Restricted/Withdrawn package or governance hold — reference-integrity audit of the Ledger against the §13.2 table. |
| NF9 | Vocabulary fragmentation | Distinct relation labels per entity pair vs. topic count — **explicitly a non-blocking health signal** (no numeric Gate 1 threshold), tracked over time. |
| NF10 | Reproducibility disclosure accuracy | **Two-part:** (a) 100% schema audit that identity/integrity digests are well-formed (with NF2); (b) replay sample of `reproducible`-flagged packages must satisfy the §19 replay-equivalence criterion — any variance outside `nondeterminism_disclosure`, or any digest mismatch, is a manifest-completeness defect (FV14). |
| NF11 | End-to-end agent consumption | **Pass/fail:** for one internal and one external signal, the structure delivered through `getPackage`/`getTopicGraph` to the agent contains relation weight, the uncollapsed score set (or the labeled unscored reason), manifest identity, per-evidence + derived visibility, routing pointer where an operational fact is needed, and `known_gaps[]` negative space — with **no** Serve ranking/collapse designed inside Compile. Fails if any element is missing or if any Serve internal leaks into Compile (validates F1 against §21). |
| NF12 | Visibility non-downgrade | **Pass/fail:** across aggregation, supersession, correction, withdrawal, and erasure, no Evidence Reference loses its recorded visibility and no derived package class falls below the most-restrictive constituent; every derived class carries a `policy_version_ref` (validates F3 against FV13). |

---


Preserved from Round 1 unchanged in substance; this revision reopens none of it.

- Lifecycle Capture → Compile → Serve → Continuous Learning, Governance & Trust cross-cutting (2026-09-02 amendment, Gate 1 closed).
- Capture lands complete authorized records within a policy-defined discovery window; semantic interpretation starts only in Compile (Capture blueprint, Gate 1 closed).
- Systems of record are authoritative for operational "what"; ECS supplies why/how and time-bound observations (ADR-0013).
- ERP operational records/status/transactions are not ECS sources; structural relationships/schemas/ontologies/entity models may be inputs (Capture blueprint, Preserve amendment).
- Topics as the unit of context (ADR-0009); type-level entities and derived, aggregated typed relations (ADR-0012); schema-bootstrapped, conversation-enriched, human-gated entity graph (ADR-0015).
- Preserve originals, translate/derive at consumption (ADR-0004).
- Two-axis Value×Volatility scoring with reasons, retained per-rater, never collapsed at write time (ADR-0008, ADR-0010); topic-grain, participant-routed rating; one free-text report action (ADR-0011); no autonomy gate this iteration.
- Serve is agent-only; retrieval mechanics, collapse-at-retrieval, and ranking (ADR-0014) belong to Serve, out of Compile's scope.
- Security: ACL recording without enforcement (ADR-0006); Phase 1 public-channel-only exposure; Phase 2 Tier 2, not designed here.
- The Preserve amendment's sequence — restriction, official decision, then deletion or restoration — governs §15's four mechanisms.
- Compilation occurs within an enterprise-controlled trust boundary; the specific pattern is an enterprise/Governance choice, not designed here.
- Personal-context vs. company-context boundary, and consequent central-vs-distributed compilation, are explicitly parked.

## 25. Recommendations (this document's proposals — not binding until accepted)

- The topic↔subject terminology mapping (§3), extended to split "tombstone" into Restricted/Withdrawn (§3, §11).
- The Minimum Context Package Contract (§9) as the concrete floor beneath the deliberately unspecified package topology, including the F3 per-evidence visibility fields and the F4 manifest identity/integrity fields.
- The package/claim/evidence state machine, including the **four** governance mechanisms — restriction, soft withdrawal, hard erasure, restoration (§11, §15) — and the F5 four-event separation.
- The Evidence Reference Ledger as the mechanism binding Compile's protection obligation to Capture's discovery-window GC, with the §13.2 retention table.
- The epistemic-basis taxonomy as claim-level metadata (§5.10).
- The Governance-owned visibility-derivation policy stamp (§18) as the recording-only way to label mixed-visibility packages.
- The replay-equivalence criterion (§19) as the checkable meaning of "reproducible."
- The functional/non-functional validation cases in §22–23, including the added FV11–FV14 and NF11–NF12.
- The failure-mode list in §20, including items 22–26 added while closing F2–F6.

## 26. Unresolved decisions — classified (F6)

Every open item is classified as: **(a)** blocking owner decision before Gate 1 can close (owner named); **(b)** framework invariant with mechanism delegated to the future AI designer (invariant/validation bound named); **(c)** Phase 2 implementation choice; or **(d)** explicitly parked separate scope. No item classified (b)/(c)/(d) is presented as demonstrated behavior anywhere in this document; §21 marks (b) branches conditional.

| # | Open item | Class | Owner / invariant-bound |
|---|---|---|---|
| 3 | **How correction reports become repairs (threshold)** | **(b) invariant, mechanism delegated** | Invariant/bounds: report is evidence, requires a compiler run, never auto-mutates, and cannot exit Contested by fiat (§11 F5 bounds, FV3). The *threshold* volume is the delegated AI-designer choice, only inside those bounds. |
| 4 | **Cross-thread/cross-channel topic continuity mechanics** | **(b) invariant, mechanism delegated** | Invariant: reattach/merge must leave `continuity_lineage[]` an unbroken evidence trail (FV1). Matching algorithm delegated (§14.1). Walkthrough §21.1 marks this a conditional branch, not demonstrated. |
| 5 | **Package granularity, split/merge, internal representation, indexing, traversal** | **(b) invariant, mechanism delegated** | Invariant/bound: must satisfy the Minimum Contract (§9). Topology delegated to the AI designer. |
| 7 | **Deployment/trust-boundary implementation pattern** | **(c) Phase 2 implementation choice** | Enterprise/Governance risk decision, outside technology-agnostic scope (§18). |
| 8 | **Machine-checkability of "assumption declared"** | **(b) invariant (Compile) + (c) out-of-scope (agent)** | Compile-side: a zero-evidence claim MUST be typed `assumption/hypothesis` and flagged — schema-checkable at 100% (NF1). Agent-side reliable declaration (ADR-0003) is a contract on something Compile does not own — Phase 2 / out of scope. |
| 9 | **Ranking/ordering competing causal explanations without erasure** | **(b) invariant (Compile) + Serve-owned ranking** | Compile invariant: retain and expose **all** competing explanations, rank none (FV2). Any ranking function is Serve's (ADR-0014), out of scope. |
| 10 | **Serve-side latency budget for recompile-vs-staleness** | **(b) invariant (Compile) + (c) Phase 2 number** | Invariant: recompile never blocks a Serve read; staleness metadata returned (NF4). The numeric budget is a Phase 2 SLO. |


---

## 27. Relationship to prior artifacts

- Every "confirmed framework requirement" in the 2026-09-03 wish list is either carried forward unchanged (§24) or given a concrete mechanism proposed as a recommendation (§25) — none is contradicted.
- Every falsification test proposed in the wish list has a corresponding functional or non-functional validation case in §22–23, now joined by the F1–F5-driven additions FV11–FV14 and NF11–NF12.
- Does not resolve the parked central-vs-distributed compilation issue (§26 item 6), per its own instruction not to resolve it implicitly.

---

## 28. References

- `docs/02-design/phase-1-framework.md` (doc-v4).
- ADR-0001 through ADR-0015 (Round 1 inspected at commit `38a53f3c5a44599b29f05b9e4eca7102c99ef6ff`).
- `docs/02-design/falsification-criteria.md`.
- ECS Capture-stage blueprint, 2026-09-02, and its Preserve-stage lifecycle-amendment Gate 1 final (2026-09-02).
- ECS Compile-stage blueprint draft, 2026-09-03 (interview-derived).

---

## 29. Consolidated Round 1 findings disposition ledger


- **F1 (walkthrough exit condition).** Closed. §21.1 steps 9–11 and §21.2 steps 8–9 carry both signals through Serve's documented read interface to the agent, exposing relation weight, uncollapsed scores (internal) / labeled unscored pattern (external), manifest identity, per-evidence + derived visibility, `known_gaps[]` negative space, and the SoR routing pointer — with the Compile/Serve boundary restated in §8 and §17 and no ranking/retrieval designed. Validated by NF11.
- **F2 (tombstone vs. release contradiction).** Closed. §11 splits the old single "Tombstoned" into Restricted, Withdrawn, Deleted, Superseded; §13.2's retention table states reference/hold retention per state (soft withdrawal **retains** references — the exact fix); §15.2 defines the four mechanisms and the erasure-propagation rule. Validated by FV5, FV11, FV12, NF7, NF8.
- **F3 (visibility collapsed).** Closed. §9 adds `visibility_class`/`acl_provenance` per Evidence Reference and a derived, policy-stamped package class; §18 names the Governance-owned derivation policy and the no-downgrade rule. Validated by FV13, NF12.
- **F4 (manifest proves presence not lineage).** Closed. §9's Compiler Manifest binds ordered digested inputs, prior-state lineage, produced outputs, policy versions, and integrity digests with a defined `manifest_identity`; §19 states the replay-equivalence criterion and permitted variance. Validated by FV9, FV14, NF2, NF10.
- **F6 (unresolved mixed with Phase 2).** Closed. §26 classifies all ten items a/b/c/d with owner (item 1: Genie) and invariant bounds; §14.1 and §21.1 mark continuity a conditional branch; no unresolved mechanic is presented as demonstrated.
- **F7 (unmeasurable validation cases).** Closed. §22 (FV1–FV14) and §23 (NF1–NF12) give each Gate 1 criterion an unambiguous logical pass/fail or an explicit non-blocking health-signal label; production numerics are labeled Phase 2; the F1–F5 missing cases are added.
- **Non-blocking editorial (page-one author).** Closed. The `Author: Bob` line is removed; page one attributes generation to the Claude Code A2A bridge recovery run `ecs-compile-stage-recovery-20260903`, route/owner friday, and reiterates that "Bob" is transport metadata.

---

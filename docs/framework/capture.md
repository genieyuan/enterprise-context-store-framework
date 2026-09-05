# Capture Stage

**Phase 1 / public-channel / security-deferred boundary:** this is a public architecture document. It does not authorize ingestion of private or restricted channels, and security enforcement is deferred to a future phase.
# ECS lifecycle blueprint — Capture

**implementation: none**  
**Lifecycle stage:** Capture  


## 1. Definition

> Capture reliably acquires enterprise-produced internal and external signals without deciding whether they are true.

Capture makes selected enterprise signal sources complete, traceable and AI-legible. It preserves source fidelity and lands the complete available source record for later classification and interpretation. It does not assign enterprise truth, resolve contradictions, apply ontologies, compile context, or become a system of record.

Capture completes when the complete source record lands successfully in the durable landing area. Established data-pipeline mechanisms handle retries, checkpoints, idempotency, ordering, late-arriving data, schema drift and mid-flight disruption; ECS does not invent a new ingestion mechanism for these solved concerns.

## 2. Architectural principles

### 2.1 Domain-selective, source-complete

The enterprise selects source classes according to the nature of its business. Once a source is declared important, Capture acquires the complete authorized signal stream at the lowest available source-native granularity, without semantic pre-filtering.

- Network packets may be essential to a network-security business but immaterial to a logistics company.
- Debug traces may be essential to a software-development company but inappropriate for unrelated domains.
- Selection happens at source/onboarding level; relevance filtering happens after landing.

Governance & Trust still constrains authorization, privacy, consent, residency and retention.

### 2.2 Capture first; classify later

Premature selection repeats a longstanding data-management failure: information judged irrelevant today is expensive or impossible to recover when tomorrow's questions change. Capture lands all available attributes from an onboarded source. Compile determines classification and contextual use; Governance & Trust defines the applicable discovery-window and retention policy.

### 2.3 AI-legible, not prematurely normalized

AI legibility means preserving the original signal with enough source and capture context to make it traceable and classifiable. Capture does not flatten every source into a large common business schema or replace records with summaries.

### 2.4 No shadow system of record

ECS primarily supplies enterprise **why** and **how**. Operational **what** remains authoritative in systems of record. Operational facts may appear incidentally inside authorized meeting, message or document signals; these remain time-bound observations, not current authoritative state. ECS does not directly source ERP or other system-of-record operational records, status or transactions. Agents must route current-state checks and updates exclusively to the owning system of record.

If an important operational fact has no system of record, ECS exposes that as a governance/data-stewardship gap rather than silently becoming the missing master.

### 2.5 Reuse qualified enterprise plumbing

Existing connectors, CDC, event streams, queues, landing zones and lake/warehouse ingestion services should be reused when they preserve the complete source record and meet traceability, authorization and replay requirements. Existing plumbing is qualified against the Capture contract; it is not reused blindly when it aggregates, drops fields, loses permissions, or obscures changes.

### 2.6 One common ingestion pipeline

Observed, imported, system-generated and proactively elicited signals use the same Capture pipeline. Proactive elicitation is a source/acquisition type, not a separate ingestion architecture. The workflow that decides to ask a person a question sits outside Capture; the question and response enter Capture with their source metadata.

## 3. Three onboarding scenarios

S1, S2 and S3 classify individual signal classes, not entire source products. A single platform may contain signal classes in more than one scenario.

### S1 — already captured and organized properly

Reuse the existing pipeline or landing store when it retains the complete source-native record at sufficient granularity and preserves traceability.


If the existing path retains only aggregates, reconnect to the atomic source and route the signal to ECS and any prior destination. Avoid uncontrolled dual writes; use established CDC, outbox or durable-stream patterns.

### S2 — captured inconsistently across the enterprise

Use source-specific adapters to land the complete record under the minimum Capture Envelope. Continue supporting existing consumers through established interfaces. Agent access through API or MCP belongs to Serve, not Capture.

Examples: Slack, Google Drive, SharePoint, enterprise file systems, email, departmental knowledge bases and collaboration platforms where formats, metadata, permissions or access patterns differ.

### S3 — not currently captured



Proactive elicitation is a special S3 producer. Example: Compile or Serve finds that a pricing exception has no rationale or expiry; an authorized workflow asks the account owner; the question and response enter the common Capture pipeline and link to the context gap.

## 4. Information flow

```text
Select and authorize a source/signal class
  → reuse qualified plumbing, normalize fragmented capture, or add instrumentation
  → authenticate and acquire
  → retain the complete source-native record and source-system metadata
  → add the minimum Capture Envelope
  → validate technical readability; quarantine malformed/unsafe payloads
  → land durably
  → emit landing acknowledgement/change notification
  → Compile classifies, interprets and recompiles affected context
```

Capture does not reject a landed record because it appears semantically irrelevant. A source create, update, delete or correction is captured as a linked change when source identity/version evidence permits; otherwise ECS records explicit best-effort correlation and ambiguity rather than claiming deterministic lineage. Captured history is never silently overwritten. Each change becomes a potential context event and triggers reevaluation of affected compiled context.

## 5. Minimum Capture Envelope

The wrapper is deliberately minimal. Its purpose is internal ECS traceability and later classification, not early business normalization.

1. **Source system identifier** — identifies the source instance/system.
2. **ECS-assigned capture identifier** — provides stable internal ECS lineage. It does not create source traceability when the source lacks a stable identifier.
3. **Capture timestamp** — records when ECS successfully landed the signal.
4. **Source-system metadata** — describes the source and acquisition environment.
5. **Source record itself** — the complete available record with all source attributes, including source-native identifiers and timestamps where available.

Examples of source-system metadata:

- **Slack:** workspace, channel, thread, tenant and source access model.
- **Google Drive:** drive, folder path, MIME type, ownership domain and sharing model.
- **ERP structural source:** system instance, tenant/company code, schema/version, entity-relationship model and ontology/catalog version; operational records, status and CDC transactions are excluded.
- **System logs:** application, host, environment, region, log stream and schema/parser version.
- **Proactive elicitation:** initiating workflow/agent, elicitation type and related context gap.

Source-system metadata describes the environment and acquisition context; the source record carries the actual source event or object. Source-native fields are not discarded merely because ECS does not yet understand them.

## 6. Changes and recompilation

A source change is not a fresh unrelated record and does not overwrite captured history. Deterministic version linkage requires stable source identity or equivalent source evidence. An ECS-assigned capture identifier supports internal lineage after landing but cannot manufacture a missing source relationship; ambiguous correlation remains explicit.

```text
source record v1 → Capture v1 → compiled context generation A
source edit v2   → Capture v2 linked to v1
                 → invalidate/reassess affected claims
                 → compiled context generation B
```

The change itself may explain why and how enterprise understanding evolved. Capture maintains landed source versions and change information where available; Compile determines contextual consequences.

## 7. Technology and operating model

Use mature data-ingestion patterns and qualified enterprise plumbing: connector frameworks, APIs, CDC, polling, file/event ingestion, durable queues, landing storage, schema registries, rescued/quarantine fields, checkpoints, idempotent processing, dead-letter handling, secrets, identity, and source-lag/gap/backfill monitoring.

Snowflake Snowpipe Streaming demonstrates channel ordering, offset tokens, recovery and exactly-once delivery. Databricks Lakeflow/Auto Loader demonstrates checkpointed processing, transactional writes, schema evolution and rescued data. These are reference patterns, not prescribed vendors.


### Provisional ownership model

Initial recommendation: a central ECS team owns standards, shared platform and certification; source onboarding may be centralized or delegated to domain teams. Federated operation is a suggestion, not mandatory.


## 8. Common mistakes and architectural traps

1. **Semantically filtering before capture.** Select sources by business-domain importance; once selected, capture the complete authorized stream and classify later.
2. **Assuming identical source scope for every company.** Relevant signal classes depend on the nature of the business.
3. **Replacing evidence with aggregation.** Derive summaries later; do not overwrite retained atomic evidence.
4. **Blindly reusing plumbing.** Existing pipelines may aggregate, strip permissions, discard changes or drop unexpected fields. Reuse by contract.
5. **Creating a shadow system of record.** ECS preserves why/how and observations; systems of record own current operational truth and updates.
6. **Placing API/MCP access inside Capture.** Capture lands records; Serve exposes authorized context and source routes.
7. **Creating a separate elicitation ingestion pipeline.** Govern the decision to elicit outside Capture; ingest question and response through the common path.
8. **Applying ontology semantics during Capture.** Capture the ontology as a source; Compile applies and evaluates it.
9. **Confusing ECS capture IDs with source traceability.** ECS IDs provide internal lineage but cannot reconstruct absent source identifiers.
10. **Centralizing every connector decision and operation.** Centralize standards and governance; keep operational ownership adaptable and revisit with evidence.

## 9. Success criteria

1. Each onboarded signal class has an explicit domain rationale and governance boundary.
2. The complete available source record lands before semantic classification.
3. Every landed record carries the minimum Capture Envelope.
4. Source changes are append-only, linked where source evidence permits, explicitly ambiguous otherwise, and trigger downstream reevaluation.
5. Current operational truth remains in and routes to the owning system of record.
6. Failures, gaps, late arrival and disruption use mature, observable pipeline mechanisms.
7. Elicited signals and ontologies use the common ingestion path without moving orchestration or semantic application into Capture.
8. The ownership model is explicitly provisional and scheduled for evidence-based reevaluation.


The complete Slack discussion is preserved separately, with every human-visible Genie and Friday message, identity and Singapore timestamp:


## 11. Gate 1 closure


## 12. Additive lifecycle amendment from the Preserve-stage discussion

The subsequent Preserve-stage discussion removed Preserve as an independent lifecycle stage. The revised lifecycle is **Capture → Compile → Serve → Continuous Learning**, with Governance & Trust cross-cutting.

Capture now explicitly owns:

- durable landing and a policy-defined discovery window;
- technical deduplication, idempotency, structural standardization and integrity validation;
- both real-time/near-real-time and batch acquisition through the same Capture contract;
- normal operational coverage, gap, checkpoint, retention and deletion telemetry, with no new ECS expiry-manifest requirement;

Operational ERP/system-of-record records and status are not ECS sources. ERP relationships, data-entity relationships, schemas and ontologies may be captured as structural sources. A meeting decision that requires an ERP transaction must be written to ERP immediately; a missing write-back is a process-integrity gap, not permission for ECS to become the source of truth.



- Verdict: `request_changes`

## 13. Sources

- Snowflake, *Channels and exactly-once delivery*: https://docs.snowflake.com/en/en/user-guide/snowpipe-streaming/snowpipe-streaming-channels
- Databricks, *Processing guarantees in Lakeflow pipelines*: https://docs.databricks.com/aws/en/ldp/best-practices/processing-guarantees
- Databricks, *Schema inference and evolution in Auto Loader*: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/schema

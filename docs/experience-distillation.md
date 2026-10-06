# Distilling enterprise experience into reusable capabilities

*Direction consolidated through 5 October 2026. Companion to the existing framework—not an
implementation specification, a new canonical object schema, or evidence of deployed capability.*

Public synthesis of the October 2026 compiler direction; internal deliberation records are not part of this publication.
Read alongside the [normative semantic contract](context-object-and-retrieval-contract.md);
earlier Phase 1 documents retain their historical scope.

> **Publication scope:** technology-neutral framework, not a deployed runtime. The Phase 1
> public-channel-only scope and recording-only ACL boundary remain unchanged. References to
> current authorization, revocation, encryption, or privacy enforcement specify obligations for
> future implementations; they do not claim those mechanisms are implemented or authorize
> private/restricted ingestion. Existing accepted ADRs are not silently superseded.

## 1. Product focus

ECS focuses on **distilling enterprise experience into reusable agent capabilities**. Context
storage and retrieval support that objective; managing agents is not the product's focus.

The intended loop is:

`enterprise work → evidence → classification → distillation → searchable capabilities → reuse → corrections and outcomes → re-distillation`

The outcome is not simply a collection of shorter documents. It is reusable understanding:
concepts, judgment frameworks, methods, procedures, and possible actions connected to enterprise
objects, with evidence and applicability intact.

## 2. A model-agnostic compiler

The framework defines two complementary responsibilities:

1. A **classification model** identifies the knowledge types present and the relevant distillation
   targets. Classification may be multi-label: one source can contain several kinds of knowledge.
2. An **AI agent** distills that material into appropriate reusable frameworks, connects their
   outputs, and preserves evidence, limitations, and ambiguity.

Model providers, sizes, confidence thresholds, training methods, and deployment choices belong
in implementation work. No particular classifier or frontier model is required by the framework.
Model output is a proposed interpretation; confidence alone cannot make it authoritative.

A governed intermediate representation, validation, and reproducible materialization can support
this process. They are enabling mechanics, not a substitute for the agent-consumable outcome.
The precise bundle schema and transaction design remain detailed-design work.

Possible AI-agent implementations include an **LLM or post-trained open-source model**.
These are alternatives, not required dependencies.

## 3. Multiple frameworks, not one universal extraction template

The compiler can express different kinds of knowledge through different frameworks and link
outputs derived from the same source. The following family is **illustrative**, not a mandated
ontology, exhaustive taxonomy, or frozen schema:

| Framework | Question it helps answer | Illustrative contents |
|---|---|---|
| Concept | What does this mean? | Definition, categories, relationships, business scope |
| Fact and state | What is asserted, where and when? | Object, assertion, valid time, source |
| Rule and decision | Under which conditions does something follow? | Conditions, consequence, exceptions, authority |
| Procedure | How might this work be performed? | Goal, inputs, steps, branches, failure handling |
| Experience or case | What happened in this situation? | Attempt, correction, stated reason, result, outcome |
| Judgment | How should this class of problem be assessed? | Diagnostic questions, criteria, trade-offs, boundaries |
| Explanation or hypothesis | Why might this happen? | Candidate mechanism, alternatives, evidence, possible tests |
| Capability or affordance | What could be done with these objects? | Objects, possible actions, intended outcomes, conditions, evidence |

These forms carry different reasoning commitments. Applying an accepted rule is not equivalent
to generalizing from one case; suggesting an explanation is not establishing causation. An agent
should be able to tell which kind of inference it is receiving.

Knowledge bases hold the assets; graphs connect them. Neither storage format automatically
produces reusable judgment. Framework selection and distillation are compiler responsibilities.

## 4. Proposed Skills: useful before publication

A **proposed Skill** is a searchable capability hypothesis. It can connect:

`object types ↔ possible actions ↔ intended outcomes ↔ conditions ↔ supporting or contradicting evidence`

It need not be published, executable, or mature enough for automation to be useful. **Every
useful fact must either create a proposed Skill or attach as supporting/contradicting evidence
to an existing one.** Useful facts are not excluded merely because they are volatile. Many
facts can contribute to one proposal; this does **not** require one artifact per fact.
Preserve facts that are not useful capability evidence, with their scope, without manufacturing
a proposal. This coverage rule grants neither publication nor execution authority.

At retrieval time, a proposed Skill can be supplied as:

- **Supporting evidence:** a relevant method or relationship that may inform reasoning, with its
  evidence and uncertainty visible.
- **A proposed action:** a possible application to the current objects and circumstances, not
  permission to execute it.

Publication is an optional branch. There is no mandatory progression from proposed Skill to
proposed action to published Skill. A proposed action may draw on a proposed or published Skill;
a proposed Skill may remain useful indefinitely without publication.

Keep four questions separate: **Is it relevant? Is it supported? Has it been published for use?
Is this particular action authorized now?** None can be inferred solely from the others.

## 5. Distill corrections and outcomes, not only final artifacts

Enterprise experience includes observable work episodes:

`task + objects + initial attempt + correction + stated reason + revised result + observed outcome`

Retain the original episode so that a proposed generalization can be checked. A finished artifact
can suggest a candidate method, but does not prove how the work was actually performed. Missing
rationale stays missing; the compiler must not invent expert reasons or capture private
chain-of-thought.

Expert approval and business success are different evidence. A correction may improve factual
interpretation without improving the eventual outcome. Conversely, an apparently successful
outcome does not establish that the recommended action caused it. Contradictions and alternative
explanations should remain available.

The learning loop revisits available knowledge as agents reuse it and new evidence arrives. This
is knowledge learning; it does not imply automatic model-weight updates.

### Synthetic renewal example

An agent recommends a discount. An account manager identifies a billing integration problem
instead. A repair is followed by renewal.

The episode can support a diagnostic framework and a proposed Skill to investigate operational
friction before commercial concessions in applicable cases. It should not become the universal
rule “never offer discounts,” nor the causal claim “the repair caused the renewal.”

A later agent can use that experience to propose a billing check. Current system facts,
applicability, and runtime authorization still determine whether and how that check proceeds.

## 6. Fit with existing ECS contracts

This direction extends the purpose of compilation without replacing the
[context object and retrieval contract](context-object-and-retrieval-contract.md):

- Source evidence (`EvidenceEvent`), governed assertions (`ContextClaim`), consequential
  relationships (`EdgeClaim`), and decision projections (`DecisionCase`) remain distinguishable.
  Frameworks and proposed Skills must preserve links back to these existing semantic objects;
  they do not replace them or establish a new approved storage primitive.
- Subjective evaluation and objective outcomes remain distinct; feedback does not silently
  rewrite canonical history.
- A task-specific Context Package remains bounded and subject to current authorization, with
  delivery recorded by its receipt. Discoverability does not bypass access controls.
- Current operational facts remain authoritative in their source systems. ERP and warehouse
  schemas supply **bootstrap candidates**, not automatic authority over business meaning.
- Derived profiles, indexes, and compilation representations cannot become independent sources
  of authority or grant execution permission.

Exact proposed-Skill schemas, their mapping onto the semantic spine, and detailed lifecycle and
retrieval contracts still require design work. This document does not introduce a parallel
canonical store, implementation mandate, or superseding ADR by implication.

## 7. Future product idea: a compiler that improves within the enterprise

Beyond the core framework, the agreed product idea is to begin with compilation expertise learned
from frontier-model examples and improve the compiler through enterprise experience:

`frontier compilation examples → validated training material → smaller compiler model → enterprise feedback → further post-training`

This is a **future product direction**, not an implemented capability or a requirement on every
ECS deployment. Model choice, training technique, acceptance thresholds, and learning cadence
remain open implementation choices. No fixed “70%” quality or coverage promise is adopted.

The intended product can accumulate two complementary assets:

1. Reusable enterprise knowledge, frameworks, and proposed Skills.
2. An enterprise-adapted compiler that becomes better at interpreting and distilling experience.

Keep their versions and evaluation separate. The compiler learns how to process enterprise
material; changing facts, authoritative policies, and access permissions remain governed context,
not authority derived from model weights.

## 8. Research inputs—not automatic adoption

**Cangjie:** the relevant inspiration is extracting reusable methods, applicability, procedures,
and boundaries from source material. Compilation bundles and reproducible outputs support that
outcome. This direction does not adopt its code, prescribe its schema, or assert enterprise
readiness. See the [upstream repository](https://github.com/kangarooking/cangjie-skill).

**Hindsight:** incremental consolidation, evidence-aware staleness, maintained framework views,
and retrieval between abstractions and source evidence are **proposed enhancements to evaluate**.
They are not approved implementation requirements or an adopted integration. The proposed
synthetic experiment should compare transfer to new tasks, citation fidelity, preservation of
contradictions, update propagation, and access-boundary behavior against the existing baseline.
See [observations](https://hindsight.vectorize.io/developer/observations) and
[mental models](https://hindsight.vectorize.io/developer/mental-models).

## 9. What must be demonstrated next

One complete, synthetic experience-to-capability example should make the Capture, Compile,
Serve, and Learning responsibilities concrete. Evaluate whether its distilled method improves a
**different** task and reduces repeated correction—not simply whether the compiler can emit a
well-formed Skill.

Evidence fidelity, unsupported generalization, disagreement preservation, current authorization,
and downstream usefulness belong alongside cost and latency in that evaluation. No benchmark
result is claimed by this document.

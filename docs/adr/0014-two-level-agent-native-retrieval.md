
# ADR-0014: Two-level retrieval — graph scopes, vector selects — with an agent-native contract

- **Status:** Accepted
- **Date:** 2026-08-17
- **Supersedes:** —

## Context

[ADR-0005](0005-serve-agents-only.md) settled that the only consumer is an agent. The
retrieval design then has to be built for one, and the first version of this design was not —
it was a human research workflow wearing an API.

Separately, the [prior-art survey](../../01-research/2026-08-17-context-graph-prior-art.md)
found that graph retrieval scores **highest factual correctness but lowest context relevance**:
traversal pulls in extraneous material and dilutes precision.

## Decision

### Two levels

**Level 1 — the graph scopes.** Resolve the task into relations and the systems that own the
relevant facts. Returns *scopes and routing*, never content.

**Level 2 — the vector index selects.** Within each scope, select content under a budget.
Returns content, provenance, and gaps.

The graph never hands text to the agent. That is what prevents the precision dilution the
survey documents: the graph narrows, it does not answer.

The two levels are a **dependency order, not a pipeline**. Everything within a level fans out —
multiple relations traverse concurrently, multiple scopes search concurrently.

**Entry does not require natural language.** An agent that already knows the entities or
relations it needs says so directly and skips resolution.

**Not every task is relational.** A direct topic lookup is available without traversal;
routing between paths is per-request, not a blanket policy.

### The agent-native contract

| Human-shaped | Agent-native | Why |
|---|---|---|
| Query string | Task + token budget + optional structured intent | The agent already has structure; making it write a sentence discards it |
| Ranked list | Budget-filling set optimised for **coverage**, redundancy penalised | An agent does not read top-down and stop. Two near-identical top hits are worse than one hit plus one different fact |
| Returns what it found | Returns what it found **and what it looked for and did not find** | See below |
| Prose | Structured provenance, collapsed score, staleness per item | The agent must decide machine-side whether to rely or to flag |
| One call | Optional cheap **coverage probe** before a budgeted fetch | Lets the agent budget before committing tokens |

**Negative space is part of the response, not an error case.** The response says what was
sought and not found, and — per
[ADR-0013](0013-context-store-enriches-systems-of-record.md) — what the store does not hold at
all and which system owns it instead.

This is not a convenience. [ADR-0003](0003-measure-context-quality-by-declared-assumptions.md)
measures the store by the assumptions an agent declares. For an agent to declare *"I assumed
the child is 4"*, retrieval must have told it that nothing about age was found. **A ranked list
structurally cannot express absence**, so without negative space the measurement loop the whole
design rests on has nothing to feed on.

**Retrieval is deterministic for identical inputs.** Agents retry. If the same task yields
different context across attempts, a changed assumption could mean the world changed or could
mean retrieval jittered, and the correction signal becomes noise. Humans tolerate search
jitter; a measurement loop cannot.

## Options considered

### Option A — Graph scopes, vector selects, agent-native contract  ✅ *chosen*

- **Upside:** Uses each structure for what it is good at. Scoping rather than returning is a
  direct answer to the documented precision-dilution problem. Coverage-under-budget matches how
  an agent actually consumes. Negative space makes ADR-0003 workable
- **Cost:** Set selection under a budget is a harder problem than ranking. Determinism
  constrains implementation
- **Risk:** Coverage optimisation needs a redundancy notion that does not yet exist

### Option B — Graph retrieval returning content directly

- **Upside:** One step
- **Why not chosen:** This is the configuration the survey found scores lowest on context
  relevance

### Option C — Vector-only, no graph

- **Upside:** Cheapest; hybrid BM25+vector beats either alone by 15–30% recall and the survey
  advises exhausting it first
- **Why not chosen:** Cannot answer relational questions about business structure, which is the
  stated purpose ([ADR-0012](0012-type-level-entities-and-typed-relations.md))

### Option D — Ranked list, as originally proposed

- **Upside:** Conventional, easy to consume, easy to evaluate with standard IR metrics
- **Why not chosen:** Ranking is a human affordance. It optimises "best first" when the agent
  needs "most informative set within budget", and it cannot express absence

## Consequences

**What gets easier:** The graph earns its place without the precision cost. Agents can budget
before committing. The assumption loop gets its input. Retries are comparable.

**What gets harder:** Coverage-optimised selection under a budget is genuinely harder than
ranking, and standard IR metrics do not measure it. Determinism rules out approaches that
depend on nondeterministic sampling.

**What we're now committed to:** Every response carries two halves — found and not-found.
Selection optimises set-level utility, not per-item score. The API is
task-and-budget-shaped, not query-shaped.

**What would make us revisit this:** Coverage selection proving intractable — the fallback is
ranking with an explicit diversity penalty, which is a weaker version of the same idea. Or
determinism proving too costly, in which case it should be a per-request flag rather than
silently abandoned, since the measurement loop depends on it.

## References

- [Prior art survey](../../01-research/2026-08-17-context-graph-prior-art.md) §4, §5
- Decision-maker: *"we find the relationship through graph retrival, we then find search the
  vector index to find the relevant topics accordingly. It should be a two level search"* and
  *"this context store is NOT decided for human. It is for agents… It has to be designed and
  optimised for machine/parallel processing and agent retrieval"*

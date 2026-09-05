
# ADR-0003: Measure context quality by the agent's declared assumptions

- **Status:** Accepted
- **Date:** 2026-08-17
- **Supersedes:** —

## Context

The store must improve over time. Anything that improves needs a signal telling it whether
each attempt went well or badly. Producing that signal is the hardest unsolved problem in
this project, and the founding discussion hit it repeatedly without resolving it
(00:00:52, 00:07:07, 00:18:21):

> 企业本来就不知道什么是好，或者是 AI 的终点在什么地方
>
> *Enterprises don't actually know what "good" is, or where AI's end state lies.*

And the paradox that blocked every attempt to answer it:

> 如果你知道什么东西是好的话，你就证明你已经有那个 context，那我为什么还需要你呢？
>
> *If you already know what's good, you already have that context — so why would I need you?*

The obvious approaches all fail:

- **Human grading of every output** — too expensive, and rating schemes decay within weeks
- **Explicit ratings tied to compensation** — get gamed immediately. The founding discussion
  identified this failure mode unprompted at 00:29:42: *"我帮你点赞… 然后你拿了钱咱们分"*
  (*I upvote yours, you get the bonus, we split it*)
- **Judging the store on final artefact quality** — conflates store failures with agent
  failures, leaving no way to know which half to fix
- **Detecting missing context directly** — requires knowing the expected shape in advance,
  which the framework rejects (§3.2) because different enterprises genuinely differ

## Decision

**The store is measured by the assumptions an agent had to declare in order to complete a

An agent doing real work must invent whatever it wasn't given. It declares those inventions.
Each declared assumption is a gap that has already revealed itself — the system never has to
detect absence, only to observe what got made up.

- **Fewer declared assumptions** on a task ⇒ the store served that task better
- **A human correcting an assumption** ⇒ confirmed real gap, *and* the correct value. This is
  the gold signal: a person spent effort to say "no, actually", which is expensive to fake
- **Uncorrected assumptions** are weak positive evidence and must not be over-weighted; silence
  is not agreement

**The store is explicitly not measured on the quality of the final artefact.** That is the
agent's responsibility.

## Options considered

### Option A — Declared assumptions as the measure  ✅ *chosen*

- **Upside:** Free and continuous — generated on every request with no human in the loop.
  Needs no ground truth, no schema, and no rating UI. Separates store failures from agent
  failures cleanly. Corrections double as labelled training data
- **Cost:** Depends on agents reliably declaring assumptions rather than silently guessing
- **Risk:** Gameable by an overconfident agent that assumes freely and declares nothing —
  which is why *corrected* assumptions, not raw counts, carry the weight

### Option B — Human rating of outputs

- **Upside:** Directly measures what we care about
- **Cost:** Expensive, decays fast, gamed once tied to compensation
- **Why not chosen:** Every known deployment of this pattern degrades within weeks

### Option C — Judge the store on final artefact quality

- **Upside:** Measures the outcome that actually matters commercially
- **Why not chosen:** Every agent bug looks like a retrieval bug and vice versa. Months get
  spent tuning the wrong half of the system

### Option D — Business outcome attribution

- **Upside:** The only measure a customer truly cares about
- **Why not chosen:** Feedback latency in months, and hopelessly confounded. Useful as a
  lagging indicator later; useless as a training signal

## Consequences

**What gets easier:** The learning loop has a gradient from day one, with no labelling
budget. Debugging gains a decision procedure: poor output with no assumptions is an agent
problem; poor output with many corrected assumptions is a store problem.

**What gets harder:** Every consuming agent must declare assumptions in a structured,
machine-readable way. That is a contract on the *consumer*, which the store does not control
— a real weakness, since the store's core metric depends on agents it doesn't own.

**What we're now committed to:** Assumption declaration and correction capture must be
first-class in the serve contract from the beginning. Retrofitting it means having collected
no learning signal for the entire intervening period.

**What would make us revisit this:** Evidence that agents declare assumptions unreliably
enough to make the signal noise — for instance if declared assumptions turn out to correlate
more with model verbosity than with actual context gaps. That would be measurable early, and
should be checked early.

## References

  00:00:52, 00:18:21, 00:18:50, 00:29:42
- [Phase 1 framework](../phase-1-framework.md) §1, §5

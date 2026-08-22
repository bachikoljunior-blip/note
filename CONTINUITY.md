# O / Chat continuity

Updated: 2026-08-23 JST

This is the sole content of the note repository main branch and the compact continuity source for this ChatGPT conversation. Maintain it proactively from conversation history as important standing assumptions, corrections, decisions, or workflow rules emerge. Do not rely on the chat window alone to retain them across a long conversation.

## Standing context

- Goal: materially accelerate arrival of genuine AGI; O is a means, not the terminal goal.
- The user has only a smartphone. Automatable/repository-side work should be done through connected tools/agents; ask the user only for irreducible account-holder actions.
- O and this ChatGPT conversation should be treated as using the same base model for reasoning about idea-generation overlap. This chat should not merely duplicate ordinary O reasoning; prioritize important observations/context O is unlikely to encounter because of its execution context.
- When this chat finds such an observation, prefer passing the observation/problem as external context rather than prematurely fixing O's solution. O should investigate, falsify, choose the method, and reject the observation if unsupported.
- Skill-in-Skill is a user-originated candidate concept, not a mandatory solution. Intended concept: a Skill may expose multiple child Skills; select relevant child branch(es) for the situation and recurse as useful, materializing only needed context. Do not assume this must be the final context architecture.
- Long-running accumulated context may itself suppress hypotheses/strategies that the same base model could generate under different context, and may make that bias hard to notice internally. This is external context for O to investigate if material to expected AGI time.
- O should receive new durable user input while execution is alive, not only after watchdog recovery; current O mechanism is agi/USER_INPUT_INBOX.json at safe semantic boundaries.
- Questions/proposals and genuinely user-only environment/permission/operation/information needs should go through O's durable user-request queue without stopping other safe work.
- User ideas, this chat's ideas, and external research are candidates/context, not automatic truth or automatic adoption.
- Avoid anchoring on illustrative numbers such as a thousand years. Optimize expected total elapsed time to AGI continuously; examples are not thresholds.
- Before writing new external context or directives into O, show the proposed wording to the user and wait for approval. Updating this note for continuity is different: do it proactively when needed so conversation assumptions are not lost.
- Prefer structural observations over one-off patches when reporting problems to O. Recent example: durable plans, continuation, heartbeat, user-input acknowledgements, repository/CI/PR state, and actual tool execution advance asynchronously; freshness/provenance/invalidation/reconciliation and decision-time context selection can therefore be a structural issue rather than an individual stale-state bug.

## Chat role

Before proposing an O improvement, ask whether it is merely something the same model inside O could readily derive from its current context. If yes, it is low-value duplication. Prefer observations, counterexamples, outside evidence, alternative framing, or context differences that O is less likely to possess. Then let O determine the response unless the user explicitly asks this chat to design it.

When conversation history changes or corrects any standing assumption, update this file as part of the conversation rather than waiting for the user to remind the assistant. Keep it compact enough to reread, but preserve distinctions that have repeatedly caused confusion.

## Current external-context items to O

1. Same base model, different context can yield substantially different hypotheses and strategies. A long-running O may become conditioned on its own history, architecture, successes, failures, and current strategy, making some model-generatable important ideas less reachable; the same accumulated context may make the bias itself hard to detect. O should investigate/falsify/address this if it materially affects expected elapsed time to AGI.
2. Long-running execution has asynchronous sources of truth. Treat freshness, provenance, invalidation, reconciliation, and decision-time context selection across durable state and live external state as a structural correctness/performance question rather than repeatedly patching individual stale snapshots.

## Pending proposal — not approved for O

Long-term context selection may itself be part of intelligence/control: as objectives, constraints, current state, evidence, failures, external research, user input, and existing design accumulate, choosing what enters the current decision can determine the outcome even when downstream reasoning is locally correct. The selector can itself be conditioned by accumulated context and may fail to notice its own blind spots. Potential external context for O should frame this as a falsifiable structural problem without prescribing Skill-in-Skill, fresh-context branching, or another specific solution. This item must not be sent to O until the user approves wording.

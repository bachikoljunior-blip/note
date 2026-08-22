# O / Chat continuity

Updated: 2026-08-23 JST

This is the sole content of the note repository main branch and the compact continuity source for this ChatGPT conversation.

## Mandatory continuity loop for this chat

- Do not wait for the user to mention this note. For O-related questions, decisions, repository actions, or references to prior discussion where historical context could matter, proactively read this file before reasoning or acting.
- Proactively update this file when conversation history adds, corrects, supersedes, or clarifies an important standing assumption, decision, distinction, workflow rule, pending proposal, or external-context item. Do not wait for the user to request an update.
- The purpose is to survive chat-context truncation. Repeatedly using this read/update loop should keep the existence and role of this note represented in recent conversation/tool activity while the durable file remains the recovery source.
- Keep the file compact enough to reread. Preserve semantic distinctions that have caused repeated confusion; compress derivable reasoning rather than accumulating transcripts.
- When carrying an insight from this chat to O, prefer the minimal context difference that caused this chat to reach a useful conclusion, rather than sending the entire derived solution or reasoning chain. O uses the same base model for this purpose, so the missing context is often more valuable than duplicating reasoning.
- Before writing a new external-context item or directive into O, show the proposed wording to the user and wait for approval. Note maintenance itself is proactive and does not require approval.

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
- Prefer structural observations over one-off patches when reporting problems to O. Durable plans, continuation, heartbeat, user-input acknowledgements, repository/CI/PR state, and actual tool execution can advance asynchronously; freshness/provenance/invalidation/reconciliation and decision-time context selection can therefore be a structural issue rather than an individual stale-state bug.

## Chat role

Before proposing an O improvement, ask whether it is merely something the same model inside O could readily derive from its current context. If yes, it is low-value duplication. Prefer observations, counterexamples, outside evidence, alternative framing, or context differences that O is less likely to possess. Then let O determine the response unless the user explicitly asks this chat to design it.

## Current external-context items already sent to O

1. Same base model, different context can yield substantially different hypotheses and strategies. A long-running O may become conditioned on its own history, architecture, successes, failures, and current strategy, making some model-generatable important ideas less reachable; the same accumulated context may make the bias itself hard to detect.
2. Long-running execution has asynchronous sources of truth. Freshness, provenance, invalidation, reconciliation, and decision-time context selection across durable state and live external state are a structural correctness/performance question rather than merely individual stale snapshots.

## Pending proposal — not approved for O

Minimal-context formulation: "Long-running execution makes the choice of what enters the current context consequential, and that context-selection decision is itself conditioned by the contexts selected before it."

This is intentionally a seed/context difference rather than a prescribed solution. Do not send it to O until the user approves it.

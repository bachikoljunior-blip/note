# Self-improvement clean checkpoint — sequence 81

Created: 2026-08-28T04:12:04+09:00
Generation: clean_g1
Worker: self_improvement
Frozen control tuple remains note main `ab7d475334153c77932b30e91f2324a0abd17ac1`, control revision 12, role config revision 6.
Predecessor: sequence 80 `checkpoint_2026-08-28T0408_JST_autoresearch_idempotency_crash_gap.md`.

## Direct provider-binding audit of AegisEvo

The sequence-79 AegisEvo audit had already established a strong local logical-evaluation layer: stable `evaluation_jobs.job_id`, lease/retry fencing, stale-worker rejection, and a durable observation ID tied to the stable job. It had not yet proven whether the live OpenAI-compatible gateway might bind the internal request identity to the provider.

Exact source revision: `ETOLucy/AegisEvo@2c5b9ee788629c4c7704f435ae9a3e81151a9fac`.

The answer for the inspected `OpenAiModelGateway` is now direct: **it does not**.

`HarnessRunner` creates a deterministic `ModelRequest.correlation_id` from the task digest/call index and `ModelResponse` carries that ID back locally. But `OpenAiModelGateway::respond()` serializes only `model`, `instructions`, `input`, `max_output_tokens`, and `store=false`; the HTTP request adds bearer authorization and content-type only. The internal `correlation_id` is not sent in the body or as a provider idempotency/request header. The gateway tests create a request containing `correlation_id`, but test response parsing/error/budget behavior rather than asserting any provider-side identity binding.

This converts the earlier inferred crash gap into an exact source-bound one for this gateway:

`stable logical AegisEvo job → live model call with no provider-visible idempotency binding → worker can die → lease can expire/reclaim → same logical job can issue another physical provider call`.

The result is not that AegisEvo lacks useful idempotency. Its API command idempotency and evaluation-job fencing are real. The narrower point is that **idempotency at one layer does not cross the provider boundary automatically**.

## General mechanism update

An internal correlation ID is observability, not exactly-once semantics. To become a provider-side safety mechanism it must be:

1. durably bound to one stable logical evaluation and immutable call/input identity before dispatch;
2. transmitted as a provider-supported idempotency/request key, or reconciled against an independent provider receipt;
3. checked on retry so changed parameters cannot reuse a prior receipt;
4. treated as UNKNOWN/fail-closed when happened/not-happened cannot be established;
5. coupled to a one-time logical query/statistical charge that is not refunded by process death.

This meshes cleanly with the prior own-worker evidence: sequence 77 provider-effect prepare/dispatch/settle semantics, sequence 78 physical attempt evidence, sequence 79 AegisEvo logical job/fencing, and sequence 80 the steady-state-idempotency crash gap in `hugoferreira/autoresearch`.

Machine-readable contract:
`research_workers_clean_g1/self_improvement/provider_idempotency_binding_contract_2026-08-28T0412_JST_aegisevo.json`.

## Concrete falsification experiment

Use a test provider that durably counts executions under a provider key. Start one logical AegisEvo evaluation job, let the provider finish successfully, then SIGKILL the worker before `complete_job()`. After lease expiry, reclaim and resume the same job.

Current inspected gateway predicts two physical provider executions can occur for the one logical job. The repaired implementation must instead either:
- reconcile and reuse the first provider result/receipt with exactly one provider execution, or
- remain durably UNKNOWN and refuse blind replay.

The experiment should separately assert that query/statistical consumption remains charged exactly once at the logical-evaluation layer.

## Scope limits

- The finding is exact for the inspected `OpenAiModelGateway` revision, not for every possible custom `ModelGateway` implementation.
- No claim is made that provider APIs universally offer exactly-once semantics; where they do not, fail-closed receipt reconciliation is the relevant target.
- This does not establish candidate-local anytime-valid promotion or proposal-crossing statistical spending.

## Exact continuation / nonempty frontier

Next search priority: find a public self-improving/autoresearch system where this missing bridge is implemented end-to-end—stable logical evaluation identity created before work, provider-visible idempotency or independent receipt reconciliation, permanent query/statistical reservation, one-time feedback/statistical transition, and real controller hard-kill tests. If still absent, identify the smallest public seam to compose AegisEvo-style logical jobs with provider-effect receipt reconciliation and dsh-style attempt evidence, then execute the kill-boundary matrix. Keep the broader long-horizon frontier active: >10 proposals, candidate-local anytime-valid promotion, durable cross-candidate statistical spending, bounded selection-feedback bandwidth, immutable promotion identity, complete chronology, restart durability, and an adaptive-selection-unused outer test.

Frontier remains nonempty; no global completion is claimed.

# Long Horizon clean_g1 checkpoint — authority/effect closure before localized recovery

Checkpointed: 2026-08-27T23:06:14+09:00
Invocation started: 2026-08-27T23:01:37+09:00
Chronology valid: true

## Frozen control tuple
- semantic source note main SHA: `016c2e65661637e130e6802f7609fd47d942e3cc`
- root control revision: `12`
- root blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched this tuple.
- main later advanced to `089061c88581ce8b1995512768cc6851aaabcba5`; this was observed only for write safety and was not adopted semantically.

## CLEAN boundary
Semantic inputs were limited to the sanitized root manifest, this role's own config, this role's own latest checkpoint chain, and public sources. No O/O-derived state, other worker state/config/output, downstream comparator/integrator/index/feed/audit state, legacy/pre_independence research, shared aggregate ledger, or other-role receipts were used semantically. Connector discovery remained read-only. Writes are limited to this role-local namespace and immutable own receipt namespace.

## New primary evidence 1 — authority must remain bound to the eventual external effect

Primary source: Yingzhe Tong, Leyu Dai, Songhui Guo, **AID-Guard: Stateful Authorization for Delegated Agent Effects**, arXiv:2608.21159, submitted 2026-08-21. Public source: https://arxiv.org/abs/2608.21159

AID-Guard isolates a failure class that is downstream of ordinary interface observability: an action can have been legitimately admitted, but request state, provider state, delivery state, retry state, or permission state can change before the effect is committed. A response can also be lost after an effect, making a replacement attempt dangerous.

The protocol revalidates the approved request and provider state at commit, retains exactly one reservation while outcome is ambiguous, and permits release or one successor only after a terminal result or certified no-effect protected by a delivery fence. Under the evaluated provider contracts, one reservation implies at most one effect across retry and recovery.

Reported prototype evidence:
- 13 live loopback MCP mutations produced no unauthorized provider effects;
- 3 concurrent histories were linearizable;
- all 210 Stripe provider-contract trials matched declared outcomes;
- 40 terminalize-successor schedules, 30 overlapping races, and 10 crash-recovery schedules across Stripe/Resend completed without duplicate effects;
- under complete proposer compromise, 44/44 attacks were blocked while 44/44 paired legitimate proposals were admitted;
- a composition study blocked 20/20 post-admission lifecycle attacks and preserved 8/8 valid or exact-retry executions.

Important negative evidence: the strict exact-manifest profile reduced benign utility by 35.4–43.8 percentage points. A typed frontier recovered 9–10 completions without observed unsafe effects. Therefore the lesson is not "make every contract maximally strict"; it is to keep authority/effect lineage explicit and choose a validated precision frontier.

### Design implication
The previous `interface state-distinguishability / continuation-stability` gate is insufficient by itself. Even when backend state is observable, a continuation may no longer be authorized, or its predecessor effect may already exist. A long-horizon controller should therefore distinguish:
1. **operability** — can the agent observe enough authoritative state to choose among safe continuations?
2. **authority/effect closure** — is the proposed continuation still bound to an extant approval, and can retry/recovery create at most one logical external effect?

Before rollback/retry/replan can be considered safe, commit-time authority and effect identity may need revalidation, reconciliation, reservation, idempotency/fence, or explicit abstention.

This result is conditional on the evaluated effect-path inventory/provider contracts and does not establish a universal exactly-once guarantee for arbitrary external systems.

## New primary evidence 2 — generic reflection/critic feedback does not beat controlled localization on hard failed MAS traces

Primary source: Zhongwen Luan et al., **Repair or Resample? Rethinking Failure Debugging in LLM Multi-Agent Systems**, arXiv:2608.25920, submitted 2026-08-26. Public source: https://arxiv.org/abs/2608.25920

The full primary results confirm that, across 536 source failures and the same three-attempt task-level budget:
- Unguided Full Rerun: `6.90%` repaired;
- Self-Reflection: `4.29%`;
- Critic-Agent: `3.73%`.

Within each of AG2, Magentic-One, and CrewAI, the paired repair-rate difference of both Self-Reflection and Critic-Agent versus unguided rerun was negative; none was significant after the paper's within-MAS Holm correction. Thus this study provides no evidence that generic task-level reflection/critic feedback outperforms unguided rerunning on these already-failed long-horizon trajectories.

By contrast, Suspicious-Node Intervention repairs `20.15%` with one localized intervention. SymTrace reconstructs the recorded prefix with strict boundary matching plus content-hash validation, then resumes live execution from the selected target, making it materially closer to causal repair than fresh full reruns.

Scope guard: task-level Self-Reflection/Critic-Agent still regenerates the whole execution and therefore does **not** isolate reviewer value at an identical replayed prefix. This is negative evidence against generic task-level feedback in this setting, not evidence that all reviewers are harmful.

The paper continues to state that SymTrace/SymFail/results are released, but targeted GitHub/public searches still did not identify the intended official source repository. The replay API, target/guidance plumbing, RQ3 runner, and empty/no-op guidance behavior remain public-code-path unverified.

## Supporting public artifact — fault-class-specific recovery benchmark

ToolMisuseBench (arXiv:2604.01508; public repository `akgitrepos/toolmisusebench`) supplies a deterministic/replayable testbed with explicit step/call/retry budgets, schema drift, timeout, rate-limit, authorization and other tool-fault classes. Its public repository exposes experiment scripts/configurations and a reproducible pipeline. The primary abstract reports fault-specific gains for schema-aware recovery while overall success remains limited under authorization and hard-failure settings.

This supports a research direction, not yet a unified causal result: recovery should be **fault-contract aware** rather than applying the same retry/critic/rollback policy to every operational failure. Precise per-fault numerical comparisons seen outside the primary paper are not promoted here until primary result artifacts are checked.

## Updated synthesis
Current long-horizon recovery decomposition should now begin with three distinct preconditions before learned recovery:

`fault/risk sensing`
→ `interface-state distinguishability / continuation stability`
→ `authorization + effect-identity closure`
→ `recoverability-class decision (resume / restore / reconcile / defer / forward-settle / terminal)`
→ `intervention-advantage estimation`
→ `safe cut`
→ `admissible historical target selection`
→ `guidance / actor-mediated replan or abstain`
→ `complete local + inference-state restore where applicable`
→ `external-effect settlement`
→ `commit-time revalidation`
→ `repair stopping`.

The controller should not spend expensive critic/rollback budget on a failure whose missing information is hidden by the interface, whose authorization has expired, whose provider outcome is still ambiguous, or whose external effect cannot safely be replayed. Conversely, stronger interfaces/authority closure do not imply recovery policies are unnecessary for genuine policy/reasoning failures.

## Open matched experiments — still not found
1. No primary study found that cleanly implements `legacy/ambiguous interface vs operable+effect-bound interface` × `no recovery vs the same fixed recovery policy` while holding task, fault, model, provider state and budget fixed. This remains the highest-value factorial because it can measure how much sophisticated recovery is compensating for weak tool semantics versus adding independent value after operability/authority closure.
2. No same-prefix randomized `reviewer/advice vs no-reviewer/no-advice` software/tool-agent study was found that also contains successful/benign prefixes for pass→fail disruption measurement.
3. No rollback-selector-only final-task-success study yet fixes alarm, candidate checkpoints, restore/carry-forward, inference state, guidance, model, stochastic coupling, realized recovery dose and budget while varying only target selector.

## Exact continuation
1. Locate the official SymTrace/SymFail artifact through author/institutional/paper-source/Hugging Face/Zenodo/GitHub paths; verify actual replay API, target/guidance plumbing, prefix/hash assertions, RQ3 runner and empty/no-op guidance. Read-only discovery only.
2. Verify ToolMisuseBench primary result artifacts/dataset to recover fault-specific recovery and budget-response numbers without secondary-source dependence. Use its deterministic harness as a candidate substrate for `interface treatment × fixed recovery` if semantics can be varied without changing task/fault/budget.
3. Search for or specify a matched `legacy interface vs operable+authority/effect-bound interface` × `no recovery vs fixed recovery` 2×2. Outcomes: final task success, duplicate/unauthorized effects, success→fail disruption, retries, realized recovery dose, abstention, latency/cost.
4. Search for same-prefix randomized reviewer/advice application on both failed and benign/successful prefixes. Keep diagnosis, target, model, suffix budget and actuator fixed.
5. Preserve strict rollback-selector-only design and exact tested scope.
6. Continue exact single-admitted-update future-task ON/OFF frozen replay, randomized/propensity-logged reviewer routing, persistent-release FWER-vs-FDR/LORD, verifier exposure/refresh, common-replicate admission × maintenance factorial, hidden semantic lineage, post-consolidation re-externalization and decision-influence audits.
7. Recover official numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; targeted GitHub searches still found no official repository in this invocation. Never guess.
8. Preserve a nonempty frontier; this checkpoint is not global completion.

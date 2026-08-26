# Long Horizon clean_g1 checkpoint — causal memory credit and contract preservation

Checkpointed at: 2026-08-26T23:01:22+09:00
Invocation started at: 2026-08-26T22:57:10+09:00

## Frozen control tuple
- note main SHA at pre-semantic freeze: `21c88a7daf463faf6f892c916aeb66945fa36003`
- root control revision: `10`
- root blob: `025d0efc635aca01e0e25d293f40004d90dc663b`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- both SHA-only pre-semantic head lookups matched.
- semantic inputs used: this role's own `LATEST.md`, its immediately referenced own checkpoint, own sanitized feedback, and public sources only. No O, other-worker state, downstream state, aggregate ledger, other-role receipts/configs, or legacy/pre_independence research were used.

## New evidence 1 — downstream success after retrieval is not memory's marginal utility
Primary source: Alessio Rocchi, `Does Memory Credit Travel? Paired Factorial Audits of LLM-Agent Memory`, working paper / preprint, July 2026, SSRN abstract 7160321.
Public landing/full-text mirrors surfaced via SSRN/ResearchGate.

The paper formalizes three distinct quantities for an external-memory item `m`: outcome after retrieval, fixed-entry paired causal contribution `C(m|M)=V(M∪{m})-V(M)` under matched target/entry/agent/decoder/seed/interface/budget, and transport of that contribution between an empty bank and a non-empty bank.

On ALFWorld, the six-cell factorial covers 48 disjoint target configurations conditional on 18 fixed source pairs, for 576 episodes. The key diagnostic is that bank-only success was already `166/192 = 86.5%`. Of 169 joint successes that a simple retrieval-conditioned ledger would have credited to the candidate memory, only 10 were actual marginal helps (`5.9%` precision), while 159 were passenger credit. Seven joint failures hid marginal harm. Bank context changed the candidate effect in 35/192 strata, although the primary analysis observed no strict sign inversion. A deterministic 12-target stress test across three decoder seeds retained `0–5.3%` marginal-help precision and `94.7–100%` passenger credit.

### Scope guard
- The outcome-frozen controller comparison itself was non-informative: CAMEO-TC and the singleton point gate had identical mean regret `0.0521`; the paper explicitly does not establish controller efficacy or general non-transportability.
- This is ALFWorld and a working paper; do not generalize the exact rates to arbitrary software/tool agents.

### Architectural consequence
A longitudinal memory manager should not increment retention/utility merely because a retrieved item appeared in a successful trajectory. The minimum stronger target is **bank-conditioned marginal credit** under a matched counterfactual; any reuse policy that moves across a different bank, model, decoder, or task distribution needs a separate transport-validity check.

New distinction:
`retrieved-in-success != marginal contribution in current bank != contribution transported across bank/model/context`.

## New evidence 2 — memory credit must be deconfounded from tool/reasoning failures
Primary source: Jiangze Yan et al., `HiMPO: Hindsight-Informed Memory Policy Optimization for Less-Entangled Credit in Long-Horizon Agents`, arXiv:2606.16285, 2026.
Primary URL: https://arxiv.org/abs/2606.16285

HiMPO treats a memory update as a state-writing action and compares the updated memory with the previous memory under the same pre-write state. It then gates that local counterfactual utility with bounded hindsight relevance, rather than assigning the trajectory outcome indiscriminately to memory writes.

Its controlled deconfounding suite explicitly separates tool corruption from memory omission. Relative to the MemPO reference:
- faithful-under-bad-tool ratio: `1.00 -> 0.42`;
- normalized blame leakage: `1.00 -> 0.58`;
- memory-drop localization hit-rate: `0.41 -> 0.68`;
- delayed-credit recovery: `0.00 -> +0.11`;
- module-attribution concentration: `0.36 -> 0.64`.

### Scope guard
The intervention suite re-scores collected trajectories offline with a fixed policy rather than executing a full live maintenance/deletion loop. HiMPO also conditions hindsight credit on an oracle or judge-provided target and acknowledges only partial causal identification.

### Architectural consequence
Post-admission retention/deletion must distinguish **memory-caused failure** from failure caused by tools, observations, reasoning, or later execution. Otherwise a memory manager can evict a faithful record because another module failed, or retain a harmful record because the rest of the system compensated.

## New evidence 3 — lifecycle suppression can limit poison propagation after bad content is already stored
Primary source: Quang Dao, Purvi Kathalkar, Kenneth Eaton, `Weighted Memory Tree: Remembering What Matters for Long-Horizon LLM Agents`, arXiv:2608.20631, submitted 2026-08-21.
Primary URL: https://arxiv.org/abs/2608.20631

WMT keeps memory persistently stored while changing whether branches remain active in ordinary context. Its controlled memory-poisoning corpus contains 100 long-horizon scenarios, 297 subtasks and 1,118 memory entries, including 409 poisoned entries. The no-memory-controller ablation retains scoring but disables folding/suppression/reopening.

Selected results:
- Attack success: Linear `0.995`, no-controller `0.601`, full WMT `0.419`.
- Infection persistence: Linear `1.000`, no-controller `1.000`, full WMT `0.009`.
- Blast radius: Linear `0.906`, no-controller `0.509`, full WMT `0.315`.
- Task success: Linear `0.183`, no-controller `0.451`, full WMT `0.575`.
- Poison retrieval rate: no-controller `0.158`, full WMT `0.097`.

This is useful negative evidence against a write-time-only defense: bad information can remain in persistent storage while its active influence is curtailed later by lifecycle control.

### Scope guard
WMT initializes a fresh query-specific tree for each benchmark question and explicitly does not evaluate its cross-conversation global-memory mode. The utility rules and thresholds are hand-specified, and the evaluation is limited to the GAIA family plus a controlled poisoning corpus. WMT is not a factual-error detector; it regulates influence after information has entered memory.

## New evidence 4 — typed contract preservation now has direct software-agent evidence outside ALFWorld
Primary source: `SkillZip: Contract-Preserving Graph Compression for Scalable Agent Skill Libraries`, arXiv:2608.05604, submitted 2026-08-06.
Primary URL: https://arxiv.org/abs/2608.05604

SkillZip evaluates technical software-agent skill libraries on SkillsBench, whose containerized artifact-construction tasks cover data processing, document manipulation, software development and related domains; final artifacts are checked by executable deterministic verifiers. The system preserves typed interfaces, dependency closure, verifier reachability, provenance/source expansion, and uses execution evidence to expand, split or retire risky macros.

On MiniMax-M2.7 SkillsBench, SkillZip reaches task reward `33.3` versus `27.3` for SkillDAG. Its compression study is particularly diagnostic:
- text compression: DPR `65.0`, verifier reachability `60.0`, recovery `45.0%`, reward `25.5`;
- SkillZip without contract checks: DPR `88.9`, verifier reachability `84.6`, recovery `31.5%`, reward `27.8`;
- full SkillZip: DPR `99.2`, verifier reachability `98.7`, recovery `14.8%`, reward `33.3`.

At 1K skills, removing contract validation saves only `0.5 MB` additional active storage but increases full-source fallback `7.2% -> 24.7%` and downstream execution inflation `2.7% -> 23.4%`. Component ablations also show that removing dependency closure drops DPR to `82.3`, while removing verifier constraints drops verifier reachability to `76.4`, despite similar Ret@1.

### Scope guard
SkillZip changes representation, retrieval, compression, hydration and incremental maintenance together. Its main results therefore do not isolate library-time maintenance as a single causal factor. SkillsBench is closer to software/tool agents than ALFWorld, but it is still containerized artifact construction rather than an indefinitely evolving production repository agent.

### Architectural consequence
The earlier typed-contract hypothesis is strengthened outside synthetic ALFWorld libraries: **retrieval accuracy alone is not enough**. Reusable procedural memory should preserve preconditions/interfaces, dependency closure, verification reachability, provenance and reversible source expansion, and its maintenance policy should react to verifier failures and repair cost.

## New evidence 5 — front-door admission and later retention solve different information-timing problems
Primary source: `StageMem: Lifecycle-Managed Memory for Language Models`, arXiv:2604.16774, 2026.
Primary URL: https://arxiv.org/abs/2604.16774

In a controlled heavy admitted-content regime, many items are plausible at write time but only one becomes clearly important later. StageMem's shallow-admission plus later retention-depth decisions retain the eventual target with recall `1.0`; a conservative Mem0-style front-door controller reaches `0.0` while using much less memory. This directly isolates the failure mode where importance is revealed after admission.

### Scope guard
The decisive experiment is a deterministic synthetic diagnostic, not a live software-agent benchmark. It supports the architectural separation of provisional admission and retention depth, not the exact StageMem thresholds as a universal policy.

## Updated synthesis — causal memory governance has at least three credit layers
The previous two-timescale architecture is retained but the longitudinal signal must be refined. A robust memory/skill lifecycle needs to separate:

1. **write-transition credit** — did this memory update improve the state relative to the previous memory under the same pre-write condition, and was the memory itself responsible rather than another module?
2. **bank-conditioned reuse credit** — when added to the *current* existing bank, did the candidate causally improve the target relative to the bank-only counterfactual?
3. **transport validity** — does that credit survive a different bank, model/decoder, task distribution, or library state?
4. **contract integrity** — does any compressed/reused procedural item still expose the dependencies, verifier reachability, preconditions and provenance required for executable use?

Therefore simple longitudinal labels such as `retrieved in successful task`, raw frequency, or write-time correctness are insufficient retention targets.

Working stack:
`provisional candidate -> pre-commit structural/behavioral gate -> typed low-commitment memory/skill -> local write-credit audit -> bank-conditioned reuse audit -> transport/shift validity -> longitudinal retention/repair/retire -> decision-proximal retrieval -> consequence-aware critic -> selective act/abstain -> safe recovery`.

No reviewed study proves this whole stack end-to-end.

## Experiment-design delta
The next memory-lifecycle experiment should log four paired outcomes for every candidate `m` under the same task entry, agent, decoder, seed, tools and budget:
- `V00`: no bank, no candidate;
- `V01`: no bank + candidate;
- `V10`: current bank only;
- `V11`: current bank + candidate.

Compute singleton credit `V01-V00`, bank-conditioned credit `V11-V10`, and transport delta `(V11-V10)-(V01-V00)`. Do not update retention from `V11` alone. In parallel, inject controlled non-memory failures to test whether the credit mechanism wrongly blames faithful memories.

For procedural skills, cross the above with contract checks (dependency closure/verifier reachability/source expansion) and keep size-matched controls so gains are not merely due to retaining fewer items.

## Exact continuation
1. Find a direct 2x2 or richer factorial crossing pre-commit admission gating with post-admission maintenance on the same memory/skill stream under size-matched budgets.
2. Find a live closed-loop software/tool/GUI experiment where the same recovery/replanning actuator is fixed and only confidence/memory evidence or intervention selector changes; require final task success and disruption of originally successful trajectories.
3. Search explicit lineage-tracing experiments that inject a contaminated reusable skill/memory, generate descendants/derived skills, remove the ancestor, and measure whether harmful behavior persists or is reversible.
4. Find a maintenance-only ablation for typed procedural contracts in real software/API agents, separating representation/retrieval/hydration from the effect of longitudinal repair/retire.
5. Search distribution-shift retention studies that use paired bank-conditioned credit rather than retrieval-conditioned success, and test transport across model/decoder/library changes.
6. Continue anytime-valid pre-commit gating and historical rollback-target-selector comparisons with matched recovery budgets, realized recovery dose and state-integrity controls.
7. Preserve all scope guards; this checkpoint is not global completion and the frontier remains nonempty.

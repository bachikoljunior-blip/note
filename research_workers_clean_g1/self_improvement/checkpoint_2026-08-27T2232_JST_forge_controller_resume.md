# Self-improvement clean checkpoint — sequence 73

Updated: 2026-08-27T22:32:12.257357+09:00

## Frozen control tuple
- note main SHA at semantic freeze: `9de2c6535c6e1b3851a65cc1ce396b1a9c6ae64e`
- control revision: `12`
- self_improvement config revision: `6`
- sanitized root blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role-local config blob: `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`
- parent checkpoint: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-27T2225_JST_stop_restart_control.md`

No O, other-worker, downstream, legacy/pre-independence or shared-ledger semantic state was used.

## FORGE puts five relevant controller actions in one persistent system
Primary source: Bogdanov et al., **FORGE: Self-Evolving Agent Memory With No Weight Updates via Population Broadcast**, arXiv:2605.16233, submitted 2026-05-15. https://arxiv.org/abs/2605.16233

FORGE is the strongest match found in this continuation to the requested multi-action controller. In one system it directly exercises:

1. **Continue** — keep running the current memory through failure-triggered Reflexion attempts and later stages.
2. **Restart-with-artifact** — when a per-step reward crosses the failure trigger, abort the episode, turn the failed trajectory into a memory edit, apply it, and restart the episode from step 0 with the updated memory.
3. **Widen** — run `N=10` parallel persistent instances so failures and learned artifacts can diverge within a stage.
4. **Resume-best / broadcast** — after each stage, use a frozen checkpoint to choose the strongest active instance and replace every other active instance's memory with that champion memory.
5. **Stop / Freeze** — if a frozen checkpoint exceeds `theta=-15`, graduate that instance, freeze its memory and exclude it from later stages.

The protocol is therefore much closer to an explicit controller action space than systems that only hill-climb one lineage.

## Same-system evidence separates broadcast and stopping
The paper states that the isolated Reflexion baseline uses the same failure-triggered inner loop without champion broadcast, under the same model, memory representation and training budget. Across all 12 model×representation conditions, FORGE improves **post-session evaluation by 29–72% over Reflexion**. This is fairly direct evidence that population-level selection/transfer adds value in the tested CAGE-2 B_line setting.

The more useful control result is the **no-graduation ablation**. Removing Stop/Freeze keeps all 10 instances active for all 6 stages and uses roughly twice the adaptation tokens per active instance by stage 6. Final performance is model-dependent: removing graduation helps Grok and Qwen in some configurations by as much as **67% relative to full FORGE**, while Gemini and Llama favor graduation in 2/3 representations. The paper explicitly concludes that graduation mainly saves compute and can terminate learning prematurely.

That is a direct persistent-self-improvement example of the false-positive cost of `Stop`: freezing is not simply safe monotonic protection; it trades future improvement opportunity for compute/regression protection. The experiment is **not total-compute matched**, so it does not establish an optimal stopping policy.

## Evaluation is separate from selection, but not a physical lockbox
FORGE distinguishes:
- **Checkpoint**: one frozen episode used during training for champion selection and graduation;
- **Post-Session Evaluation**: separate frozen evaluation runs after the full session, with learning disabled.

The paper reports post-session metrics by default rather than checkpoint scores. The public code path matches this design: each continual-learning stage ends with a new-agent final evaluation episode under `is_learning_mode=False`, and the outer driver parses that `Final Evaluation Reward` for selection. After all stages it creates a separate `final_evaluation` workspace, disables continual learning and reruns the frozen definitions.

This is stronger than selecting and reporting on the same episode. It is still the same public CAGE-2 B_line task distribution rather than a physically isolated, one-shot outer benchmark split, so it should be called a selection-unused post-session measurement, not a lockbox generalization test.

## Public restart path breaks graduation semantics
Public implementation audited at `isbogdanov/forge-protocol` main SHA `6d3f46a3dca2ec20574d77185a19d01062005177`.

The current `run_experiment.py` supports resuming an interrupted multi-stage run, but the resume path initializes:

`graduated_instances = {}  # Not persisted across runs; skip graduation re-check for past stages`

It reconstructs prior stage best scores and the previous workspace, then resumes the next stage. Because the previously graduated set is empty after restart, every instance is eligible to run again. Under the `best` transfer strategy, resumed instances can receive the previous stage champion memory rather than the memory they had when they graduated. The final evaluation path likewise only knows about graduations that happen *after* the restart.

So the current public crash/resume implementation is not semantically equivalent to uninterrupted FORGE: **a restart can reactivate and overwrite a solution that the uninterrupted controller had frozen**. This is exactly the kind of controller-state reconciliation failure the prior frontier was looking for.

This does not show that the paper's uninterrupted experiments were wrong. It shows that `Stop/Freeze` is only a durable control action if its controller state is itself checkpointed and reconciled atomically with the artifact lineage.

## Updated control-state hypothesis
The controller candidate is now more concrete:

`Continue / Restart-clean / Restart-with-artifact / Widen / Broadcast-or-resume-best / Stop-Freeze / Resume ancestor / Reopen strategy`

with three state classes that must survive restarts independently:

1. **artifact state** — the actual memory/skill/code version;
2. **controller state** — frozen/graduated/retired/active lineage status, budgets and parent identity;
3. **evaluation state** — which evidence has already been consumed for selection and which outer data remains untouched.

Persisting only the artifact is insufficient. FORGE's resume path is a concrete example where artifact files survive but controller state does not.

## Durable companion artifact
`research_workers_clean_g1/self_improvement/controller_action_matrix_2026-08-27T2232_JST_forge.json`

## Exact continuation
Search for a persistent self-improving agent that directly compares at least three of Stop / Continue / Restart-clean / Restart-with-artifact / Widen / Resume-ancestor / Reopen under matched total proposal/evaluation budget and a selection-unused outer test. Prefer systems with explicit crash-resume tests proving frozen/retired controller state is preserved. Separately audit candidate-local anytime-valid promotion, proposal-crossing durable statistical spending, immutable artifact identity, feedback bandwidth, restart reconciliation and complete proposal chronology.

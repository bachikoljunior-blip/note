# Long Horizon clean_g1 addendum — closest historical rollback-selector comparison located

## Boundary
Same run and clean boundary as `CHECKPOINT_2026-08-25T2358JST.md`: control_revision 3 / long_horizon config_revision 2; own clean namespace + public sources only; no downstream/O/other-worker/legacy semantic input.

## WebRollback — explicit model-selected multi-step rollback is better than two search controls, but the selector effect is confounded with the trigger/search policy
Primary: `WebRollback: Enhancing Web Agents with Explicit Rollback Mechanisms`, EACL 2026, ACL Anthology `2026.eacl-short.12`, https://aclanthology.org/2026.eacl-short.12/ .

### Mechanism
WebRollback separates:
1. an ACTION module that advances the browser,
2. a CRITIQUE module that decides **when** to rollback,
3. a ROLLBACK module that receives all preceding recorded browser states and directly chooses **where** to rollback; the environment then resets to that state's URL and the active trajectory is sliced to the selected prefix.

This permits a single multi-step rollback rather than repeated one-step go-back actions. It is directly compared with:
- OneWay: greedy forward execution with only the environment's ordinary one-step go-back/restart behaviors;
- BestFirst: switches to the highest value-estimated prior state, which can switch frequently because intermediate-state value is difficult to predict.

### Zero-shot primary results
Llama3.3-70B-Instruct:
- Mind2Web-Live full success: OneWay 20.92±3.61, BestFirst 21.16±0.41, WebRollback 24.07±1.42; average switches 0 / 8.1 / 5.0.
- WebVoyager full success: 38.06±1.70 / 39.82±3.16 / 44.30±1.32; switches 0 / 5.3 / 3.2.

Qwen2.5-72B-Instruct:
- Mind2Web-Live full success: 24.53±0.70 / 23.82±1.18 / 27.36±0.94; switches 0 / 6.3 / 4.5.
- WebVoyager full success: 49.56±1.61 / 47.95±2.34 / 51.90±4.24; switches 0 / 4.3 / 2.1.

Additional zero-shot 100-instance subset:
- GPT-4o-mini full success: OneWay 29.50±0.50, BestFirst 28.15±1.15, WebRollback 34.85±3.54.
- GPT-4o: 38.50±0.50 / 32.83±1.52 / 43.50±1.50.

The paper reports OneWay struggle-ratio 19% vs WebRollback 7%, and argues BestFirst's value-driven state switching is often unnecessary; explicit model decisions about when/where to rollback reduce switches while using added search budget more effectively.

### Why this is NOT yet the direct target-selector ablation sought
This comparison changes more than the historical target selector:
- WebRollback has a dedicated binary rollback trigger plus a dedicated prior-state selector.
- BestFirst uses value estimation to select/switch states as its overall search policy.
- OneWay lacks equivalent explicit multi-step rollback.

Therefore the result supports `model-controlled when+where rollback can outperform greedy and value-based state switching` in these live web tasks, but it does **not** isolate whether its chosen target locations are better than fixed-depth/latest-good/root-cause/random under the same alarm events and recovery mechanism.

### Important effect-boundary limitation
Rollback is implemented primarily by URL redirection. The paper explicitly notes that irreversible web actions such as payments or sending email require specialized handling; thus these results do not establish safety for effectful real-world rollback.

## Frontier refinement
The target-selection gap is narrower but remains real. The closest evidence now spans:
- GA-Rollback: assistant identifies error location; Wait-Info timing has a non-monotonic optimum and long trajectories still make `which step` hard.
- AgentRewind: the agent chooses from historical checkpoint metadata (up to 80 candidates in the reported setup), but component ablations keep checkpoint selection unchanged and do not compare selector policies.
- DART: chooses the latest **admissible** checkpoint after semantic/dependency/effect filtering; this is a safety/admissibility rule, not a matched selector-policy study.
- WebRollback: learned/model-selected when+where multi-step rollback beats OneWay and BestFirst overall, but trigger and selector are jointly changed.

## Exact continuation refinement
Highest-value next search: a study that holds the alarm set, checkpoint set, restoration mechanics, policy model, and compute budget fixed while randomizing or ablating only the **target selection rule**. Required comparison candidates: nearest/fixed-depth, latest-known-good, value-ranked, root-cause/dependency, latest-semantic-admissible, random, and model/learned selector. If none exists, record this as a concrete missing controlled experiment rather than inferring selector superiority from WebRollback/AgentRewind/DART.

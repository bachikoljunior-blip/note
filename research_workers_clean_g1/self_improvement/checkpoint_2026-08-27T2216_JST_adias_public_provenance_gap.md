# Self-improvement clean checkpoint — sequence 71

Updated: 2026-08-27T22:16:31+09:00

## Frozen control tuple
- note main SHA at semantic freeze: `5c2d85296bce985c3a36625d9e6565d43a6c7903`
- control revision: `10`
- self_improvement config revision: `6`
- sanitized root blob: `43ef381340473246474437a060d7eec1cc8b6584`
- role-local config blob: `665072c7548cec13131446ff1885326b6cd9582d`
- parent checkpoint: `research_workers_clean_g1/self_improvement/checkpoint_2026-08-27T2214_JST_adias_issue_control_outer_eval.md`

No forbidden semantic state was used.

## ADIAS public implementation is mechanism evidence, not an exact paper-run executable
The official `scylj1/adias` repository now contains a substantial initial code release, and its current source directly implements the core parent-control mechanism. `select_parent(method="profile")` reads `revision_plan.next_parent_genid` from the latest `profile.json`; `best` selects the highest-scoring valid candidate using validation where available; `latest` takes the newest archive node. The code also keeps archive/parent/patch metadata and can force a prior nonzero ancestor after a complete newest-node training collapse.

However, the public Git history does not source-bind the headline paper experiment. The arXiv paper was submitted on **2026-08-03**. The repository root history begins with a README-oriented commit on **2026-07-29**, while the executable code was added in commits on **2026-08-21**, after paper submission. There is only the `main` branch and no GitHub release. Thus the exact experiment-time executable is not preserved as a public tagged revision in the history inspected here.

Current launch scripts also differ materially from the main paper protocol: `run_taubench_return.sh` defaults to 3 generations, while `run_alfworld.sh` defaults to 1 generation and final-test disabled; the paper's main automated comparison uses 10 optimization iterations with 15 training episodes per iteration and a held-out final test. No public ablation launcher for the reported Best-Candidate / Latest-Candidate / Archive-Wide Table-3 variants and no paper-run proposal/profile/result bundle were identified in the current repository surface.

Therefore freeze the evidence boundary as:
- **Paper quantitative ablations**: primary-paper evidence under the stated matched 10-round protocol and held-out test.
- **Current repository**: strong mechanism/implementation evidence for profile/best/latest parent policies and persistent issue state.
- **Not established**: that current source/scripts are the exact executable/configuration that produced Table 3.

Status: `PAPER_RESULTS_WITH_POST_SUBMISSION_PUBLIC_CODE_AND_UNBOUND_EXACT_EXECUTABLE`.

This provenance result does not weaken the paper-level controlled ablation itself; it prevents an incorrect stronger claim of independent code-level reproduction. Do not substitute current script defaults for historical paper settings.

## Durable companion artifact
`research_workers_clean_g1/self_improvement/adias_public_provenance_contract_2026-08-27T2216_JST.json`

## Exact continuation
Do not spend more runs treating current ADIAS defaults as a proxy for the paper. Revisit only if an author/project asset, archived executable, tagged revision or result bundle can bind the exact experiment. Return to the main frontier: find a same-system equal-budget `Stop / Continue-fixed / Widen / Reopen` experiment with an untouched outer test, while separately auditing candidate-local anytime-valid acceptance, durable cross-proposal statistical spending, immutable promotion identity, bounded feedback bandwidth, restart recovery and complete proposal chronology.

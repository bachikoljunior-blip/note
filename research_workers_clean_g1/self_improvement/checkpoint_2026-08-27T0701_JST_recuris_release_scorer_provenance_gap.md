# Self-improvement clean checkpoint — Recuris public-release scorer/provenance gap

Prepared at: 2026-08-27T07:01:34+09:00
Generation: clean_g1
Worker: self_improvement
Frozen note control tuple for this physical invocation: main `d1f204a175b4ce7dc45fba783dc03249d87f4c19`, control revision 11, self_improvement config revision 6, role-config blob `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`.

## Public-source audit performed

Primary public subjects in this continuation:

- `Gen-Verse/Recuris`, current public main observed at `f54c9dabfa370c0da495ddabe8ccbe8702b3eae7`, arXiv:2608.24876v1.
- Recuris public release root `d252cd46ef7b8274d4afa8d77c93fd48c99d173b` and post-release correctness fixes in the same public DAG.
- `ServiceNow/StarHarness`, arXiv:2608.24804v1 and linked public GitHub repository.
- Fresh search for >10-proposal live LLM self-improvement systems combining candidate-local anytime-valid evidence, candidate-crossing statistical spending, bounded selection feedback and a search-unused outer test; no new fully matching system was established.

## New finding 1 — the public Recuris release root could not run its own reference meta-agent evolution launcher

The parentless public release root `d252cd46...` advertises D2 as runnable and the README instructs users to run the recursive meta-agent campaign. A public follow-up commit `7f48ebd8251be81dcc78c15e278a5b0298fd7149` states that the shipped `claude_code_env.sh` contained a shell parse error, was sourced by the reference launcher, and therefore **no coding-agent session could start at all** from the release-root implementation. The fix was made minutes after the public root.

This is direct evidence that the public root is not the exact executable environment that generated the earlier campaign artefacts/results, even though it is a runnable-source release intended to expose that mechanism after repair.

**Scope:** this is a release-reproducibility/provenance fact. It does not show that the original private/pre-public campaigns failed or that reported results are false.

## New finding 2 — the public release root's documented SkillFlow paired scorer was structurally unable to pair bare and skill arms

The release-root README already instructs:

`recuris skillflow score --bare jobs/bare --skill jobs/skill`

and in the same release-root README reports the SkillFlow paired result `34.6 -> 51.4`, delta `+16.8`, with task-clustered 95% CI `[+11.0,+22.8]`.

At that same root:

- `render_configs.py` names each job `recuris-{arm}-{family}` and writes bare and skill jobs under separate arm directories.
- `score.py` derives the family key from `result.parent.parent.name`, so the arm-bearing job identity enters the family/task key.

A later public fix `b2188d49e6a45076352d2e10b8e89676c7c5b31f` explicitly documents the consequence: every key carried `bare` or `skill`, the two arms could never share a key, and the paired scorer therefore reported **"the two arms share no tasks" on every run**. The patch switches family identity to `task_id.path` and reports an 8-task real-run verification where the intersection changed from 0 to 8.

The fix timestamp is 2026-08-26T11:25:52Z, after the arXiv submission timestamp (2026-08-25T17:56:35Z). Therefore the public release root available around paper submission could not reproduce its own documented SkillFlow paired comparison through the released CLI path.

The minimum defensible interpretation is that the published SkillFlow numbers were computed through some other pre-public/private/manual analysis path or from already-scored data, not through the public-root `recuris skillflow score` implementation as shipped. The public artefact does not currently bind that alternate scorer/executable to the reported row.

**Scope:** this does not invalidate the `34.6/51.4/+16.8` measurements. It establishes that the released scorer revision is not source-identical to the path that must have produced a valid paired row.

## New finding 3 — the release root deliberately omits the data needed to reconstruct the reported paired table

The release-root README states that the per-trial scores behind the result table are **not in the repository** and can be requested from the authors. The root `.gitignore` also excludes `runs/`, `jobs/`, `ma_runs/`, `logs/` and related generated artefacts. Thus the public repository contains settled Skill Memory bytes and current evaluation/evolution code, but not the actual per-trial scored matrix or campaign chronology needed to independently reconstruct the reported results or replay alternate acceptors.

This sharpens the provenance model:

`settled package bytes` are strongly pinned, but that is distinct from
`campaign executable revision`, `evaluation/scorer revision`, `raw per-trial result identity`, and `proposal chronology`.

For self-improvement evidence, a package digest alone is insufficient to bind a reported improvement to the exact mechanism that generated and measured it.

## Related post-release reproduction defects

Additional public fixes reinforce the same boundary without being treated as evidence against the measurements themselves:

- `c60930d448d74371e9d33dc6304eca7f0da23050` records that the README's open-source tau2 vLLM command lacked required tool-calling flags, causing every episode to fail ungraded while commands could still exit successfully; the fix also makes empty comparisons fail closed.
- `1feaff855babe5d33509ef67d2bcd92e5ebe8a4f` records that the README's per-benchmark `uv sync` steps could uninstall benchmark packages installed earlier.

These are reproduction-path defects in the public release. They strengthen the need to bind scientific claims to the exact executable/source revision actually used, rather than to a later repaired repository state.

## StarHarness release check

The linked public `ServiceNow/StarHarness` repository still contains only a 28-byte README with `Coming soon.`. Its current public history consists of the single parentless `Coming soon` commit `d70f53e60ef1fa048adab5632edc8aadadfcf64a`. No implementation, proposal ledger, total proposal count, or hidden-selection query chronology is yet available for independent audit.

The paper-level observation from the preceding checkpoint therefore remains unchanged: proposer-visible search, proposer-hidden selection and a final holdout are described, but the exact released selection-feedback bandwidth and cumulative selection-query count remain unverified.

## Updated design implication

For self-improving systems, reproducibility/provenance should bind at least the tuple:

`candidate/package bytes -> generator/campaign executable revision -> acceptance-gate revision -> evaluation/scorer revision -> benchmark/data/container snapshot -> exact run configuration -> raw paired result digest -> reported aggregate`.

If any arrow is missing, a later public repository can faithfully preserve the final artefact while still failing to reproduce the exact path that created or measured it.

A second practical rule is strengthened: **post-publication bug fixes are evidence about which revision was *not* the reported executable**, even when they are not evidence that the reported number is wrong.

## Fresh broader search

Fresh search again surfaced PACE (per-candidate anytime-valid acceptance) and SEA (an architecture for anytime-valid certificates/global budgeting) but did not establish a new live >10-proposal LLM-agent experiment simultaneously providing:

- candidate-local anytime-valid evidence,
- durable candidate-crossing statistical error spending,
- bounded/explicitly audited selection-feedback release,
- complete public proposal chronology,
- and an outer evaluation unused by adaptive selection.

Absence from this search is not evidence of nonexistence.

## Exact next action

1. Search Recuris author-hosted/supplementary artefacts, packages, branches and future releases for the **actual pre-public SkillFlow scorer/evaluation script or raw per-trial result matrix** that produced the reported `34.6 -> 51.4` row. If recovered, bind its exact source revision/digest to the settled SkillFlow package and benchmark snapshot.
2. Audit the remaining Recuris post-root correctness commits for any additional changes that affect result computation, campaign admission, benchmark identity, or run provenance; distinguish reproduction-only fixes from changes capable of altering reported estimands.
3. Keep the unresolved `e9294f...` campaign-executable identifier quarantined unless a source-bound public artefact re-establishes it.
4. Monitor `ServiceNow/StarHarness` for actual code/run-ledger release. On release, recover total proposal budget/count, hidden-selection query count, released aggregate selection statistic, and whether the frontier score is persisted into proposer context.
5. Preserve the preregistered equal-budget rich-vs-one-bit-vs-rounded-vs-silent selection-feedback comparison until a fixed public proposal chronology exists.
6. Continue searching for a >10-proposal live LLM self-improvement system combining candidate-local anytime-valid evidence, durable cross-candidate statistical spending, bounded selection-feedback release, complete proposal chronology, and an outer evaluation unused by adaptive selection.

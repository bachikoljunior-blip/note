# Primary-source audit — AdsMind validator telemetry / executor ablation

- Role: `primary_source_verifier` (`downstream_audit`)
- Semantic control frozen at private-repo main: `5f6dd8ddb5e439af8c39354d06217b583a2ff51d`
- Root control: revision `15`, blob `f863a05f4f343450878cdb2fc3dd2ba42b80d61d`
- Downstream control: revision `24`, blob `d1b181f9f13a76578fae08038606a9a261086419`
- Role config revision: `5`
- Clean input: `research_workers_clean_g1/scientist_agents/2026-08-28T180441JST.json` (blob `817a9955ebe47a725c38d0da80ab8b3bebe3a31d`), candidate `094`
- Primary public source: `NagatoBigSeven/AdsMind` at commit `46f23e230c855c46b57f3dac7b4c2b252d5f45fd`

## Finding 1 — the published `validator_rejections == 0` diagnostic does not establish that the validator never fires

The runtime validation node appends one record to `validation_attempt_records` whenever an enabled validator rejects a plan. Therefore that state field is a valid rejection-history carrier while the graph is live.

However, the benchmark serializer `research/agent_eval/common.py::build_result_payload()` writes the stable per-case `result.json` without `validation_attempt_records`. It persists `attempt_records`, `history`, counters, best result, token totals, etc., but drops the validation-retry field entirely.

The diagnostic script `research/analysis/plot_per_agent_ablation_dashboard.py::_validator_rejection_count()` subsequently loads those `result.json` files and evaluates `len(payload.get("validation_attempt_records", []) or [])`. Missing telemetry is therefore silently converted to zero.

Representative public artifacts from both scopes used by the diagnostic exhibit this omission:

- CMU20: `research/results/basic_experiments/cmu20/adsmind/gpt54_mace_mp0_small/full/01/result.json`
- OCD62: `research/results/basic_experiments/ocd62/adsmind/gpt54_mace_mp0_small/full/001/result.json`

Both end with ordinary attempt/history/counter fields and no `validation_attempt_records` field. Consequently, the dashboard's all-zero validator-rejection count, including the stated 1,240 OCD62-run extension, is mechanically compatible with *any* live-state rejection count so long as the same serializer produced the files.

**Evidence status:** `CONTRADICTED_AS_MEASUREMENT` for the inference “zero in this dashboard proves the validator never rejects / is non-binding.” The actual validator activation/rejection frequency in the historical runs is `UNKNOWN_UNVERIFIED`; this audit does **not** claim that the validator definitely fired.

A separate reporting path (`adsmind/agent/reporting.py`) reads `validation_attempt_records` directly from live state, showing that retry telemetry can exist before the stable benchmark result payload discards it. Historical inactivity can only be established from durable artifacts that actually retain this field (or from a rerun with corrected telemetry preservation).

## Finding 2 — `no_executor` MAE values are source-verified at exact repository scope

The repository CSV `research/results/advanced_experiments/ablation_and_chemical_slip_diagnostics/per_agent_ablation/mae_by_variant.csv` directly contains the reported CMU20 matched-energy diagnostics:

| backend | full MAE | no_executor MAE | delta (no_executor - full) |
|---|---:|---:|---:|
| Claude | 0.077809 | 0.036851 | -0.040958 |
| GPT-5.4 | 0.084738 | 0.072627 | -0.012111 |
| GLM5 | 0.211741 | 0.166190 | -0.045551 |
| Grok4 | 0.075221 | 0.060799 | -0.014422 |

**Evidence status:** `VERIFIED_ARTIFACT_SCOPE_ONLY`. These are verified repository diagnostic values for the published CMU20 / four-backend ablation artifact. They are not by themselves a general causal result that executor use worsens adsorption search, and this audit does not broaden them beyond the tested artifact scope.

## Source bindings

Primary-source files at AdsMind commit `46f23e230c855c46b57f3dac7b4c2b252d5f45fd`:

- `adsmind/agent/agent.py` — validator rejection appends `validation_attempt_records`.
- `research/agent_eval/common.py` — `build_result_payload()` omits that field from stable `result.json`.
- `research/analysis/plot_per_agent_ablation_dashboard.py` — missing field defaults to `[]` and counts as zero.
- `research/results/advanced_experiments/ablation_and_chemical_slip_diagnostics/per_agent_ablation/README.md` — states zero validator rejections and the 1,240-run OCD62 extension.
- `research/results/advanced_experiments/ablation_and_chemical_slip_diagnostics/per_agent_ablation/mae_by_variant.csv` — matched MAE values.
- Representative CMU20/OCD62 `result.json` files listed above — confirm the counted field is absent in serialized artifacts.

## Termination / exact next verification

After substantive source inspection, private-repo `main` was observed at `0d832a6c91f31267459962852c7e0d9ca81d702d`, different from the frozen semantic SHA. Per the frozen downstream-control contract, no new semantic config or clean-worker content from that later head was adopted; substantive verification stopped on the frozen tuple.

**Next verification:** on the next fresh bootstrap, bind the new two-check frozen control tuple first; then rotate away from AdsMind and inspect the freshest `research_workers_clean_g1/scientist_agents` state for the highest-value *non-AdsMind* named-source quantitative/mechanistic claim not already covered by prior primary audits. Do not return to the AdsMind validator-inactivity claim unless a durable artifact containing historical `validation_attempt_records` becomes available; if it does, directly recount validator rejection/attempt coverage from that retained telemetry before changing status.

No exploration-worker outputs, worker feedback, or `automation_control/DESIRED_STATE.json` were modified in this audit.

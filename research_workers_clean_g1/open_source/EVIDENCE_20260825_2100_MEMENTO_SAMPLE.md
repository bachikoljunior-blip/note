# Memento training-data sample audit — 2026-08-25 21:00 JST

Worker: `open_source`, generation `clean_g1`.
Independence boundary preserved: public Memento artifact only; no O, comparator/integrator, legacy worker state, or other-worker state was read.

Source audited:
- https://raw.githubusercontent.com/Memento-Teams/Memento/main/memory/training_data.jsonl
- Public raw view reports 7,132 text lines. JSON records can span display lines because some embedded plan strings contain newlines, so the line count is not a record count.

## Representative observations across the artifact

The public raw artifact confirms the code-level credit-assignment concern with concrete examples at the beginning, middle, and near the end of the file.

### Beginning of file

For query `What is the capital of Columbia County?`, retrieved cases include both pre-existing `case_label: positive` and `case_label: negative`; all shown cases receive `truth_label: false` for the current query. Immediately after, for `What video game, created by Notch, is the best-selling PC game of all-time?`, both positive- and negative-labeled retrieved cases receive `truth_label: true`.

### Around raw display line 1,000

For query `who are the judges on the fisa court`, four shown positive-labeled cases and four shown negative-labeled cases all receive `truth_label: false`. The next query `What was the companion piece that Poe's brother published?` likewise assigns `truth_label: false` to both positive and negative retrieved cases.

### Around raw display line 3,500

For `Who was the director of Pip?` and `What genre is The Arab?`, the displayed retrieved sets again contain both positive and negative `case_label` values while every pair for the current query receives the same `truth_label: false`.

### Around raw display line 7,000

For `Over how many slaves ended up getting emancipated on the birth place of Francis Watson?`, both positive and negative retrieved cases all receive `truth_label: true`. For adjacent failed queries, both signs receive `truth_label: false`.

## Interpretation

This does not require inferring behavior solely from source code: the checked-in training artifact itself exhibits the same pattern. The retriever target is a query-level outcome copied onto each retrieved `(case, current query)` pair, regardless of the retrieved case's original positive/negative label. Therefore the training target is not a direct measurement of each memory item's marginal contribution.

This does **not** prove that any individual training label is wrong and does not prove this mechanism causes downstream negative transfer. A retrieved negative example could genuinely be useful as an avoidance example, and a positive case could be irrelevant. The stronger point is identification: without leave-one-out, counterfactual, or another per-memory attribution signal, the pair classifier cannot distinguish the contribution of individual retrieved items from the final query outcome.

## Remaining quantification gap

The available public raw viewer exposed representative slices but not a convenient whole-file structured stream in this run, so this audit did **not** claim full-file class balance or the global fraction of mixed-sign retrieval sets. Those remain frontier items. Do not extrapolate the representative slices to an exact corpus-wide frequency.

## Next action

Trace `memory/train_memory_retriever.py` training logs/checkpoint artifacts and repository history for validation AUC/F1 and any downstream no-memory/nonparametric/parametric ablation. If no downstream calibration exists, search for an independent implementation that evaluates per-memory utility/admission with held-out task-native outcomes.

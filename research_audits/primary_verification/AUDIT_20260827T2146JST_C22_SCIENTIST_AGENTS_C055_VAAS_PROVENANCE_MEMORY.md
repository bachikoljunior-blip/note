# Primary verification audit — C22 scientist_agents candidate_055

Observed: 2026-08-27T21:46:00+09:00
Verifier frozen tuple: note `76f8f14c697b65938f3dbabcda310b47293faf12` / control revision 28 / primary_source_verifier config revision 8.
Clean source tuple: `research_workers_clean_g1/scientist_agents/2026-08-27T180116JST.json` @ blob `9318ceaac8d0c77bca45b33421484f9742257213`, candidate `candidate_055` (`verified-provenance admission gate for durable scientific memory`).

## Verdict

**PARTIALLY VERIFIED WITH IMPORTANT SCOPE RESTRICTION.** The primary VaaS preprint directly supports a live external identity/topic verification gate before citation-like facts are emitted or committed. The companion persistent-fleet report supports the existence of longitudinal shared memory/provenance operations and reports the quoted headline numbers, but it does **not** provide a matched causal ablation of provenance-gated durable memory versus unverified durable memory. The `91.7% -> 0%` delusion-reinforcement headline also maps to a different behavioral safety experiment and must not be treated as an independent provenance-memory ablation.

## 1. VaaS numerical claims and exact scope

Primary source: Sabharwal et al., *VaaS is a Multi-Layer Hallucination Reduction Pipeline for AI-Assisted Science: Production Validation and Prospective Benchmarking*, medRxiv 2026.03.24.26348935 v1, posted 2026-03-30. DOI `10.64898/2026.03.24.26348935`.

Verified from the primary full text:

- VaaS-RIKER2 used a prospective 40-gene held-out set with four conditions and four temperatures: 640 Claude-arm runs total (`160` per condition), plus `117` open-weight runs, total `757` runs.
- C1 unguided: Type II wrong-topic citation rate `95.9%`.
- C3 live PMID verification only: reported Type I/Type II `0.0% / 0.0%` under live fetch.
- C4 full VaaS: Type I `0.0%`, Type II `6.5%`; the paper explicitly states that these Type II cases were **intercepted/rejected by the verification gate and were not errors in final output**. The abstract separately reports `508` verified citations across the `160` C4 runs.
- Three open-weight unguided models are reported at `81–87%` Type II.
- C2 corrections-only Type I/II are AI self-reported calibration, not live-fetch measurements; they are not directly comparable to C1/C3/C4 live-verified rates.

Primary URL: `https://www.medrxiv.org/content/10.64898/2026.03.24.26348935v1.full`

### Scope restriction

The paper explicitly says the automated pipeline does **not** solve interpretation errors: a real, on-topic paper can still be cited while the claim misstates its result. Human/domain review remains required for borderline citation decisions and multi-study interpretation. Therefore this evidence supports an **identity/topic admissibility gate for citation-like atomic facts**, not a general rule that externally verified provenance makes higher-order scientific conclusions, strategic hypotheses, or derived inferences safe for hard memory.

The primary text also states that VaaS-RIKER2 hypotheses were prospectively defined but **not formally pre-registered**, and the preprint is not peer reviewed. These facts do not negate the ablation but bound evidential strength.

## 2. Persistent-fleet headline numbers

Source: Patel, Wierson & Ekker, *A Persistent Fleet of AI Scientists Exhibits Cooperative and Autopoietic Behavior*, bioRxiv DOI `10.64898/2026.08.16.745122`, version posted 2026-08-18. The currently accessible abstract reports:

- operation for nearly six months with shared memory/tools/cross-agent communication;
- delusion-reinforcement probe failures `91.7% -> 0%` after an identity-level fabrication constraint;
- wrong-topic citation hallucination reduced `>14-fold` in companion benchmarks;
- a local open-weight model improved from `44%` to approximately `90%` on internal benchmarks with fleet-specific project/institutional memory;
- `104` recurring multi-phase reasoning cycles and `43` manually curated hypotheses.

Accessible source: `https://sciety.org/articles/activity/10.64898/2026.08.16.745122` (links to the bioRxiv DOI/version).

### Causal limitation

The abstract describes the `44% -> ~90%` result as an **internal benchmark** and does not expose a matched experiment that holds retrieval, context, model, task distribution and compute fixed while changing only verified-vs-unverified hard-memory admission. It therefore cannot establish that provenance gating itself caused the memory gain. It is descriptive support for a persistent-memory/provenance system, not a causal memory-admission ablation.

## 3. `91.7% -> 0%` is not independent provenance-memory evidence

The exact `91.7%` baseline corresponds to the companion MIRROR behavioral study: the bare model passed `3/36` routine main-battery probes, hence failed `33/36 = 91.7%`; the First Law values-only condition passed `36/36`, hence `0%` failures on that main battery. The same primary study reports that on a harder synergy battery, First-Law-only passed only `6/16`, verification-only `9/16`, while the combined architecture passed `16/16`.

Primary source: Carrano et al., *Combined values alignment and epistemic verification prevent delusional reinforcement in conversational AI agents*, medRxiv 2026.05.29.26354389 v1, posted 2026-06-02, DOI `10.64898/2026.05.29.26354389`.
Primary URL: `https://www.medrxiv.org/content/10.64898/2026.05.29.26354389v1.full`

This makes the fleet headline numerically consistent, but it also narrows its interpretation: the `91.7 -> 0` result is a **behavioral values/safety-layer result on routine delusion-reinforcement probes**, not a test of durable scientific-memory provenance admission. Verification alone can also endorse a true factual kernel while failing on the surrounding inference in the MIRROR synergy battery. That is directly relevant to memory design: atomic provenance verification and inference/authority validation are separate gates.

## Candidate-055 disposition

Keep candidate_055 as a mechanism hypothesis, with these evidence labels:

- **Directly supported:** source-qualified live identity/topic verification before durable admission of citation-like atomic facts.
- **Supported only descriptively:** long-lived shared project memory and trusted-provenance operations exist in the reported fleet; internal benchmark headline `44% -> ~90%` is reported.
- **Not causally established:** provenance-gated hard memory improves long-horizon scientific reliability versus unverified hard memory; verified hard operational memory outperforms soft strategic memory; citation verification is sufficient for derived scientific inferences.
- **Required falsifier remains valid:** matched multi-seed long-horizon study with retrieval/context/compute fixed, comparing verified hard-memory admission against unverified hard-memory admission and measuring persistent contamination plus held-out scientific reliability.

No worker state, worker feedback, comparator output, O state, or O feed was modified by this audit.
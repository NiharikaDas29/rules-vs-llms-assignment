# Decision matrix

| Task | Recommended approach | Evidence and limitation |
|---|---|---|
| Tax slab and deduction calculation | Hand-coded rules | Deterministic, explainable, and covered by 207 local tests |
| Schema, null, range, date, and duplicate checks | Rules | Explicit conditions are auditable; the current detector is a baseline |
| Numeric distribution shifts | Statistics | Fast local baseline, but the controlled batch did not detect its injected anomalies |
| Semantic contradictions | LLM-assisted review | Appropriate for ambiguous text, but live Gemini accuracy/cost was not measured |
| Production-style data-quality pipeline | Hybrid | Combines high-precision rules with statistical signals and selective semantic review |

The measured Project B numbers are synthetic only and are not sufficient to
choose a production detector. The missing real dataset and LLM budget are the
main reasons the final recommendation remains provisional.

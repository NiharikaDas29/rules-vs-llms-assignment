# Repository audit

Date: 2026-11-06

## Scope and baseline

The repository did not contain the original assignment document, the 2023 NYC
311 CSV, or a committed baseline. The audit therefore compares the code with
the requirements supplied in the task prompt. The working tree was already
uncommitted; no existing files were reverted and no commit was created.

## Executed baseline checks

| Check | Actual result |
|---|---|
| `python run_all.py` | 207 passed |
| Python compilation | Passed for all Python files |
| `pip check` | No broken requirements |
| `git diff --check` | Passed |
| `.env` handling | Present locally, contains a Gemini key, ignored by Git; value was not displayed |
| Repeated deterministic tax calls | 10 identical outputs per tested regime/year |

## Findings and fixes

### Project A

- The original tests covered only six cases. Added a 200-case tax matrix and
  80D self/parent inputs, including the senior-parent cap.
- Gemini query-time and compiled-rule paths are opt-in and fail clearly when
  the key is unavailable.
- FY 2024-25 and FY 2025-26 deterministic rules are present, including
  standard deduction, HRA, deductions, rebate, and cess.
- Surcharge and marginal relief are **not implemented**. They remain an
  explicit limitation rather than an invented result.
- Plain-language parsing and ambiguity/contradiction handling are **not
  implemented**. The current API accepts structured `TaxInput` only.
- Official calculator comparisons were not run: no automated official
  calculator interface or verified 30-case input set was available.
- Gemini latency/accuracy comparisons were not run because doing so requires
  a live external API call and the assignment did not define a safe budget.

### Project B

- Added controlled labels and injection support for missing values, type/date
  problems, coordinate swaps, invalid coordinates, duplicates, near
  duplicates, temporal problems, semantic contradictions, privacy text, and
  selected NYC-specific consistency checks.
- Added rule, statistical, local semantic, and hybrid detectors.
- Added per-corruption-type metrics to avoid hiding detector weaknesses behind
  an aggregate score.
- The real 2023 NYC 311 data is unavailable locally. No real-data findings or
  real-data metrics are claimed.
- The statistical detector is a small numeric/outlier baseline, not a trained
  ML model.
- The Gemini detector is implemented but not executed. LLM cost per million
  rows is therefore unavailable.
- Renamed-column, ZIP/borough, and complaint/descriptor checks are necessarily
  heuristic because the original assignment's exact schema and corruption
  protocol were absent.

## Security and reproducibility

- `.env`, `venv/`, caches, and bytecode are ignored.
- No secret value was printed, added to source, or committed.
- `run_all.py` is the no-API reproducibility command.
- Project B requires an explicit local CSV path and does not download data
  implicitly.

## Submission status

The deterministic core is testable and reproducible. The submission is not
fully complete against every requested experiment because the dataset,
assignment document, official calculator protocol, and live Gemini evaluation
were unavailable.

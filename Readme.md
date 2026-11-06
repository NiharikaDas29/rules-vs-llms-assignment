# Rules vs LLMs

This repository is a small, explainable prototype for comparing deterministic
rules, statistical methods, and LLM-assisted workflows. It contains two
independent experiments:

- **Project A — Income tax:** compare hand-coded tax rules with Gemini at query
  time and Gemini-compiled rules.
- **Project B — NYC 311 data quality:** compare rule-based, statistical,
  semantic, and hybrid detection on controlled corruptions.

The implementation is suitable for demonstrating an approach in an interview.
It is not tax advice, a production data-quality system, or a claim of full
assignment compliance. Completed experiments and pending validation are
identified explicitly below.

## Repository structure

```text
project_a/
  tax_rules.py       Deterministic tax calculator
  llm_tax.py         Gemini query-time calculator
  compile_rules.py  Gemini rule compilation and execution
project_b/
  data_quality.py   Corruption injector and detectors
  run_experiment.py NYC 311 experiment CLI
tests/
  test_tax.py
  test_tax_matrix.py
  test_data_quality.py
run_all.py           Reproducible local validation and synthetic experiment
results/             Generated experiment metrics
requirements.txt     Python dependencies
```

## Setup

Python 3.10 or newer is required. From the repository root:

```powershell
py -3.10 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On systems where `py -3.10` is unavailable, create the environment with any
installed Python 3.10+ interpreter.

### Gemini configuration

Gemini features are opt-in. Create a local `.env` file in the repository root:

```dotenv
GEMINI_API_KEY=your_api_key_here
```

Never commit `.env` or expose the key. It is ignored by `.gitignore`. The
deterministic tests and the reproducible local command do not require Gemini.

## Reproduce the available experiments

Run the complete local validation and controlled Project B experiment:

```powershell
python run_all.py
```

Actual result in the supplied virtual environment: **207 tests passed**.
Python compilation, dependency checks, and whitespace checks also passed.

Optional Gemini commands:

```powershell
python project_a\llm_tax.py
python project_a\compile_rules.py --fy 2024-25
```

## Project A: income tax rules vs LLMs

### Objective

Compare a transparent Python implementation with two LLM workflows using the
same supplied tax rules and taxpayer inputs.

### Approaches

1. **Hand-coded rules —** [project_a/tax_rules.py](project_a/tax_rules.py)
   calculates old- and new-regime tax for FY 2024–25 and FY 2025–26. It covers
   slab rates, standard deduction, HRA, 80C, 80CCD(1B), 80D for the taxpayer
   and senior parents, self-occupied home-loan interest, Section 87A rebate,
   and 4% cess.
2. **LLM at query time —** [project_a/llm_tax.py](project_a/llm_tax.py) sends
   the rules and structured taxpayer data to Gemini, requests JSON, and records
   actual response latency. It does not call the hand-coded calculator.
3. **LLM-compiled rules —** [project_a/compile_rules.py](project_a/compile_rules.py)
   asks Gemini for a JSON configuration, validates it, saves it, and executes
   the configuration locally without calling Gemini for each calculation.

The deterministic implementation was tested with a 200-case tax matrix plus
focused edge cases. Repeated local calculations produced identical outputs.
See [RESULTS_A.md](RESULTS_A.md) for the executed coverage and limitations.

## Project B: NYC 311 data quality

### Objective

Evaluate how different detection strategies identify labelled data-quality
corruptions such as missing values, type and date problems, invalid or swapped
coordinates, duplicates, temporal inconsistencies, semantic contradictions,
and privacy-like text.

### Approaches

1. **Rules/schema detector —** explicit checks for required columns, nulls,
   types, ranges, dates, duplicates, and selected NYC-specific consistency
   rules.
2. **Statistical detector —** a lightweight numeric outlier and missing-value
   baseline.
3. **Semantic detector —** a deterministic local text baseline plus an
   optional Gemini semantic detector.

A **hybrid** detector combines the local rule, statistical, and semantic
signals. The experiment reports recall, false-positive rate, processing time,
throughput, and per-corruption-type metrics where measurable.

The specified 2023 NYC 311 dataset was not available locally. Therefore the
available Project B results use a small controlled **synthetic** fixture and
must not be interpreted as real NYC 311 findings. To run the CLI with a local
CSV:

```powershell
python project_b\run_experiment.py C:\path\to\nyc_311_2023.csv
```

See [RESULTS_B.md](RESULTS_B.md) for the actual synthetic measurements and
their limitations.

## Known limitations and pending validation

The following requirements remain incomplete:

- Validation against the actual 2023 NYC 311 dataset.
- At least 30 comparisons with the official Income Tax Department calculator.
- Live Gemini evaluation, including measured accuracy, latency, and
  compiled-rule equivalence.
- Plain-language tax parsing and testing of 50 varied descriptions.
- Surcharge and marginal relief.
- Real-data Project B metrics and Gemini cost per million rows.

These limitations are intentional and documented rather than replaced with
invented results. The prototype currently provides reproducible deterministic
and synthetic experiments; external dataset, official-calculator, and live
LLM validation remain pending.

## Design decision

Rules are preferred for stable, auditable tax logic and schema checks.
Statistics are useful for distribution shifts and numeric outliers. LLMs are
most appropriate for ambiguous semantic review, with latency, cost, and human
review controls. A hybrid pipeline is the most practical data-quality design,
but the recommendation remains provisional until real-data and live-LLM
validation is completed.

See:

- [AUDIT_REPORT.md](AUDIT_REPORT.md) — repository audit and submission status
- [RESULTS_A.md](RESULTS_A.md) — Project A tests and limitations
- [RESULTS_B.md](RESULTS_B.md) — synthetic Project B results
- [DECISION_MATRIX.md](DECISION_MATRIX.md) — approach selection
- [AI_USAGE.md](AI_USAGE.md) — AI assistance disclosure

No commit or push is performed by the project workflow.

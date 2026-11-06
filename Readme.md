# Rules vs LLMs

An experimental comparison of **deterministic rules, statistical methods, and Large Language Models (LLMs)** across two practical problem domains: income-tax calculation and data-quality detection.

This project explores how different approaches perform in terms of accuracy, consistency, execution time, explainability, and practical applicability. It focuses on understanding where traditional rule-based systems work best, where LLMs add value, and how combining both can create more effective solutions.

## Projects Overview

### Project A — Income Tax Calculation

A comparative implementation of three approaches for calculating income tax under India's old and new tax regimes.

- **Rule-Based Approach:** A deterministic Python tax engine implementing predefined tax provisions.
- **LLM at Query Time:** Uses Gemini to interpret tax rules and calculate tax dynamically for individual requests.
- **LLM-Compiled Rules:** Uses Gemini to convert tax provisions into a structured rule configuration, which is subsequently executed locally.

The implementation covers multiple tax provisions, including standard deduction, HRA exemption, Sections 80C, 80CCD(1B), 80D, home-loan interest, Section 87A rebate, and applicable cess.

### Project B — NYC 311 Data Quality

An experimental data-quality framework using NYC 311 service-request data concepts to evaluate different approaches to identifying corrupted or inconsistent records.

The implementation explores:

- **Rule-Based Detection:** Schema validation, missing values, duplicates, date inconsistencies, and predefined data constraints.
- **Statistical Detection:** Identifying anomalies using numerical and distribution-based checks.
- **Semantic Detection:** Examining textual inconsistencies using local detection logic and optional Gemini-based analysis.
- **Hybrid Detection:** Combining multiple detection approaches to identify potential data-quality issues.

Controlled data corruptions are used to evaluate detector behavior and compare their effectiveness.

## Repository Structure

```text
project_a/
    tax_rules.py
    llm_tax.py
    compile_rules.py

project_b/
    data_quality.py
    run_experiment.py

tests/
    test_tax.py
    test_tax_matrix.py
    test_data_quality.py

results/
    project_b_metrics.json

run_all.py
requirements.txt
Readme.md
RESULTS_A.md
RESULTS_B.md
DECISION_MATRIX.md
AUDIT_REPORT.md
AI_USAGE.md
```

## Getting Started

### Prerequisites

- Python 3.10 or later
- Git
- Gemini API key (only for optional Gemini-based functionality)

### Installation

Clone the repository:

```bash
git clone https://github.com/NiharikaDas29/rules-vs-llms-assignment.git
cd rules-vs-llms-assignment
```

Create and activate a virtual environment:

```bash
python -m venv venv
```

On Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

### Gemini API Configuration

To use the optional Gemini-powered components, create a `.env` file in the project root:

```dotenv
GEMINI_API_KEY=your_api_key_here
```

Keep your API key private. The `.env` file is excluded through `.gitignore`.

The deterministic tests and local reproducibility command can run without a Gemini API key.

## Running the Experiments

Execute the complete local validation and controlled data-quality experiment:

```bash
python run_all.py
```

The reported execution in the development environment completed with:

**207 tests passed.**

Python compilation, dependency consistency, and Git whitespace checks were also verified.

### Optional Gemini Experiments

```bash
python project_a/llm_tax.py
python project_a/compile_rules.py --fy 2024-25
```

These commands require a valid Gemini API key and the corresponding API configuration.

## Results and Evaluation

The experiments are documented separately to keep implementation details, measurements, and design decisions transparent.

| Document | Description |
|---|---|
| [RESULTS_A.md](RESULTS_A.md) | Income-tax implementation and test results |
| [RESULTS_B.md](RESULTS_B.md) | Data-quality experiment and synthetic measurements |
| [DECISION_MATRIX.md](DECISION_MATRIX.md) | Comparison of rules, statistics, LLMs, and hybrid approaches |
| [AUDIT_REPORT.md](AUDIT_REPORT.md) | Implementation review and outstanding requirements |
| [AI_USAGE.md](AI_USAGE.md) | Disclosure of AI tools and their usage |

## Current Scope and Limitations

The current implementation provides a working experimental foundation, but some parts of the original evaluation remain incomplete:

- Validation against the actual NYC 311 dataset for calendar year 2023.
- At least 30 comparisons against the official Income Tax Department calculator.
- Live Gemini evaluation for accuracy, latency, and compiled-rule equivalence.
- Plain-language tax input parsing and evaluation of 50 varied descriptions.
- Surcharge and marginal-relief calculations.
- Real-data detection metrics and measured Gemini cost at scale.

Project B's currently reported measurements are based on controlled synthetic data, not actual NYC 311 records. Similarly, the tax implementation has not undergone the required full official-calculator validation.

These limitations are documented in the respective result reports.

## Design Perspective

The experiments explore the trade-offs between three approaches:

- **Rules** provide predictable, explainable, and auditable execution for well-defined logic.
- **Statistical methods** help identify unusual patterns and distribution changes that predefined rules may miss.
- **LLMs** offer flexibility when interpreting ambiguous or unstructured information, but introduce additional considerations around consistency, latency, and cost.
- **Hybrid systems** combine these strengths by applying deterministic checks first and reserving more expensive semantic analysis for cases where it adds value.

The central objective is not to maximize LLM usage, but to identify the most appropriate approach for each component based on its requirements and observed behavior.

---

*This repository is an experimental take-home project intended for technical evaluation and discussion. It is not a production-ready system or a substitute for professional tax advice.*

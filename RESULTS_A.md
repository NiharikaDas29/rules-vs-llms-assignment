# Project A results

## Executed deterministic validation

Command:

```powershell
python run_all.py
```

Actual result: **207 passed** in approximately 0.94 seconds in the supplied
virtual environment. This includes six focused tests and 200 parameterized
tax cases.

The repeated-execution probe called each tested combination ten times. The
outputs were identical for:

- FY 2024-25 and FY 2025-26
- old and new regimes
- standard deduction and 80D self/parent deduction cases

## Coverage

Implemented and locally tested:

- Old/new regime slab calculations
- FY 2024-25 and FY 2025-26 configurations
- Standard deduction
- HRA exemption
- 80C, 80CCD(1B), 80D self, and 80D senior parents
- Self-occupied home-loan interest
- 87A rebate
- 4% cess
- Input validation and unsupported-year errors
- Tax slab matrix cases

Not implemented or not externally verified:

- Surcharge and marginal relief
- Plain-language taxpayer parsing
- Ambiguous/contradictory natural-language handling
- 30 comparisons with the official calculator
- Live Gemini response accuracy, latency, and compiled-rule equivalence

The Gemini modules are import-tested and have structured error handling, but no
live API result is reported because that would be an external, billable call
and no evaluation budget was supplied.

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "project_a"))
from tax_rules import TaxInput, calculate_final_tax


def test_fy_2024_new_regime_rebate():
    income, result = calculate_final_tax(TaxInput(salary=750000), "new", "2024-25")
    assert income == 675000
    assert result["Final tax payable"] == 0


def test_fy_2025_new_slabs_and_rebate():
    income, result = calculate_final_tax(TaxInput(salary=1275000), "new", "2025-26")
    assert income == 1200000
    assert result["87A rebate"] > 0
    assert result["Final tax payable"] == 0


def test_old_regime_hra_and_deductions():
    person = TaxInput(salary=1200000, basic_salary=600000, hra_received=180000,
                      rent_paid=120000, section_80c=200000, home_loan_interest=250000)
    income, result = calculate_final_tax(person, "old")
    assert income == 740000
    assert result["Final tax payable"] > 0


def test_invalid_inputs():
    with pytest.raises(ValueError):
        TaxInput(salary=-1)
    with pytest.raises(ValueError):
        calculate_final_tax(TaxInput(salary=1), "new", "2030-31")

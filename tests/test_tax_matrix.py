import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "project_a"))
from tax_rules import TaxInput, calculate_final_tax


CASES = [
    (salary, age, regime, fy)
    for salary in range(100000, 5100000, 50000)
    for age in (30, 65)
    for regime in ("old", "new")
    for fy in ("2024-25", "2025-26")
][:200]


@pytest.mark.parametrize("salary,age,regime,fy", CASES)
def test_tax_matrix_is_finite_and_non_negative(salary, age, regime, fy):
    income, result = calculate_final_tax(TaxInput(salary=salary, age=age), regime, fy)
    assert income >= 0
    assert result["Final tax payable"] >= 0
    assert result["Health and education cess"] >= 0


from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple

@dataclass
class TaxInput:
    salary: float
    age: int = 30
    basic_salary: float = 0
    hra_received: float = 0
    rent_paid: float = 0
    is_metro: bool = False
    section_80c: float = 0
    section_80ccd_1b: float = 0
    section_80d: float = 0
    section_80d_parents: float = 0
    parents_are_senior: bool = False
    home_loan_interest: float = 0
    self_occupied_home: bool = True

    def __post_init__(self):
        for field_name, value in asdict(self).items():
            if field_name in ("is_metro", "parents_are_senior", "self_occupied_home"):
                continue
            if not isinstance(value, (int, float)) or value < 0:
                raise ValueError(f"{field_name} must be a non-negative number")
        if not isinstance(self.age, int) or self.age < 0:
            raise ValueError("age must be a non-negative integer")


OLD_REGIME_SLABS = [
    (250000, 0.00),
    (500000, 0.05),
    (1000000, 0.20),
    (float("inf"), 0.30)
]

FY_RULES = {
    "2024-25": {
        "new_slabs": [(300000, 0.00), (700000, 0.05), (1000000, 0.10),
                      (1200000, 0.15), (1500000, 0.20), (float("inf"), 0.30)],
        "new_rebate_limit": 700000,
        "new_rebate": 25000,
    },
    "2025-26": {
        "new_slabs": [(400000, 0.00), (800000, 0.05), (1200000, 0.10),
                      (1600000, 0.15), (2000000, 0.20), (2400000, 0.25),
                      (float("inf"), 0.30)],
        "new_rebate_limit": 1200000,
        "new_rebate": 60000,
    },
}

STANDARD_DEDUCTION = {"old": 50000, "new": 75000}


def calculate_tax(taxable_income: float, slabs: List[Tuple[float, float]]) -> float:

    tax = 0
    previous_limit = 0

    for upper_limit, rate in slabs:

        if taxable_income <= previous_limit:
            break

        taxable_amount = min(
            taxable_income, upper_limit
        ) - previous_limit

        tax += taxable_amount * rate
        previous_limit = upper_limit

    return round(tax, 2)



def calculate_old_regime_deductions(person: TaxInput) -> Dict[str, float]:

    # HRA exemption
    hra = 0

    if person.rent_paid > 0 and person.basic_salary > 0:

        salary_percentage = (
            0.50 if person.is_metro else 0.40
        )

        hra = max(0, min(
            person.hra_received,
            person.rent_paid - 0.10 * person.basic_salary,
            salary_percentage * person.basic_salary
        ))

    section_80c = min(person.section_80c, 150000)
    section_80ccd = min(person.section_80ccd_1b, 50000)
    section_80d = min(person.section_80d, 50000 if person.age >= 60 else 25000)
    section_80d_parents = min(
        person.section_80d_parents, 50000 if person.parents_are_senior else 25000
    )
    home_loan = min(person.home_loan_interest, 200000) if person.self_occupied_home else 0

    total = (
        hra + section_80c + section_80ccd
        + section_80d + section_80d_parents + home_loan
    )

    return {
        "HRA exemption": hra,
        "Section 80C": section_80c,
        "Section 80CCD(1B)": section_80ccd,
        "Section 80D": section_80d,
        "Section 80D parents": section_80d_parents,
        "Home loan interest": home_loan,
        "Total deductions": total
    }



def calculate_tax_payable(
    taxable_income: float, tax: float, regime: str, fy: str = "2024-25"
) -> Dict[str, float]:

    rebate = 0

    if regime == "old" and taxable_income <= 500000:
        rebate = min(tax, 12500)

    elif regime == "new":
        rules = FY_RULES[fy]
        if taxable_income <= rules["new_rebate_limit"]:
            rebate = min(tax, rules["new_rebate"])

    tax_after_rebate = max(0, tax - rebate)

    cess = tax_after_rebate * 0.04

    final_tax = tax_after_rebate + cess

    return {
        "Slab tax": round(tax, 2),
        "87A rebate": round(rebate, 2),
        "Tax after rebate": round(tax_after_rebate, 2),
        "Health and education cess": round(cess, 2),
        "Final tax payable": round(final_tax)
    }


def calculate_final_tax(
    person: TaxInput, regime: str, fy: str = "2024-25"
) -> Tuple[float, Dict[str, float]]:

    if regime not in ("old", "new"):
        raise ValueError("Invalid tax regime")
    if fy not in FY_RULES:
        raise ValueError(f"Unsupported financial year: {fy}")

    standard_deduction = STANDARD_DEDUCTION[regime]

    total_deductions = 0

    if regime == "old":
        deductions = calculate_old_regime_deductions(person)
        total_deductions = deductions["Total deductions"]

    taxable_income = max(
        0,
        person.salary - standard_deduction - total_deductions
    )

    if regime == "old":
        first_exemption = 500000 if person.age >= 80 else 300000 if person.age >= 60 else 250000
        if person.age >= 80:
            slabs = [(500000, 0.00), (1000000, 0.20), (float("inf"), 0.30)]
        else:
            slabs = [(first_exemption, 0.00), (500000, 0.05),
                     (1000000, 0.20), (float("inf"), 0.30)]
    else:
        slabs = FY_RULES[fy]["new_slabs"]

    slab_tax = calculate_tax(taxable_income, slabs)

    result = calculate_tax_payable(
        taxable_income, slab_tax, regime, fy
    )

    return taxable_income, result


if __name__ == "__main__":

    person = TaxInput(
        salary=1200000,
        age=30,
        basic_salary=600000,
        hra_received=180000,
        rent_paid=120000,
        is_metro=False,
        section_80c=150000,
        section_80ccd_1b=50000,
        section_80d=25000,
        home_loan_interest=200000
    )

    print("=" * 45)
    print("       INCOME TAX CALCULATOR")
    print("       FY 2024-25")
    print("=" * 45)

    print("\nGROSS SALARY:", f"Rs. {person.salary:,.2f}")

    for regime in ["old", "new"]:

        income, result = calculate_final_tax(person, regime)

        print(f"\n{regime.upper()} REGIME")
        print(f"Taxable Income: Rs. {income:,.2f}")

        for key, value in result.items():
            print(f"{key}: Rs. {value:,.2f}")

    print("\n" + "=" * 45)
    print("          TEST COMPLETED")
    print("=" * 45)

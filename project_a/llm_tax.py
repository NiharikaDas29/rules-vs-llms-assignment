"""Gemini-at-query-time tax calculation.

This module deliberately does not import or call the hand-coded calculator.
The supplied rule text is the only calculation authority for this approach.
"""

import json
import os
import time
from typing import Any, Dict

from dotenv import load_dotenv
from google import genai

from tax_rules import TaxInput

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def _client() -> genai.Client:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY in .env before using Gemini.")
    return genai.Client(api_key=api_key)


def rules_text(fy: str = "2024-25") -> str:
    if fy == "2024-25":
        new = "3L nil, 3-7L 5%, 7-10L 10%, 10-12L 15%, 12-15L 20%, above 15L 30%; rebate up to 7L capped at 25,000."
    elif fy == "2025-26":
        new = "4L nil, 4-8L 5%, 8-12L 10%, 12-16L 15%, 16-20L 20%, 20-24L 25%, above 24L 30%; rebate up to 12L capped at 60,000."
    else:
        raise ValueError(f"Unsupported financial year: {fy}")
    return f"""Financial year {fy}. Old regime slabs are 0-2.5L (3L for age 60+, 5L for age 80+), 5% to 5L, 20% to 10L, then 30%. New regime: {new}
Standard deduction is 50,000 old and 75,000 new. Old deductions: HRA exemption under the three statutory limits, 80C capped at 150,000, 80CCD(1B) capped at 50,000, 80D capped at 25,000, and self-occupied home-loan interest capped at 200,000. Cess is 4%. Apply rebate before cess."""


def calculate_with_llm(person: TaxInput, fy: str = "2024-25") -> Dict[str, Any]:
    prompt = f"""You are an Indian income-tax calculator. Use only these rules:
{rules_text(fy)}

Taxpayer JSON:
{json.dumps(person.__dict__)}

Calculate both regimes independently. Return JSON with keys old and new, each containing
taxable_income, slab_tax, rebate, cess, final_tax, and assumptions. Do not call Python
code or invent missing inputs."""
    start = time.perf_counter()
    response = _client().models.generate_content(
        model=MODEL,
        contents=prompt,
        config={"response_mime_type": "application/json"},
    )
    latency_seconds = time.perf_counter() - start
    try:
        result = json.loads(response.text)
    except (TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Gemini returned non-JSON tax output.") from exc
    result["latency_seconds"] = round(latency_seconds, 4)
    return result


if __name__ == "__main__":
    print(calculate_with_llm(TaxInput(salary=1200000)))

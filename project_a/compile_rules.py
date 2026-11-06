"""Compile tax prose into JSON with Gemini, then execute the saved configuration."""

import json
from pathlib import Path
from typing import Any, Dict

from llm_tax import _client, rules_text, MODEL


def compile_rules_with_llm(fy: str, output_path: str = "project_a/compiled_rules.json") -> Dict[str, Any]:
    prompt = f"""Convert the following Indian tax rules into JSON. Preserve every numeric
threshold and rate. Use keys financial_year, old, new, cess_rate, and standard_deduction.
Each regime must contain slabs as [upper_limit, rate] pairs and rebate_limit/rebate.
Return JSON only.

{rules_text(fy)}"""
    response = _client().models.generate_content(
        model=MODEL,
        contents=prompt,
        config={"response_mime_type": "application/json"},
    )
    try:
        config = json.loads(response.text)
    except (TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Gemini returned an invalid rules configuration.") from exc
    validate_compiled_rules(config, fy)
    Path(output_path).write_text(json.dumps(config, indent=2), encoding="utf-8")
    return config


def validate_compiled_rules(config: Dict[str, Any], fy: str) -> None:
    required = {"financial_year", "old", "new", "cess_rate", "standard_deduction"}
    if set(config) < required or config["financial_year"] != fy:
        raise ValueError("Compiled rules are missing required top-level fields.")
    if config["cess_rate"] != 0.04:
        raise ValueError("Compiled rules must use 4% cess.")
    for regime in ("old", "new"):
        data = config[regime]
        if not data.get("slabs") or not isinstance(data.get("rebate"), (int, float)):
            raise ValueError(f"Compiled {regime} regime is incomplete.")
        previous = -1
        for upper, rate in data["slabs"]:
            if upper <= previous or not 0 <= rate <= 1:
                raise ValueError(f"Invalid {regime} slab sequence.")
            previous = upper


def calculate_from_compiled(person: Dict[str, Any], config: Dict[str, Any], regime: str) -> Dict[str, float]:
    validate_compiled_rules(config, config["financial_year"])
    if regime not in ("old", "new"):
        raise ValueError("Invalid tax regime")
    taxable = max(0, person["salary"] - config["standard_deduction"][regime])
    tax = 0.0
    previous = 0
    for upper, rate in config[regime]["slabs"]:
        amount = max(0, min(taxable, upper) - previous)
        tax += amount * rate
        previous = upper
        if taxable <= upper:
            break
    rebate = min(tax, config[regime]["rebate"]) if taxable <= config[regime]["rebate_limit"] else 0
    after_rebate = max(0, tax - rebate)
    cess = after_rebate * config["cess_rate"]
    return {"taxable_income": taxable, "slab_tax": tax, "rebate": rebate,
            "cess": cess, "final_tax": round(after_rebate + cess)}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compile tax rules with Gemini.")
    parser.add_argument("--fy", default="2024-25", choices=("2024-25", "2025-26"))
    parser.add_argument("--output", default="project_a/compiled_rules.json")
    args = parser.parse_args()
    print(json.dumps(compile_rules_with_llm(args.fy, args.output), indent=2))

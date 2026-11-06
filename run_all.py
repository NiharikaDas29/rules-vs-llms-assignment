"""Run the reproducible local validation suite without requiring an API key."""

import subprocess
import sys
from pathlib import Path

import pandas as pd

from project_b.data_quality import (
    evaluate, hybrid_detect, inject_corruptions, rule_detect, semantic_detect,
    statistical_detect,
)

ROOT = Path(__file__).parent
PYTHON_FILES = [
    *ROOT.joinpath("project_a").glob("*.py"),
    *ROOT.joinpath("project_b").glob("*.py"),
    *ROOT.joinpath("tests").glob("*.py"),
]


def main() -> int:
    compile_result = subprocess.run(
        [sys.executable, "-m", "py_compile", *(str(path) for path in PYTHON_FILES)],
        cwd=ROOT,
    )
    if compile_result.returncode:
        return compile_result.returncode
    test_result = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT)
    if test_result.returncode:
        return test_result.returncode
    fixture = pd.DataFrame({
        "Unique Key": [1, 2, 3, 4],
        "Created Date": ["01/01/2023"] * 4,
        "Closed Date": ["01/02/2023"] * 4,
        "Latitude": [40.7] * 4,
        "Longitude": [-73.9] * 4,
        "Incident Zip": ["10001"] * 4,
        "Status": ["Open"] * 4,
        "Descriptor": ["issue"] * 4,
        "Agency": ["NYPD"] * 4,
        "Complaint Type": ["Noise"] * 4,
        "Resolution Description": ["Closed"] * 4,
    })
    corrupted, labels = inject_corruptions(fixture)
    print(f"Controlled Project B rows: {len(corrupted)}")
    for name, detector in (
        ("rules", rule_detect),
        ("statistics", statistical_detect),
        ("semantic", semantic_detect),
        ("hybrid", hybrid_detect),
    ):
        detection = detector(corrupted)
        print(name, evaluate(detection.flags, labels))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

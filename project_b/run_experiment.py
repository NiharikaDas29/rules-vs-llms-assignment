import argparse
import json
from pathlib import Path

import pandas as pd

from data_quality import (
    evaluate, evaluate_by_type, hybrid_detect, inject_corruptions, rule_detect, semantic_detect,
    statistical_detect,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the NYC 311 data-quality experiment.")
    parser.add_argument("csv", type=Path, help="Local 2023 NYC 311 CSV file")
    args = parser.parse_args()
    frame = pd.read_csv(args.csv, low_memory=False)
    corrupted, labels = inject_corruptions(frame)
    results = {}
    for name, detector in (("rules", rule_detect), ("statistics", statistical_detect),
                           ("semantic", semantic_detect), ("hybrid", hybrid_detect)):
        detection = detector(corrupted)
        metrics = evaluate(detection.flags, labels)
        metrics["by_type"] = evaluate_by_type(detection.flags, labels)
        metrics.update(seconds=detection.seconds, rows=len(corrupted),
                       throughput_rows_per_second=len(corrupted) / max(detection.seconds, 1e-9))
        results[name] = metrics
    output = Path("results")
    output.mkdir(exist_ok=True)
    (output / "project_b_metrics.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()

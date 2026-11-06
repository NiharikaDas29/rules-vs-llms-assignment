import pandas as pd

from project_b.data_quality import (
    evaluate, hybrid_detect, inject_corruptions, rule_detect, semantic_detect,
)


def test_injection_and_rule_detection_have_labels():
    source = pd.DataFrame({
        "Unique Key": [1, 2, 3],
        "Created Date": ["01/01/2023", "01/02/2023", "01/03/2023"],
        "Closed Date": ["01/02/2023", "01/03/2023", "01/04/2023"],
        "Latitude": [40.7, 40.8, 40.9],
        "Longitude": [-73.9, -73.8, -73.7],
    })
    corrupted, labels = inject_corruptions(source)
    metrics = evaluate(rule_detect(corrupted).flags, labels)
    assert len(corrupted) >= len(source)
    assert 0 <= metrics["recall"] <= 1


def test_semantic_detector_flags_contradiction():
    frame = pd.DataFrame({"Status": ["Closed"], "Descriptor": ["unresolved issue"]})
    assert semantic_detect(frame).flags["semantic_contradiction"].iloc[0]


def test_hybrid_detector_returns_flags():
    frame = pd.DataFrame({"Status": ["Closed"], "Descriptor": ["unresolved issue"]})
    result = hybrid_detect(frame)
    assert result.flags["semantic_contradiction"].iloc[0]

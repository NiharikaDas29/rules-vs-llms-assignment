"""Small, reproducible NYC 311 data-quality experiment.

The detector accepts the real 2023 NYC 311 CSV path, but never downloads or
loads the multi-gigabyte dataset implicitly. Synthetic labels are kept separate
from findings in the unmodified input.
"""

from dataclasses import dataclass
import json
import os
from typing import Dict, Tuple
import time

import numpy as np
import pandas as pd


@dataclass
class DetectionResult:
    flags: pd.DataFrame
    seconds: float


def inject_corruptions(frame: pd.DataFrame, seed: int = 7) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    data = frame.copy()
    labels = pd.DataFrame(False, index=data.index, columns=[
        "missing_values", "type_inconsistency", "date_problem", "invalid_coordinates",
        "duplicate", "near_duplicate", "temporal_inconsistency", "geographic_inconsistency",
        "semantic_contradiction", "privacy_issue", "renamed_column", "coordinate_swapped",
        "zip_borough", "complaint_descriptor", "resolution_status"])
    n = len(data)
    if n == 0:
        return data, labels
    sample = rng.choice(data.index, size=max(1, min(n, n // 20)), replace=False)
    if "Agency" in data:
        data.loc[sample, "Agency"] = np.nan
        labels.loc[sample, "missing_values"] = True
    if "Created Date" in data:
        data.loc[sample, "Created Date"] = "not-a-date"
        labels.loc[sample, "date_problem"] = True
    if "Latitude" in data:
        data.loc[sample, "Latitude"] = 999.0
        labels.loc[sample, "invalid_coordinates"] = True
    if "Latitude" in data and "Longitude" in data:
        original_latitude = data.loc[sample, "Latitude"].copy()
        data.loc[sample, "Latitude"] = data.loc[sample, "Longitude"].to_numpy()
        data.loc[sample, "Longitude"] = original_latitude.to_numpy()
        labels.loc[sample, "coordinate_swapped"] = True
    if "Incident Zip" in data:
        data["Incident Zip"] = data["Incident Zip"].astype("object")
        data.loc[sample, "Incident Zip"] = "unknown"
        labels.loc[sample, "type_inconsistency"] = True
        labels.loc[sample, "zip_borough"] = True
    if "Closed Date" in data:
        data.loc[sample, "Closed Date"] = "01/01/2000"
        labels.loc[sample, "temporal_inconsistency"] = True
    if "Descriptor" in data and "Status" in data:
        data.loc[sample, "Descriptor"] = "closed but unresolved"
        data.loc[sample, "Status"] = "Closed"
        labels.loc[sample, "semantic_contradiction"] = True
        if "Resolution Description" in data:
            data.loc[sample, "Resolution Description"] = "Resolved"
            labels.loc[sample, "resolution_status"] = True
    if "Complaint Type" in data and "Descriptor" in data:
        data.loc[sample, "Complaint Type"] = "Noise"
        data.loc[sample, "Descriptor"] = "Water leak"
        labels.loc[sample, "complaint_descriptor"] = True
    if "Descriptor" in data:
        data.loc[sample, "Descriptor"] = data.loc[sample, "Descriptor"].astype(str) + " call 212-555-0100"
        labels.loc[sample, "privacy_issue"] = True
    if "Unique Key" in data:
        duplicate_rows = data.loc[sample].copy()
        labels.loc[sample, "duplicate"] = True
        data = pd.concat([data, duplicate_rows], ignore_index=True)
        labels = pd.concat(
            [labels, labels.loc[sample].assign(duplicate=True).reset_index(drop=True)],
            ignore_index=True,
        )
        data = data.reset_index(drop=True)
    if "Complaint Type" in data and "Descriptor" in data:
        near_duplicate_rows = data.loc[sample].copy()
        near_duplicate_rows["Descriptor"] = near_duplicate_rows["Descriptor"].astype(str) + " minor"
        labels.loc[sample, "near_duplicate"] = True
        data = pd.concat([data, near_duplicate_rows], ignore_index=True)
        near_labels = labels.loc[sample].copy().reset_index(drop=True)
        near_labels["near_duplicate"] = True
        labels = pd.concat([labels, near_labels], ignore_index=True)
    return data, labels


def rule_detect(frame: pd.DataFrame) -> DetectionResult:
    start = time.perf_counter()
    flags = pd.DataFrame(index=frame.index)
    required = ["Unique Key", "Created Date", "Closed Date", "Latitude", "Longitude"]
    missing_required = any(column not in frame.columns for column in required)
    flags["missing_columns"] = missing_required
    flags["renamed_column"] = missing_required
    flags["missing_values"] = frame.isna().any(axis=1)
    if "Created Date" in frame:
        created = pd.to_datetime(frame["Created Date"], errors="coerce")
        flags["date_problem"] = created.isna()
    if "Latitude" in frame and "Longitude" in frame:
        flags["invalid_coordinates"] = (~pd.to_numeric(frame["Latitude"], errors="coerce").between(-90, 90)
                                        | ~pd.to_numeric(frame["Longitude"], errors="coerce").between(-180, 180))
    if "Unique Key" in frame:
        flags["duplicate"] = frame["Unique Key"].duplicated(keep=False)
    if "Incident Zip" in frame:
        flags["type_inconsistency"] = (
            frame["Incident Zip"].notna()
            & ~frame["Incident Zip"].astype(str).str.fullmatch(r"\d{5}", na=False)
        )
    if "Latitude" in frame and "Longitude" in frame:
        flags["coordinate_swapped"] = (
            pd.to_numeric(frame["Latitude"], errors="coerce").abs().between(70, 80)
            & pd.to_numeric(frame["Longitude"], errors="coerce").abs().between(35, 45)
        )
    if "Closed Date" in frame and "Created Date" in frame:
        created = pd.to_datetime(frame["Created Date"], errors="coerce")
        closed = pd.to_datetime(frame["Closed Date"], errors="coerce")
        flags["temporal_inconsistency"] = closed.notna() & created.notna() & (closed < created)
    if {"Latitude", "Longitude"} <= set(frame.columns):
        flags["geographic_inconsistency"] = (
            ~pd.to_numeric(frame["Latitude"], errors="coerce").between(40.4, 41.0)
            | ~pd.to_numeric(frame["Longitude"], errors="coerce").between(-74.3, -73.6)
        )
    if {"Complaint Type", "Descriptor"} <= set(frame.columns):
        flags["near_duplicate"] = frame.duplicated(
            subset=["Complaint Type", "Descriptor"], keep=False
        )
        flags["complaint_descriptor"] = (
            frame["Complaint Type"].astype(str).str.lower().eq("noise")
            & frame["Descriptor"].astype(str).str.contains("water", case=False, na=False)
        )
    if {"Status", "Resolution Description"} <= set(frame.columns):
        flags["resolution_status"] = (
            frame["Status"].astype(str).str.lower().eq("closed")
            & frame["Resolution Description"].astype(str).str.contains(
                "open|unresolved", case=False, na=False
            )
        )
    return DetectionResult(flags, time.perf_counter() - start)


def statistical_detect(frame: pd.DataFrame) -> DetectionResult:
    start = time.perf_counter()
    flags = pd.DataFrame(index=frame.index)
    numeric = frame.select_dtypes(include=np.number)
    if not numeric.empty:
        z = ((numeric - numeric.mean()) / numeric.std(ddof=0).replace(0, np.nan)).abs()
        flags["numeric_outlier"] = z.gt(4).any(axis=1).fillna(False)
    else:
        flags["numeric_outlier"] = False
    flags["missing_value_spike"] = frame.isna().mean(axis=1) > max(0.25, frame.isna().mean(axis=1).quantile(.99))
    return DetectionResult(flags, time.perf_counter() - start)


def semantic_detect(frame: pd.DataFrame) -> DetectionResult:
    start = time.perf_counter()
    flags = pd.DataFrame(index=frame.index)
    flags["semantic_contradiction"] = False
    flags["complaint_descriptor"] = False
    flags["resolution_status"] = False
    if {"Status", "Descriptor"} <= set(frame.columns):
        flags["semantic_contradiction"] = (
            frame["Status"].astype(str).str.lower().eq("closed")
            & frame["Descriptor"].astype(str).str.contains("unresolved|open", case=False, na=False)
        )
        flags["complaint_descriptor"] = (
            frame["Status"].astype(str).str.lower().eq("closed")
            & frame["Descriptor"].astype(str).str.contains("unresolved|open", case=False, na=False)
        )
    if {"Status", "Resolution Description"} <= set(frame.columns):
        flags["resolution_status"] = (
            frame["Status"].astype(str).str.lower().eq("closed")
            & frame["Resolution Description"].astype(str).str.contains(
                "open|unresolved", case=False, na=False
            )
        )
    text = frame.fillna("").astype(str).agg(lambda row: " ".join(row), axis=1)
    flags["privacy_issue"] = False
    flags["privacy_issue"] = text.str.contains(
        r"\b\d{3}[-.\s]\d{2}[-.\s]\d{4}\b|\b\d{16}\b", regex=True, na=False
    )
    return DetectionResult(flags, time.perf_counter() - start)


def hybrid_detect(frame: pd.DataFrame) -> DetectionResult:
    start = time.perf_counter()
    rule_flags = rule_detect(frame).flags
    statistical_flags = statistical_detect(frame).flags
    semantic_flags = semantic_detect(frame).flags
    flags = pd.concat([rule_flags, statistical_flags, semantic_flags], axis=1)
    flags = flags.T.groupby(level=0).any().T
    return DetectionResult(flags, time.perf_counter() - start)


def llm_semantic_detect(frame: pd.DataFrame) -> DetectionResult:
    """Ask Gemini to classify semantic contradictions and privacy indicators."""
    from dotenv import load_dotenv
    from google import genai

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY in .env before using LLM detection.")
    start = time.perf_counter()
    rows = frame.fillna("").astype(str).to_dict(orient="records")
    response = genai.Client(api_key=api_key).models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=(
            "Classify each row. Return JSON array with one object per row containing "
            "semantic_contradiction and privacy_issue booleans. Do not infer missing facts.\n"
            + json.dumps(rows)
        ),
        config={"response_mime_type": "application/json"},
    )
    try:
        values = json.loads(response.text)
        flags = pd.DataFrame(values, index=frame.index).reindex(
            columns=["semantic_contradiction", "privacy_issue"], fill_value=False
        ).fillna(False).astype(bool)
    except (TypeError, json.JSONDecodeError, ValueError) as exc:
        raise RuntimeError("Gemini returned invalid data-quality JSON.") from exc
    return DetectionResult(flags, time.perf_counter() - start)


def evaluate(predicted: pd.DataFrame, labels: pd.DataFrame) -> Dict[str, float]:
    predicted_any = predicted.reindex(columns=labels.columns, fill_value=False).any(axis=1)
    actual_any = labels.any(axis=1)
    tp = int((predicted_any & actual_any).sum())
    fp = int((predicted_any & ~actual_any).sum())
    fn = int((~predicted_any & actual_any).sum())
    return {"recall": tp / (tp + fn) if tp + fn else 0.0,
            "false_positive_rate": fp / max(1, int((~actual_any).sum()))}


def evaluate_by_type(predicted: pd.DataFrame, labels: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    metrics = {}
    for column in labels.columns:
        actual = labels[column].astype(bool)
        detected = predicted.get(column, pd.Series(False, index=labels.index)).astype(bool)
        tp = int((actual & detected).sum())
        fp = int((~actual & detected).sum())
        fn = int((actual & ~detected).sum())
        metrics[column] = {
            "recall": tp / (tp + fn) if tp + fn else 0.0,
            "false_positive_rate": fp / max(1, int((~actual).sum())),
        }
    return metrics

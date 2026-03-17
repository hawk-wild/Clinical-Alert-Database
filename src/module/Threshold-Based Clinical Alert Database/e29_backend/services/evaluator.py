from fastapi import HTTPException

from e29_backend.db import (
    compliance_collection,
    escalation_paths_collection,
    patient_groups_collection,
    thresholds_collection,
)
from e29_backend.models import IngestionInput, OutcomeFeedback
from e29_backend.utils import next_id, now_utc, serialize_doc


def _find_group(age_in_months: int, condition_tag: str) -> dict | None:
    return patient_groups_collection().find_one(
        {
            "age_min_months": {"$lte": age_in_months},
            "age_max_months": {"$gte": age_in_months},
            "condition_tag": condition_tag,
        }
    )


def _resolve_violation(threshold: dict, payload: IngestionInput) -> tuple[bool, str]:
    threshold_kind = (threshold.get("threshold_type") or "Absolute").lower()
    observed_value = payload.observed_value
    min_value = float(threshold["min_value"])
    max_value = float(threshold["max_value"])

    absolute_violation = observed_value < min_value or observed_value > max_value

    if threshold_kind in {"clinical", "absolute"}:
        return absolute_violation, "Absolute threshold check"

    if threshold_kind == "relative":
        if payload.baseline_value is None:
            return absolute_violation, "Relative fallback to absolute"
        relative_change = ((observed_value - payload.baseline_value) / payload.baseline_value) * 100
        relative_violation = abs(relative_change) > 20
        return relative_violation or absolute_violation, "Relative threshold check"

    if threshold_kind == "trend-based":
        if not payload.trend_window:
            return absolute_violation, "Trend-based fallback to absolute"
        moving_avg = sum(payload.trend_window) / len(payload.trend_window)
        trend_violation = abs(observed_value - moving_avg) > max(10, 0.1 * moving_avg)
        return trend_violation or absolute_violation, "Trend-based threshold check"

    if threshold_kind == "combination":
        relative_trigger = False
        trend_trigger = False
        if payload.baseline_value is not None:
            relative_change = ((observed_value - payload.baseline_value) / payload.baseline_value) * 100
            relative_trigger = abs(relative_change) > 15
        if payload.trend_window:
            moving_avg = sum(payload.trend_window) / len(payload.trend_window)
            trend_trigger = abs(observed_value - moving_avg) > max(8, 0.08 * moving_avg)
        return absolute_violation or relative_trigger or trend_trigger, "Combination threshold check"

    return absolute_violation, "Unknown type fallback to absolute"


def evaluate_reading(payload: IngestionInput) -> dict:
    group = _find_group(payload.age_in_months, payload.condition_tag)
    if not group:
        raise HTTPException(status_code=404, detail="No matching Patient-group for age and condition")

    threshold = thresholds_collection().find_one(
        {
            "group_id": group["group_id"],
            "parameter_name": payload.parameter_name,
            "is_active": True,
        }
    )
    if not threshold:
        raise HTTPException(status_code=404, detail="No active Threshold for this patient-group and parameter")

    violated, check_mode = _resolve_violation(threshold, payload)
    violation_status = "Violation" if violated else "Within Limit"
    trigger_message = (
        f"{payload.parameter_name} exceeded safe limit"
        if violated
        else f"{payload.parameter_name} within safe limit"
    )

    compliance_col = compliance_collection()
    compliance_id = next_id("CMP", compliance_col.count_documents({}))
    compliance_doc = {
        "compliance_id": compliance_id,
        "trigger_message": trigger_message,
        "threshold_id": threshold["threshold_id"],
        "observed_value": payload.observed_value,
        "check_timestamp": now_utc(),
        "violation_status": violation_status,
    }
    compliance_col.insert_one(compliance_doc)

    escalation_path = None
    if violated:
        escalation_path = escalation_paths_collection().find_one({"threshold_id": threshold["threshold_id"]})

    return {
        "group": serialize_doc(group),
        "threshold": serialize_doc(threshold),
        "compliance": serialize_doc(compliance_col.find_one({"compliance_id": compliance_id})),
        "escalation_path": serialize_doc(escalation_path),
        "check_mode": check_mode,
    }


def apply_adaptive_threshold(threshold_id: str) -> dict:
    threshold_col = thresholds_collection()
    threshold = threshold_col.find_one({"threshold_id": threshold_id})
    if not threshold:
        raise HTTPException(status_code=404, detail="Threshold not found")

    docs = list(compliance_collection().find({"threshold_id": threshold_id}).sort("check_timestamp", -1).limit(30))
    if len(docs) < 5:
        raise HTTPException(status_code=400, detail="At least 5 compliance points are required for adaptation")

    values = [float(doc["observed_value"]) for doc in docs]
    avg = sum(values) / len(values)
    spread = max(5.0, avg * 0.08)
    new_min = round(avg - spread, 2)
    new_max = round(avg + spread, 2)

    threshold_col.update_one(
        {"threshold_id": threshold_id},
        {"$set": {"min_value": new_min, "max_value": new_max}},
    )
    updated = threshold_col.find_one({"threshold_id": threshold_id})
    return {
        "message": "Adaptive threshold updated",
        "threshold": serialize_doc(updated),
    }


def learn_from_outcome(payload: OutcomeFeedback) -> dict:
    threshold_col = thresholds_collection()
    threshold = threshold_col.find_one({"threshold_id": payload.threshold_id})
    if not threshold:
        raise HTTPException(status_code=404, detail="Threshold not found")

    min_value = float(threshold["min_value"])
    max_value = float(threshold["max_value"])

    if payload.outcome == "false_positive":
        max_value = round(max_value + 2, 2)
        min_value = round(min_value - 2, 2)
    elif payload.outcome == "false_negative":
        max_value = round(max_value - 2, 2)
        min_value = round(min_value + 2, 2)

    threshold_col.update_one(
        {"threshold_id": payload.threshold_id},
        {"$set": {"min_value": min_value, "max_value": max_value}},
    )
    updated = threshold_col.find_one({"threshold_id": payload.threshold_id})

    return {
        "message": "Threshold updated using outcome feedback",
        "applied_outcome": payload.outcome,
        "threshold": serialize_doc(updated),
    }
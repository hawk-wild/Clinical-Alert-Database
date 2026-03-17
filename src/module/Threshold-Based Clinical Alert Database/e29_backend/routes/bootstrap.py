from datetime import datetime, timezone

from fastapi import APIRouter

from e29_backend.db import (
    compliance_collection,
    ensure_indexes,
    escalation_paths_collection,
    patient_groups_collection,
    thresholds_collection,
)


router = APIRouter()


@router.post("/bootstrap")
def bootstrap_data() -> dict:
    ensure_indexes()

    pg_seed = [
        {
            "group_id": "PG001",
            "group_name": "Adult Hypertension",
            "age_min_months": 216,
            "age_max_months": 720,
            "gender": "All",
            "condition_tag": "Hypertension",
        },
        {
            "group_id": "PG002",
            "group_name": "Senior Cardiac Risk",
            "age_min_months": 721,
            "age_max_months": 1080,
            "gender": "All",
            "condition_tag": "CardiacRisk",
        },
    ]

    th_seed = [
        {
            "threshold_id": "TH001",
            "is_active": True,
            "parameter_name": "Systolic_BP",
            "threshold_type": "Clinical",
            "min_value": 90,
            "max_value": 140,
            "created_at": datetime(2026, 3, 17, 10, 0, 0, tzinfo=timezone.utc),
            "group_id": "PG001",
        },
        {
            "threshold_id": "TH002",
            "is_active": True,
            "parameter_name": "Heart_Rate",
            "threshold_type": "Trend-based",
            "min_value": 55,
            "max_value": 110,
            "created_at": datetime(2026, 3, 17, 11, 0, 0, tzinfo=timezone.utc),
            "group_id": "PG002",
        },
    ]

    esc_seed = [
        {
            "escalation_id": "ESC001",
            "primary_role": "Nurse",
            "secondary_role": "Doctor",
            "alert_level": "High",
            "pathway_name": "Blood Pressure Alert",
            "response_time_limit": 10,
            "threshold_id": "TH001",
        },
        {
            "escalation_id": "ESC002",
            "primary_role": "Doctor",
            "secondary_role": "Cardiologist",
            "alert_level": "Critical",
            "pathway_name": "Cardiac Risk Alert",
            "response_time_limit": 5,
            "threshold_id": "TH002",
        },
    ]

    cmp_seed = [
        {
            "compliance_id": "CMP001",
            "trigger_message": "Systolic BP exceeded safe limit",
            "threshold_id": "TH001",
            "observed_value": 155,
            "check_timestamp": datetime(2026, 3, 17, 9, 45, 0, tzinfo=timezone.utc),
            "violation_status": "Violation",
        },
        {
            "compliance_id": "CMP002",
            "trigger_message": "Heart Rate within safe limit",
            "threshold_id": "TH002",
            "observed_value": 88,
            "check_timestamp": datetime(2026, 3, 17, 9, 55, 0, tzinfo=timezone.utc),
            "violation_status": "Within Limit",
        },
    ]

    for doc in pg_seed:
        patient_groups_collection().update_one({"group_id": doc["group_id"]}, {"$set": doc}, upsert=True)
    for doc in th_seed:
        thresholds_collection().update_one({"threshold_id": doc["threshold_id"]}, {"$set": doc}, upsert=True)
    for doc in esc_seed:
        escalation_paths_collection().update_one(
            {"escalation_id": doc["escalation_id"]}, {"$set": doc}, upsert=True
        )
    for doc in cmp_seed:
        compliance_collection().update_one({"compliance_id": doc["compliance_id"]}, {"$set": doc}, upsert=True)

    return {
        "message": "Bootstrap complete",
        "counts": {
            "Patient-group": patient_groups_collection().count_documents({}),
            "Threshold": thresholds_collection().count_documents({}),
            "Escalation-path": escalation_paths_collection().count_documents({}),
            "Compliance": compliance_collection().count_documents({}),
        },
    }
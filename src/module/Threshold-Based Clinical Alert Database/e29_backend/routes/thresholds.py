from fastapi import APIRouter, HTTPException

from e29_backend.db import patient_groups_collection, thresholds_collection
from e29_backend.models import ThresholdCreate
from e29_backend.utils import serialize_doc, serialize_many


router = APIRouter()


@router.get("/thresholds")
def list_thresholds() -> list[dict]:
    docs = list(thresholds_collection().find({}).sort("threshold_id", 1))
    return serialize_many(docs)


@router.get("/thresholds/{threshold_id}")
def get_threshold(threshold_id: str) -> dict:
    doc = thresholds_collection().find_one({"threshold_id": threshold_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Threshold not found")
    return serialize_doc(doc)


@router.post("/thresholds")
def create_threshold(payload: ThresholdCreate) -> dict:
    if thresholds_collection().find_one({"threshold_id": payload.threshold_id}):
        raise HTTPException(status_code=409, detail="threshold_id already exists")
    if not patient_groups_collection().find_one({"group_id": payload.group_id}):
        raise HTTPException(status_code=400, detail="group_id does not exist in Patient-group")
    thresholds_collection().insert_one(payload.model_dump())
    created = thresholds_collection().find_one({"threshold_id": payload.threshold_id})
    if not created:
        raise HTTPException(status_code=500, detail="Threshold creation verification failed")
    return serialize_doc(created)


@router.put("/thresholds/{threshold_id}")
def update_threshold(threshold_id: str, payload: ThresholdCreate) -> dict:
    existing = thresholds_collection().find_one({"threshold_id": threshold_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Threshold not found")
    if not patient_groups_collection().find_one({"group_id": payload.group_id}):
        raise HTTPException(status_code=400, detail="group_id does not exist in Patient-group")
    thresholds_collection().update_one({"threshold_id": threshold_id}, {"$set": payload.model_dump()})
    updated = thresholds_collection().find_one({"threshold_id": payload.threshold_id})
    if not updated:
        raise HTTPException(status_code=500, detail="Threshold update verification failed")
    return serialize_doc(updated)


@router.delete("/thresholds/{threshold_id}")
def delete_threshold(threshold_id: str) -> dict:
    result = thresholds_collection().delete_one({"threshold_id": threshold_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Threshold not found")
    return {"deleted": threshold_id}
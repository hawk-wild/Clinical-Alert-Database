from fastapi import APIRouter, HTTPException

from e29_backend.db import escalation_paths_collection, thresholds_collection
from e29_backend.models import EscalationPathCreate
from e29_backend.utils import serialize_doc, serialize_many


router = APIRouter()


@router.get("/escalation-paths")
def list_escalation_paths() -> list[dict]:
    docs = list(escalation_paths_collection().find({}).sort("escalation_id", 1))
    return serialize_many(docs)


@router.get("/escalation-paths/{escalation_id}")
def get_escalation_path(escalation_id: str) -> dict:
    doc = escalation_paths_collection().find_one({"escalation_id": escalation_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Escalation-path not found")
    return serialize_doc(doc)


@router.post("/escalation-paths")
def create_escalation_path(payload: EscalationPathCreate) -> dict:
    if escalation_paths_collection().find_one({"escalation_id": payload.escalation_id}):
        raise HTTPException(status_code=409, detail="escalation_id already exists")
    if not thresholds_collection().find_one({"threshold_id": payload.threshold_id}):
        raise HTTPException(status_code=400, detail="threshold_id does not exist in Threshold")
    escalation_paths_collection().insert_one(payload.model_dump())
    created = escalation_paths_collection().find_one({"escalation_id": payload.escalation_id})
    if not created:
        raise HTTPException(status_code=500, detail="Escalation-path creation verification failed")
    return serialize_doc(created)


@router.put("/escalation-paths/{escalation_id}")
def update_escalation_path(escalation_id: str, payload: EscalationPathCreate) -> dict:
    existing = escalation_paths_collection().find_one({"escalation_id": escalation_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Escalation-path not found")
    if not thresholds_collection().find_one({"threshold_id": payload.threshold_id}):
        raise HTTPException(status_code=400, detail="threshold_id does not exist in Threshold")
    escalation_paths_collection().update_one({"escalation_id": escalation_id}, {"$set": payload.model_dump()})
    updated = escalation_paths_collection().find_one({"escalation_id": payload.escalation_id})
    if not updated:
        raise HTTPException(status_code=500, detail="Escalation-path update verification failed")
    return serialize_doc(updated)


@router.delete("/escalation-paths/{escalation_id}")
def delete_escalation_path(escalation_id: str) -> dict:
    result = escalation_paths_collection().delete_one({"escalation_id": escalation_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Escalation-path not found")
    return {"deleted": escalation_id}
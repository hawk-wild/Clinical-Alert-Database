from fastapi import APIRouter, HTTPException

from e29_backend.db import patient_groups_collection
from e29_backend.models import PatientGroupCreate
from e29_backend.utils import serialize_doc, serialize_many


router = APIRouter()


@router.get("/patient-groups")
def list_patient_groups() -> list[dict]:
    docs = list(patient_groups_collection().find({}).sort("group_id", 1))
    return serialize_many(docs)


@router.get("/patient-groups/{group_id}")
def get_patient_group(group_id: str) -> dict:
    doc = patient_groups_collection().find_one({"group_id": group_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Patient-group not found")
    return serialize_doc(doc)


@router.post("/patient-groups")
def create_patient_group(payload: PatientGroupCreate) -> dict:
    if patient_groups_collection().find_one({"group_id": payload.group_id}):
        raise HTTPException(status_code=409, detail="group_id already exists")
    patient_groups_collection().insert_one(payload.model_dump())
    return serialize_doc(patient_groups_collection().find_one({"group_id": payload.group_id}))


@router.put("/patient-groups/{group_id}")
def update_patient_group(group_id: str, payload: PatientGroupCreate) -> dict:
    existing = patient_groups_collection().find_one({"group_id": group_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Patient-group not found")
    patient_groups_collection().update_one({"group_id": group_id}, {"$set": payload.model_dump()})
    return serialize_doc(patient_groups_collection().find_one({"group_id": payload.group_id}))


@router.delete("/patient-groups/{group_id}")
def delete_patient_group(group_id: str) -> dict:
    result = patient_groups_collection().delete_one({"group_id": group_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Patient-group not found")
    return {"deleted": group_id}
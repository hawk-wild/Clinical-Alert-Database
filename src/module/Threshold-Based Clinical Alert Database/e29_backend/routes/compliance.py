from fastapi import APIRouter, HTTPException

from e29_backend.db import compliance_collection, thresholds_collection
from e29_backend.models import ComplianceCreate
from e29_backend.services.reports import compliance_summary
from e29_backend.utils import serialize_doc, serialize_many


router = APIRouter()


@router.get("/compliance")
def list_compliance() -> list[dict]:
    docs = list(compliance_collection().find({}).sort("check_timestamp", -1))
    return serialize_many(docs)


@router.get("/compliance/{compliance_id}")
def get_compliance(compliance_id: str) -> dict:
    doc = compliance_collection().find_one({"compliance_id": compliance_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Compliance not found")
    return serialize_doc(doc)


@router.post("/compliance")
def create_compliance(payload: ComplianceCreate) -> dict:
    if compliance_collection().find_one({"compliance_id": payload.compliance_id}):
        raise HTTPException(status_code=409, detail="compliance_id already exists")
    if not thresholds_collection().find_one({"threshold_id": payload.threshold_id}):
        raise HTTPException(status_code=400, detail="threshold_id does not exist in Threshold")
    compliance_collection().insert_one(payload.model_dump())
    created = compliance_collection().find_one({"compliance_id": payload.compliance_id})
    if not created:
        raise HTTPException(status_code=500, detail="Compliance creation verification failed")
    return serialize_doc(created)


@router.get("/reports/compliance-summary")
def get_compliance_summary() -> dict:
    return compliance_summary()
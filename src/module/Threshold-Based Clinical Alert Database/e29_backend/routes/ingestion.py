from fastapi import APIRouter

from e29_backend.models import IngestionInput, OutcomeFeedback
from e29_backend.services.evaluator import (
    apply_adaptive_threshold,
    evaluate_reading,
    learn_from_outcome,
)


router = APIRouter()


@router.post("/ingestion/evaluate")
def evaluate_threshold(payload: IngestionInput) -> dict:
    return evaluate_reading(payload)


@router.post("/ingestion/adaptive/{threshold_id}")
def adaptive_threshold(threshold_id: str) -> dict:
    return apply_adaptive_threshold(threshold_id)


@router.post("/ingestion/outcome-feedback")
def outcome_feedback(payload: OutcomeFeedback) -> dict:
    return learn_from_outcome(payload)
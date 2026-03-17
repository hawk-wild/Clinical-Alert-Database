from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from e29_backend.routes import (
    bootstrap,
    compliance,
    escalation_paths,
    ingestion,
    patient_groups,
    thresholds,
)


app = FastAPI(
    title="E-29 Threshold-Based Clinical Alert Database",
    version="1.0.0",
    description="Category E / Module 29 backend prototype",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patient_groups.router, prefix="/api/e29", tags=["patient-groups"])
app.include_router(thresholds.router, prefix="/api/e29", tags=["thresholds"])
app.include_router(escalation_paths.router, prefix="/api/e29", tags=["escalation-paths"])
app.include_router(compliance.router, prefix="/api/e29", tags=["compliance"])
app.include_router(ingestion.router, prefix="/api/e29", tags=["ingestion"])
app.include_router(bootstrap.router, prefix="/api/e29", tags=["bootstrap"])


@app.get("/")
def health() -> dict:
    return {
        "module": "E-29",
        "category": "E",
        "name": "Threshold-Based Clinical Alert Database",
        "status": "ok",
    }
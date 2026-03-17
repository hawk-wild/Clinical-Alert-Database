from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PatientGroupBase(BaseModel):
    group_id: str
    group_name: str
    age_min_months: int = Field(ge=0)
    age_max_months: int = Field(ge=0)
    gender: str
    condition_tag: str


class PatientGroupCreate(PatientGroupBase):
    pass


class PatientGroup(PatientGroupBase):
    id: str = Field(alias="_id")
    model_config = ConfigDict(populate_by_name=True)


class ThresholdBase(BaseModel):
    threshold_id: str
    is_active: bool = True
    parameter_name: str
    threshold_type: str
    min_value: float
    max_value: float
    created_at: datetime
    group_id: str


class ThresholdCreate(ThresholdBase):
    pass


class Threshold(ThresholdBase):
    id: str = Field(alias="_id")
    model_config = ConfigDict(populate_by_name=True)


class EscalationPathBase(BaseModel):
    escalation_id: str
    primary_role: str
    secondary_role: str
    alert_level: str
    pathway_name: str
    response_time_limit: int = Field(ge=0)
    threshold_id: str


class EscalationPathCreate(EscalationPathBase):
    pass


class EscalationPath(EscalationPathBase):
    id: str = Field(alias="_id")
    model_config = ConfigDict(populate_by_name=True)


class ComplianceBase(BaseModel):
    compliance_id: str
    trigger_message: str
    threshold_id: str
    observed_value: float
    check_timestamp: datetime
    violation_status: Literal["Violation", "Within Limit"]


class ComplianceCreate(ComplianceBase):
    pass


class Compliance(ComplianceBase):
    id: str = Field(alias="_id")
    model_config = ConfigDict(populate_by_name=True)


class IngestionInput(BaseModel):
    parameter_name: str
    observed_value: float
    age_in_months: int = Field(ge=0)
    condition_tag: str
    baseline_value: float | None = None
    previous_value: float | None = None
    trend_window: list[float] = Field(default_factory=list)


class OutcomeFeedback(BaseModel):
    threshold_id: str
    observed_value: float
    outcome: Literal["true_positive", "false_positive", "true_negative", "false_negative"]

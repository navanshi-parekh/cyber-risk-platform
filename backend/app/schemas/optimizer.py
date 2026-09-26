from typing import List, Dict, Any
from pydantic import BaseModel, Field


class ControlItemSchema(BaseModel):
    control_id: str = Field(..., example="CTRL-EDR-01")
    name: str = Field(..., example="Deploy EDR Agents on Servers")
    category: str = Field(..., example="Endpoint")
    cost: float = Field(..., description="Implementation cost in INR", example=800000.0)
    risk_reduction_delta: float = Field(..., description="Expected reduction in EAL (INR)", example=1200000.0)
    framework_mapping: List[str] = Field(default=[], example=["RBI Sec 3.2", "SEBI CSCRF 4.1"])
    mandatory: bool = Field(default=False, example=False)


class OptimizationRequest(BaseModel):
    budget_limit: float = Field(..., description="Total available budget in INR", example=1000000.0)
    baseline_eal: float = Field(..., description="Current baseline enterprise EAL in INR", example=2900000.0)
    candidate_controls: List[ControlItemSchema]


class SuggestControlsRequest(BaseModel):
    total_findings: int = Field(..., ge=0)
    critical_count: int = Field(..., ge=0)
    kev_count: int = Field(..., ge=0)
    mean_fair_vuln_prob: float = Field(..., ge=0.0, le=1.0)
    baseline_eal: float = Field(..., ge=0.0)


class OptimizationResponse(BaseModel):
    budget_constraint: float
    total_spend: float
    budget_utilized_percentage: float
    baseline_eal: float
    residual_eal: float
    total_risk_reduced: float
    portfolio_rosi: float
    selected_controls: List[Dict[str, Any]]
    deferred_controls: List[Dict[str, Any]]
    solver_status: str
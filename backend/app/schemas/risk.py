from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class LossRangeSchema(BaseModel):
    low: float = Field(..., description="10th percentile loss estimate in INR", example=500000.0)
    mode: float = Field(..., description="Most likely loss estimate in INR", example=1500000.0)
    high: float = Field(..., description="90th percentile loss estimate in INR", example=4000000.0)


class ScenarioRequest(BaseModel):
    scenario_id: str = Field(..., example="SCEN-RANSOMWARE-01")
    name: str = Field(..., example="Ransomware on Core Banking DB")
    tef_low: float = Field(..., description="Threat Event Frequency low (events/yr)", example=0.5)
    tef_high: float = Field(..., description="Threat Event Frequency high (events/yr)", example=3.0)
    vuln_prob: float = Field(..., description="Vulnerability probability (0.0 to 1.0)", example=0.65)
    primary_loss: LossRangeSchema
    secondary_loss_prob: float = Field(default=0.40, example=0.40)
    secondary_loss: LossRangeSchema


class SimulationResponse(BaseModel):
    scenario_id: str
    scenario_name: str
    iterations: int
    mean_eal: float
    median_loss: float
    std_dev: float
    min_loss: float
    max_loss: float
    var_90: float
    var_95: float
    var_99: float
    loss_exceedance_curve: List[Dict[str, float]]
    histogram_bins: List[Dict[str, Any]]
"""
Open FAIR Risk Quantification REST Endpoint with Historical Run Persistence.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.app.core.database import get_db
from backend.app.models.simulation_run import SimulationRun
from backend.app.schemas.risk import ScenarioRequest, SimulationResponse
from backend.app.services.fair_engine.monte_carlo import (
    FairMonteCarloEngine,
    ScenarioInput,
    LossParameters,
)

router = APIRouter()
monte_carlo_engine = FairMonteCarloEngine(iterations=10000)


class IngestedScanBridgePayload(BaseModel):
    scanner_source: str
    total_findings: int
    mean_fair_vuln_prob: float
    critical_count: int
    kev_count: int
    top_vulnerability: str
    target_asset_name: str = "Enterprise Core Production Cluster"


class HistoricalRunItem(BaseModel):
    id: str
    scenario_id: str
    scenario_name: str
    timestamp: str
    mean_eal: float
    var_95: float
    residual_eal: float
    allocated_budget: float
    total_risk_reduced: float
    portfolio_rosi: float
    source: str


class HistoricalTrendResponse(BaseModel):
    total_runs: int
    runs: List[HistoricalRunItem]


@router.get("/history", response_model=HistoricalTrendResponse, summary="Get Historical Risk Trajectory Runs")
async def get_simulation_run_history(
    limit: int = 12,
    db: AsyncSession = Depends(get_db),
):
    """Returns past simulation executions to calculate month-over-month risk trends."""
    result = await db.execute(
        select(SimulationRun).order_by(SimulationRun.timestamp.asc()).limit(limit)
    )
    records = result.scalars().all()
    
    items = [
        HistoricalRunItem(
            id=r.id,
            scenario_id=r.scenario_id,
            scenario_name=r.scenario_name,
            timestamp=r.timestamp.strftime("%b %Y"),
            mean_eal=r.mean_eal,
            var_95=r.var_95,
            residual_eal=r.residual_eal,
            allocated_budget=r.allocated_budget,
            total_risk_reduced=r.total_risk_reduced,
            portfolio_rosi=r.portfolio_rosi,
            source=r.source or "manual_run",
        )
        for r in records
    ]
    
    return HistoricalTrendResponse(total_runs=len(items), runs=items)


@router.post("/simulate", response_model=SimulationResponse)
async def run_fair_simulation(payload: ScenarioRequest, db: AsyncSession = Depends(get_db)):
    try:
        scenario = ScenarioInput(
            scenario_id=payload.scenario_id,
            name=payload.name,
            tef_low=payload.tef_low,
            tef_high=payload.tef_high,
            vuln_prob=payload.vuln_prob,
            primary_loss=LossParameters(
                low=payload.primary_loss.low,
                mode=payload.primary_loss.mode,
                high=payload.primary_loss.high,
            ),
            secondary_loss_prob=payload.secondary_loss_prob,
            secondary_loss=LossParameters(
                low=payload.secondary_loss.low,
                mode=payload.secondary_loss.mode,
                high=payload.secondary_loss.high,
            ),
        )
        res = monte_carlo_engine.run_scenario(scenario)

        # Persist Run to Database
        db_run = SimulationRun(
            scenario_id=res.scenario_id,
            scenario_name=res.scenario_name,
            iterations=res.iterations,
            mean_eal=res.mean_eal,
            var_90=res.var_90,
            var_95=res.var_95,
            var_99=res.var_99,
            source="manual_run",
        )
        db.add(db_run)
        await db.commit()

        return SimulationResponse(
            scenario_id=res.scenario_id,
            scenario_name=res.scenario_name,
            iterations=res.iterations,
            mean_eal=res.mean_eal,
            median_loss=res.median_loss,
            std_dev=res.std_dev,
            min_loss=res.min_loss,
            max_loss=res.max_loss,
            var_90=res.var_90,
            var_95=res.var_95,
            var_99=res.var_99,
            loss_exceedance_curve=res.loss_exceedance_curve,
            histogram_bins=res.histogram_bins,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/simulate-from-scan", response_model=SimulationResponse)
async def simulate_risk_from_ingested_scan(payload: IngestedScanBridgePayload, db: AsyncSession = Depends(get_db)):
    try:
        base_tef_low = 0.5 + (payload.kev_count * 0.75)
        base_tef_high = 2.0 + (payload.critical_count * 0.8) + (payload.kev_count * 1.5)
        vuln_prob = max(0.05, min(0.99, payload.mean_fair_vuln_prob))

        loss_multiplier = 1.0 + (payload.critical_count * 0.35) + (payload.kev_count * 0.7)
        primary_low = round(500000.0 * loss_multiplier, 2)
        primary_mode = round(1500000.0 * loss_multiplier, 2)
        primary_high = round(4000000.0 * loss_multiplier, 2)

        sec_low = round(1000000.0 * loss_multiplier, 2)
        sec_mode = round(3000000.0 * loss_multiplier, 2)
        sec_high = round(8000000.0 * loss_multiplier, 2)

        scenario = ScenarioInput(
            scenario_id=f"SCEN-SCAN-{payload.scanner_source.upper().replace(' ', '-')}",
            name=f"{payload.target_asset_name} ({payload.top_vulnerability})",
            tef_low=round(base_tef_low, 2),
            tef_high=round(base_tef_high, 2),
            vuln_prob=round(vuln_prob, 4),
            primary_loss=LossParameters(low=primary_low, mode=primary_mode, high=primary_high),
            secondary_loss_prob=min(0.85, 0.30 + (payload.kev_count * 0.2)),
            secondary_loss=LossParameters(low=sec_low, mode=sec_mode, high=sec_high),
        )
        res = monte_carlo_engine.run_scenario(scenario)

        # Persist Ingested Scan Run
        db_run = SimulationRun(
            scenario_id=res.scenario_id,
            scenario_name=res.scenario_name,
            iterations=res.iterations,
            mean_eal=res.mean_eal,
            var_90=res.var_90,
            var_95=res.var_95,
            var_99=res.var_99,
            source="scan_ingestion",
        )
        db.add(db_run)
        await db.commit()

        return SimulationResponse(
            scenario_id=res.scenario_id,
            scenario_name=res.scenario_name,
            iterations=res.iterations,
            mean_eal=res.mean_eal,
            median_loss=res.median_loss,
            std_dev=res.std_dev,
            min_loss=res.min_loss,
            max_loss=res.max_loss,
            var_90=res.var_90,
            var_95=res.var_95,
            var_99=res.var_99,
            loss_exceedance_curve=res.loss_exceedance_curve,
            histogram_bins=res.histogram_bins,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to bridge scan to FAIR: {str(e)}")
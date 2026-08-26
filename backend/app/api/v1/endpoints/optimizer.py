from fastapi import APIRouter, HTTPException
from backend.app.schemas.optimizer import OptimizationRequest, OptimizationResponse
from backend.app.services.optimizer.milp_solver import (
    SecurityInvestmentOptimizer,
    CandidateControl,
)

router = APIRouter()
optimizer = SecurityInvestmentOptimizer()


@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_budget_allocation(payload: OptimizationRequest):
    """
    Runs the 0-1 Knapsack optimizer against a list of candidate controls and budget constraint.
    Returns the optimal control package, residual EAL, and portfolio ROSI percentage.
    """
    try:
        candidate_controls = [
            CandidateControl(
                control_id=c.control_id,
                name=c.name,
                category=c.category,
                cost=c.cost,
                risk_reduction_delta=c.risk_reduction_delta,
                framework_mapping=c.framework_mapping,
                mandatory=c.mandatory,
            )
            for c in payload.candidate_controls
        ]

        out = optimizer.optimize_allocation(
            candidate_controls=candidate_controls,
            budget_limit=payload.budget_limit,
            baseline_eal=payload.baseline_eal,
        )

        return OptimizationResponse(
            budget_constraint=out.budget_constraint,
            total_spend=out.total_spend,
            budget_utilized_percentage=out.budget_utilized_percentage,
            baseline_eal=out.baseline_eal,
            residual_eal=out.residual_eal,
            total_risk_reduced=out.total_risk_reduced,
            portfolio_rosi=out.portfolio_rosi,
            selected_controls=out.selected_controls,
            deferred_controls=out.deferred_controls,
            solver_status=out.solver_status,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
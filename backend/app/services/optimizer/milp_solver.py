"""
0-1 Knapsack Security Control Optimizer.
Maximizes total enterprise risk reduction subject to a strict financial budget constraint.
Implements exact branch-and-bound optimization without external solver dependencies.
"""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class CandidateControl:
    """Security control candidate available for allocation."""
    control_id: str
    name: str
    category: str              # e.g., "IAM", "Endpoint", "Network", "Cloud"
    cost: float                # Capital + Implementation cost in ₹
    risk_reduction_delta: float # Reduction in Expected Annual Loss (ΔEAL) in ₹
    framework_mapping: List[str] # e.g., ["RBI Sec 3.2", "SEBI CSCRF 4.1"]
    mandatory: bool = False    # Force inclusion for non-negotiable statutory compliance


@dataclass
class OptimizationOutput:
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


class SecurityInvestmentOptimizer:
    """Exact 0-1 Knapsack Optimizer with mandatory compliance constraint support."""

    def optimize_allocation(
        self,
        candidate_controls: List[CandidateControl],
        budget_limit: float,
        baseline_eal: float,
    ) -> OptimizationOutput:
        if budget_limit < 0:
            raise ValueError("Budget limit cannot be negative.")

        # 1. Handle Mandatory Controls first
        mandatory_controls = [c for c in candidate_controls if c.mandatory]
        optional_controls = [c for c in candidate_controls if not c.mandatory]

        mandatory_spend = sum(c.cost for c in mandatory_controls)
        mandatory_reduction = sum(c.risk_reduction_delta for c in mandatory_controls)

        remaining_budget = budget_limit - mandatory_spend
        if remaining_budget < 0:
            return OptimizationOutput(
                budget_constraint=round(budget_limit, 2),
                total_spend=round(mandatory_spend, 2),
                budget_utilized_percentage=round((mandatory_spend / budget_limit) * 100.0, 2),
                baseline_eal=round(baseline_eal, 2),
                residual_eal=round(baseline_eal, 2),
                total_risk_reduced=0.0,
                portfolio_rosi=0.0,
                selected_controls=[],
                deferred_controls=[self._to_dict(c, False) for c in candidate_controls],
                solver_status="Infeasible: Mandatory controls exceed budget limit",
            )

        # 2. Branch & Bound / Dynamic Knapsack on optional controls
        best_selection_mask: List[bool] = [False] * len(optional_controls)
        best_reduction: float = 0.0

        def solve_knapsack(idx: int, current_cost: float, current_reduction: float, current_mask: List[bool]):
            nonlocal best_reduction, best_selection_mask

            if current_cost > remaining_budget:
                return

            if current_reduction > best_reduction:
                best_reduction = current_reduction
                best_selection_mask = list(current_mask)

            if idx >= len(optional_controls):
                return

            # Branch 1: Pick control at idx
            current_mask[idx] = True
            solve_knapsack(
                idx + 1,
                current_cost + optional_controls[idx].cost,
                current_reduction + optional_controls[idx].risk_reduction_delta,
                current_mask,
            )

            # Branch 2: Skip control at idx
            current_mask[idx] = False
            solve_knapsack(idx + 1, current_cost, current_reduction, current_mask)

        solve_knapsack(0, 0.0, 0.0, [False] * len(optional_controls))

        # 3. Format Output
        selected: List[Dict[str, Any]] = [self._to_dict(c, True) for c in mandatory_controls]
        deferred: List[Dict[str, Any]] = []

        total_spend = mandatory_spend
        total_risk_reduced = mandatory_reduction

        for i, ctrl in enumerate(optional_controls):
            if best_selection_mask[i]:
                selected.append(self._to_dict(ctrl, True))
                total_spend += ctrl.cost
                total_risk_reduced += ctrl.risk_reduction_delta
            else:
                deferred.append(self._to_dict(ctrl, False))

        residual_eal = max(0.0, baseline_eal - total_risk_reduced)
        net_benefit = total_risk_reduced - total_spend
        portfolio_rosi = (net_benefit / total_spend * 100.0) if total_spend > 0 else 0.0
        budget_pct = (total_spend / budget_limit * 100.0) if budget_limit > 0 else 0.0

        return OptimizationOutput(
            budget_constraint=round(budget_limit, 2),
            total_spend=round(total_spend, 2),
            budget_utilized_percentage=round(budget_pct, 2),
            baseline_eal=round(baseline_eal, 2),
            residual_eal=round(residual_eal, 2),
            total_risk_reduced=round(total_risk_reduced, 2),
            portfolio_rosi=round(portfolio_rosi, 2),
            selected_controls=selected,
            deferred_controls=deferred,
            solver_status="Optimal",
        )

    @staticmethod
    def _to_dict(ctrl: CandidateControl, selected: bool) -> Dict[str, Any]:
        return {
            "control_id": ctrl.control_id,
            "name": ctrl.name,
            "category": ctrl.category,
            "cost": ctrl.cost,
            "risk_reduction_delta": ctrl.risk_reduction_delta,
            "framework_mapping": ctrl.framework_mapping,
            "mandatory": ctrl.mandatory,
            "selected": selected,
        }
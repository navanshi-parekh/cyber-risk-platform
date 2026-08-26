"""
Return on Security Investment (ROSI) calculation engine.
Formula: ROSI (%) = ((Risk Mitigation Delta - Cost of Control) / Cost of Control) * 100
"""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class ROSIResult:
    control_id: str
    control_name: str
    cost: float
    risk_reduction_amount: float
    net_benefit: float
    rosi_percentage: float


class ROSICalculator:
    @staticmethod
    def calculate_single(
        control_id: str,
        control_name: str,
        cost: float,
        pre_mitigation_eal: float,
        post_mitigation_eal: float,
    ) -> ROSIResult:
        """Calculates single control Return on Security Investment."""
        if cost <= 0:
            raise ValueError("Control cost must be greater than zero.")

        risk_reduction = max(0.0, pre_mitigation_eal - post_mitigation_eal)
        net_benefit = risk_reduction - cost
        rosi_percentage = (net_benefit / cost) * 100.0

        return ROSIResult(
            control_id=control_id,
            control_name=control_name,
            cost=round(cost, 2),
            risk_reduction_amount=round(risk_reduction, 2),
            net_benefit=round(net_benefit, 2),
            rosi_percentage=round(rosi_percentage, 2),
        )

    @staticmethod
    def calculate_portfolio(
        total_cost: float,
        baseline_portfolio_eal: float,
        optimized_residual_eal: float,
    ) -> Dict[str, Any]:
        """Calculates aggregated portfolio-level ROSI metrics."""
        total_risk_reduced = max(0.0, baseline_portfolio_eal - optimized_residual_eal)
        net_savings = total_risk_reduced - total_cost
        portfolio_rosi = (net_savings / total_cost * 100.0) if total_cost > 0 else 0.0

        return {
            "total_investment": round(total_cost, 2),
            "total_risk_mitigated": round(total_risk_reduced, 2),
            "net_financial_benefit": round(net_savings, 2),
            "portfolio_rosi_percentage": round(portfolio_rosi, 2),
        }
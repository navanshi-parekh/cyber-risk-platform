"""
Natural Language CISO Executive Query & Decision-Support Endpoint.
Provides conversational AI analysis for executive leadership, translating technical
vulnerabilities, FAIR quantitative exposure, Knapsack allocations, and statutory
compliance (RBI / SEBI CSCRF) into board-level strategic answers.

Grounded in live data: the latest persisted Monte Carlo run, the latest ingested
scan, and the current infrastructure posture -- not a static demo snapshot.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import httpx

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.models.simulation_run import SimulationRun
from backend.app.models.ingested_scan import IngestedScan
from backend.app.api.v1.endpoints.compliance import _build_telemetry
from backend.app.services.compliance.framework_mapper import StatutoryComplianceEngine
from backend.app.services.optimizer.milp_solver import SecurityInvestmentOptimizer, CandidateControl
from backend.app.services.optimizer.control_recommender import derive_controls_from_scan

logger = logging.getLogger(__name__)
router = APIRouter()

OLLAMA_API_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "mistral"

_FALLBACK_CONTROLS = [
    CandidateControl("CTRL-01", "Deploy EDR on Core DB Cluster", "Endpoint", 800000, 1200000, ["RBI Sec 3.2", "NIST CSF DE.CM"], False),
    CandidateControl("CTRL-02", "Enforce Multi-Factor Authentication (MFA)", "IAM", 200000, 700000, ["SEBI CSCRF 4.1", "ISO 27001 A.9"], True),
    CandidateControl("CTRL-03", "Deploy Web Application Firewall (WAF)", "Network", 500000, 600000, ["SEBI CSCRF 7.3"], False),
    CandidateControl("CTRL-04", "Automated Patch Automation Engine", "Vulnerability", 400000, 550000, ["RBI Sec 5.1"], False),
    CandidateControl("CTRL-05", "Employee Anti-Phishing Training", "Human", 150000, 300000, ["NIST CSF PR.AT"], False),
]


# ---------------------------------------------------------------------------
# Pydantic Request / Response Models
# ---------------------------------------------------------------------------

class AgentQueryRequest(BaseModel):
    query: str = Field(
        ...,
        description="Plain-text executive question (e.g., 'What is our biggest financial risk today?')",
        example="What is our highest financial risk today and what should we prioritize?",
    )
    budget_limit: Optional[float] = Field(
        default=1000000.0,
        description="Optional budget constraint for investment advice in INR",
    )


class StrategicRecommendation(BaseModel):
    control_id: str
    control_name: str
    investment_cost_inr: float
    expected_risk_mitigation_inr: float
    statutory_alignment: List[str]


class AgentQueryResponse(BaseModel):
    query: str
    executive_summary: str
    quantified_exposure: Dict[str, Any]
    regulatory_impact: Dict[str, Any]
    prioritized_roadmap: List[StrategicRecommendation]
    timestamp: str


# ---------------------------------------------------------------------------
# Domain Knowledge & Intent Parsing Logic
# ---------------------------------------------------------------------------

class CISOExecutiveAgent:
    """Synthesizes risk, optimization, and statutory telemetry into executive briefings."""

    @classmethod
    def _format_inr(cls, amount: float) -> str:
        if amount >= 10000000:
            return f"₹ {amount / 10000000:.2f} Cr"
        if amount >= 100000:
            return f"₹ {amount / 100000:.2f} L"
        return f"₹ {amount:,.0f}"

    @classmethod
    def _rule_based_summary(cls, query: str, budget_limit: float, ctx: Dict[str, Any]) -> str:
        """Keyword-templated fallback used when no LLM is configured or reachable."""
        norm_query = query.lower()
        opt = ctx["optimizer"]
        comp = ctx["compliance"]

        if any(w in norm_query for w in ["biggest", "highest", "top risk", "critical", "danger"]):
            return (
                f"Our primary financial risk exposure stems from **{ctx['scenario_name']}** on asset **{ctx['top_risk_asset']}**, "
                f"representing an Expected Annual Loss (EAL) of **{cls._format_inr(ctx['baseline_expected_annual_loss_inr'])}** and a "
                f"95% Value-at-Risk (VaR) of **{cls._format_inr(ctx['value_at_risk_95_inr'])}**. "
                f"This is driven by {', '.join(ctx['top_cves'])}."
            )
        if any(w in norm_query for w in ["rbi", "sebi", "compliance", "fine", "penalty", "regulatory"]):
            top_gaps = ", ".join(f"**{c['section']}** ({c['title']})" for c in comp["failed_clauses"][:2]) or "no open mandates"
            return (
                f"Our current regulatory compliance rating is **{comp['score_percent']}%** across RBI and SEBI CSCRF frameworks, "
                f"carrying a secondary fine liability of **{cls._format_inr(comp['total_penalty_exposure_inr'])}**. "
                f"The highest regulatory risk is non-compliance with {top_gaps}."
            )
        if any(w in norm_query for w in ["spend", "budget", "allocate", "invest", "recommend", "buy", "roi", "rosi"]):
            return (
                f"With an allocated capital budget of **{cls._format_inr(budget_limit)}**, the MILP optimization model "
                f"recommends deploying **{opt['controls_selected']} controls**, mitigating **{cls._format_inr(opt['total_risk_reduced_inr'])}** "
                f"in annual loss exposure. This yields a projected **Portfolio ROSI of {opt['portfolio_rosi_percent']:.1f}%**, "
                f"reducing our net residual EAL to **{cls._format_inr(opt['residual_eal_inr'])}**."
            )
        return (
            f"Enterprise cyber exposure currently stands at **{cls._format_inr(ctx['baseline_expected_annual_loss_inr'])} EAL** with a "
            f"1-in-20 year worst-case 95% VaR of **{cls._format_inr(ctx['value_at_risk_95_inr'])}**. Allocating "
            f"**{cls._format_inr(budget_limit)}** toward prioritized controls will satisfy core **RBI/SEBI** mandates while "
            f"eliminating **{cls._format_inr(opt['total_risk_reduced_inr'])}** of quantifiable risk."
        )

    @classmethod
    async def _generate_summary(cls, query: str, budget_limit: float, ctx: Dict[str, Any]) -> str:
        """Calls local Ollama Mistral with live data as grounding context.
        Falls back to rule-based template if Ollama is unreachable or call fails."""
        system_prompt = (
            "You are the AI CISO decision-support assistant embedded in a bank's cyber risk "
            "quantification platform (Open FAIR + MILP capital allocation, RBI/SEBI CSCRF compliance). "
            "Answer the executive's question directly and specifically using ONLY the LIVE_DATA JSON "
            "provided below -- do not invent figures, assets, CVEs, or controls not present in it. "
            "Write for a board/CFO audience: 3-5 sentences, confident and concrete, bold the key rupee "
            "figures and percentages with **markdown**. If the data doesn't contain something needed to "
            "answer, say so plainly instead of guessing.\n\n"
            f"LIVE_DATA:\n{json.dumps(ctx, indent=2)}"
        )

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    OLLAMA_API_URL,
                    json={
                        "model": OLLAMA_MODEL,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": query},
                        ],
                        "stream": False,
                    },
                )
                response.raise_for_status()
                data = response.json()
                text = data.get("message", {}).get("content", "").strip()
                return text or cls._rule_based_summary(query, budget_limit, ctx)
        except httpx.ConnectError:
            logger.warning("Ollama connection failed; falling back to rule-based agent summary.")
        except httpx.TimeoutException:
            logger.warning("Ollama timeout; falling back to rule-based agent summary.")
        except Exception as e:
            logger.warning("Ollama error: %s; falling back to rule-based agent summary.", str(e))

        return cls._rule_based_summary(query, budget_limit, ctx)

    @classmethod
    async def process_query(cls, query: str, budget_limit: float, db: AsyncSession) -> AgentQueryResponse:
        # 1. Latest live Monte Carlo run (falls back to a labeled baseline if none exists yet)
        run_result = await db.execute(select(SimulationRun).order_by(desc(SimulationRun.timestamp)).limit(1))
        latest_run = run_result.scalars().first()
        baseline_eal = latest_run.mean_eal if latest_run else 2901400.0
        var_95 = latest_run.var_95 if latest_run else 12300000.0
        scenario_label = latest_run.scenario_name if latest_run else "Core Banking Cluster Ransomware Exposure (no live run yet)"

        # 2. Latest ingested scan drives the top-risk asset/CVE narrative and real candidate controls
        scan_result = await db.execute(select(IngestedScan).order_by(desc(IngestedScan.uploaded_at)).limit(1))
        latest_scan = scan_result.scalars().first()

        if latest_scan and latest_scan.total_findings_parsed > 0:
            findings_sorted = sorted(latest_scan.findings or [], key=lambda f: f.get("cvss_score", 0), reverse=True)
            top_finding = findings_sorted[0] if findings_sorted else None
            top_asset = top_finding.get("asset_ip", "Unknown Asset") if top_finding else "Unknown Asset"
            critical_cves = [
                f"{f.get('cve_list', ['N/A'])[0]} ({f.get('vulnerability_name', 'Unknown')})"
                for f in findings_sorted[:2]
                if f.get("cve_list")
            ] or ["No CVEs on record"]
            candidate_controls = derive_controls_from_scan(
                total_findings=latest_scan.total_findings_parsed,
                critical_count=latest_scan.critical_findings_count,
                kev_count=latest_scan.kev_weaponized_count,
                mean_fair_vuln_prob=latest_scan.mean_fair_vuln_prob,
                baseline_eal=baseline_eal,
            )
        else:
            top_asset = "No scan ingested yet — run Technical SOC upload for asset-level detail"
            critical_cves = ["No scan ingested yet"]
            candidate_controls = _FALLBACK_CONTROLS

        # 3. Live statutory compliance posture (real infra posture + real scan-derived vuln clauses)
        telemetry = await _build_telemetry(db)
        compliance_audit = StatutoryComplianceEngine.evaluate_all(telemetry)
        penalty_exposure = compliance_audit["total_penalty_exposure_inr"]

        # 4. Live MILP optimizer run over the real candidate set
        solver = SecurityInvestmentOptimizer()
        opt_result = solver.optimize_allocation(candidate_controls, budget_limit=budget_limit, baseline_eal=baseline_eal)

        # 5. Ground an LLM in the live figures gathered above for a genuine natural-language
        # answer to the specific question asked (falls back to a rule-based template if no
        # ANTHROPIC_API_KEY is configured, or if the API call itself fails).
        failed_clauses = [c for c in compliance_audit["clauses"] if c["status"] == "NON_COMPLIANT"]
        live_context = {
            "scenario_name": scenario_label,
            "top_risk_asset": top_asset,
            "top_cves": critical_cves,
            "baseline_expected_annual_loss_inr": round(baseline_eal, 2),
            "value_at_risk_95_inr": round(var_95, 2),
            "requested_budget_inr": budget_limit,
            "optimizer": {
                "solver_status": opt_result.solver_status,
                "controls_selected": len(opt_result.selected_controls),
                "total_spend_inr": opt_result.total_spend,
                "total_risk_reduced_inr": opt_result.total_risk_reduced,
                "residual_eal_inr": opt_result.residual_eal,
                "portfolio_rosi_percent": opt_result.portfolio_rosi,
                "selected_controls": opt_result.selected_controls,
                "deferred_controls": opt_result.deferred_controls,
            },
            "compliance": {
                "score_percent": compliance_audit["compliance_score"],
                "total_penalty_exposure_inr": penalty_exposure,
                "failed_clauses": failed_clauses,
            },
        }

        summary = await cls._generate_summary(query, budget_limit, live_context)

        recommendations = [
            StrategicRecommendation(
                control_id=c["control_id"],
                control_name=c["name"],
                investment_cost_inr=c["cost"],
                expected_risk_mitigation_inr=c["risk_reduction_delta"],
                statutory_alignment=c.get("framework_mapping", []),
            )
            for c in opt_result.selected_controls
        ]

        return AgentQueryResponse(
            query=query,
            executive_summary=summary,
            quantified_exposure={
                "baseline_eal_inr": baseline_eal,
                "var_95_inr": var_95,
                "residual_eal_inr": opt_result.residual_eal,
                "net_risk_reduction_inr": opt_result.total_risk_reduced,
            },
            regulatory_impact={
                "compliance_score_percent": compliance_audit["compliance_score"],
                "statutory_penalty_liability_inr": penalty_exposure,
                "failed_mandates_count": compliance_audit["failed_clauses"],
            },
            prioritized_roadmap=recommendations,
            timestamp=datetime.now().isoformat(),
        )


# ---------------------------------------------------------------------------
# API Route
# ---------------------------------------------------------------------------

@router.post(
    "/query",
    response_model=AgentQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Executive Natural Language Query & Decision-Support",
)
async def ask_executive_ciso_agent(payload: AgentQueryRequest, db: AsyncSession = Depends(get_db)):
    """
    Accepts executive natural language questions, contextualizes organizational risk
    metrics (FAIR stochastic curves, Knapsack allocations, and statutory audit data),
    and returns a structured board briefing grounded in the latest live data.
    """
    if not payload.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query string cannot be empty.",
        )

    try:
        return await CISOExecutiveAgent.process_query(
            query=payload.query,
            budget_limit=payload.budget_limit or 1000000.0,
            db=db,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent processing failed: {str(e)}",
        )

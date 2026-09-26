"""
Board Briefing PDF Export Endpoint.
Builds the executive report from the latest live simulation/ingestion data
in the database (not hardcoded figures) and streams it to HTTP clients.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import Response
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.app.core.database import get_db
from backend.app.models.simulation_run import SimulationRun
from backend.app.models.ingested_scan import IngestedScan
from backend.app.services.optimizer.milp_solver import SecurityInvestmentOptimizer, CandidateControl
from backend.app.services.optimizer.control_recommender import derive_controls_from_scan
from backend.app.services.report_generator.pdf_builder import CISOReportBuilder

router = APIRouter()

_FALLBACK_CONTROLS = [
    CandidateControl("CTRL-01", "Deploy EDR on Core DB Cluster", "Endpoint", 800000, 1200000, ["RBI Sec 3.2", "NIST CSF DE.CM"], False),
    CandidateControl("CTRL-02", "Enforce Multi-Factor Authentication (MFA)", "IAM", 200000, 700000, ["SEBI CSCRF 4.1", "ISO 27001 A.9"], True),
    CandidateControl("CTRL-03", "Deploy Web Application Firewall (WAF)", "Network", 500000, 600000, ["ISO 27001 A.12", "PCI-DSS 6.6"], False),
    CandidateControl("CTRL-04", "Automated Patch Automation Engine", "Vulnerability", 400000, 550000, ["RBI Sec 5.1"], False),
    CandidateControl("CTRL-05", "Employee Security & Anti-Phishing Training", "Human Layer", 150000, 300000, ["NIST CSF PR.AT"], False),
]


@router.get("/board-briefing")
async def generate_board_briefing_pdf(
    budget: float = Query(default=1000000.0, description="Allocated security budget in INR"),
    db: AsyncSession = Depends(get_db),
):
    try:
        # 1. Latest FAIR simulation run (whichever came last: manual or scan-derived)
        run_result = await db.execute(
            select(SimulationRun).order_by(desc(SimulationRun.timestamp)).limit(1)
        )
        latest_run = run_result.scalars().first()

        if latest_run is None:
            raise HTTPException(
                status_code=404,
                detail="No simulation run found yet. Run a Monte Carlo simulation before exporting a briefing.",
            )

        # 2. Latest ingested scan, if any, drives real candidate controls + technical section
        scan_result = await db.execute(
            select(IngestedScan).order_by(desc(IngestedScan.uploaded_at)).limit(1)
        )
        latest_scan = scan_result.scalars().first()

        if latest_scan and latest_scan.total_findings_parsed > 0:
            candidates = derive_controls_from_scan(
                total_findings=latest_scan.total_findings_parsed,
                critical_count=latest_scan.critical_findings_count,
                kev_count=latest_scan.kev_weaponized_count,
                mean_fair_vuln_prob=latest_scan.mean_fair_vuln_prob,
                baseline_eal=latest_run.mean_eal,
            )
            scan_summary = {
                "filename": latest_scan.filename,
                "detected_scanner": latest_scan.detected_scanner,
                "total_findings_parsed": latest_scan.total_findings_parsed,
                "critical_findings_count": latest_scan.critical_findings_count,
                "kev_weaponized_count": latest_scan.kev_weaponized_count,
                "mean_fair_vuln_prob": latest_scan.mean_fair_vuln_prob,
            }
            top_findings = sorted(
                latest_scan.findings or [],
                key=lambda f: f.get("cvss_score", 0),
                reverse=True,
            )
            data_source_note = f"Live scan ingestion ({latest_scan.detected_scanner}, {latest_scan.filename})."
        else:
            candidates = _FALLBACK_CONTROLS
            scan_summary = None
            top_findings = []
            data_source_note = "Baseline demo scenario (no live scan ingested)."

        # 3. Run the same optimizer the dashboard uses, so the PDF matches what's on screen
        optimizer = SecurityInvestmentOptimizer()
        opt_out = optimizer.optimize_allocation(
            candidate_controls=candidates,
            budget_limit=budget,
            baseline_eal=latest_run.mean_eal,
        )

        # 4. Historical trend for the trajectory table
        hist_result = await db.execute(
            select(SimulationRun).order_by(SimulationRun.timestamp.asc()).limit(6)
        )
        history_rows = [
            {
                "timestamp": r.timestamp.strftime("%b %Y"),
                "mean_eal": r.mean_eal,
                "var_95": r.var_95,
                "allocated_budget": r.allocated_budget,
                "portfolio_rosi": r.portfolio_rosi,
            }
            for r in hist_result.scalars().all()
        ]

        pdf_bytes = CISOReportBuilder.generate_pdf(
            scenario_name=latest_run.scenario_name,
            baseline_eal=latest_run.mean_eal,
            var_90=latest_run.var_90,
            var_95=latest_run.var_95,
            var_99=latest_run.var_99,
            iterations=latest_run.iterations,
            allocated_budget=budget,
            optimal_spend=opt_out.total_spend,
            residual_eal=opt_out.residual_eal,
            risk_reduced=opt_out.total_risk_reduced,
            rosi=opt_out.portfolio_rosi,
            budget_utilized_percentage=opt_out.budget_utilized_percentage,
            solver_status=opt_out.solver_status,
            selected_controls=opt_out.selected_controls,
            deferred_controls=opt_out.deferred_controls,
            scan_summary=scan_summary,
            top_findings=top_findings,
            historical_runs=history_rows,
            data_source_note=data_source_note,
        )

        filename = f"CISO_Board_Briefing_{datetime.now().strftime('%Y%m%d')}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Expose-Headers": "Content-Disposition",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF compilation failed: {str(e)}")

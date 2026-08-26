"""
Board Briefing PDF Export Endpoint.
Streams the generated executive report directly to HTTP clients with attachment headers.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from datetime import datetime

from backend.app.services.report_generator.pdf_builder import CISOReportBuilder

router = APIRouter()


@router.get("/board-briefing")
async def generate_board_briefing_pdf(
    budget: float = Query(default=1000000.0, description="Allocated security budget in INR"),
    scenario_name: str = Query(default="Core Banking Cluster Ransomware Exposure", description="Evaluated risk scenario name"),
):
    try:
        pdf_bytes = CISOReportBuilder.generate_pdf(
            scenario_name=scenario_name,
            baseline_eal=2901400.0,
            var_95=12300000.0,
            allocated_budget=budget,
            optimal_spend=budget,
            residual_eal=1001400.0,
            risk_reduced=1900000.0,
            rosi=90.0,
            compliance_score=67,
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF compilation failed: {str(e)}")
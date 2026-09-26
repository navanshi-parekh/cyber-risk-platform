"""
Statutory Compliance & Regulatory Audit Endpoint.
Evaluates RBI / SEBI CSCRF mandates against real telemetry: vulnerability-related
clauses are derived from the latest ingested scan (critical/KEV counts), while
org-configurable controls (EDR, MFA, WAF, backups, SOC) come from a persisted,
CISO-editable infrastructure posture record.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.app.core.database import get_db
from backend.app.models.infrastructure_posture import InfrastructurePosture
from backend.app.models.ingested_scan import IngestedScan
from backend.app.services.compliance.framework_mapper import StatutoryComplianceEngine

router = APIRouter()


class PostureUpdate(BaseModel):
    has_edr_installed: bool
    mfa_enforced_on_admins: bool
    waf_active_blocking: bool
    immutable_backups_configured: bool
    soc_telemetry_integrated: bool


async def _get_or_create_posture(db: AsyncSession) -> InfrastructurePosture:
    result = await db.execute(select(InfrastructurePosture).where(InfrastructurePosture.id == 1))
    posture = result.scalars().first()
    if posture is None:
        posture = InfrastructurePosture(id=1)
        db.add(posture)
        await db.commit()
        await db.refresh(posture)
    return posture


async def _build_telemetry(db: AsyncSession) -> Dict[str, Any]:
    posture = await _get_or_create_posture(db)

    scan_result = await db.execute(select(IngestedScan).order_by(desc(IngestedScan.uploaded_at)).limit(1))
    latest_scan = scan_result.scalars().first()

    if latest_scan and latest_scan.total_findings_parsed > 0:
        unpatched_critical_cves = latest_scan.critical_findings_count
        vapt_sla_breached = latest_scan.kev_weaponized_count > 0
    else:
        unpatched_critical_cves = 0
        vapt_sla_breached = False

    return {
        "has_edr_installed": posture.has_edr_installed,
        "mfa_enforced_on_admins": posture.mfa_enforced_on_admins,
        "waf_active_blocking": posture.waf_active_blocking,
        "immutable_backups_configured": posture.immutable_backups_configured,
        "soc_telemetry_integrated": posture.soc_telemetry_integrated,
        "unpatched_critical_cves": unpatched_critical_cves,
        "vapt_sla_breached": vapt_sla_breached,
    }


@router.get("/posture")
async def get_infrastructure_posture(db: AsyncSession = Depends(get_db)):
    """Returns the CISO-editable infrastructure control posture used for compliance scoring."""
    posture = await _get_or_create_posture(db)
    return {
        "has_edr_installed": posture.has_edr_installed,
        "mfa_enforced_on_admins": posture.mfa_enforced_on_admins,
        "waf_active_blocking": posture.waf_active_blocking,
        "immutable_backups_configured": posture.immutable_backups_configured,
        "soc_telemetry_integrated": posture.soc_telemetry_integrated,
    }


@router.put("/posture")
async def update_infrastructure_posture(payload: PostureUpdate, db: AsyncSession = Depends(get_db)):
    """Updates the infrastructure control posture; compliance audits reflect this immediately."""
    posture = await _get_or_create_posture(db)
    posture.has_edr_installed = payload.has_edr_installed
    posture.mfa_enforced_on_admins = payload.mfa_enforced_on_admins
    posture.waf_active_blocking = payload.waf_active_blocking
    posture.immutable_backups_configured = payload.immutable_backups_configured
    posture.soc_telemetry_integrated = payload.soc_telemetry_integrated
    await db.commit()
    return {"status": "updated"}


@router.get("/rbi-audit")
async def get_rbi_compliance_audit(db: AsyncSession = Depends(get_db)):
    """Returns RBI Cyber Security Framework compliance status."""
    telemetry = await _build_telemetry(db)
    return StatutoryComplianceEngine.evaluate_rbi(telemetry)


@router.get("/sebi-audit")
async def get_sebi_compliance_audit(db: AsyncSession = Depends(get_db)):
    """Returns SEBI CSCRF compliance status."""
    telemetry = await _build_telemetry(db)
    return StatutoryComplianceEngine.evaluate_sebi(telemetry)


@router.get("/unified-audit")
async def get_unified_compliance_audit(db: AsyncSession = Depends(get_db)):
    """Returns unified RBI + SEBI CSCRF compliance status and fine liabilities."""
    telemetry = await _build_telemetry(db)
    return StatutoryComplianceEngine.evaluate_all(telemetry)

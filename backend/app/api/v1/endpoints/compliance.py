from fastapi import APIRouter
from backend.app.services.compliance.framework_mapper import StatutoryComplianceEngine

router = APIRouter()

# Current mock infrastructure telemetry state
DEFAULT_TELEMETRY = {
    "has_edr_installed": False,               # Fails RBI 3.2 & SEBI 14.1 (CTRL-01)
    "unpatched_critical_cves": 2,             # Fails RBI 5.1 (CTRL-04)
    "mfa_enforced_on_admins": True,           # Passes RBI 4.1 & SEBI 4.1 (CTRL-02)
    "waf_active_blocking": False,             # Fails SEBI 7.3 (CTRL-03)
    "vapt_sla_breached": False,               # Passes SEBI 8.2
    "immutable_backups_configured": True,     # Passes SEBI 11.4
    "soc_telemetry_integrated": False,        # Fails SEBI 14.1
}


@router.get("/rbi-audit")
async def get_rbi_compliance_audit():
    """Returns RBI Cyber Security Framework compliance status."""
    return StatutoryComplianceEngine.evaluate_rbi(DEFAULT_TELEMETRY)


@router.get("/sebi-audit")
async def get_sebi_compliance_audit():
    """Returns SEBI CSCRF compliance status."""
    return StatutoryComplianceEngine.evaluate_sebi(DEFAULT_TELEMETRY)


@router.get("/unified-audit")
async def get_unified_compliance_audit():
    """Returns unified RBI + SEBI CSCRF compliance status and fine liabilities."""
    return StatutoryComplianceEngine.evaluate_all(DEFAULT_TELEMETRY)
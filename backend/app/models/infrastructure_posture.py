"""
SQLAlchemy ORM Model for CISO-configurable infrastructure control posture.
Singleton row (id=1) representing the org's current control state for the
regulatory clauses that can't be inferred from a vulnerability scan alone
(EDR deployment, MFA enforcement, WAF mode, backup posture, SOC integration).
"""

from sqlalchemy import Column, Integer, Boolean
from backend.app.core.database import Base


class InfrastructurePosture(Base):
    __tablename__ = "infrastructure_posture"

    id = Column(Integer, primary_key=True, default=1)

    has_edr_installed = Column(Boolean, default=False)
    mfa_enforced_on_admins = Column(Boolean, default=True)
    waf_active_blocking = Column(Boolean, default=False)
    immutable_backups_configured = Column(Boolean, default=True)
    soc_telemetry_integrated = Column(Boolean, default=False)

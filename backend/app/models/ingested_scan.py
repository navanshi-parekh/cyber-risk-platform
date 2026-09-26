"""
SQLAlchemy ORM Model for Persisted Vulnerability Scan Ingestions.
Stores the last enriched scan server-side so it survives across sessions/devices.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON
from backend.app.core.database import Base


class IngestedScan(Base):
    __tablename__ = "ingested_scans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    detected_scanner = Column(String(64), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, index=True)

    total_findings_parsed = Column(Integer, default=0)
    critical_findings_count = Column(Integer, default=0)
    kev_weaponized_count = Column(Integer, default=0)
    mean_fair_vuln_prob = Column(Float, default=0.0)

    findings = Column(JSON, nullable=False, default=list)

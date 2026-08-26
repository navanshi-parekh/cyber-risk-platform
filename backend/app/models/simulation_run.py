"""
SQLAlchemy ORM Model for Historical FAIR Simulation Runs and Risk Auditing.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON
from backend.app.core.database import Base


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scenario_id = Column(String(64), nullable=False, index=True)
    scenario_name = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # FAIR Simulation Output Metrics (in INR)
    iterations = Column(Integer, default=10000)
    mean_eal = Column(Float, nullable=False)
    var_90 = Column(Float, nullable=False)
    var_95 = Column(Float, nullable=False)
    var_99 = Column(Float, nullable=False)
    
    # Associated Capital Allocation Telemetry (if optimized)
    allocated_budget = Column(Float, default=0.0)
    residual_eal = Column(Float, default=0.0)
    total_risk_reduced = Column(Float, default=0.0)
    portfolio_rosi = Column(Float, default=0.0)
    
    # Metadata & curve snapshots
    source = Column(String(64), default="manual_run")  # "manual_run", "scan_ingestion", "scheduled_audit"
    curve_sample = Column(JSON, nullable=True)
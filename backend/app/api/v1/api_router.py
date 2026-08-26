from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    ingestion,
    assets,
    threat_intel,
    risk,
    optimizer,
    compliance,
    agent,
    reports,
)

api_router = APIRouter()

api_router.include_router(ingestion.router, prefix="/ingestion", tags=["Ingestion"])
api_router.include_router(assets.router, prefix="/assets", tags=["Assets"])
api_router.include_router(threat_intel.router, prefix="/threat-intel", tags=["Threat Intel"])
api_router.include_router(risk.router, prefix="/risk", tags=["FAIR Risk Engine"])
api_router.include_router(optimizer.router, prefix="/optimizer", tags=["Budget Optimizer"])
api_router.include_router(compliance.router, prefix="/compliance", tags=["Compliance Mapping"])
api_router.include_router(agent.router, prefix="/agent", tags=["AI Executive Agent"])
api_router.include_router(reports.router, prefix="/reports", tags=["PDF Reports"])
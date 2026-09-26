from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from backend.app.api.v1.api_router import api_router
from backend.app.core.config import settings
from backend.app.core.database import engine, Base, AsyncSessionLocal
from backend.app.models.simulation_run import SimulationRun


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Seed historical 6-month risk reduction trajectory if empty
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(SimulationRun))
        existing = result.scalars().first()
        if not existing:
            now = datetime.utcnow()
            history_seeds = [
                SimulationRun(
                    scenario_id="SCEN-HIST-01",
                    scenario_name="Core Banking Infrastructure",
                    timestamp=now - timedelta(days=150),
                    iterations=10000,
                    mean_eal=4500000.0,
                    var_90=14200000.0,
                    var_95=18500000.0,
                    var_99=23000000.0,
                    allocated_budget=0.0,
                    residual_eal=4500000.0,
                    total_risk_reduced=0.0,
                    portfolio_rosi=0.0,
                    source="baseline_audit",
                ),
                SimulationRun(
                    scenario_id="SCEN-HIST-02",
                    scenario_name="Core Banking Infrastructure",
                    timestamp=now - timedelta(days=120),
                    iterations=10000,
                    mean_eal=3900000.0,
                    var_90=12800000.0,
                    var_95=16200000.0,
                    var_99=20100000.0,
                    allocated_budget=500000.0,
                    residual_eal=3400000.0,
                    total_risk_reduced=500000.0,
                    portfolio_rosi=0.0,
                    source="scheduled_audit",
                ),
                SimulationRun(
                    scenario_id="SCEN-HIST-03",
                    scenario_name="Core Banking Infrastructure",
                    timestamp=now - timedelta(days=90),
                    iterations=10000,
                    mean_eal=3400000.0,
                    var_90=11200000.0,
                    var_95=14500000.0,
                    var_99=18000000.0,
                    allocated_budget=800000.0,
                    residual_eal=2600000.0,
                    total_risk_reduced=800000.0,
                    portfolio_rosi=45.0,
                    source="scheduled_audit",
                ),
                SimulationRun(
                    scenario_id="SCEN-HIST-04",
                    scenario_name="Core Banking Infrastructure",
                    timestamp=now - timedelta(days=60),
                    iterations=10000,
                    mean_eal=3100000.0,
                    var_90=10100000.0,
                    var_95=13200000.0,
                    var_99=16800000.0,
                    allocated_budget=1000000.0,
                    residual_eal=2100000.0,
                    total_risk_reduced=1000000.0,
                    portfolio_rosi=70.0,
                    source="scheduled_audit",
                ),
                SimulationRun(
                    scenario_id="SCEN-HIST-05",
                    scenario_name="Core Banking Infrastructure",
                    timestamp=now - timedelta(days=30),
                    iterations=10000,
                    mean_eal=2901400.0,
                    var_90=9800000.0,
                    var_95=12300000.0,
                    var_99=15100000.0,
                    allocated_budget=1000000.0,
                    residual_eal=1001400.0,
                    total_risk_reduced=1900000.0,
                    portfolio_rosi=90.0,
                    source="scheduled_audit",
                ),
            ]
            session.add_all(history_seeds)
            await session.commit()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok", "service": settings.PROJECT_NAME}

@app.get(f"{settings.API_V1_STR}/health")
async def api_health_check() -> dict:
    return {"status": "ok", "service": settings.PROJECT_NAME, "api": settings.API_V1_STR}

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)
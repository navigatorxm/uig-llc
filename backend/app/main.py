from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.routers import (
    properties,
    leads,
    outreach,
    documents,
    deals,
    webhooks,
    dashboard,
    agents,
    lpi,
    auth,
)
from app.routers import (
    admin_auth,
    admin_pipeline,
    admin_settings,
    admin_costs,
    admin_automations,
    admin_accounts,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables and seed master admins on startup."""
    from app.database import engine, Base, SessionLocal
    import app.models  # noqa — ensure all models are registered
    Base.metadata.create_all(bind=engine)
    # Seed master admin accounts
    db = SessionLocal()
    try:
        from app.routers.admin_auth import seed_master_admins
        seed_master_admins(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="UIG Property Acquisition Pipeline",
    description=(
        "Automated real estate acquisition system for United Investing Group LLC. "
        "Powered by UIG's private earth-mapping satellite division — issuing LPI "
        "(LiDAR Property Identifier) certificates for every 10x10m land parcel near "
        "all major Indian airports."
    ),
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core acquisition pipeline
app.include_router(properties.router, prefix="/api", tags=["Properties"])
app.include_router(leads.router, prefix="/api", tags=["Leads"])
app.include_router(outreach.router, prefix="/api", tags=["Outreach"])
app.include_router(documents.router, prefix="/api", tags=["Documents"])
app.include_router(deals.router, prefix="/api", tags=["Deals"])
app.include_router(webhooks.router, prefix="/api", tags=["Webhooks"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])

# UIG Satellite & LPI division
app.include_router(lpi.router, prefix="/api", tags=["LPI Certificates"])

# Agent partner network
app.include_router(agents.router, prefix="/api", tags=["Agent Network"])

# Authentication
app.include_router(auth.router)

# Admin dashboard
app.include_router(admin_auth.router)
app.include_router(admin_pipeline.router)
app.include_router(admin_settings.router)
app.include_router(admin_costs.router)
app.include_router(admin_automations.router)
app.include_router(admin_accounts.router)


@app.get("/health", tags=["Health"])
def health_check():
    from app.data.airports import AIRPORTS
    return {
        "status": "ok",
        "service": "UIG Property Acquisition Pipeline",
        "version": "2.0.0",
        "coverage": {
            "airports_mapped": len(AIRPORTS),
            "cities_active": len({a.city for a in AIRPORTS}),
            "lpi_authority": "UIG Satellite Mapping Division",
        },
    }

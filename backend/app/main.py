from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import (
    properties,
    leads,
    outreach,
    documents,
    deals,
    webhooks,
    dashboard,
)

app = FastAPI(
    title="UIG Property Acquisition Pipeline",
    description="Automated real estate acquisition system for United Investing Group LLC",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(properties.router, prefix="/api", tags=["Properties"])
app.include_router(leads.router, prefix="/api", tags=["Leads"])
app.include_router(outreach.router, prefix="/api", tags=["Outreach"])
app.include_router(documents.router, prefix="/api", tags=["Documents"])
app.include_router(deals.router, prefix="/api", tags=["Deals"])
app.include_router(webhooks.router, prefix="/api", tags=["Webhooks"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "UIG Property Acquisition Pipeline"}

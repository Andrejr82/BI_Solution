"""
API V1 Router
Combines all v1 endpoints
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    analytics,
    auth,
    reports,
    auth_alt,
    metrics,
    chat,
    rupturas,
    transfers,
    diagnostics,
    learning,
    playground,
    frontend_logs,
    shared,
    preferences,
    insights
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router)
api_router.include_router(auth_alt.router_alt)  # Login alternativo
api_router.include_router(analytics.router)
api_router.include_router(reports.router)
api_router.include_router(admin.router)
api_router.include_router(metrics.router)  # Dashboard metrics
api_router.include_router(chat.router)  # BI Chat

# New Endpoints
api_router.include_router(rupturas.router)
api_router.include_router(transfers.router)
api_router.include_router(diagnostics.router)
api_router.include_router(learning.router)
api_router.include_router(playground.router)
api_router.include_router(shared.router)
api_router.include_router(preferences.router)
api_router.include_router(insights.router)

# Frontend Logs
api_router.include_router(frontend_logs.router)
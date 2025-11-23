"""
API V1 Router
Combines all v1 endpoints
"""

from fastapi import APIRouter

from app.api.v1.endpoints import admin, analytics, auth, reports

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router)
api_router.include_router(analytics.router)
api_router.include_router(reports.router)
api_router.include_router(admin.router)

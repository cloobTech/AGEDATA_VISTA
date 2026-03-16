from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.routes import auth, project, data_processing, uploaded_file, user, reports, notifications, subscription, plan, chat_agent
from services.data_processing.visualization.plot_config import register_professional_theme
from settings.pydantic_config import settings
import os
import logging

_startup_logger = logging.getLogger(__name__)


# Register Plotly theme
register_professional_theme()

app = FastAPI(
    title="Data Processing API",
    description="API for data processing",
    version="1.0.0",
    docs_url="/",
    redoc_url=None,
)


origins = [
    settings.FRONTEND_URL,
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    os.getenv("FRONTEND_URL", "http://localhost:5173"),
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "Authorization", "X-Request-ID"],
)


app.include_router(auth.router)
app.include_router(project.router)
app.include_router(data_processing.router)
app.include_router(uploaded_file.router)
app.include_router(user.router)
app.include_router(reports.router)
app.include_router(notifications.router)
app.include_router(subscription.router)
app.include_router(plan.router)
app.include_router(chat_agent.router)

# Alias routers: notificationsSlice.js sends requests with full path /api/v1/notifications/...
# because baseURL already contains /api/v1, resulting in double prefix.
# We mount a second copy of the notifications router at the double-prefix path.
from fastapi import APIRouter as _APIRouter
from api.v1.routes.notifications import (
    get_user_notifications_route,
    get_notification_by_id_route,
    delete_notification_route,
    update_notification_route,
)
from api.v1.utils.get_db_session import get_db_session as _get_db_session
from api.v1.utils.current_user import get_current_user as _get_current_user

_notifications_alias_router = _APIRouter(
    tags=['Notification (alias)'],
    prefix='/api/v1/api/v1/notifications'
)
_notifications_alias_router.add_api_route('', get_user_notifications_route, methods=['GET'])
_notifications_alias_router.add_api_route('/{notification_id}', get_notification_by_id_route, methods=['GET'])
_notifications_alias_router.add_api_route('/{notification_id}', delete_notification_route, methods=['DELETE'])
_notifications_alias_router.add_api_route('/{notification_id}', update_notification_route, methods=['PUT'])
app.include_router(_notifications_alias_router)


@app.on_event("startup")
async def startup_event():
    """Auto-seed subscription plans on startup so registration never fails
    with 'Plan not found' on a fresh database."""
    try:
        from storage import db
        from models.subscription_plan import Plan
        from sqlalchemy import select

        async with db.get_session() as session:
            result = await session.execute(select(Plan).limit(1))
            existing = result.scalars().first()
            if not existing:
                plans = [
                    Plan(name="trial", price=0.0, duration_days=36500),
                    Plan(name="Pro", price=19.99, duration_days=30),
                    Plan(name="Enterprise", price=99.99, duration_days=30),
                ]
                session.add_all(plans)
                await session.commit()
                _startup_logger.info("Auto-seeded %d subscription plans.", len(plans))
            else:
                _startup_logger.debug("Subscription plans already present — skipping auto-seed.")
    except Exception as exc:
        _startup_logger.warning("Auto-seed skipped: %s", exc)


@app.get("/api/v1")
async def read_root():
    """Check server status"""
    return {"server_status": "Server is running fine..."}

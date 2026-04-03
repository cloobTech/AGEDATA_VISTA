"""
main.py — AGEARC FastAPI application entry point.

Security middleware stack (innermost → outermost):
  1. LimitBodySizeMiddleware   — reject bodies > 100 MB (Phase 3A)
  2. GZipMiddleware            — compress large responses (Phase 9B)
  3. HTTPSRedirectMiddleware   — production-only, forces HTTPS (Phase 3B)
  4. CORSMiddleware            — origin / credential whitelist
  5. add_security_headers      — HSTS, X-Content-Type-Options, etc. (Phase 3B)

Rate limiting on auth routes via slowapi (Phase 2E).
"""

import os
import logging
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from api.v1.limiter import limiter

from api.v1.routes import (
    auth, project, data_processing, uploaded_file, user,
    reports, notifications, subscription, plan, chat_agent,
)
from api.v1.routes.models import router as models_router
from schemas.errors import ErrorResponse
from services.data_processing.visualization.plot_config import register_professional_theme
from settings.pydantic_config import settings

_startup_logger = logging.getLogger(__name__)

# Register Plotly professional theme
register_professional_theme()

# ── FastAPI app ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Data Processing API",
    description="API for data processing",
    version="1.0.0",
    docs_url="/",
    redoc_url=None,
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        401: {"model": ErrorResponse, "description": "Unauthorised"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Not found"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)

# Attach the limiter to the app state and register the 429 handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Body size limit middleware (Phase 3A) ────────────────────────────────────

_MAX_BODY_BYTES = 100 * 1024 * 1024  # 100 MB


class LimitBodySizeMiddleware(BaseHTTPMiddleware):
    """Reject requests whose Content-Length exceeds 100 MB before reading the body.

    This prevents memory exhaustion from large payload attacks.
    The check is advisory for chunked transfers — the body will still be
    streamed, but the limit prevents unbounded reads.
    """
    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > _MAX_BODY_BYTES:
                    return JSONResponse(
                        {"detail": "Request body too large (max 100 MB)"},
                        status_code=413,
                    )
            except ValueError:
                pass  # Malformed Content-Length — let FastAPI handle it
        return await call_next(request)


app.add_middleware(LimitBodySizeMiddleware)

# ── GZip compression (Phase 9B) ───────────────────────────────────────────────
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ── HTTPS redirect — production only (Phase 3B) ───────────────────────────────
if os.environ.get("DEV_ENV", "development").lower() == "production":
    from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
    app.add_middleware(HTTPSRedirectMiddleware)

# ── Security headers (Phase 3B) ───────────────────────────────────────────────

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add standard security headers to every response."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
    if os.environ.get("DEV_ENV", "development").lower() == "production":
        response.headers["Strict-Transport-Security"] = (
            "max-age=63072000; includeSubDomains; preload"
        )
    return response


# ── CORS ─────────────────────────────────────────────────────────────────────

origins = [
    "https://agearc.app",
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
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID", "Accept"],
    expose_headers=["Content-Type", "Authorization", "X-Request-ID"],
)

# ── Exception handlers ────────────────────────────────────────────────────────

@app.exception_handler(HTTPException)
async def http_exc_handler(request: Request, exc: HTTPException):
    """Pass HTTPExceptions through as-is so 4xx responses are never swallowed
    by the generic Exception handler below."""
    return await http_exception_handler(request, exc)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all handler that logs the full traceback but returns a sanitised
    message to the client, preventing internal implementation details from
    leaking in 500 responses."""
    _startup_logger.error(
        "Unhandled exception for %s %s: %s",
        request.method,
        request.url.path,
        exc,
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again."},
    )


# ── Routers ───────────────────────────────────────────────────────────────────

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
app.include_router(models_router)

# Alias router: notificationsSlice.js sends requests with double prefix
# /api/v1/api/v1/notifications — mount an alias so both paths work.
from fastapi import APIRouter as _APIRouter
from api.v1.routes.notifications import (
    get_user_notifications_route,
    get_notification_by_id_route,
    delete_notification_route,
    update_notification_route,
)

_notifications_alias_router = _APIRouter(
    tags=["Notification (alias)"],
    prefix="/api/v1/api/v1/notifications",
)
_notifications_alias_router.add_api_route("", get_user_notifications_route, methods=["GET"])
_notifications_alias_router.add_api_route("/{notification_id}", get_notification_by_id_route, methods=["GET"])
_notifications_alias_router.add_api_route("/{notification_id}", delete_notification_route, methods=["DELETE"])
_notifications_alias_router.add_api_route("/{notification_id}", update_notification_route, methods=["PUT"])
app.include_router(_notifications_alias_router)


# ── Health check (Phase 3I) ───────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health_check():
    """Return application health status. Used by load balancers and monitoring."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


# ── Startup event ─────────────────────────────────────────────────────────────

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


# ── Legacy root check ─────────────────────────────────────────────────────────

@app.get("/api/v1")
async def read_root():
    """Check server status"""
    return {"server_status": "Server is running fine..."}

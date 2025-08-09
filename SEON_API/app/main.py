from __future__ import annotations

import time
import uuid
from typing import Callable

from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .utils.errors import (
    install_exception_handlers,
    success_envelope,
)
from .utils.security import require_api_key
from .routes import fraud as fraud_routes
from .routes import aml as aml_routes
from .routes import lists as lists_routes
from .routes import labels as labels_routes
from .routes import exclusion as exclusion_routes
from .routes import debug as debug_routes


def create_app() -> FastAPI:
    app = FastAPI(
        title="SEON Mock Service",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS for localhost development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    # Request ID + simple timing logging
    @app.middleware("http")
    async def request_context(request: Request, call_next: Callable):
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = req_id
        start = time.perf_counter()
        try:
            response: Response = await call_next(request)
        except Exception:
            # Let exception handlers format the error envelope
            raise
        finally:
            duration_ms = int((time.perf_counter() - start) * 1000)
            # Basic structured log (stdout)
            path = request.url.path
            method = request.method
            status = getattr(request.state, "status_code", None)
            if status is None and "response" in locals():
                status = response.status_code
            print(
                {
                    "level": "INFO",
                    "event": "http_request",
                    "method": method,
                    "path": path,
                    "status": status,
                    "duration_ms": duration_ms,
                    "request_id": req_id,
                }
            )
        # Echo request id
        if "response" in locals():
            response.headers["X-Request-ID"] = req_id
            return response
        # Fallback in odd cases (shouldn't hit)
        return JSONResponse(
            content={"success": False, "error": {"code": "INTERNAL_ERROR", "message": "Unhandled"}},
            status_code=500,
            headers={"X-Request-ID": req_id},
        )

    # Error/exception handlers to standardize envelopes
    install_exception_handlers(app)

    # Health endpoints
    @app.get("/__health")
    async def health() -> dict:
        return success_envelope({"status": "ok", "env": settings.env})

    # Mount routers (all require API key except debug/health)
    app.include_router(
        fraud_routes.router,
        prefix="",
        tags=["fraud"],
        dependencies=[Depends(require_api_key)],
    )
    app.include_router(
        aml_routes.router,
        prefix="",
        tags=["aml"],
        dependencies=[Depends(require_api_key)],
    )
    app.include_router(
        lists_routes.router,
        prefix="",
        tags=["lists"],
        dependencies=[Depends(require_api_key)],
    )
    app.include_router(
        labels_routes.router,
        prefix="",
        tags=["labels"],
        dependencies=[Depends(require_api_key)],
    )
    app.include_router(
        exclusion_routes.router,
        prefix="",
        tags=["exclusion"],
        dependencies=[Depends(require_api_key)],
    )
    app.include_router(
        debug_routes.router,
        prefix="",
        tags=["debug"],
    )

    return app


app = create_app()

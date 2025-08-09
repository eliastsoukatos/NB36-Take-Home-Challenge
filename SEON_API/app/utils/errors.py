from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def success_envelope(data: Dict[str, Any] | Any) -> Dict[str, Any]:
    return {"success": True, "error": {}, "data": data}


def error_envelope(code: str, message: str) -> Dict[str, Any]:
    return {"success": False, "error": {"code": code, "message": message}}


def _short_validation_message(exc: RequestValidationError) -> str:
    # Create a concise message from validation errors
    try:
        first = exc.errors()[0]
        loc = ".".join(str(x) for x in first.get("loc", []) if x != "body")
        msg = first.get("msg", "Invalid request")
        if loc:
            return f"{loc}: {msg}"
        return msg
    except Exception:
        return "Invalid request payload"


def install_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        # Normalize all validation errors (incl. JSON body issues) to 400 envelope
        message = _short_validation_message(exc)
        payload = error_envelope("VALIDATION_ERROR", message)
        status_code = 400
        # annotate for logging middleware
        try:
            request.state.status_code = status_code
        except Exception:
            pass
        return JSONResponse(content=payload, status_code=status_code)

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, exc: HTTPException):
        status_code = exc.status_code or 500
        detail = (exc.detail or "") if isinstance(exc.detail, str) else str(exc.detail)

        # Map auth-related details to friendly messages
        if status_code == 401:
            if detail == "AUTH_MISSING_KEY":
                payload = error_envelope("AUTH_MISSING_KEY", "X-API-KEY required")
            elif detail == "AUTH_INVALID_KEY":
                payload = error_envelope("AUTH_INVALID_KEY", "Invalid API key")
            else:
                payload = error_envelope("AUTH_ERROR", "Unauthorized")
        elif status_code == 400:
            payload = error_envelope("BAD_REQUEST", detail or "Bad request")
        else:
            payload = error_envelope(f"HTTP_{status_code}", detail or "HTTP error")

        # annotate for logging middleware
        try:
            request.state.status_code = status_code
        except Exception:
            pass
        return JSONResponse(content=payload, status_code=status_code, headers=getattr(exc, "headers", None))

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception):
        # Generic 500
        payload = error_envelope("INTERNAL_ERROR", "Internal server error")
        status_code = 500
        try:
            request.state.status_code = status_code
        except Exception:
            pass
        return JSONResponse(content=payload, status_code=status_code)

"""
Custom exceptions for the application.
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class UzhathunaiException(Exception):
    """Base exception for Uzhathunai application."""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(UzhathunaiException):
    """Authentication related errors."""
    pass


class ValidationError(UzhathunaiException):
    """Validation related errors."""
    pass


class ConflictError(UzhathunaiException):
    """Resource conflict errors."""
    pass


class NotFoundError(UzhathunaiException):
    """Resource not found errors."""
    pass


class PermissionError(UzhathunaiException):
    """Permission/authorization related errors."""
    pass


class RateLimitError(UzhathunaiException):
    """Rate limiting errors."""
    pass


class ServiceError(UzhathunaiException):
    """Service layer errors."""
    pass


# HTTP Exception helpers
def create_http_exception(
    status_code: int,
    message: str,
    error_code: str,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> HTTPException:
    """Create standardized HTTP exception."""
    from datetime import datetime
    import uuid
    
    return HTTPException(
        status_code=status_code,
        detail={
            "success": False,
            "message": message,
            "error_code": error_code,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": request_id or str(uuid.uuid4())[:8]
        }
    )


def bad_request_exception(
    message: str = "Bad request",
    error_code: str = "BAD_REQUEST",
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> HTTPException:
    """Create bad request exception."""
    return create_http_exception(
        status.HTTP_400_BAD_REQUEST,
        message,
        error_code,
        details,
        request_id
    )


def unauthorized_exception(
    message: str = "Unauthorized",
    error_code: str = "UNAUTHORIZED",
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> HTTPException:
    """Create unauthorized exception."""
    return create_http_exception(
        status.HTTP_401_UNAUTHORIZED,
        message,
        error_code,
        details,
        request_id
    )


def forbidden_exception(
    message: str = "Forbidden",
    error_code: str = "FORBIDDEN",
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> HTTPException:
    """Create forbidden exception."""
    return create_http_exception(
        status.HTTP_403_FORBIDDEN,
        message,
        error_code,
        details,
        request_id
    )


def conflict_exception(
    message: str = "Resource conflict",
    error_code: str = "CONFLICT",
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> HTTPException:
    """Create conflict exception."""
    return create_http_exception(
        status.HTTP_409_CONFLICT,
        message,
        error_code,
        details,
        request_id
    )


def validation_exception(
    message: str = "Validation failed",
    field_errors: Optional[Dict[str, list]] = None,
    request_id: Optional[str] = None
) -> HTTPException:
    """Create validation exception."""
    details = {"field_errors": field_errors or {}}
    return create_http_exception(
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        message,
        "VALIDATION_ERROR",
        details,
        request_id
    )


def rate_limit_exception(
    message: str = "Rate limit exceeded",
    retry_after: Optional[int] = None,
    request_id: Optional[str] = None
) -> HTTPException:
    """Create rate limit exception."""
    details = {"retry_after": retry_after} if retry_after else {}
    return create_http_exception(
        status.HTTP_429_TOO_MANY_REQUESTS,
        message,
        "RATE_LIMIT_EXCEEDED",
        details,
        request_id
    )


def internal_server_exception(
    message: str = "Internal server error",
    error_code: str = "INTERNAL_SERVER_ERROR",
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> HTTPException:
    """Create internal server error exception."""
    return create_http_exception(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        message,
        error_code,
        details,
        request_id
    )
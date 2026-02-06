"""
AggroConnect Backend v2.0 - Agricultural Management API
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time
import uuid

from app.core.config import settings
from app.core.logging import configure_logging, log_application_startup, log_application_shutdown, get_logger
from app.core.database import engine, Base

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    configure_logging()
    log_application_startup()
    logger.info("Database connection established")
    
    yield
    
    # Shutdown
    log_application_shutdown()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Comprehensive agricultural supply chain and farm management solution",
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    default_response_class=JSONResponse
)

# Mount static files (uploads)
from fastapi.staticfiles import StaticFiles
import os

upload_dir = settings.UPLOAD_DIR
# Ensure directory exists just in case
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID and logging middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Add request ID, logging, and timing to all requests."""
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    
    # Log request start
    logger.info(
        "Request started",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": str(request.url.path),
            "client_ip": request.client.host if request.client else None
        }
    )
    
    start_time = time.time()
    
    # Remove blocking debug print

    try:
        response = await call_next(request)
        # Remove blocking debug print
        process_time = (time.time() - start_time) * 1000
        
        # Log request completion
        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": str(request.url.path),
                "status_code": response.status_code,
                "duration_ms": f"{process_time:.2f}"
            }
        )
        
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        
        return response
        
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        
        # Log request failure
        logger.error(
            "Request failed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": str(request.url.path),
                "duration_ms": f"{process_time:.2f}",
                "error": str(e)
            },
            exc_info=True
        )
        raise


# Exception handlers
from app.core.exceptions import (
    NotFoundError,
    ConflictError,
    ValidationError as AppValidationError,
    PermissionError as AppPermissionError,
    AuthenticationError,
    ServiceError
)


@app.exception_handler(NotFoundError)
async def not_found_exception_handler(request: Request, exc: NotFoundError):
    """Handle not found errors."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "success": False,
            "message": exc.message,
            "error_code": exc.error_code,
            "data": exc.details,
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )


@app.exception_handler(ConflictError)
async def conflict_exception_handler(request: Request, exc: ConflictError):
    """Handle conflict errors."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "success": False,
            "message": exc.message,
            "error_code": exc.error_code,
            "data": exc.details,
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )


@app.exception_handler(AppValidationError)
async def app_validation_exception_handler(request: Request, exc: AppValidationError):
    """Handle application validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": exc.message,
            "error_code": exc.error_code,
            "data": exc.details,
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )


@app.exception_handler(AppPermissionError)
async def permission_exception_handler(request: Request, exc: AppPermissionError):
    """Handle permission errors."""
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "success": False,
            "message": exc.message,
            "error_code": exc.error_code,
            "data": exc.details,
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )


@app.exception_handler(AuthenticationError)
async def authentication_exception_handler(request: Request, exc: AuthenticationError):
    """Handle authentication errors."""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "success": False,
            "message": exc.message,
            "error_code": exc.error_code,
            "data": exc.details,
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )


@app.exception_handler(ServiceError)
async def service_exception_handler(request: Request, exc: ServiceError):
    """Handle service errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": exc.message,
            "error_code": exc.error_code,
            "data": exc.details,
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    errors = {}
    for error in exc.errors():
        field = ".".join(str(x) for x in error["loc"][1:])
        if field not in errors:
            errors[field] = []
        errors[field].append(error["msg"])
    
    # Log validation error (without reading body to avoid hangs)
    logger.warning(
        "Validation error",
        extra={
            "request_id": getattr(request.state, "request_id", "unknown"),
            "path": str(request.url.path),
            "errors": errors
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation failed",
            "error_code": "VALIDATION_ERROR",
            "data": {"field_errors": errors},
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(
        "Unhandled exception",
        error=str(exc),
        path=request.url.path,
        method=request.method,
        request_id=getattr(request.state, "request_id", "unknown")
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": "INTERNAL_SERVER_ERROR",
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Uzhathunai Farming Platform v2.0",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


# API v1 router
from app.api.v1 import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

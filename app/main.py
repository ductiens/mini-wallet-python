import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import db_manager
from app.common.exceptions import AppException
from app.common.response import error_response
from fastapi.exceptions import RequestValidationError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to database
    try:
        await db_manager.connect()
    except Exception as e:
        logger.error(f"Startup database connection failed: {e}")
    yield
    # Shutdown: Close database connection
    await db_manager.close()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Global Exception Handlers for Unified API Responses
@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    return error_response(
        message=exc.message,
        error_code=exc.error_code,
        status_code=exc.status_code,
        details=exc.details
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return error_response(
        message="Validation failed",
        error_code="VALIDATION_ERROR",
        status_code=422,
        details=exc.errors()
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc: Exception):
    logger.error(f"Unhandled server error: {exc}", exc_info=True)
    if settings.DEBUG:
        return error_response(
            message=str(exc),
            error_code="INTERNAL_SERVER_ERROR",
            status_code=500
        )
    return error_response(
        message="An unexpected error occurred",
        error_code="INTERNAL_SERVER_ERROR",
        status_code=500
    )

# Set up CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/health")
async def health_check():
    mongodb_status = "unhealthy"
    try:
        if db_manager.client:
            await db_manager.client.admin.command("ping")
            mongodb_status = "healthy"
    except Exception as e:
        logger.error(f"Health check ping to MongoDB failed: {e}")
        mongodb_status = "unhealthy"

    overall_status = "healthy" if mongodb_status == "healthy" else "degraded"

    return {
        "status": overall_status,
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "services": {
            "mongodb": mongodb_status
        }
    }

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs": "/docs",
        "version": settings.APP_VERSION
    }

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import db_manager

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

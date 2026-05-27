import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import db_manager
from app.common.exceptions import AppException
from app.common.response import error_response
from fastapi.exceptions import RequestValidationError

from app.modules.transactions.repository import ensure_indexes as ensure_transactions_indexes
from app.modules.transactions.router import router as transactions_router
from app.modules.risk.repository import ensure_indexes as ensure_risk_indexes
from app.modules.risk.router import router as risk_router
from app.modules.analytics.router import router as analytics_router
from app.modules.agents.router import router as agents_router

# Legacy imports restored for backward compatibility with active test suites
from app.modules.users.repository import ensure_indexes as ensure_users_indexes
from app.modules.users.router import router as users_router
from app.modules.wallets.repository import ensure_indexes as ensure_wallets_indexes
from app.modules.wallets.router import router as wallets_router
from app.modules.ledger.repository import ensure_indexes as ensure_ledger_indexes
from app.modules.ledger.router import router as ledger_router


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
        if db_manager.db is not None:
            # Ensure index setups for new modules
            await ensure_transactions_indexes(db_manager.db)
            logger.info("Transactions database indexes ensured successfully.")
            await ensure_risk_indexes(db_manager.db)
            logger.info("Risk database indexes ensured successfully.")
            
            # Legacy index setups restored
            await ensure_users_indexes(db_manager.db)
            logger.info("Legacy Users database indexes ensured.")
            await ensure_wallets_indexes(db_manager.db)
            logger.info("Legacy Wallets database indexes ensured.")
            await ensure_ledger_indexes(db_manager.db)
            logger.info("Legacy Ledger database indexes ensured.")
    except Exception as e:
        logger.error(f"Startup database connection or index setup failed: {e}")
    yield
    # Shutdown: Close database connection
    await db_manager.close()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# New analytical & agentic routers registered
app.include_router(transactions_router)
app.include_router(risk_router)
app.include_router(analytics_router)
app.include_router(agents_router)

# Legacy routers registered for backward compatibility
app.include_router(users_router)
app.include_router(wallets_router)
app.include_router(ledger_router)

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


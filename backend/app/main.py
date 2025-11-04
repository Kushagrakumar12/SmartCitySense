"""
SmartCitySense Backend - Main Application
FastAPI application setup with routes, middleware, and configuration
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
import structlog
from datetime import datetime

from app.config import settings
from app.utils.logger import setup_logging
from app.routes import auth, events, reports, alerts, summaries, stats, alerts_simple, analytics, sentiments, subscriptions
from app.models.common import HealthCheckResponse, ErrorResponse

# Setup logging
setup_logging()
logger = structlog.get_logger()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    logger.info("Starting SmartCitySense Backend", version=settings.APP_VERSION)
    logger.info("CORS Origins configured", origins=settings.CORS_ORIGINS)
    
    # Initialize Firebase
    try:
        from app.utils.firebase_client import firebase_client
        logger.info("Firebase initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {str(e)}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SmartCitySense Backend")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for SmartCitySense - Live city intelligence platform",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = datetime.utcnow()
    
    # Log request
    logger.info(
        "incoming_request",
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else None
    )
    
    try:
        response = await call_next(request)
        
        # Log response
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_seconds=duration
        )
        
        return response
        
    except Exception as e:
        logger.error(
            "request_failed",
            method=request.method,
            path=request.url.path,
            error=str(e)
        )
        raise


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions"""
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        error=str(exc),
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error",
            detail="An unexpected error occurred"
        ).model_dump()
    )


# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
@limiter.limit("10/minute")
async def health_check(request: Request):
    """
    Health check endpoint
    
    Returns the status of the backend service and its dependencies.
    """
    services = {
        "backend": "healthy",
        "firebase": "unknown",
        "ai_ml": "unknown"
    }
    
    # Check Firebase
    try:
        from app.utils.firebase_client import firebase_client
        db = firebase_client.get_db()
        services["firebase"] = "healthy"
    except:
        services["firebase"] = "unhealthy"
    
    # Check AI/ML service
    try:
        from app.services.ai_client import ai_ml_client
        is_healthy = await ai_ml_client.health_check()
        services["ai_ml"] = "healthy" if is_healthy else "unhealthy"
    except:
        services["ai_ml"] = "unhealthy"
    
    return HealthCheckResponse(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow().isoformat(),
        services=services
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Backend API for SmartCitySense",
        "docs": "/docs",
        "health": "/health"
    }


# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(alerts_simple.router, prefix="/api")  # Use simple alerts instead
# app.include_router(alerts.router, prefix="/api")  # Disabled - requires Firebase indexes
app.include_router(summaries.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(sentiments.router, prefix="/api")
app.include_router(subscriptions.router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

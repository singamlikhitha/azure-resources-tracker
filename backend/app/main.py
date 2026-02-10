"""
Azure Resources Tracker - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

from app.config import get_settings
from app.routers import webhook, resources, health
from app.utils.logger import setup_logging

# Setup logging
setup_logging()
logger = structlog.get_logger()

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("application_starting", version=settings.APP_VERSION)
    yield
    logger.info("application_shutting_down")


# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Automated Azure Resource Group and GitHub Repository Creation via SharePoint",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(webhook.router, prefix="/api/webhook", tags=["Webhook"])
app.include_router(resources.router, prefix="/api/resources", tags=["Resources"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Azure Resources Tracker API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

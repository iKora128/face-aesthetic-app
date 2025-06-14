"""Main FastAPI application with modern Python practices."""

import os
import sys
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.api.v1 import analysis, auth, chat, linebot
from app.config import settings
from app.utils.exceptions import setup_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup
    logger.info("🚀 Starting Face Aesthetic API")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"API Prefix: {settings.api_prefix}")

    # Ensure upload directory exists
    os.makedirs(settings.upload_path, exist_ok=True)
    logger.info(f"Upload directory: {settings.upload_path}")

    # Log configuration
    if settings.debug:
        logger.info("🔧 Debug mode enabled - detailed logging active")

    yield

    # Shutdown
    logger.info("🛑 Shutting down Face Aesthetic API")


def create_application() -> FastAPI:
    """Create FastAPI application with all configurations."""

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="韓国の美意識と黄金比に基づく顔面美容分析AI + ChatGPT相談チャットボット",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )

    # Configure logging
    setup_logging()

    # Add middlewares
    setup_middlewares(app)

    # Setup exception handlers
    setup_exception_handlers(app)

    # Include routers
    setup_routers(app)

    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy", "version": settings.app_version}

    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root() -> dict[str, str]:
        """Root endpoint with API information."""
        return {
            "message": "Face Aesthetic API",
            "version": settings.app_version,
            "docs": "/docs" if settings.debug else "disabled",
        }

    return app


def setup_logging() -> None:
    """Configure application logging."""
    # Remove default logger
    logger.remove()

    # Add console logger
    logger.add(
        sys.stdout,
        format=settings.log_format,
        level=settings.log_level,
        colorize=True,
    )

    # Add file logger for production
    if settings.is_production:
        logger.add(
            "logs/app.log",
            format=settings.log_format,
            level=settings.log_level,
            rotation="500 MB",
            retention="10 days",
            compression="zip",
        )


def setup_middlewares(app: FastAPI) -> None:
    """Setup application middlewares."""

    # Security middleware
    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"],  # Configure this properly in production
        )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )

    # Compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all requests."""
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Log request details
        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )

        return response


def setup_routers(app: FastAPI) -> None:
    """Setup API routers."""
    # API v1 routes
    app.include_router(
        auth.router,
        prefix=f"{settings.api_prefix}/auth",
        tags=["Authentication"],
    )

    app.include_router(
        analysis.router,
        prefix=f"{settings.api_prefix}/analysis",
        tags=["Face Analysis"],
    )

    app.include_router(
        chat.router,
        prefix=f"{settings.api_prefix}/chat",
        tags=["Chatbot"],
    )

    app.include_router(
        linebot.router,
        prefix=f"{settings.api_prefix}/linebot",
        tags=["LINE Bot"],
    )


# Create the application instance
app = create_application()


def main() -> None:
    """Main entry point for the application."""
    logger.info("🎯 Face Aesthetic API - Starting server")

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
        access_log=settings.debug,
    )


if __name__ == "__main__":
    main()
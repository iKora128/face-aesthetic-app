"""Custom exceptions and error handling for Face Aesthetic API."""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from loguru import logger


class FaceAestheticError(Exception):
    """Base exception for Face Aesthetic API."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(FaceAestheticError):
    """Validation error exception."""

    def __init__(
        self,
        message: str = "Validation failed",
        field: str | None = None,
        value: Any = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.get("details", {})
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = value
        super().__init__(message, "VALIDATION_ERROR", details)


class AuthenticationError(FaceAestheticError):
    """Authentication error exception."""

    def __init__(
        self,
        message: str = "Authentication failed",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, "AUTHENTICATION_ERROR", kwargs.get("details"))


class AuthorizationError(FaceAestheticError):
    """Authorization error exception."""

    def __init__(
        self,
        message: str = "Authorization failed",
        required_permission: str | None = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.get("details", {})
        if required_permission:
            details["required_permission"] = required_permission
        super().__init__(message, "AUTHORIZATION_ERROR", details)


class FileUploadError(FaceAestheticError):
    """File upload error exception."""

    def __init__(
        self,
        message: str = "File upload failed",
        filename: str | None = None,
        file_size: int | None = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.get("details", {})
        if filename:
            details["filename"] = filename
        if file_size:
            details["file_size"] = file_size
        super().__init__(message, "FILE_UPLOAD_ERROR", details)


class AnalysisError(FaceAestheticError):
    """Face analysis error exception."""

    def __init__(
        self,
        message: str = "Face analysis failed",
        stage: str | None = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.get("details", {})
        if stage:
            details["analysis_stage"] = stage
        super().__init__(message, "ANALYSIS_ERROR", details)


class ChatbotError(FaceAestheticError):
    """Chatbot service error exception."""

    def __init__(
        self,
        message: str = "Chatbot service failed",
        provider: str | None = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.get("details", {})
        if provider:
            details["provider"] = provider
        super().__init__(message, "CHATBOT_ERROR", details)


class ExternalServiceError(FaceAestheticError):
    """External service error exception."""

    def __init__(
        self,
        message: str = "External service error",
        service: str | None = None,
        status_code: int | None = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.get("details", {})
        if service:
            details["service"] = service
        if status_code:
            details["status_code"] = status_code
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", details)


class DatabaseError(FaceAestheticError):
    """Database operation error exception."""

    def __init__(
        self,
        message: str = "Database operation failed",
        operation: str | None = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.get("details", {})
        if operation:
            details["operation"] = operation
        super().__init__(message, "DATABASE_ERROR", details)


class RateLimitError(FaceAestheticError):
    """Rate limit exceeded error exception."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        limit: int | None = None,
        reset_time: int | None = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.get("details", {})
        if limit:
            details["limit"] = limit
        if reset_time:
            details["reset_time"] = reset_time
        super().__init__(message, "RATE_LIMIT_ERROR", details)


def setup_exception_handlers(app: FastAPI) -> None:
    """Set up global exception handlers for the FastAPI app."""

    @app.exception_handler(FaceAestheticError)
    async def face_aesthetic_error_handler(
        request: Request, exc: FaceAestheticError
    ) -> JSONResponse:
        """Handle custom Face Aesthetic API errors."""
        logger.error(f"Face Aesthetic Error: {exc.message} - Details: {exc.details}")

        # Determine HTTP status code based on error type
        status_code_map = {
            "VALIDATION_ERROR": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "AUTHENTICATION_ERROR": status.HTTP_401_UNAUTHORIZED,
            "AUTHORIZATION_ERROR": status.HTTP_403_FORBIDDEN,
            "FILE_UPLOAD_ERROR": status.HTTP_400_BAD_REQUEST,
            "ANALYSIS_ERROR": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "CHATBOT_ERROR": status.HTTP_503_SERVICE_UNAVAILABLE,
            "EXTERNAL_SERVICE_ERROR": status.HTTP_503_SERVICE_UNAVAILABLE,
            "DATABASE_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "RATE_LIMIT_ERROR": status.HTTP_429_TOO_MANY_REQUESTS,
        }

        status_code = status_code_map.get(
            exc.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR
        )

        return JSONResponse(
            status_code=status_code,
            content={
                "error": True,
                "error_code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
                "request_id": getattr(request.state, "request_id", None),
            },
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        """Handle ValueError exceptions."""
        logger.error(f"Value Error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": True,
                "error_code": "VALUE_ERROR",
                "message": str(exc),
                "details": {},
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle general exceptions."""
        logger.exception(f"Unhandled exception: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": True,
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred",
                "details": {"exception_type": type(exc).__name__},
            },
        )
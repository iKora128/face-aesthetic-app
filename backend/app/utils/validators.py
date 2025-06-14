"""Validation utilities for Face Aesthetic API."""

import re
from typing import Any

from app.utils.exceptions import ValidationError


class ImageValidator:
    """Validator for image uploads."""

    ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/webp"]
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MIN_DIMENSION = 100
    MAX_DIMENSION = 4000

    @classmethod
    def validate_upload(
        cls,
        filename: str | None,
        content_type: str | None,
        file_size: int,
    ) -> None:
        """Validate file upload parameters."""
        # Validate filename
        if not filename:
            raise ValidationError("Filename is required", field="filename")

        if not cls._is_valid_filename(filename):
            raise ValidationError(
                "Invalid filename format", field="filename", value=filename
            )

        # Validate content type
        if not content_type:
            raise ValidationError("Content type is required", field="content_type")

        if content_type not in cls.ALLOWED_MIME_TYPES:
            raise ValidationError(
                f"Unsupported file type. Allowed types: {', '.join(cls.ALLOWED_MIME_TYPES)}",
                field="content_type",
                value=content_type,
            )

        # Validate file size
        if file_size <= 0:
            raise ValidationError("File is empty", field="file_size", value=file_size)

        if file_size > cls.MAX_FILE_SIZE:
            raise ValidationError(
                f"File too large. Maximum size: {cls.MAX_FILE_SIZE // (1024*1024)}MB",
                field="file_size",
                value=file_size,
            )

    @staticmethod
    def _is_valid_filename(filename: str) -> bool:
        """Check if filename is valid."""
        # Basic filename validation
        if len(filename) > 255:
            return False

        # Check for valid extension
        valid_extensions = [".jpg", ".jpeg", ".png", ".webp"]
        if not any(filename.lower().endswith(ext) for ext in valid_extensions):
            return False

        # Check for dangerous characters
        dangerous_chars = ["<", ">", ":", '"', "|", "?", "*", "\\"]
        if any(char in filename for char in dangerous_chars):
            return False

        return True


class UserValidator:
    """Validator for user-related data."""

    @staticmethod
    def validate_email(email: str) -> None:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError("Invalid email format", field="email", value=email)

    @staticmethod
    def validate_password(password: str) -> None:
        """Validate password strength."""
        if len(password) < 8:
            raise ValidationError(
                "Password must be at least 8 characters long",
                field="password",
            )

        if len(password) > 100:
            raise ValidationError(
                "Password must be less than 100 characters",
                field="password",
            )

        # Check for required character types
        checks = [
            (any(c.isupper() for c in password), "uppercase letter"),
            (any(c.islower() for c in password), "lowercase letter"), 
            (any(c.isdigit() for c in password), "digit"),
        ]

        missing = [desc for check, desc in checks if not check]
        if missing:
            raise ValidationError(
                f"Password must contain at least one {', '.join(missing)}",
                field="password",
            )

    @staticmethod
    def validate_full_name(full_name: str) -> None:
        """Validate full name."""
        if not full_name or not full_name.strip():
            raise ValidationError("Full name is required", field="full_name")

        if len(full_name.strip()) < 1:
            raise ValidationError("Full name cannot be empty", field="full_name")

        if len(full_name) > 100:
            raise ValidationError(
                "Full name must be less than 100 characters",
                field="full_name",
                value=full_name,
            )


class AnalysisValidator:
    """Validator for analysis-related data."""

    VALID_ANALYSIS_TYPES = ["full", "basic", "proportions_only", "harmony_only"]
    VALID_CONTEXT_TYPES = ["general", "analysis_review", "beauty_advice", "improvement_plan"]

    @classmethod
    def validate_analysis_type(cls, analysis_type: str) -> None:
        """Validate analysis type."""
        if analysis_type not in cls.VALID_ANALYSIS_TYPES:
            raise ValidationError(
                f"Invalid analysis type. Valid types: {', '.join(cls.VALID_ANALYSIS_TYPES)}",
                field="analysis_type",
                value=analysis_type,
            )

    @classmethod
    def validate_context_type(cls, context_type: str) -> None:
        """Validate chat context type."""
        if context_type not in cls.VALID_CONTEXT_TYPES:
            raise ValidationError(
                f"Invalid context type. Valid types: {', '.join(cls.VALID_CONTEXT_TYPES)}",
                field="context_type",
                value=context_type,
            )

    @staticmethod
    def validate_user_notes(user_notes: str | None) -> None:
        """Validate user notes."""
        if user_notes is not None:
            if len(user_notes) > 500:
                raise ValidationError(
                    "User notes must be less than 500 characters",
                    field="user_notes",
                    value=user_notes,
                )

    @staticmethod
    def validate_chat_message(message: str) -> None:
        """Validate chat message content."""
        if not message or not message.strip():
            raise ValidationError("Message cannot be empty", field="message")

        if len(message) > 2000:
            raise ValidationError(
                "Message must be less than 2000 characters",
                field="message",
                value=message,
            )

    @staticmethod
    def validate_session_title(title: str | None) -> None:
        """Validate chat session title."""
        if title is not None:
            if len(title) > 200:
                raise ValidationError(
                    "Session title must be less than 200 characters",
                    field="title",
                    value=title,
                )
"""User models using modern Pydantic v2 practices."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Base user model with common fields."""

    email: EmailStr = Field(description="User email address")
    full_name: str = Field(min_length=1, max_length=100, description="Full name")
    is_active: bool = Field(default=True, description="User active status")


class UserCreate(UserBase):
    """User creation model."""

    password: str = Field(
        min_length=8, max_length=100, description="User password"
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            msg = "Password must contain at least one uppercase letter"
            raise ValueError(msg)
        if not any(c.islower() for c in v):
            msg = "Password must contain at least one lowercase letter"
            raise ValueError(msg)
        if not any(c.isdigit() for c in v):
            msg = "Password must contain at least one digit"
            raise ValueError(msg)
        return v


class UserUpdate(BaseModel):
    """User update model with optional fields."""

    full_name: str | None = Field(
        default=None, min_length=1, max_length=100, description="Full name"
    )
    is_active: bool | None = Field(default=None, description="User active status")


class UserProfile(BaseModel):
    """Extended user profile information."""

    model_config = ConfigDict(from_attributes=True)

    bio: str | None = Field(default=None, max_length=500, description="User bio")
    avatar_url: str | None = Field(default=None, description="Avatar image URL")
    date_of_birth: datetime | None = Field(
        default=None, description="Date of birth"
    )
    gender: str | None = Field(
        default=None, 
        pattern=r"^(male|female|other|prefer_not_to_say)$",
        description="Gender"
    )
    location: str | None = Field(
        default=None, max_length=100, description="Location"
    )
    preferences: dict[str, Any] = Field(
        default_factory=dict, description="User preferences"
    )


class User(UserBase):
    """Complete user model with all fields."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(description="User unique identifier")
    created_at: datetime = Field(description="User creation timestamp")
    updated_at: datetime = Field(description="User last update timestamp")
    last_login: datetime | None = Field(
        default=None, description="Last login timestamp"
    )
    email_verified: bool = Field(default=False, description="Email verification status")
    analysis_count: int = Field(default=0, description="Number of analyses performed")
    subscription_tier: str = Field(
        default="free", description="User subscription tier"
    )
    profile: UserProfile | None = Field(default=None, description="User profile")


class UserInDB(User):
    """User model as stored in database (includes sensitive data)."""

    hashed_password: str = Field(description="Hashed password")


class UserPublic(BaseModel):
    """Public user information (safe for external exposure)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(description="User unique identifier")
    full_name: str = Field(description="Full name")
    avatar_url: str | None = Field(default=None, description="Avatar image URL")
    created_at: datetime = Field(description="User creation timestamp")
    analysis_count: int = Field(description="Number of analyses performed")


class UserStats(BaseModel):
    """User statistics and analytics."""

    model_config = ConfigDict(from_attributes=True)

    total_analyses: int = Field(description="Total number of analyses")
    average_score: float | None = Field(
        default=None, description="Average beauty score"
    )
    last_analysis: datetime | None = Field(
        default=None, description="Last analysis timestamp"
    )
    favorite_features: list[str] = Field(
        default_factory=list, description="Most analyzed features"
    )
    improvement_trends: dict[str, Any] = Field(
        default_factory=dict, description="Score improvement trends"
    )
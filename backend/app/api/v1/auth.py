"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.models.user import User, UserCreate, UserPublic
from app.utils.exceptions import AuthenticationError

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate) -> UserPublic:
    """Register a new user."""
    # TODO: Implement user registration with Supabase
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Registration endpoint not yet implemented"
    )


@router.post("/login")
async def login_user(email: str, password: str) -> dict[str, str]:
    """Authenticate user and return tokens."""
    # TODO: Implement user login with Supabase
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Login endpoint not yet implemented"
    )


@router.post("/logout")
async def logout_user() -> dict[str, str]:
    """Logout user."""
    # TODO: Implement user logout
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=User)
async def get_current_user() -> User:
    """Get current authenticated user."""
    # TODO: Implement get current user
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get current user endpoint not yet implemented"
    )


@router.post("/refresh")
async def refresh_token() -> dict[str, str]:
    """Refresh access token."""
    # TODO: Implement token refresh
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token refresh endpoint not yet implemented"
    )
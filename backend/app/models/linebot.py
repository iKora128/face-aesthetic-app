"""LINE Bot Pydantic models."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class LineBotUser(BaseModel):
    """LINE Bot user model."""

    id: UUID
    line_user_id: str = Field(..., description="LINE user ID")
    user_id: Optional[UUID] = Field(None, description="Internal user ID")
    display_name: Optional[str] = Field(None, description="Display name")
    picture_url: Optional[str] = Field(None, description="Profile picture URL")
    status_message: Optional[str] = Field(None, description="Status message")
    language: str = Field(default="ja", description="User language")
    is_active: bool = Field(default=True, description="Is user active")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_interaction_at: Optional[datetime] = Field(None, description="Last interaction")


class LineBotUserCreate(BaseModel):
    """LINE Bot user creation model."""

    line_user_id: str
    display_name: Optional[str] = None
    picture_url: Optional[str] = None
    status_message: Optional[str] = None
    language: str = "ja"


class LineBotUserUpdate(BaseModel):
    """LINE Bot user update model."""

    display_name: Optional[str] = None
    picture_url: Optional[str] = None
    status_message: Optional[str] = None
    language: Optional[str] = None
    is_active: Optional[bool] = None


class LineBotAnalysisRequest(BaseModel):
    """LINE Bot analysis request model."""

    line_user_id: str = Field(..., description="LINE user ID")
    image_url: str = Field(..., description="Image URL from LINE")
    message_id: str = Field(..., description="LINE message ID")
    analysis_type: str = Field(default="full", description="Analysis type")


class LineBotResponse(BaseModel):
    """LINE Bot response model."""

    response_type: str = Field(..., description="Response type (text, image, carousel)")
    text: Optional[str] = Field(None, description="Text response")
    image_url: Optional[str] = Field(None, description="Image URL")
    quick_replies: Optional[list[str]] = Field(None, description="Quick reply options")
    carousel_items: Optional[list[dict]] = Field(None, description="Carousel items")


class LineBotWebhookEvent(BaseModel):
    """LINE Bot webhook event model."""

    type: str = Field(..., description="Event type")
    message: Optional[dict] = Field(None, description="Message data")
    source: dict = Field(..., description="Event source")
    timestamp: int = Field(..., description="Event timestamp")
    mode: str = Field(..., description="Channel mode")
    webhook_event_id: str = Field(..., description="Webhook event ID")
    delivery_context: dict = Field(..., description="Delivery context")


class LineBotTextMessage(BaseModel):
    """LINE Bot text message model."""

    text: str = Field(..., description="Message text")
    emojis: Optional[list[dict]] = Field(None, description="Emojis in message")


class LineBotImageMessage(BaseModel):
    """LINE Bot image message model."""

    id: str = Field(..., description="Message ID")
    content_provider: dict = Field(..., description="Content provider info")
    image_set: Optional[dict] = Field(None, description="Image set info")


class LineBotQuickReply(BaseModel):
    """LINE Bot quick reply model."""

    items: list[dict] = Field(..., description="Quick reply items")


class LineBotFlexMessage(BaseModel):
    """LINE Bot flex message model."""

    alt_text: str = Field(..., description="Alternative text")
    contents: dict = Field(..., description="Flex message contents")


class LineBotCarouselTemplate(BaseModel):
    """LINE Bot carousel template model."""

    type: str = Field(default="carousel", description="Template type")
    columns: list[dict] = Field(..., description="Carousel columns")


class LineBotButtonTemplate(BaseModel):
    """LINE Bot button template model."""

    type: str = Field(default="buttons", description="Template type")
    thumbnail_image_url: Optional[str] = Field(None, description="Thumbnail image URL")
    image_aspect_ratio: Optional[str] = Field(None, description="Image aspect ratio")
    image_size: Optional[str] = Field(None, description="Image size")
    image_background_color: Optional[str] = Field(None, description="Image background color")
    title: Optional[str] = Field(None, description="Title")
    text: str = Field(..., description="Text")
    default_action: Optional[dict] = Field(None, description="Default action")
    actions: list[dict] = Field(..., description="Actions")
"""Chat and chatbot models using modern Pydantic v2 practices."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ChatMessage(BaseModel):
    """Individual chat message model."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(description="Message unique identifier")
    session_id: UUID = Field(description="Chat session identifier")
    role: str = Field(
        pattern=r"^(user|assistant|system)$",
        description="Message role (user, assistant, system)"
    )
    content: str = Field(min_length=1, description="Message content")
    created_at: datetime = Field(description="Message creation timestamp")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional message metadata"
    )
    analysis_reference: UUID | None = Field(
        default=None, description="Referenced analysis ID if applicable"
    )


class ChatRequest(BaseModel):
    """Chat request from user."""

    message: str = Field(
        min_length=1, max_length=2000, description="User message content"
    )
    session_id: UUID | None = Field(
        default=None, description="Existing session ID (if any)"
    )
    analysis_id: UUID | None = Field(
        default=None, description="Analysis ID for context"
    )
    context_type: str = Field(
        default="general",
        pattern=r"^(general|analysis_review|beauty_advice|improvement_plan)$",
        description="Type of conversation context"
    )
    include_analysis_data: bool = Field(
        default=True, description="Whether to include analysis data in context"
    )


class ChatResponse(BaseModel):
    """Chat response from assistant."""

    message: str = Field(description="Assistant response message")
    session_id: UUID = Field(description="Chat session identifier")
    message_id: UUID = Field(description="Response message identifier")
    suggestions: list[str] = Field(
        default_factory=list, description="Suggested follow-up questions"
    )
    analysis_insights: dict[str, Any] = Field(
        default_factory=dict, description="Analysis-based insights"
    )
    beauty_tips: list[str] = Field(
        default_factory=list, description="Personalized beauty tips"
    )
    created_at: datetime = Field(description="Response creation timestamp")


class ChatSession(BaseModel):
    """Chat session model."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(description="Session unique identifier")
    user_id: UUID = Field(description="User identifier")
    title: str = Field(description="Session title/summary")
    context_type: str = Field(description="Session context type")
    analysis_id: UUID | None = Field(
        default=None, description="Primary analysis being discussed"
    )
    created_at: datetime = Field(description="Session creation timestamp")
    updated_at: datetime = Field(description="Session last update timestamp")
    message_count: int = Field(default=0, description="Number of messages in session")
    is_active: bool = Field(default=True, description="Session active status")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Session metadata"
    )


class ChatSessionCreate(BaseModel):
    """Chat session creation model."""

    title: str | None = Field(
        default=None, max_length=200, description="Session title"
    )
    context_type: str = Field(
        default="general",
        pattern=r"^(general|analysis_review|beauty_advice|improvement_plan)$",
        description="Session context type"
    )
    analysis_id: UUID | None = Field(
        default=None, description="Analysis ID for context"
    )
    initial_message: str | None = Field(
        default=None, max_length=2000, description="Initial user message"
    )


class ChatSessionSummary(BaseModel):
    """Chat session summary for listing."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(description="Session identifier")
    title: str = Field(description="Session title")
    context_type: str = Field(description="Session context type")
    message_count: int = Field(description="Number of messages")
    last_message_at: datetime = Field(description="Last message timestamp")
    created_at: datetime = Field(description="Session creation timestamp")
    analysis_score: float | None = Field(
        default=None, description="Related analysis score if applicable"
    )


class ConversationContext(BaseModel):
    """Context data for improving conversation quality."""

    user_name: str | None = Field(default=None, description="User's preferred name")
    analysis_summary: dict[str, Any] = Field(
        default_factory=dict, description="Key analysis insights"
    )
    beauty_goals: list[str] = Field(
        default_factory=list, description="User's beauty goals"
    )
    previous_advice: list[str] = Field(
        default_factory=list, description="Previously given advice"
    )
    improvement_areas: list[str] = Field(
        default_factory=list, description="Areas user wants to improve"
    )
    session_history: list[dict[str, Any]] = Field(
        default_factory=list, description="Recent session summaries"
    )


class ChatAnalytics(BaseModel):
    """Chat session analytics and insights."""

    model_config = ConfigDict(from_attributes=True)

    total_sessions: int = Field(description="Total number of chat sessions")
    total_messages: int = Field(description="Total number of messages")
    average_session_length: float = Field(description="Average messages per session")
    most_discussed_topics: list[str] = Field(
        description="Most frequently discussed topics"
    )
    user_satisfaction_indicators: dict[str, Any] = Field(
        description="Satisfaction metrics"
    )
    common_questions: list[str] = Field(description="Frequently asked questions")
    improvement_tracking: dict[str, Any] = Field(
        description="User improvement progress"
    )
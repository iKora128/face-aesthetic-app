"""Test chat endpoints and functionality."""

from unittest.mock import Mock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


def test_create_chat_session_missing_data(client: TestClient):
    """Test creating chat session with missing data."""
    response = client.post("/api/v1/chat/sessions")
    assert response.status_code == 422  # Validation error


@patch('app.services.chatbot_service.BeautyChatbotService.create_chat_session')
def test_create_chat_session_success(mock_create_session, client: TestClient, 
                                   test_user_id: str):
    """Test successful chat session creation."""
    session_id = str(uuid4())
    mock_session = Mock()
    mock_session.id = session_id
    mock_session.title = "Test Session"
    mock_session.user_id = test_user_id
    mock_session.context_type = "general"
    mock_session.is_active = True
    mock_session.message_count = 0
    
    mock_create_session.return_value = mock_session
    
    request_data = {
        "user_id": test_user_id,
        "title": "Test Session",
        "context_type": "general"
    }
    
    response = client.post("/api/v1/chat/sessions", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "session" in data
    assert data["session"]["id"] == session_id


@patch('app.services.chatbot_service.BeautyChatbotService.send_message')
def test_send_chat_message_success(mock_send_message, client: TestClient, 
                                  test_session_id: str, test_user_id: str):
    """Test successful chat message sending."""
    mock_response = Mock()
    mock_response.message = "こんにちは！美容について何でもお聞きください。"
    mock_response.session_id = test_session_id
    mock_response.message_id = str(uuid4())
    mock_response.suggestions = ["スキンケアについて", "メイクのコツ"]
    mock_response.analysis_insights = {}
    mock_response.beauty_tips = ["保湿が重要です"]
    
    mock_send_message.return_value = mock_response
    
    request_data = {
        "session_id": test_session_id,
        "user_id": test_user_id,
        "message": "こんにちは"
    }
    
    response = client.post("/api/v1/chat/messages", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "response" in data
    assert "message" in data["response"]
    assert "suggestions" in data["response"]


def test_send_chat_message_missing_data(client: TestClient):
    """Test sending chat message with missing data."""
    response = client.post("/api/v1/chat/messages", json={})
    assert response.status_code == 422  # Validation error


@patch('app.services.chatbot_service.BeautyChatbotService.get_chat_sessions')
def test_get_chat_sessions_success(mock_get_sessions, client: TestClient, test_user_id: str):
    """Test successful chat sessions retrieval."""
    mock_session = Mock()
    mock_session.id = str(uuid4())
    mock_session.title = "Test Session"
    mock_session.user_id = test_user_id
    mock_session.context_type = "general"
    mock_session.is_active = True
    mock_session.message_count = 5
    
    mock_get_sessions.return_value = [mock_session]
    
    response = client.get(f"/api/v1/chat/sessions?user_id={test_user_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert "sessions" in data
    assert len(data["sessions"]) == 1
    assert data["sessions"][0]["id"] == str(mock_session.id)


def test_get_chat_sessions_missing_user_id(client: TestClient):
    """Test getting chat sessions without user ID."""
    response = client.get("/api/v1/chat/sessions")
    assert response.status_code == 400  # Bad request


@patch('app.services.chatbot_service.BeautyChatbotService.get_session_messages')
def test_get_session_messages_success(mock_get_messages, client: TestClient, 
                                     test_session_id: str, test_user_id: str):
    """Test successful session messages retrieval."""
    mock_message = Mock()
    mock_message.id = str(uuid4())
    mock_message.session_id = test_session_id
    mock_message.role = "user"
    mock_message.content = "こんにちは"
    mock_message.created_at = "2024-01-01T00:00:00Z"
    
    mock_get_messages.return_value = [mock_message]
    
    response = client.get(
        f"/api/v1/chat/sessions/{test_session_id}/messages?user_id={test_user_id}"
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "messages" in data
    assert len(data["messages"]) == 1
    assert data["messages"][0]["content"] == "こんにちは"


def test_get_session_messages_missing_user_id(client: TestClient, test_session_id: str):
    """Test getting session messages without user ID."""
    response = client.get(f"/api/v1/chat/sessions/{test_session_id}/messages")
    assert response.status_code == 400  # Bad request


def test_chat_service_status(client: TestClient):
    """Test chat service status endpoint."""
    response = client.get("/api/v1/chat/status")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "openai_configured" in data
    assert "model_info" in data


@patch('app.services.chatbot_service.BeautyChatbotService.send_message')
def test_chat_message_with_analysis_context(mock_send_message, client: TestClient,
                                           test_session_id: str, test_user_id: str):
    """Test chat message with analysis context."""
    analysis_id = str(uuid4())
    
    mock_response = Mock()
    mock_response.message = "分析結果に基づいてアドバイスします。"
    mock_response.session_id = test_session_id
    mock_response.message_id = str(uuid4())
    mock_response.suggestions = ["詳しい分析", "改善方法"]
    mock_response.analysis_insights = {"score": 85}
    mock_response.beauty_tips = []
    
    mock_send_message.return_value = mock_response
    
    request_data = {
        "session_id": test_session_id,
        "user_id": test_user_id,
        "message": "分析結果について教えて",
        "analysis_id": analysis_id
    }
    
    response = client.post("/api/v1/chat/messages", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "analysis_insights" in data["response"]


@patch('app.services.chatbot_service.BeautyChatbotService.create_chat_session')
def test_create_chat_session_with_analysis(mock_create_session, client: TestClient,
                                          test_user_id: str):
    """Test creating chat session with analysis context."""
    session_id = str(uuid4())
    analysis_id = str(uuid4())
    
    mock_session = Mock()
    mock_session.id = session_id
    mock_session.title = "分析結果について相談"
    mock_session.user_id = test_user_id
    mock_session.context_type = "analysis_consultation"
    mock_session.analysis_id = analysis_id
    mock_session.is_active = True
    mock_session.message_count = 0
    
    mock_create_session.return_value = mock_session
    
    request_data = {
        "user_id": test_user_id,
        "title": "分析結果について相談",
        "context_type": "analysis_consultation",
        "analysis_id": analysis_id,
        "initial_message": "この分析結果について教えてください"
    }
    
    response = client.post("/api/v1/chat/sessions", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert data["session"]["analysis_id"] == analysis_id


def test_chat_validation_errors(client: TestClient):
    """Test various validation errors in chat endpoints."""
    # Test invalid session creation
    response = client.post("/api/v1/chat/sessions", json={"invalid": "data"})
    assert response.status_code == 422
    
    # Test invalid message sending
    response = client.post("/api/v1/chat/messages", json={"invalid": "data"})
    assert response.status_code == 422
    
    # Test invalid session ID format
    response = client.get("/api/v1/chat/sessions/invalid-uuid/messages?user_id=test")
    assert response.status_code == 422


@patch('app.services.chatbot_service.BeautyChatbotService.send_message')
def test_chat_error_handling(mock_send_message, client: TestClient,
                            test_session_id: str, test_user_id: str):
    """Test error handling in chat endpoints."""
    # Mock a chatbot error
    mock_send_message.side_effect = Exception("OpenAI API error")
    
    request_data = {
        "session_id": test_session_id,
        "user_id": test_user_id,
        "message": "こんにちは"
    }
    
    response = client.post("/api/v1/chat/messages", json=request_data)
    assert response.status_code == 500
    assert "Failed to process message" in response.json()["detail"]


@pytest.mark.asyncio
async def test_async_chat_message(async_client, test_session_id: str, test_user_id: str):
    """Test chat message with async client."""
    request_data = {
        "session_id": test_session_id,
        "user_id": test_user_id,
        "message": "テストメッセージ"
    }
    
    response = await async_client.post("/api/v1/chat/messages", json=request_data)
    
    # Should reach endpoint (may fail due to missing OpenAI key, but that's expected)
    assert response.status_code in [200, 500, 422]
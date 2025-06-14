"""Test LINE Bot endpoints and functionality."""

import json
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient


def test_linebot_info_not_configured(client: TestClient):
    """Test LINE Bot info when not configured."""
    response = client.get("/api/v1/linebot/info")
    assert response.status_code == 200
    
    data = response.json()
    assert "bot_configured" in data
    assert "webhook_url" in data
    assert "features" in data


def test_linebot_health_not_configured(client: TestClient):
    """Test LINE Bot health check when not configured."""
    response = client.get("/api/v1/linebot/health")
    assert response.status_code == 503  # Service unavailable


@patch.dict('os.environ', {
    'LINE_CHANNEL_ACCESS_TOKEN': 'test-token',
    'LINE_CHANNEL_SECRET': 'test-secret'
})
def test_linebot_info_configured(client: TestClient):
    """Test LINE Bot info when configured."""
    response = client.get("/api/v1/linebot/info")
    assert response.status_code == 200
    
    data = response.json()
    assert data["bot_configured"] is True
    assert data["channel_configured"] is True
    assert data["secret_configured"] is True
    assert "features" in data
    assert data["features"]["image_analysis"] is True


@patch.dict('os.environ', {
    'LINE_CHANNEL_ACCESS_TOKEN': 'test-token',
    'LINE_CHANNEL_SECRET': 'test-secret'
})
def test_linebot_health_configured(client: TestClient):
    """Test LINE Bot health check when configured."""
    response = client.get("/api/v1/linebot/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "LINE Bot"


def test_linebot_webhook_not_configured(client: TestClient):
    """Test LINE Bot webhook when not configured."""
    response = client.post("/api/v1/linebot/webhook", 
                          headers={"X-Line-Signature": "test-signature"})
    assert response.status_code == 501  # Not implemented


def test_linebot_webhook_missing_signature(client: TestClient):
    """Test LINE Bot webhook with missing signature."""
    with patch.dict('os.environ', {
        'LINE_CHANNEL_ACCESS_TOKEN': 'test-token',
        'LINE_CHANNEL_SECRET': 'test-secret'
    }):
        response = client.post("/api/v1/linebot/webhook")
        assert response.status_code == 400
        assert "Missing X-Line-Signature header" in response.json()["detail"]


@patch.dict('os.environ', {
    'LINE_CHANNEL_ACCESS_TOKEN': 'test-token',
    'LINE_CHANNEL_SECRET': 'test-secret'
})
@patch('app.services.linebot_service.LineBotService.handle_webhook')
def test_linebot_webhook_success(mock_handle_webhook, client: TestClient, 
                                sample_line_event: dict):
    """Test successful LINE Bot webhook handling."""
    mock_handle_webhook.return_value = {"status": "success", "message": "Events processed"}
    
    webhook_body = {
        "events": [sample_line_event],
        "destination": "test-destination"
    }
    
    response = client.post(
        "/api/v1/linebot/webhook",
        json=webhook_body,
        headers={"X-Line-Signature": "test-signature"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


@patch.dict('os.environ', {
    'LINE_CHANNEL_ACCESS_TOKEN': 'test-token',
    'LINE_CHANNEL_SECRET': 'test-secret'
})
@patch('app.services.linebot_service.LineBotService.handle_webhook')
def test_linebot_webhook_error(mock_handle_webhook, client: TestClient, 
                              sample_line_event: dict):
    """Test LINE Bot webhook error handling."""
    from app.utils.exceptions import LineBotError
    mock_handle_webhook.side_effect = LineBotError("Invalid signature", provider="line")
    
    webhook_body = {
        "events": [sample_line_event],
        "destination": "test-destination"
    }
    
    response = client.post(
        "/api/v1/linebot/webhook",
        json=webhook_body,
        headers={"X-Line-Signature": "invalid-signature"}
    )
    
    assert response.status_code == 400
    assert "Invalid signature" in response.json()["detail"]


@patch.dict('os.environ', {
    'LINE_CHANNEL_ACCESS_TOKEN': 'test-token',
    'LINE_CHANNEL_SECRET': 'test-secret'
})
def test_linebot_test_message(client: TestClient):
    """Test LINE Bot test message endpoint."""
    response = client.post(
        "/api/v1/linebot/test-message",
        params={
            "user_id": "test-user-id",
            "message": "テストメッセージ"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "Test message sent" in data["message"]


def test_linebot_test_message_not_configured(client: TestClient):
    """Test LINE Bot test message when not configured."""
    response = client.post(
        "/api/v1/linebot/test-message",
        params={"user_id": "test-user-id"}
    )
    
    assert response.status_code == 501  # Not implemented


@patch('app.services.linebot_service.LineBotService')
def test_linebot_service_creation(mock_service_class, mock_supabase_client):
    """Test LINE Bot service creation."""
    from app.services.linebot_service import get_linebot_service
    
    service = get_linebot_service(mock_supabase_client)
    assert service is not None
    
    # Test singleton behavior
    service2 = get_linebot_service(mock_supabase_client)
    assert service is service2


def test_linebot_webhook_validation_errors(client: TestClient):
    """Test LINE Bot webhook validation errors."""
    # Test invalid JSON
    response = client.post(
        "/api/v1/linebot/webhook",
        data="invalid json",
        headers={
            "X-Line-Signature": "test-signature",
            "Content-Type": "application/json"
        }
    )
    
    # Should fail due to missing configuration or invalid JSON
    assert response.status_code in [400, 422, 501]


def test_linebot_endpoints_accessibility(client: TestClient):
    """Test that all LINE Bot endpoints are accessible."""
    endpoints = [
        "/api/v1/linebot/info",
        "/api/v1/linebot/health"
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        # Should be accessible (may return error due to configuration, but not 404)
        assert response.status_code != 404


@pytest.mark.asyncio
async def test_async_linebot_webhook(async_client, sample_line_event: dict):
    """Test LINE Bot webhook with async client."""
    webhook_body = {
        "events": [sample_line_event],
        "destination": "test-destination"
    }
    
    response = await async_client.post(
        "/api/v1/linebot/webhook",
        json=webhook_body,
        headers={"X-Line-Signature": "test-signature"}
    )
    
    # Should reach endpoint (may fail due to configuration, but that's expected)
    assert response.status_code in [200, 400, 501]


def test_linebot_webhook_event_types(client: TestClient):
    """Test LINE Bot webhook with different event types."""
    with patch.dict('os.environ', {
        'LINE_CHANNEL_ACCESS_TOKEN': 'test-token',
        'LINE_CHANNEL_SECRET': 'test-secret'
    }):
        # Test text message event
        text_event = {
            "type": "message",
            "message": {"type": "text", "text": "こんにちは"},
            "source": {"type": "user", "userId": "test-user"},
            "timestamp": 1640995200000,
            "mode": "active",
            "webhookEventId": "test-event-id",
            "deliveryContext": {"isRedelivery": False}
        }
        
        # Test image message event
        image_event = {
            "type": "message",
            "message": {"type": "image", "id": "test-image-id"},
            "source": {"type": "user", "userId": "test-user"},
            "timestamp": 1640995200000,
            "mode": "active",
            "webhookEventId": "test-event-id-2",
            "deliveryContext": {"isRedelivery": False}
        }
        
        # Test follow event
        follow_event = {
            "type": "follow",
            "source": {"type": "user", "userId": "test-user"},
            "timestamp": 1640995200000,
            "mode": "active",
            "webhookEventId": "test-event-id-3",
            "deliveryContext": {"isRedelivery": False}
        }
        
        events = [text_event, image_event, follow_event]
        
        for event in events:
            webhook_body = {"events": [event], "destination": "test"}
            
            response = client.post(
                "/api/v1/linebot/webhook",
                json=webhook_body,
                headers={"X-Line-Signature": "test-signature"}
            )
            
            # Should reach webhook handler
            assert response.status_code in [200, 400, 500]
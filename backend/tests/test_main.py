"""Test main application endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "timestamp" in data


def test_root_endpoint(client: TestClient):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "Face Aesthetic AI" in data["message"]


def test_api_info(client: TestClient):
    """Test API info endpoint."""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    
    data = response.json()
    assert data["app_name"] == "Face Aesthetic AI Backend"
    assert "version" in data
    assert "environment" in data


def test_cors_headers(client: TestClient):
    """Test CORS headers are present."""
    response = client.options("/api/v1/", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET"
    })
    
    # CORS preflight should return 200
    assert response.status_code == 200
    
    # Check CORS headers in actual request
    response = client.get("/api/v1/", headers={
        "Origin": "http://localhost:3000"
    })
    
    assert "access-control-allow-origin" in response.headers


def test_not_found_endpoint(client: TestClient):
    """Test 404 for non-existent endpoint."""
    response = client.get("/non-existent-endpoint")
    assert response.status_code == 404


def test_method_not_allowed(client: TestClient):
    """Test 405 for wrong HTTP method."""
    response = client.post("/health")
    assert response.status_code == 405


@pytest.mark.asyncio
async def test_async_health_check(async_client):
    """Test health check with async client."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
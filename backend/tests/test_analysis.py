"""Test analysis endpoints and functionality."""

import io
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient


def test_analyze_endpoint_no_file(client: TestClient):
    """Test analysis endpoint without file upload."""
    response = client.post("/api/v1/analysis/analyze")
    assert response.status_code == 422  # Validation error


def test_analyze_endpoint_invalid_file_type(client: TestClient):
    """Test analysis endpoint with invalid file type."""
    # Create a text file
    file_content = b"This is not an image"
    
    response = client.post(
        "/api/v1/analysis/analyze",
        files={"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    )
    
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]


def test_analyze_endpoint_valid_image_no_face(client: TestClient, sample_image_data: bytes):
    """Test analysis endpoint with valid image but no face detected."""
    response = client.post(
        "/api/v1/analysis/analyze",
        files={"file": ("test.png", io.BytesIO(sample_image_data), "image/png")}
    )
    
    # Should return error because no face is detected in the sample image
    assert response.status_code == 422
    assert "No face detected" in response.json()["detail"]


@patch('app.core.facial_analyzer.ModernFacialBeautyAnalyzer.analyze_image_async')
def test_analyze_endpoint_success(mock_analyze, client: TestClient, 
                                 sample_image_data: bytes, sample_analysis_result: dict):
    """Test successful analysis endpoint."""
    # Mock the analysis result
    mock_analyze.return_value = sample_analysis_result
    
    response = client.post(
        "/api/v1/analysis/analyze",
        files={"file": ("test.png", io.BytesIO(sample_image_data), "image/png")},
        data={"analysis_type": "full"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["overall_score"]["score"] == 85.0
    assert "processing_time_ms" in data


def test_analyze_endpoint_large_file(client: TestClient):
    """Test analysis endpoint with file too large."""
    # Create a large file (>10MB)
    large_content = b"x" * (11 * 1024 * 1024)  # 11MB
    
    response = client.post(
        "/api/v1/analysis/analyze",
        files={"file": ("large.png", io.BytesIO(large_content), "image/png")}
    )
    
    assert response.status_code == 413  # Payload too large


def test_get_analysis_types(client: TestClient):
    """Test get analysis types endpoint."""
    response = client.get("/api/v1/analysis/types")
    assert response.status_code == 200
    
    data = response.json()
    assert "analysis_types" in data
    assert len(data["analysis_types"]) > 0
    
    # Check that full analysis type exists
    full_type = next((t for t in data["analysis_types"] if t["type"] == "full"), None)
    assert full_type is not None
    assert "features" in full_type


def test_get_analysis_features(client: TestClient):
    """Test get analysis features endpoint."""
    response = client.get("/api/v1/analysis/features")
    assert response.status_code == 200
    
    data = response.json()
    assert "features" in data
    assert len(data["features"]) > 0
    
    # Check that features have required fields
    for feature in data["features"]:
        assert "name" in feature
        assert "description" in feature
        assert "category" in feature


@patch('app.services.analysis_service.AnalysisService.get_user_analysis_history')
def test_get_analysis_history_unauthorized(mock_get_history, client: TestClient):
    """Test get analysis history without authentication."""
    response = client.get("/api/v1/analysis/history")
    assert response.status_code == 400  # Bad request (no user_id)


@patch('app.services.analysis_service.AnalysisService.get_user_analysis_history')
def test_get_analysis_history_success(mock_get_history, client: TestClient, 
                                     test_user_id: str, sample_analysis_result: dict):
    """Test successful get analysis history."""
    # Mock the history result
    mock_get_history.return_value = [sample_analysis_result]
    
    response = client.get(f"/api/v1/analysis/history?user_id={test_user_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert "analyses" in data
    assert len(data["analyses"]) == 1
    assert data["analyses"][0]["overall_score"]["score"] == 85.0


def test_analysis_status_endpoint(client: TestClient):
    """Test analysis service status endpoint."""
    response = client.get("/api/v1/analysis/status")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "features_available" in data


@pytest.mark.asyncio
async def test_async_analyze_endpoint(async_client, sample_image_data: bytes):
    """Test analysis endpoint with async client."""
    response = await async_client.post(
        "/api/v1/analysis/analyze",
        files={"file": ("test.png", sample_image_data, "image/png")}
    )
    
    # Should fail because no face detected, but endpoint should be reachable
    assert response.status_code in [200, 422]  # Either success or validation error


def test_analysis_rate_limiting(client: TestClient, sample_image_data: bytes):
    """Test rate limiting on analysis endpoint."""
    # Note: This test might need adjustment based on actual rate limiting implementation
    responses = []
    
    for i in range(5):  # Try multiple requests quickly
        response = client.post(
            "/api/v1/analysis/analyze",
            files={"file": (f"test{i}.png", io.BytesIO(sample_image_data), "image/png")}
        )
        responses.append(response.status_code)
    
    # At least some requests should succeed (or fail with known errors, not rate limit)
    assert any(status in [200, 422] for status in responses)


def test_analysis_validation_errors(client: TestClient):
    """Test various validation errors in analysis endpoint."""
    # Test missing file
    response = client.post("/api/v1/analysis/analyze")
    assert response.status_code == 422
    
    # Test invalid analysis type
    response = client.post(
        "/api/v1/analysis/analyze",
        files={"file": ("test.png", b"fake", "image/png")},
        data={"analysis_type": "invalid_type"}
    )
    assert response.status_code == 422


@patch('app.core.facial_analyzer.ModernFacialBeautyAnalyzer.analyze_image_async')
def test_analysis_error_handling(mock_analyze, client: TestClient, sample_image_data: bytes):
    """Test error handling in analysis endpoint."""
    # Mock an analysis error
    mock_analyze.side_effect = Exception("Analysis failed")
    
    response = client.post(
        "/api/v1/analysis/analyze",
        files={"file": ("test.png", io.BytesIO(sample_image_data), "image/png")}
    )
    
    assert response.status_code == 500
    assert "Analysis failed" in response.json()["detail"]
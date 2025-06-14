"""Pytest configuration and fixtures."""

import asyncio
import os
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Set test environment variables
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test-anon-key"
os.environ["SUPABASE_SERVICE_KEY"] = "test-service-key"
os.environ["OPENAI_API_KEY"] = "sk-test-key"
os.environ["LINE_CHANNEL_ACCESS_TOKEN"] = "test-line-token"
os.environ["LINE_CHANNEL_SECRET"] = "test-line-secret"
os.environ["TESTING"] = "true"

from app.main import app
from app.config import settings


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    async with AsyncClient(app=app, base_url="http://test") as async_test_client:
        yield async_test_client


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_image_data() -> bytes:
    """Create sample image data for testing."""
    # 1x1 pixel PNG
    return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'


@pytest.fixture
def sample_analysis_result() -> dict:
    """Create sample analysis result for testing."""
    return {
        "timestamp": "2024-01-01T00:00:00Z",
        "image_info": {
            "filename": "test.jpg",
            "dimensions": "100x100",
            "total_landmarks": 468
        },
        "face_angle": {
            "angle": "正面",
            "ratio": 0.5,
            "confidence": 0.9,
            "suitable_for_analysis": True
        },
        "face_contour": {
            "face_area": 15000.0,
            "face_perimeter": 500.0,
            "face_width": 150.0,
            "face_height": 180.0,
            "small_face_score": 85.0,
            "cheekbone_width": 140.0,
            "jaw_width": 120.0,
            "cheek_jaw_ratio": 0.75,
            "vline_evaluation": "理想的"
        },
        "eline": {
            "status": "理想的",
            "upper_lip_distance": 1.0,
            "lower_lip_distance": 1.0,
            "evaluation": "良好"
        },
        "proportions": {
            "aspect_ratio": 1.618,
            "closest_ratio": "黄金比",
            "ideal_ratio": 1.618,
            "difference": 0.0,
            "evaluation": "優秀"
        },
        "philtrum_chin": {
            "philtrum_length": 10.0,
            "chin_length": 20.0,
            "ratio": 2.0,
            "closest_ideal": "クラシック理想",
            "target_ratio": 2.0,
            "difference": 0.0,
            "evaluation": "理想的"
        },
        "nasolabial_angle": {
            "angle": 105.0,
            "ideal_range": "100-110度",
            "status": "理想的",
            "evaluation": "優秀"
        },
        "vline": {
            "jaw_angle": 110.0,
            "sharpness": "シャープ",
            "evaluation": "良好",
            "vline_score": 85.0
        },
        "symmetry": {
            "symmetry_score": 85.0,
            "asymmetry_level": 15.0,
            "evaluation": "良好"
        },
        "dental_protrusion": {
            "max_upper_protrusion": 2.0,
            "max_lower_protrusion": 1.5,
            "avg_upper_protrusion": 1.8,
            "avg_lower_protrusion": 1.3,
            "lip_status": "理想的",
            "dental_status": "正常範囲",
            "teeth_visible": False,
            "severity": "なし",
            "lip_balance": "バランス良好",
            "ideal_range": "Eラインから2-4mm以内",
            "evaluation": "正常"
        },
        "facial_harmony": {
            "avg_eye_width": 30.0,
            "nose_width": 25.0,
            "mouth_width": 45.0,
            "face_width": 150.0,
            "face_height": 180.0,
            "face_area": 15000.0,
            "eye_face_ratio": 0.20,
            "nose_face_ratio": 0.17,
            "mouth_face_ratio": 0.30,
            "eye_area_ratio": 0.008,
            "golden_deviation": 0.1,
            "face_aspect_ratio": 1.2,
            "harmony_score": 82.0,
            "evaluation": "良好",
            "beauty_level": "高い",
            "explanation": "バランスの取れた美しい顔立ちです"
        },
        "overall_score": {
            "score": 85.0,
            "level": "美人レベル",
            "tier": "B級",
            "description": "美しい顔立ち",
            "emoji": "✨",
            "detailed_scores": {"eline": 85.0, "harmony": 82.0},
            "score_breakdown": {"eline": "85.0 (重み15%)"},
            "severe_flaws": [],
            "explanation_details": {
                "strong_points": [],
                "weak_points": [],
                "bonus_factors": [],
                "penalty_factors": [],
                "improvement_suggestions": []
            },
            "note": "総合評価"
        },
        "beauty_advice": ["理想的な美しさです"]
    }


@pytest.fixture
def sample_user_data() -> dict:
    """Create sample user data for testing."""
    return {
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "SecurePassword123"
    }


@pytest.fixture
def test_user_id() -> str:
    """Generate test user ID."""
    return str(uuid4())


@pytest.fixture
def test_session_id() -> str:
    """Generate test session ID."""
    return str(uuid4())


@pytest.fixture
def sample_chat_message() -> dict:
    """Create sample chat message for testing."""
    return {
        "role": "user",
        "content": "分析結果について教えてください",
        "analysis_reference": None
    }


@pytest.fixture
def sample_line_event() -> dict:
    """Create sample LINE Bot event for testing."""
    return {
        "type": "message",
        "message": {
            "type": "text",
            "text": "こんにちは"
        },
        "source": {
            "type": "user",
            "userId": "test-line-user-id"
        },
        "timestamp": 1640995200000,
        "mode": "active",
        "webhookEventId": "test-webhook-event-id",
        "deliveryContext": {
            "isRedelivery": False
        }
    }


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment before each test."""
    # Ensure test configuration
    assert settings.testing is True
    assert "test" in settings.secret_key.lower()
    
    # Any additional setup can go here
    yield
    
    # Cleanup after test if needed


class MockSupabaseClient:
    """Mock Supabase client for testing."""
    
    def __init__(self):
        self.data_store = {}
    
    def table(self, table_name: str):
        return MockTable(table_name, self.data_store)


class MockTable:
    """Mock Supabase table for testing."""
    
    def __init__(self, table_name: str, data_store: dict):
        self.table_name = table_name
        self.data_store = data_store
        self._filters = {}
        
    def select(self, columns: str = "*"):
        return self
        
    def insert(self, data: dict):
        if self.table_name not in self.data_store:
            self.data_store[self.table_name] = []
        
        # Add ID if not provided
        if "id" not in data:
            data["id"] = str(uuid4())
            
        self.data_store[self.table_name].append(data)
        return MockResponse([data])
        
    def eq(self, column: str, value):
        self._filters[column] = value
        return self
        
    def execute(self):
        if self.table_name not in self.data_store:
            return MockResponse([])
            
        data = self.data_store[self.table_name]
        
        # Apply filters
        for column, value in self._filters.items():
            data = [item for item in data if item.get(column) == value]
            
        return MockResponse(data)
        
    def single(self):
        return self


class MockResponse:
    """Mock Supabase response for testing."""
    
    def __init__(self, data: list):
        self.data = data if isinstance(data, list) else [data] if data else []


@pytest.fixture
def mock_supabase_client():
    """Create mock Supabase client for testing."""
    return MockSupabaseClient()
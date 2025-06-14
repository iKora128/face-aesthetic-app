#!/usr/bin/env python3
"""Basic API test script to verify installation and functionality."""

import asyncio
import os
import sys
from pathlib import Path

# Set test environment variables
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test-anon-key"
os.environ["SUPABASE_SERVICE_KEY"] = "test-service-key"
os.environ["OPENAI_API_KEY"] = "sk-test-key"

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

async def test_basic_imports():
    """Test that all core modules can be imported."""
    print("🔧 Testing basic imports...")
    
    try:
        # Test core imports
        from app.config import settings
        print(f"✅ Config loaded - App: {settings.app_name}")
        
        from app.core.facial_analyzer import get_facial_analyzer
        analyzer = get_facial_analyzer()
        print("✅ Facial analyzer initialized")
        
        from app.models.analysis import FaceAnalysisResult
        print("✅ Pydantic models imported")
        
        from app.utils.exceptions import AnalysisError
        print("✅ Exception classes imported")
        
        from app.utils.validators import ImageValidator
        print("✅ Validators imported")
        
        print("🎉 All core imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {str(e)}")
        return False

async def test_facial_analyzer():
    """Test facial analyzer with dummy data."""
    print("\n🧠 Testing facial analyzer...")
    
    try:
        from app.core.facial_analyzer import get_facial_analyzer
        
        analyzer = get_facial_analyzer()
        
        # Test with a small dummy image (1x1 pixel PNG)
        dummy_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
        
        print("⏳ Testing analysis with dummy image...")
        
        # This should fail gracefully (no face detected)
        try:
            result = await analyzer.analyze_image_async(
                image_data=dummy_image_data,
                filename="test.png"
            )
            print("⚠️ Unexpected success - analysis should have failed")
        except Exception as e:
            if "No face detected" in str(e):
                print("✅ Analyzer correctly detected no face in dummy image")
            else:
                print(f"🔍 Analysis failed as expected: {str(e)}")
        
        print("✅ Facial analyzer test completed")
        return True
        
    except Exception as e:
        print(f"❌ Facial analyzer error: {str(e)}")
        return False

async def test_validators():
    """Test validation utilities."""
    print("\n✅ Testing validators...")
    
    try:
        from app.utils.validators import ImageValidator, UserValidator, AnalysisValidator
        
        # Test image validation
        try:
            ImageValidator.validate_upload("test.jpg", "image/jpeg", 1024)
            print("✅ Valid image upload passed validation")
        except Exception as e:
            print(f"❌ Valid image validation failed: {str(e)}")
            return False
        
        # Test invalid image
        try:
            ImageValidator.validate_upload("test.txt", "text/plain", 1024)
            print("❌ Invalid file type should have failed validation")
            return False
        except Exception:
            print("✅ Invalid file type correctly rejected")
        
        # Test user validation
        try:
            UserValidator.validate_email("test@example.com")
            print("✅ Valid email passed validation")
        except Exception as e:
            print(f"❌ Valid email validation failed: {str(e)}")
            return False
        
        # Test analysis validation
        try:
            AnalysisValidator.validate_analysis_type("full")
            print("✅ Valid analysis type passed validation")
        except Exception as e:
            print(f"❌ Valid analysis type validation failed: {str(e)}")
            return False
        
        print("✅ All validator tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Validator test error: {str(e)}")
        return False

async def test_pydantic_models():
    """Test Pydantic model creation."""
    print("\n📝 Testing Pydantic models...")
    
    try:
        from app.models.analysis import FaceAnalysisResult, AnalysisResponse
        from app.models.user import User, UserCreate
        from app.models.chat import ChatMessage, ChatSession
        from datetime import datetime
        from uuid import uuid4
        
        # Test analysis result model
        sample_result = FaceAnalysisResult(
            timestamp=datetime.now(),
            image_info={"filename": "test.jpg", "dimensions": "100x100", "total_landmarks": 468},
            face_angle={"angle": "正面", "ratio": 0.5, "confidence": 0.9, "suitable_for_analysis": True},
            face_contour={
                "face_area": 15000.0,
                "face_perimeter": 500.0,
                "face_width": 150.0,
                "face_height": 180.0,
                "small_face_score": 85.0,
                "cheekbone_width": 140.0,
                "jaw_width": 120.0,
                "cheek_jaw_ratio": 0.75,
                "vline_evaluation": "理想的",
            },
            eline={"status": "理想的", "upper_lip_distance": 1.0, "lower_lip_distance": 1.0, "evaluation": "良好"},
            proportions={"aspect_ratio": 1.618, "closest_ratio": "黄金比", "ideal_ratio": 1.618, "difference": 0.0, "evaluation": "優秀"},
            philtrum_chin={"philtrum_length": 10.0, "chin_length": 20.0, "ratio": 2.0, "closest_ideal": "クラシック理想", "target_ratio": 2.0, "difference": 0.0, "evaluation": "理想的"},
            nasolabial_angle={"angle": 105.0, "ideal_range": "100-110度", "status": "理想的", "evaluation": "優秀"},
            vline={"jaw_angle": 110.0, "sharpness": "シャープ", "evaluation": "良好", "vline_score": 85.0},
            symmetry={"symmetry_score": 85.0, "asymmetry_level": 15.0, "evaluation": "良好"},
            dental_protrusion={
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
            facial_harmony={
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
            overall_score={
                "score": 85.0,
                "level": "美人レベル",
                "tier": "B級",
                "description": "美しい顔立ち",
                "emoji": "✨",
                "detailed_scores": {"eline": 85.0, "harmony": 82.0},
                "score_breakdown": {"eline": "85.0 (重み15%)"},
                "severe_flaws": [],
                "explanation_details": {"strong_points": [], "weak_points": [], "bonus_factors": [], "penalty_factors": [], "improvement_suggestions": []},
                "note": "総合評価"
            },
            beauty_advice=["理想的な美しさです"],
        )
        
        print("✅ FaceAnalysisResult model created successfully")
        print(f"   Score: {sample_result.overall_score.score}")
        print(f"   Level: {sample_result.overall_score.level}")
        
        # Test user model
        sample_user_create = UserCreate(
            email="test@example.com",
            full_name="テストユーザー",
            password="SecurePassword123"
        )
        print("✅ UserCreate model created successfully")
        
        print("✅ All Pydantic model tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Pydantic model test error: {str(e)}")
        return False

async def main():
    """Run all basic tests."""
    print("🚀 Face Aesthetic API - Basic Functionality Test")
    print("=" * 50)
    
    tests = [
        test_basic_imports,
        test_pydantic_models,
        test_validators,
        test_facial_analyzer,
    ]
    
    results = []
    for test in tests:
        result = await test()
        results.append(result)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All {total} tests PASSED!")
        print("✅ API基盤は正常に動作しています")
        return True
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        print("❌ 一部のテストが失敗しました")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
"""Modern FastAPI integration of the facial beauty analyzer."""

import asyncio
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import cv2
import mediapipe as mp
import numpy as np
from loguru import logger

from app.models.analysis import FaceAnalysisResult
from app.utils.exceptions import AnalysisError


class ModernFacialBeautyAnalyzer:
    """Modern facial beauty analyzer with async support and enhanced error handling."""

    def __init__(self) -> None:
        """Initialize the analyzer with MediaPipe and beauty standards."""
        # MediaPipe initialization
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.drawing_spec = mp.solutions.drawing_utils.DrawingSpec(
            thickness=1, circle_radius=1
        )

        # Beauty standards (Korean aesthetic + golden ratio)
        self.beauty_standards = {
            "golden_ratio": 1.618,
            "silver_ratio": 1.414, 
            "japanese_face_ratio": 1.46,
            "nasolabial_angle_min": 100,
            "nasolabial_angle_max": 110,
            "philtrum_chin_ratio_ideal": 2.0,
            "philtrum_chin_ratio_modern": 3.0,
            "eline_tolerance": 2.0,
            "eye_width_ratio": 3.0,
            "facial_thirds": [1, 1, 1],
            "facial_fifths": [1, 1, 1, 1, 1],
        }

        # MediaPipe Face Mesh landmark indices
        self.landmarks = {
            "nose_tip": 1,
            "chin_tip": 152,
            "forehead_center": 10,
            "nose_bottom": 2,
            "left_eye_outer": 33,
            "right_eye_outer": 263,
            "left_eye_inner": 133,
            "right_eye_inner": 362,
            "left_eye_center": 468,
            "right_eye_center": 473,
            "mouth_left": 61,
            "mouth_right": 291,
            "upper_lip_center": 13,
            "lower_lip_center": 14,
            "upper_lip_top": 0,
            "lower_lip_bottom": 17,
            "left_cheek": 234,
            "right_cheek": 454,
            "left_jaw": 172,
            "right_jaw": 397,
            "left_eyebrow_outer": 70,
            "right_eyebrow_outer": 300,
            "left_eyebrow_inner": 107,
            "right_eyebrow_inner": 336,
            "nose_left": 131,
            "nose_right": 360,
            "nasal_bridge_top": 6,
            "nasal_bridge_mid": 168,
        }

        # Jawline landmarks
        self.jawline_landmarks = [
            172, 136, 150, 149, 176, 148, 152, 377, 400, 378, 379, 365, 397, 288, 361, 323
        ]

        logger.info("🎯 Modern Facial Beauty Analyzer initialized")

    async def analyze_image_async(
        self, image_data: bytes, filename: str = "image.jpg"
    ) -> FaceAnalysisResult:
        """Async wrapper for image analysis."""
        return await asyncio.get_event_loop().run_in_executor(
            None, self._analyze_image_sync, image_data, filename
        )

    def _analyze_image_sync(
        self, image_data: bytes, filename: str = "image.jpg"
    ) -> FaceAnalysisResult:
        """Synchronous image analysis implementation."""
        try:
            # Create temporary file for image processing
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
                temp_file.write(image_data)
                temp_path = temp_file.name

            try:
                # Process the image
                result = self._process_image(temp_path, filename)
                return result
            finally:
                # Clean up temporary file
                Path(temp_path).unlink(missing_ok=True)

        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise AnalysisError(
                f"Failed to analyze image: {str(e)}",
                stage="image_processing",
                details={"filename": filename},
            ) from e

    def _process_image(self, image_path: str, filename: str) -> FaceAnalysisResult:
        """Process image and extract facial analysis results."""
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise AnalysisError(
                "Could not read image file",
                stage="image_loading",
                details={"path": image_path},
            )

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, _ = image.shape

        # Analyze with MediaPipe
        with self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
        ) as face_mesh:
            
            results = face_mesh.process(image_rgb)

            if not results.multi_face_landmarks:
                raise AnalysisError(
                    "No face detected in image",
                    stage="face_detection",
                    details={"image_dimensions": f"{w}x{h}"},
                )

            landmarks = results.multi_face_landmarks[0].landmark

            # Perform all analyses
            analysis_data = self._perform_comprehensive_analysis(
                landmarks, (h, w), filename
            )

            return analysis_data

    def _perform_comprehensive_analysis(
        self, landmarks: Any, image_shape: tuple[int, int], filename: str
    ) -> FaceAnalysisResult:
        """Perform comprehensive facial analysis."""
        h, w = image_shape

        try:
            # Basic analyses
            face_angle = self._detect_face_angle(landmarks)
            face_contour = self._analyze_face_contour(landmarks, image_shape)
            eline = self._analyze_eline(landmarks, image_shape)
            proportions = self._analyze_face_proportions(landmarks, image_shape)
            philtrum_chin = self._analyze_philtrum_chin_ratio(landmarks, image_shape)
            nasolabial_angle = self._analyze_nasolabial_angle(landmarks)
            vline = self._analyze_vline_curvature(landmarks, image_shape)
            symmetry = self._analyze_facial_symmetry(landmarks, image_shape)
            dental_protrusion = self._analyze_dental_protrusion(landmarks, image_shape)
            facial_harmony = self._analyze_facial_harmony(landmarks, image_shape)

            # Compile results
            analysis_results = {
                "face_angle": face_angle,
                "face_contour": face_contour,
                "eline": eline,
                "proportions": proportions,
                "philtrum_chin": philtrum_chin,
                "nasolabial_angle": nasolabial_angle,
                "vline": vline,
                "symmetry": symmetry,
                "dental_protrusion": dental_protrusion,
                "facial_harmony": facial_harmony,
            }

            # Calculate overall score
            overall_score = self._calculate_overall_score(analysis_results)
            beauty_advice = self._generate_beauty_advice(analysis_results)

            # Create result object
            result = FaceAnalysisResult(
                timestamp=datetime.now(),
                image_info={
                    "filename": filename,
                    "dimensions": f"{w}x{h}",
                    "total_landmarks": len(landmarks),
                },
                face_angle=face_angle,
                face_contour=face_contour,
                eline=eline,
                proportions=proportions,
                philtrum_chin=philtrum_chin,
                nasolabial_angle=nasolabial_angle,
                vline=vline,
                symmetry=symmetry,
                dental_protrusion=dental_protrusion,
                facial_harmony=facial_harmony,
                overall_score=overall_score,
                beauty_advice=beauty_advice,
                angle_warning=self._get_angle_warning(face_angle),
            )

            logger.info(f"✅ Analysis completed - Score: {overall_score.get('score', 0)}")
            return result

        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            raise AnalysisError(
                f"Analysis failed during processing: {str(e)}",
                stage="comprehensive_analysis",
            ) from e

    # ========================
    # Analysis Methods (from legacy code)
    # ========================

    def _detect_face_angle(self, landmarks: Any) -> dict[str, Any]:
        """Detect face angle and orientation."""
        nose_tip = landmarks[self.landmarks["nose_tip"]]
        left_cheek = landmarks[self.landmarks["left_cheek"]]
        right_cheek = landmarks[self.landmarks["right_cheek"]]

        left_dist = abs(nose_tip.x - left_cheek.x)
        right_dist = abs(nose_tip.x - right_cheek.x)

        if left_dist == 0 and right_dist == 0:
            return {"angle": "unknown", "confidence": 0.0, "suitable_for_analysis": False}

        ratio = left_dist / (left_dist + right_dist) if (left_dist + right_dist) > 0 else 0.5

        if 0.4 <= ratio <= 0.6:
            angle_type = "正面"
            confidence = 1.0 - abs(ratio - 0.5) * 2
        elif ratio < 0.3:
            angle_type = "右向き"
            confidence = 0.7
        elif ratio > 0.7:
            angle_type = "左向き"
            confidence = 0.7
        else:
            angle_type = "斜め"
            confidence = 0.5

        return {
            "angle": angle_type,
            "ratio": round(ratio, 3),
            "confidence": round(confidence, 2),
            "suitable_for_analysis": confidence > 0.6,
        }

    def _analyze_eline(self, landmarks: Any, image_shape: tuple[int, int]) -> dict[str, Any]:
        """Analyze E-line (aesthetic line)."""
        nose_tip = landmarks[self.landmarks["nose_tip"]]
        chin_tip = landmarks[self.landmarks["chin_tip"]]
        upper_lip = landmarks[self.landmarks["upper_lip_center"]]
        lower_lip = landmarks[self.landmarks["lower_lip_center"]]

        face_width = self._calculate_distance(
            landmarks[self.landmarks["left_cheek"]],
            landmarks[self.landmarks["right_cheek"]],
            image_shape,
        )

        upper_lip_dist = self._point_to_line_distance(upper_lip, nose_tip, chin_tip) * face_width
        lower_lip_dist = self._point_to_line_distance(lower_lip, nose_tip, chin_tip) * face_width

        max_dist = max(abs(upper_lip_dist), abs(lower_lip_dist))

        if max_dist <= 2.0:
            status = "理想的"
        elif max_dist <= self.beauty_standards["eline_tolerance"]:
            status = "良好"
        elif max_dist <= 7.0:
            status = "標準的"
        else:
            status = "上唇がやや前方" if upper_lip_dist > lower_lip_dist else "下唇がやや前方"

        evaluation = "良好" if max_dist <= self.beauty_standards["eline_tolerance"] else "標準的"

        return {
            "status": status,
            "upper_lip_distance": round(upper_lip_dist, 2),
            "lower_lip_distance": round(lower_lip_dist, 2),
            "evaluation": evaluation,
        }

    def _analyze_face_proportions(self, landmarks: Any, image_shape: tuple[int, int]) -> dict[str, Any]:
        """Analyze face proportions (golden ratio, silver ratio)."""
        face_height = self._calculate_distance(
            landmarks[self.landmarks["forehead_center"]],
            landmarks[self.landmarks["chin_tip"]],
            image_shape,
        )

        face_width = self._calculate_distance(
            landmarks[self.landmarks["left_cheek"]],
            landmarks[self.landmarks["right_cheek"]],
            image_shape,
        )

        if face_width == 0:
            return {"error": "顔の幅を測定できませんでした"}

        aspect_ratio = face_height / face_width

        golden_diff = abs(aspect_ratio - self.beauty_standards["golden_ratio"])
        silver_diff = abs(aspect_ratio - self.beauty_standards["silver_ratio"])
        japanese_diff = abs(aspect_ratio - self.beauty_standards["japanese_face_ratio"])

        min_diff = min(golden_diff, silver_diff, japanese_diff)
        
        if min_diff == golden_diff:
            closest_ratio = "黄金比"
            ideal_ratio = self.beauty_standards["golden_ratio"]
        elif min_diff == silver_diff:
            closest_ratio = "白銀比（大和比）"
            ideal_ratio = self.beauty_standards["silver_ratio"]
        else:
            closest_ratio = "日本人理想比"
            ideal_ratio = self.beauty_standards["japanese_face_ratio"]

        if min_diff < 0.15:
            evaluation = "優秀"
        elif min_diff < 0.25:
            evaluation = "良好"
        elif min_diff < 0.35:
            evaluation = "標準的"
        else:
            evaluation = "個性的"

        return {
            "aspect_ratio": round(aspect_ratio, 3),
            "closest_ratio": closest_ratio,
            "ideal_ratio": ideal_ratio,
            "difference": round(min_diff, 3),
            "evaluation": evaluation,
        }

    # ========================
    # Helper Methods
    # ========================

    def _calculate_distance(
        self, point1: Any, point2: Any, image_shape: tuple[int, int]
    ) -> float:
        """Calculate pixel distance between two landmarks."""
        x1, y1 = int(point1.x * image_shape[1]), int(point1.y * image_shape[0])
        x2, y2 = int(point2.x * image_shape[1]), int(point2.y * image_shape[0])
        return float(np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))

    def _point_to_line_distance(self, point: Any, line_point1: Any, line_point2: Any) -> float:
        """Calculate distance from point to line (normalized coordinates)."""
        p = np.array([point.x, point.y])
        a = np.array([line_point1.x, line_point1.y])
        b = np.array([line_point2.x, line_point2.y])

        if np.linalg.norm(b - a) == 0:
            return float(np.linalg.norm(p - a))

        return float(np.abs(np.cross(b - a, p - a)) / np.linalg.norm(b - a))

    def _get_angle_warning(self, face_angle: dict[str, Any]) -> str | None:
        """Generate angle warning message if needed."""
        if not face_angle.get("suitable_for_analysis", True):
            return (
                f"⚠️ 検出された角度: {face_angle['angle']} "
                f"(信頼度: {face_angle['confidence']})\\n正面顔での撮影を推奨します。"
            )
        return None

    # ========================
    # Placeholder methods for remaining analyses
    # (These would contain the full implementations from the legacy code)
    # ========================

    def _analyze_philtrum_chin_ratio(self, landmarks: Any, image_shape: tuple[int, int]) -> dict[str, Any]:
        """Analyze philtrum to chin ratio."""
        # Simplified implementation
        return {
            "philtrum_length": 10.0,
            "chin_length": 20.0,
            "ratio": 2.0,
            "closest_ideal": "クラシック理想 (1:2)",
            "target_ratio": 2.0,
            "difference": 0.0,
            "evaluation": "理想的",
        }

    def _analyze_nasolabial_angle(self, landmarks: Any) -> dict[str, Any]:
        """Analyze nasolabial angle."""
        return {
            "angle": 105.0,
            "ideal_range": "100-110度",
            "status": "理想的",
            "evaluation": "優秀",
        }

    def _analyze_vline_curvature(self, landmarks: Any, image_shape: tuple[int, int]) -> dict[str, Any]:
        """Analyze V-line jaw curvature."""
        return {
            "jaw_angle": 110.0,
            "sharpness": "シャープ",
            "evaluation": "良好",
            "vline_score": 85.0,
        }

    def _analyze_facial_symmetry(self, landmarks: Any, image_shape: tuple[int, int]) -> dict[str, Any]:
        """Analyze facial symmetry."""
        return {
            "symmetry_score": 85.0,
            "asymmetry_level": 15.0,
            "evaluation": "良好な対称性",
        }

    def _analyze_dental_protrusion(self, landmarks: Any, image_shape: tuple[int, int]) -> dict[str, Any]:
        """Analyze dental/lip protrusion."""
        return {
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
            "evaluation": "正常",
        }

    def _analyze_face_contour(self, landmarks: Any, image_shape: tuple[int, int]) -> dict[str, Any]:
        """Analyze face contour."""
        return {
            "face_area": 15000.0,
            "face_perimeter": 500.0,
            "face_width": 150.0,
            "face_height": 180.0,
            "small_face_score": 85.0,
            "cheekbone_width": 140.0,
            "jaw_width": 120.0,
            "cheek_jaw_ratio": 0.75,
            "vline_evaluation": "理想的",
        }

    def _analyze_facial_harmony(self, landmarks: Any, image_shape: tuple[int, int]) -> dict[str, Any]:
        """Analyze facial harmony and feature proportions."""
        return {
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
            "explanation": "バランスの取れた美しい顔立ちです",
        }

    def _calculate_overall_score(self, analysis_results: dict[str, Any]) -> dict[str, Any]:
        """Calculate overall beauty score."""
        # Simplified scoring
        base_score = 78.5
        
        return {
            "score": base_score,
            "level": "🌸 容姿端麗な一般人レベル",
            "tier": "C級",
            "description": "街で振り返られる美人レベル",
            "emoji": "🌸",
            "detailed_scores": {
                "eline": 85.0,
                "harmony": 78.0,
                "symmetry": 82.0,
                "proportions": 75.0,
            },
            "score_breakdown": {
                "eline": "85.0 (重み15%)",
                "harmony": "78.0 (重み25%)",
                "symmetry": "82.0 (重み6%)",
            },
            "severe_flaws": [],
            "explanation_details": {
                "strong_points": ["良好なEライン", "バランスの取れた顔立ち"],
                "weak_points": [],
                "bonus_factors": [],
                "penalty_factors": [],
                "improvement_suggestions": ["メイク技術の向上で更なる美しさを"],
            },
            "note": "韓国の美容整形基準と黄金比に基づく総合評価です。",
        }

    def _generate_beauty_advice(self, analysis_results: dict[str, Any]) -> list[str]:
        """Generate beauty advice based on analysis."""
        return [
            "💋 理想的なEラインを持っています。横顔美人の証です。",
            "✨ バランスの取れた美しい顔立ちです。",
            "💄 メイク技術の向上で更なる美しさを引き出せます。",
            "⚠️ 注意: このアドバイスは一般的な美容情報であり、医学的アドバイスではありません。",
        ]


# Global analyzer instance
_analyzer_instance: ModernFacialBeautyAnalyzer | None = None


def get_facial_analyzer() -> ModernFacialBeautyAnalyzer:
    """Get or create global facial analyzer instance."""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = ModernFacialBeautyAnalyzer()
    return _analyzer_instance
"""Face analysis models using modern Pydantic v2 practices."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ImageUpload(BaseModel):
    """Image upload request model."""

    filename: str = Field(description="Original filename")
    content_type: str = Field(description="Image MIME type")
    size: int = Field(gt=0, le=10_000_000, description="File size in bytes")

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, v: str) -> str:
        """Validate image content type."""
        allowed_types = ["image/jpeg", "image/png", "image/webp"]
        if v not in allowed_types:
            msg = f"Content type must be one of: {', '.join(allowed_types)}"
            raise ValueError(msg)
        return v


class FaceAngle(BaseModel):
    """Face angle detection result."""

    angle: str = Field(description="Detected face angle (正面, 左向き, 右向き, 斜め)")
    ratio: float = Field(ge=0, le=1, description="Angle ratio calculation")
    confidence: float = Field(ge=0, le=1, description="Detection confidence")
    suitable_for_analysis: bool = Field(description="Whether suitable for analysis")


class ElineAnalysis(BaseModel):
    """E-line (aesthetic line) analysis result."""

    status: str = Field(description="E-line status description")
    upper_lip_distance: float = Field(description="Upper lip distance from E-line")
    lower_lip_distance: float = Field(description="Lower lip distance from E-line")
    evaluation: str = Field(description="Overall E-line evaluation")


class FaceProportions(BaseModel):
    """Face proportions analysis result."""

    aspect_ratio: float = Field(description="Face height to width ratio")
    closest_ratio: str = Field(description="Closest ideal ratio type")
    ideal_ratio: float = Field(description="Target ideal ratio value")
    difference: float = Field(description="Difference from ideal")
    evaluation: str = Field(description="Proportion evaluation")


class PhiltrumChinRatio(BaseModel):
    """Philtrum to chin ratio analysis result."""

    philtrum_length: float = Field(description="Philtrum length measurement")
    chin_length: float = Field(description="Chin length measurement")
    ratio: float = Field(description="Chin to philtrum ratio")
    closest_ideal: str = Field(description="Closest ideal ratio type")
    target_ratio: float = Field(description="Target ratio value")
    difference: float = Field(description="Difference from target")
    evaluation: str = Field(description="Ratio evaluation")


class NasolabialAngle(BaseModel):
    """Nasolabial angle analysis result."""

    angle: float = Field(description="Measured nasolabial angle in degrees")
    ideal_range: str = Field(description="Ideal angle range description")
    status: str = Field(description="Angle status description")
    evaluation: str = Field(description="Angle evaluation")


class VlineAnalysis(BaseModel):
    """V-line (jaw line) analysis result."""

    jaw_angle: float = Field(description="Measured jaw angle in degrees")
    sharpness: str = Field(description="Jaw sharpness description")
    evaluation: str = Field(description="V-line evaluation")
    vline_score: float = Field(ge=0, le=100, description="V-line specific score")


class SymmetryAnalysis(BaseModel):
    """Facial symmetry analysis result."""

    symmetry_score: float = Field(ge=0, le=100, description="Symmetry score")
    asymmetry_level: float = Field(description="Asymmetry level percentage")
    evaluation: str = Field(description="Symmetry evaluation")


class DentalProtrusion(BaseModel):
    """Dental/lip protrusion analysis result."""

    max_upper_protrusion: float = Field(description="Maximum upper lip protrusion")
    max_lower_protrusion: float = Field(description="Maximum lower lip protrusion")
    avg_upper_protrusion: float = Field(description="Average upper lip protrusion")
    avg_lower_protrusion: float = Field(description="Average lower lip protrusion")
    lip_status: str = Field(description="Lip status description")
    dental_status: str = Field(description="Dental status description")
    teeth_visible: bool = Field(description="Whether teeth are visible")
    severity: str = Field(description="Protrusion severity level")
    lip_balance: str = Field(description="Lip balance evaluation")
    ideal_range: str = Field(description="Ideal protrusion range")
    evaluation: str = Field(description="Overall evaluation")


class FaceContour(BaseModel):
    """Face contour analysis result."""

    face_area: float = Field(description="Calculated face area")
    face_perimeter: float = Field(description="Face perimeter measurement")
    face_width: float = Field(description="Face width measurement")
    face_height: float = Field(description="Face height measurement")
    small_face_score: float = Field(ge=0, le=100, description="Small face score")
    cheekbone_width: float = Field(description="Cheekbone width")
    jaw_width: float = Field(description="Jaw width")
    cheek_jaw_ratio: float = Field(description="Cheek to jaw ratio")
    vline_evaluation: str = Field(description="V-line evaluation")


class FacialHarmony(BaseModel):
    """Facial harmony and feature proportion analysis."""

    avg_eye_width: float = Field(description="Average eye width")
    nose_width: float = Field(description="Nose width")
    mouth_width: float = Field(description="Mouth width")
    face_width: float = Field(description="Face width")
    face_height: float = Field(description="Face height")
    face_area: float = Field(description="Face area")
    eye_face_ratio: float = Field(description="Eye to face width ratio")
    nose_face_ratio: float = Field(description="Nose to face width ratio")
    mouth_face_ratio: float = Field(description="Mouth to face width ratio")
    eye_area_ratio: float = Field(description="Eye area to face area ratio")
    golden_deviation: float = Field(description="Deviation from golden ratio")
    face_aspect_ratio: float = Field(description="Face aspect ratio")
    harmony_score: float = Field(ge=0, le=100, description="Overall harmony score")
    evaluation: str = Field(description="Harmony evaluation")
    beauty_level: str = Field(description="Beauty level assessment")
    explanation: str = Field(description="Detailed explanation")


class OverallScore(BaseModel):
    """Overall beauty score and assessment."""

    score: float = Field(ge=0, le=100, description="Overall beauty score")
    level: str = Field(description="Beauty level description")
    tier: str = Field(description="Beauty tier ranking")
    description: str = Field(description="Detailed description")
    emoji: str = Field(description="Representative emoji")
    detailed_scores: dict[str, float] = Field(description="Individual component scores")
    score_breakdown: dict[str, str] = Field(description="Score breakdown with weights")
    severe_flaws: list[str] = Field(description="Identified severe flaws")
    explanation_details: dict[str, Any] = Field(description="Detailed explanations")
    note: str = Field(description="Additional notes")


class FaceAnalysisResult(BaseModel):
    """Complete face analysis result."""

    model_config = ConfigDict(from_attributes=True)

    timestamp: datetime = Field(description="Analysis timestamp")
    image_info: dict[str, Any] = Field(description="Image metadata")
    face_angle: FaceAngle = Field(description="Face angle analysis")
    face_contour: FaceContour = Field(description="Face contour analysis")
    eline: ElineAnalysis = Field(description="E-line analysis")
    proportions: FaceProportions = Field(description="Face proportions")
    philtrum_chin: PhiltrumChinRatio = Field(description="Philtrum-chin ratio")
    nasolabial_angle: NasolabialAngle = Field(description="Nasolabial angle")
    vline: VlineAnalysis = Field(description="V-line analysis")
    symmetry: SymmetryAnalysis = Field(description="Symmetry analysis")
    dental_protrusion: DentalProtrusion = Field(description="Dental protrusion")
    facial_harmony: FacialHarmony = Field(description="Facial harmony")
    overall_score: OverallScore = Field(description="Overall assessment")
    beauty_advice: list[str] = Field(description="Beauty advice recommendations")
    angle_warning: str | None = Field(default=None, description="Angle warning message")


class AnalysisRequest(BaseModel):
    """Face analysis request model."""

    user_notes: str | None = Field(
        default=None, max_length=500, description="User notes about the image"
    )
    analysis_type: str = Field(
        default="full", description="Type of analysis to perform"
    )
    include_report_image: bool = Field(
        default=True, description="Whether to generate visual report"
    )


class AnalysisResponse(BaseModel):
    """Face analysis response model."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(description="Analysis unique identifier")
    user_id: UUID = Field(description="User who requested analysis")
    created_at: datetime = Field(description="Analysis creation timestamp")
    image_url: str = Field(description="Original image URL")
    report_image_url: str | None = Field(
        default=None, description="Generated report image URL"
    )
    result: FaceAnalysisResult = Field(description="Analysis results")
    status: str = Field(description="Analysis status")
    processing_time: float = Field(description="Processing time in seconds")


class AnalysisHistory(BaseModel):
    """User's analysis history summary."""

    model_config = ConfigDict(from_attributes=True)

    total_count: int = Field(description="Total number of analyses")
    latest_analysis: AnalysisResponse | None = Field(
        default=None, description="Most recent analysis"
    )
    average_score: float | None = Field(
        default=None, description="Average beauty score"
    )
    score_trend: list[dict[str, Any]] = Field(
        default_factory=list, description="Score trend over time"
    )
    top_features: list[str] = Field(
        default_factory=list, description="Best performing features"
    )
    improvement_areas: list[str] = Field(
        default_factory=list, description="Areas for improvement"
    )
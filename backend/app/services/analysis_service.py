"""Analysis service for handling face analysis operations."""

import asyncio
from datetime import datetime
from uuid import UUID, uuid4

from loguru import logger
from supabase import Client

from app.core.facial_analyzer import get_facial_analyzer
from app.models.analysis import AnalysisResponse, FaceAnalysisResult
from app.services.storage_service import get_storage_service
from app.utils.exceptions import AnalysisError, DatabaseError


class AnalysisService:
    """Service for managing face analysis operations."""

    def __init__(self, supabase_client: Client) -> None:
        """Initialize analysis service."""
        self.supabase = supabase_client
        self.analyzer = get_facial_analyzer()
        self.storage_service = get_storage_service(supabase_client)

    async def analyze_face_image(
        self,
        user_id: UUID,
        image_data: bytes,
        filename: str,
        user_notes: str | None = None,
        analysis_type: str = "full",
        include_report_image: bool = True,
    ) -> AnalysisResponse:
        """Analyze face image and store results."""
        analysis_id = uuid4()
        start_time = datetime.now()

        try:
            logger.info(f"🔍 Starting analysis {analysis_id} for user {user_id}")

            # Step 1: Upload original image to storage
            image_url = await self.storage_service.upload_image(
                user_id=user_id,
                image_data=image_data,
                filename=filename,
                image_type="analysis",
            )

            # Step 2: Perform facial analysis
            analysis_result = await self.analyzer.analyze_image_async(
                image_data=image_data, filename=filename
            )

            # Step 3: Generate report image if requested
            report_image_url = None
            if include_report_image:
                # TODO: Implement report generation
                # report_image_url = await self._generate_report_image(analysis_result, user_id)
                pass

            # Step 4: Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()

            # Step 5: Store analysis results in database
            analysis_record = await self._store_analysis_result(
                analysis_id=analysis_id,
                user_id=user_id,
                image_url=image_url,
                report_image_url=report_image_url,
                analysis_result=analysis_result,
                processing_time=processing_time,
                user_notes=user_notes,
                analysis_type=analysis_type,
                filename=filename,
                image_size=len(image_data),
            )

            logger.info(f"✅ Analysis {analysis_id} completed successfully")

            return AnalysisResponse(
                id=analysis_id,
                user_id=user_id,
                created_at=analysis_record["created_at"],
                image_url=image_url,
                report_image_url=report_image_url,
                result=analysis_result,
                status="completed",
                processing_time=processing_time,
            )

        except Exception as e:
            logger.error(f"❌ Analysis {analysis_id} failed: {str(e)}")
            
            # Store failure record
            await self._store_analysis_failure(
                analysis_id=analysis_id,
                user_id=user_id,
                error=str(e),
                processing_time=(datetime.now() - start_time).total_seconds(),
            )

            raise AnalysisError(
                f"Face analysis failed: {str(e)}",
                stage="analysis_service",
                details={"analysis_id": str(analysis_id)},
            ) from e

    async def get_analysis_result(
        self, analysis_id: UUID, user_id: UUID
    ) -> AnalysisResponse:
        """Get stored analysis result."""
        try:
            response = (
                self.supabase.table("analysis_results")
                .select("*")
                .eq("id", str(analysis_id))
                .eq("user_id", str(user_id))
                .single()
                .execute()
            )

            if not response.data:
                raise AnalysisError(
                    "Analysis result not found",
                    stage="database_query",
                    details={"analysis_id": str(analysis_id)},
                )

            data = response.data
            
            # Reconstruct FaceAnalysisResult from stored JSON
            analysis_result = self._reconstruct_analysis_result(data)

            return AnalysisResponse(
                id=UUID(data["id"]),
                user_id=UUID(data["user_id"]),
                created_at=datetime.fromisoformat(data["created_at"]),
                image_url=data["original_image_url"],
                report_image_url=data.get("report_image_url"),
                result=analysis_result,
                status="completed",
                processing_time=data.get("processing_time_seconds", 0.0),
            )

        except Exception as e:
            logger.error(f"Failed to get analysis result: {str(e)}")
            raise DatabaseError(
                f"Failed to retrieve analysis result: {str(e)}",
                operation="get_analysis_result",
            ) from e

    async def get_user_analysis_history(
        self, user_id: UUID, limit: int = 10, offset: int = 0
    ) -> list[AnalysisResponse]:
        """Get user's analysis history."""
        try:
            response = (
                self.supabase.table("analysis_results")
                .select("*")
                .eq("user_id", str(user_id))
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )

            results = []
            for data in response.data:
                analysis_result = self._reconstruct_analysis_result(data)
                
                results.append(
                    AnalysisResponse(
                        id=UUID(data["id"]),
                        user_id=UUID(data["user_id"]),
                        created_at=datetime.fromisoformat(data["created_at"]),
                        image_url=data["original_image_url"],
                        report_image_url=data.get("report_image_url"),
                        result=analysis_result,
                        status="completed",
                        processing_time=data.get("processing_time_seconds", 0.0),
                    )
                )

            return results

        except Exception as e:
            logger.error(f"Failed to get analysis history: {str(e)}")
            raise DatabaseError(
                f"Failed to retrieve analysis history: {str(e)}",
                operation="get_analysis_history",
            ) from e

    async def delete_analysis_result(
        self, analysis_id: UUID, user_id: UUID
    ) -> None:
        """Delete analysis result and associated images."""
        try:
            # Get analysis data first
            response = (
                self.supabase.table("analysis_results")
                .select("original_image_url, report_image_url")
                .eq("id", str(analysis_id))
                .eq("user_id", str(user_id))
                .single()
                .execute()
            )

            if not response.data:
                raise AnalysisError(
                    "Analysis result not found",
                    stage="database_query",
                    details={"analysis_id": str(analysis_id)},
                )

            # Delete from database
            self.supabase.table("analysis_results").delete().eq(
                "id", str(analysis_id)
            ).eq("user_id", str(user_id)).execute()

            # Delete associated images
            data = response.data
            if data.get("original_image_url"):
                await self.storage_service.delete_image_by_url(data["original_image_url"])
            
            if data.get("report_image_url"):
                await self.storage_service.delete_image_by_url(data["report_image_url"])

            logger.info(f"🗑️ Deleted analysis {analysis_id}")

        except Exception as e:
            logger.error(f"Failed to delete analysis result: {str(e)}")
            raise DatabaseError(
                f"Failed to delete analysis result: {str(e)}",
                operation="delete_analysis_result",
            ) from e

    async def _store_analysis_result(
        self,
        analysis_id: UUID,
        user_id: UUID,
        image_url: str,
        report_image_url: str | None,
        analysis_result: FaceAnalysisResult,
        processing_time: float,
        user_notes: str | None,
        analysis_type: str,
        filename: str,
        image_size: int,
    ) -> dict:
        """Store analysis result in database."""
        try:
            # Convert analysis result to JSON format
            analysis_data = {
                "id": str(analysis_id),
                "user_id": str(user_id),
                "original_image_url": image_url,
                "original_filename": filename,
                "image_size_bytes": image_size,
                "image_mime_type": "image/jpeg",  # TODO: Detect actual MIME type
                "image_dimensions": analysis_result.image_info.get("dimensions"),
                "analysis_type": analysis_type,
                "processing_time_seconds": processing_time,
                "user_notes": user_notes,
                "face_angle": analysis_result.face_angle.model_dump(),
                "face_contour": analysis_result.face_contour.model_dump(),
                "eline_analysis": analysis_result.eline.model_dump(),
                "face_proportions": analysis_result.proportions.model_dump(),
                "philtrum_chin_ratio": analysis_result.philtrum_chin.model_dump(),
                "nasolabial_angle": analysis_result.nasolabial_angle.model_dump(),
                "vline_analysis": analysis_result.vline.model_dump(),
                "symmetry_analysis": analysis_result.symmetry.model_dump(),
                "dental_protrusion": analysis_result.dental_protrusion.model_dump(),
                "facial_harmony": analysis_result.facial_harmony.model_dump(),
                "overall_score": analysis_result.overall_score.model_dump(),
                "beauty_advice": analysis_result.beauty_advice,
                "report_image_url": report_image_url,
                "report_generated": report_image_url is not None,
                "face_detection_confidence": 0.95,  # TODO: Extract from actual analysis
                "analysis_warnings": [],
                "angle_warning": analysis_result.angle_warning,
            }

            response = (
                self.supabase.table("analysis_results")
                .insert(analysis_data)
                .execute()
            )

            return response.data[0]

        except Exception as e:
            logger.error(f"Failed to store analysis result: {str(e)}")
            raise DatabaseError(
                f"Failed to store analysis result: {str(e)}",
                operation="store_analysis_result",
            ) from e

    async def _store_analysis_failure(
        self,
        analysis_id: UUID,
        user_id: UUID,
        error: str,
        processing_time: float,
    ) -> None:
        """Store analysis failure for debugging."""
        try:
            failure_data = {
                "id": str(analysis_id),
                "user_id": str(user_id),
                "original_image_url": "",
                "original_filename": "failed_analysis",
                "image_size_bytes": 0,
                "image_mime_type": "",
                "analysis_type": "failed",
                "processing_time_seconds": processing_time,
                "face_angle": {"error": error},
                "face_contour": {"error": error},
                "eline_analysis": {"error": error},
                "face_proportions": {"error": error},
                "philtrum_chin_ratio": {"error": error},
                "nasolabial_angle": {"error": error},
                "vline_analysis": {"error": error},
                "symmetry_analysis": {"error": error},
                "dental_protrusion": {"error": error},
                "facial_harmony": {"error": error},
                "overall_score": {"error": error, "score": 0},
                "beauty_advice": [f"分析エラー: {error}"],
                "analysis_warnings": [error],
            }

            self.supabase.table("analysis_results").insert(failure_data).execute()

        except Exception as e:
            logger.error(f"Failed to store analysis failure: {str(e)}")
            # Don't raise here to avoid masking original error

    def _reconstruct_analysis_result(self, data: dict) -> FaceAnalysisResult:
        """Reconstruct FaceAnalysisResult from database JSON."""
        return FaceAnalysisResult(
            timestamp=datetime.fromisoformat(data["created_at"]),
            image_info={
                "filename": data["original_filename"],
                "dimensions": data.get("image_dimensions", ""),
                "total_landmarks": 468,
            },
            face_angle=data["face_angle"],
            face_contour=data["face_contour"],
            eline=data["eline_analysis"],
            proportions=data["face_proportions"],
            philtrum_chin=data["philtrum_chin_ratio"],
            nasolabial_angle=data["nasolabial_angle"],
            vline=data["vline_analysis"],
            symmetry=data["symmetry_analysis"],
            dental_protrusion=data["dental_protrusion"],
            facial_harmony=data["facial_harmony"],
            overall_score=data["overall_score"],
            beauty_advice=data["beauty_advice"],
            angle_warning=data.get("angle_warning"),
        )


# Global service instances
_analysis_service_instance: AnalysisService | None = None


def get_analysis_service(supabase_client: Client) -> AnalysisService:
    """Get or create analysis service instance."""
    global _analysis_service_instance
    if _analysis_service_instance is None:
        _analysis_service_instance = AnalysisService(supabase_client)
    return _analysis_service_instance
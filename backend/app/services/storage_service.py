"""Storage service for handling Supabase Storage operations."""

import asyncio
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from loguru import logger
from supabase import Client

from app.utils.exceptions import FileUploadError


class StorageService:
    """Service for managing file uploads and storage operations."""

    def __init__(self, supabase_client: Client) -> None:
        """Initialize storage service."""
        self.supabase = supabase_client

    async def upload_image(
        self,
        user_id: UUID,
        image_data: bytes,
        filename: str,
        image_type: str = "analysis",
    ) -> str:
        """Upload image to Supabase Storage and return URL."""
        try:
            # Determine bucket based on image type
            bucket_name = self._get_bucket_name(image_type)
            
            # Generate unique file path
            file_extension = self._get_file_extension(filename)
            unique_filename = f"{uuid4()}{file_extension}"
            file_path = f"{user_id}/{unique_filename}"

            logger.info(f"📤 Uploading image to {bucket_name}/{file_path}")

            # Upload to Supabase Storage
            response = self.supabase.storage.from_(bucket_name).upload(
                file_path, image_data, {"content-type": self._get_mime_type(file_extension)}
            )

            if hasattr(response, 'error') and response.error:
                raise FileUploadError(
                    f"Storage upload failed: {response.error}",
                    filename=filename,
                    file_size=len(image_data),
                )

            # Get public URL
            public_url = self.supabase.storage.from_(bucket_name).get_public_url(file_path)

            # Store metadata in database
            await self._store_image_metadata(
                user_id=user_id,
                original_filename=filename,
                storage_path=file_path,
                storage_bucket=bucket_name,
                file_size=len(image_data),
                image_type=image_type,
                public_url=public_url,
            )

            logger.info(f"✅ Image uploaded successfully: {public_url}")
            return public_url

        except Exception as e:
            logger.error(f"❌ Image upload failed: {str(e)}")
            raise FileUploadError(
                f"Failed to upload image: {str(e)}",
                filename=filename,
                file_size=len(image_data),
            ) from e

    async def delete_image_by_url(self, image_url: str) -> None:
        """Delete image by URL."""
        try:
            # Extract path from URL
            # Format: https://project.supabase.co/storage/v1/object/public/bucket/path
            url_parts = image_url.split("/")
            if len(url_parts) < 3:
                raise FileUploadError("Invalid image URL format")

            bucket_name = url_parts[-2]
            file_path = url_parts[-1]

            # Delete from storage
            response = self.supabase.storage.from_(bucket_name).remove([file_path])

            if hasattr(response, 'error') and response.error:
                logger.warning(f"Storage deletion warning: {response.error}")

            # Remove metadata from database
            self.supabase.table("stored_images").delete().eq(
                "storage_path", file_path
            ).execute()

            logger.info(f"🗑️ Image deleted: {image_url}")

        except Exception as e:
            logger.error(f"Failed to delete image: {str(e)}")
            # Don't raise exception for deletion failures to avoid blocking other operations

    async def get_image_metadata(self, image_url: str) -> dict | None:
        """Get image metadata from database."""
        try:
            url_parts = image_url.split("/")
            file_path = url_parts[-1]

            response = (
                self.supabase.table("stored_images")
                .select("*")
                .eq("storage_path", file_path)
                .single()
                .execute()
            )

            return response.data

        except Exception as e:
            logger.error(f"Failed to get image metadata: {str(e)}")
            return None

    async def cleanup_expired_images(self) -> None:
        """Clean up expired temporary images."""
        try:
            # Find expired images
            response = (
                self.supabase.table("stored_images")
                .select("*")
                .eq("is_temporary", True)
                .lt("expires_at", datetime.now().isoformat())
                .execute()
            )

            expired_images = response.data
            if not expired_images:
                return

            logger.info(f"🧹 Cleaning up {len(expired_images)} expired images")

            for image in expired_images:
                try:
                    # Delete from storage
                    self.supabase.storage.from_(image["storage_bucket"]).remove(
                        [image["storage_path"]]
                    )

                    # Delete metadata
                    self.supabase.table("stored_images").delete().eq(
                        "id", image["id"]
                    ).execute()

                except Exception as e:
                    logger.error(f"Failed to delete expired image {image['id']}: {str(e)}")

        except Exception as e:
            logger.error(f"Failed to cleanup expired images: {str(e)}")

    async def _store_image_metadata(
        self,
        user_id: UUID,
        original_filename: str,
        storage_path: str,
        storage_bucket: str,
        file_size: int,
        image_type: str,
        public_url: str,
    ) -> None:
        """Store image metadata in database."""
        try:
            metadata = {
                "user_id": str(user_id),
                "original_filename": original_filename,
                "storage_path": storage_path,
                "storage_bucket": storage_bucket,
                "file_size_bytes": file_size,
                "mime_type": self._get_mime_type(self._get_file_extension(original_filename)),
                "image_type": image_type,
                "is_temporary": image_type == "temp",
                "expires_at": (
                    datetime.now() + timedelta(hours=24)
                    if image_type == "temp"
                    else None
                ),
            }

            self.supabase.table("stored_images").insert(metadata).execute()

        except Exception as e:
            logger.error(f"Failed to store image metadata: {str(e)}")
            # Don't raise to avoid failing the entire upload

    def _get_bucket_name(self, image_type: str) -> str:
        """Get appropriate bucket name for image type."""
        bucket_map = {
            "analysis": "user-images",
            "report": "report-images",
            "avatar": "avatars",
            "temp": "user-images",
        }
        return bucket_map.get(image_type, "user-images")

    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename."""
        if "." in filename:
            return "." + filename.split(".")[-1].lower()
        return ".jpg"  # Default extension

    def _get_mime_type(self, file_extension: str) -> str:
        """Get MIME type from file extension."""
        mime_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg", 
            ".png": "image/png",
            ".webp": "image/webp",
        }
        return mime_map.get(file_extension.lower(), "image/jpeg")


# Global service instance
_storage_service_instance: StorageService | None = None


def get_storage_service(supabase_client: Client) -> StorageService:
    """Get or create storage service instance."""
    global _storage_service_instance
    if _storage_service_instance is None:
        _storage_service_instance = StorageService(supabase_client)
    return _storage_service_instance
"""Image processing utilities."""

import io
from typing import Tuple

import cv2
import numpy as np
from PIL import Image

from app.utils.exceptions import ValidationError


class ImageProcessor:
    """Utility class for image processing operations."""

    @staticmethod
    def validate_image_data(image_data: bytes) -> Tuple[bool, str]:
        """Validate image data format and readability."""
        try:
            # Try to open with PIL
            image = Image.open(io.BytesIO(image_data))
            image.verify()
            
            # Check format
            if image.format not in ['JPEG', 'PNG', 'WEBP']:
                return False, f"Unsupported format: {image.format}"
            
            # Check dimensions
            if image.size[0] < 100 or image.size[1] < 100:
                return False, "Image too small (minimum 100x100)"
            
            if image.size[0] > 4000 or image.size[1] > 4000:
                return False, "Image too large (maximum 4000x4000)"
            
            return True, "Valid image"
            
        except Exception as e:
            return False, f"Invalid image data: {str(e)}"

    @staticmethod
    def get_image_info(image_data: bytes) -> dict:
        """Get basic image information."""
        try:
            image = Image.open(io.BytesIO(image_data))
            return {
                "format": image.format,
                "mode": image.mode,
                "size": image.size,
                "width": image.size[0],
                "height": image.size[1],
            }
        except Exception as e:
            raise ValidationError(f"Cannot read image info: {str(e)}")

    @staticmethod
    def prepare_for_analysis(image_data: bytes) -> np.ndarray:
        """Prepare image for MediaPipe analysis."""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            
            # Decode image
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValidationError("Cannot decode image")
            
            # Convert BGR to RGB (MediaPipe expects RGB)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            return image_rgb
            
        except Exception as e:
            raise ValidationError(f"Cannot prepare image for analysis: {str(e)}")

    @staticmethod
    def resize_if_needed(image_data: bytes, max_dimension: int = 1024) -> bytes:
        """Resize image if it's too large, maintaining aspect ratio."""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Check if resize is needed
            if max(image.size) <= max_dimension:
                return image_data
            
            # Calculate new dimensions
            ratio = max_dimension / max(image.size)
            new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
            
            # Resize image
            resized = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert back to bytes
            output = io.BytesIO()
            format_to_use = image.format if image.format in ['JPEG', 'PNG', 'WEBP'] else 'JPEG'
            resized.save(output, format=format_to_use, quality=90)
            
            return output.getvalue()
            
        except Exception as e:
            raise ValidationError(f"Cannot resize image: {str(e)}")
            
    @staticmethod
    def detect_mime_type(image_data: bytes) -> str:
        """Detect MIME type from image data."""
        try:
            image = Image.open(io.BytesIO(image_data))
            format_map = {
                'JPEG': 'image/jpeg',
                'PNG': 'image/png', 
                'WEBP': 'image/webp',
            }
            return format_map.get(image.format, 'image/jpeg')
        except Exception:
            return 'image/jpeg'  # Default fallback
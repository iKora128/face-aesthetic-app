"""Core functionality package for Face Aesthetic API."""

from .facial_analyzer import ModernFacialBeautyAnalyzer, get_facial_analyzer

__all__ = [
    "ModernFacialBeautyAnalyzer",
    "get_facial_analyzer",
]
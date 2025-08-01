"""
Pydantic data models for the scraper system.

This package contains all data models used throughout the scraper pipeline:
- Configuration models for validating site settings
- Content models for raw and processed content
- Output models for standardized JSON generation
"""

from .config import ScraperType, ContentMapping, SiteConfig
from .content import RawContent, EnhancedContent, ContentStatus
from .output import StandardOutput, DealOutput

__all__ = [
    # Configuration models
    "ScraperType",
    "ContentMapping", 
    "SiteConfig",
    
    # Content models
    "RawContent",
    "EnhancedContent",
    "ContentStatus",
    
    # Output models
    "StandardOutput",
    "DealOutput",
]
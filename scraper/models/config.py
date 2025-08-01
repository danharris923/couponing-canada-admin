"""
Configuration models for the scraper system.
These models define the structure and validation for site configuration.
"""

from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, field_validator, ConfigDict


class ScraperType(str, Enum):
    """Supported scraper types."""
    RSS = "rss"
    WORDPRESS = "wordpress" 
    CUSTOM = "custom"


class ContentMapping(BaseModel):
    """
    Defines how to map scraped fields to standard output format.
    
    This model specifies the field paths in the source data that correspond
    to the standard content fields needed by the frontend.
    """
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    title: str = Field(..., min_length=1, description="Field path for title")
    url: str = Field(..., min_length=1, description="Field path for URL")
    image: str = Field(..., min_length=1, description="Field path for image")
    excerpt: str = Field(..., min_length=1, description="Field path for excerpt/description")
    category: Optional[str] = Field(None, description="Field path for category")
    date: Optional[str] = Field(None, description="Field path for publication date")
    
    @field_validator('title', 'url', 'image', 'excerpt')
    @classmethod
    def validate_required_fields(cls, v):
        """Ensure required mapping fields are not empty."""
        if not v or v.strip() == "":
            raise ValueError("Required mapping field cannot be empty")
        return v.strip()


class SiteConfig(BaseModel):
    """
    Main site configuration model.
    
    This model defines all settings needed to configure and run a content site,
    including scraper type, content sources, and processing options.
    """
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    site_name: str = Field(
        ..., 
        min_length=1, 
        max_length=100, 
        description="Display name for the site"
    )
    scraper_type: ScraperType = Field(
        ..., 
        description="Type of scraper to use"
    )
    feeds: List[HttpUrl] = Field(
        ..., 
        min_length=1, 
        description="List of content feed URLs"
    )
    content_mapping: ContentMapping = Field(
        ..., 
        description="Field mapping configuration"
    )
    update_interval: int = Field(
        3600, 
        ge=300, 
        le=86400, 
        description="Update interval in seconds (5min - 24hrs)"
    )
    ai_enhancement_enabled: bool = Field(
        True, 
        description="Enable AI content enhancement"
    )
    affiliate_tag: Optional[str] = Field(
        None, 
        max_length=50, 
        description="Affiliate tracking tag"
    )
    
    @field_validator('site_name')
    @classmethod
    def validate_site_name(cls, v):
        """Ensure site name is valid."""
        if not v or v.strip() == "":
            raise ValueError("Site name cannot be empty")
        return v.strip()
    
    @field_validator('feeds')
    @classmethod
    def validate_feeds(cls, v):
        """Ensure at least one feed URL is provided and limit count."""
        if not v:
            raise ValueError("At least one feed URL is required")
        if len(v) > 20:
            raise ValueError("Maximum 20 feed URLs allowed")
        return v
    
    @field_validator('affiliate_tag')
    @classmethod
    def validate_affiliate_tag(cls, v):
        """Validate affiliate tag format."""
        if v is not None:
            v = v.strip()
            if v == "":
                return None
            if not v.replace('-', '').replace('_', '').isalnum():
                raise ValueError(
                    "Affiliate tag can only contain letters, numbers, hyphens, and underscores"
                )
        return v


class ScraperSettings(BaseModel):
    """
    Runtime settings for scraper operations.
    
    These settings control scraper behavior but are not part of the main
    site configuration that users typically modify.
    """
    
    model_config = ConfigDict(validate_assignment=True)
    
    request_timeout: int = Field(30, ge=5, le=120, description="HTTP request timeout in seconds")
    max_concurrent_requests: int = Field(5, ge=1, le=20, description="Maximum concurrent HTTP requests")
    retry_attempts: int = Field(3, ge=1, le=10, description="Number of retry attempts for failed requests")
    cache_duration: int = Field(3600, ge=300, le=86400, description="Cache duration in seconds")
    user_agent: str = Field(
        "Mozilla/5.0 (compatible; ContentScraper/1.0)", 
        min_length=10,
        description="User agent string for HTTP requests"
    )
    respect_robots_txt: bool = Field(True, description="Whether to respect robots.txt")
    
    @field_validator('user_agent')
    @classmethod
    def validate_user_agent(cls, v):
        """Ensure user agent is reasonable."""
        if not v or v.strip() == "":
            raise ValueError("User agent cannot be empty")
        if len(v.strip()) < 10:
            raise ValueError("User agent should be at least 10 characters")
        return v.strip()
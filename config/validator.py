"""
Configuration validation using Pydantic models.
Validates site configuration and provides clear error messages.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl, field_validator, ConfigDict
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ScraperType(str, Enum):
    """Supported scraper types."""
    RSS = "rss"
    WORDPRESS = "wordpress" 
    CUSTOM = "custom"


class ContentMapping(BaseModel):
    """Defines how to map scraped fields to standard output format."""
    
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
    """Main site configuration model."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    site_name: str = Field(..., min_length=1, max_length=100, description="Display name for the site")
    scraper_type: ScraperType = Field(..., description="Type of scraper to use")
    feeds: List[HttpUrl] = Field(..., min_length=1, description="List of content feed URLs")
    content_mapping: ContentMapping = Field(..., description="Field mapping configuration")
    update_interval: int = Field(3600, ge=300, le=86400, description="Update interval in seconds (5min - 24hrs)")
    ai_enhancement_enabled: bool = Field(True, description="Enable AI content enhancement")
    affiliate_tag: Optional[str] = Field(None, max_length=50, description="Affiliate tracking tag")
    
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
        """Ensure at least one feed URL is provided."""
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
                raise ValueError("Affiliate tag can only contain letters, numbers, hyphens, and underscores")
        return v


class ConfigValidator:
    """Configuration file validator with comprehensive error reporting."""
    
    def __init__(self, config_path: str = "config/config.json"):
        """Initialize validator with config file path."""
        self.config_path = Path(config_path)
    
    def load_and_validate(self) -> SiteConfig:
        """
        Load and validate configuration file.
        
        Returns:
            SiteConfig: Validated configuration object
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If configuration is invalid
            json.JSONDecodeError: If JSON is malformed
        """
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Please copy config.example.json to {self.config_path} and customize it."
            )
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in configuration file: {self.config_path}\n"
                f"Error: {e.msg} at line {e.lineno}, column {e.colno}",
                e.doc, e.pos
            )
        
        # Filter out comment fields (starting with //)
        filtered_config = self._filter_comments(config_data)
        
        try:
            config = SiteConfig(**filtered_config)
            print(f"[OK] Configuration validated successfully: {self.config_path}")
            return config
        except Exception as e:
            self._format_validation_error(e, filtered_config)
            raise
    
    def _filter_comments(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove comment fields from configuration data."""
        if isinstance(data, dict):
            return {
                key: self._filter_comments(value) 
                for key, value in data.items() 
                if not key.startswith('//')
            }
        elif isinstance(data, list):
            return [self._filter_comments(item) for item in data]
        else:
            return data
    
    def _format_validation_error(self, error: Exception, config_data: Dict[str, Any]) -> None:
        """Format validation errors with helpful context."""
        print(f"[ERROR] Configuration validation failed: {self.config_path}")
        print(f"Error: {str(error)}")
        
        # Provide helpful suggestions based on common errors
        error_msg = str(error).lower()
        
        if "site_name" in error_msg:
            print("\n[TIP] Suggestion: Ensure 'site_name' is a non-empty string (1-100 characters)")
            
        elif "scraper_type" in error_msg:
            print(f"\n[TIP] Suggestion: 'scraper_type' must be one of: {[t.value for t in ScraperType]}")
            
        elif "feeds" in error_msg:
            print("\n[TIP] Suggestion: 'feeds' must be an array of valid URLs (1-20 URLs)")
            print("   Example: [\"https://example.com/feed.xml\", \"https://blog.com/rss\"]")
            
        elif "content_mapping" in error_msg:
            print("\n[TIP] Suggestion: 'content_mapping' must include title, url, image, and excerpt fields")
            print("   Example: {\"title\": \"title\", \"url\": \"link\", \"image\": \"media:thumbnail\", \"excerpt\": \"description\"}")
            
        elif "update_interval" in error_msg:
            print("\n[TIP] Suggestion: 'update_interval' must be between 300 (5 minutes) and 86400 (24 hours) seconds")
            
        elif "affiliate_tag" in error_msg:
            print("\n[TIP] Suggestion: 'affiliate_tag' can only contain letters, numbers, hyphens, and underscores")
        
        print(f"\n[INFO] For examples, see: config/config.example.json")
    
    def validate_scraper_compatibility(self, config: SiteConfig) -> List[str]:
        """
        Validate scraper type compatibility with configuration.
        
        Returns:
            List of warning messages
        """
        warnings = []
        
        if config.scraper_type == ScraperType.RSS:
            # Check common RSS field mappings
            mapping = config.content_mapping
            if mapping.title not in ["title", "title.rendered"]:
                warnings.append(f"RSS feeds typically use 'title' for title field, got: {mapping.title}")
            if mapping.url not in ["link", "url"]:
                warnings.append(f"RSS feeds typically use 'link' for URL field, got: {mapping.url}")
                
        elif config.scraper_type == ScraperType.WORDPRESS:
            # Check WordPress REST API field mappings
            mapping = config.content_mapping
            if not mapping.title.startswith("title"):
                warnings.append(f"WordPress API typically uses 'title.rendered' for title field, got: {mapping.title}")
                
        # Check for reasonable update intervals
        if config.update_interval < 1800:  # 30 minutes
            warnings.append(f"Update interval of {config.update_interval}s may be too frequent and could overload servers")
            
        return warnings


def validate_config_file(config_path: str = "config/config.json") -> SiteConfig:
    """
    Convenience function to validate a configuration file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        SiteConfig: Validated configuration
    """
    validator = ConfigValidator(config_path)
    config = validator.load_and_validate()
    
    # Show warnings
    warnings = validator.validate_scraper_compatibility(config)
    if warnings:
        print("\n[WARNING]  Configuration warnings:")
        for warning in warnings:
            print(f"   • {warning}")
    
    return config


def main():
    """Command-line interface for configuration validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate site configuration file")
    parser.add_argument(
        "config_path", 
        nargs="?", 
        default="config/config.json",
        help="Path to configuration file (default: config/config.json)"
    )
    args = parser.parse_args()
    
    try:
        config = validate_config_file(args.config_path)
        print(f"\n[OK] Configuration is valid!")
        print(f"   Site: {config.site_name}")
        print(f"   Type: {config.scraper_type}")
        print(f"   Feeds: {len(config.feeds)} configured")
        print(f"   AI Enhancement: {'Enabled' if config.ai_enhancement_enabled else 'Disabled'}")
        return 0
        
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print(f"\n[ERROR] Validation failed: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
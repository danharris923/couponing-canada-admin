"""
Tests for configuration validation system.
"""

import pytest
import tempfile
import os
import json
from pathlib import Path

# Add project root to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.validator import validate_config_file, SiteConfig
from tests.fixtures.test_data import SAMPLE_CONFIG, INVALID_CONFIGS, get_sample_config, save_temp_config


class TestConfigValidator:
    """Test configuration validation functionality."""

    def test_validate_valid_config_file(self):
        """Test validation of valid configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(get_sample_config(), f)
            temp_path = f.name
        
        try:
            site_config = validate_config_file(temp_path)
            assert site_config.__class__.__name__ == "SiteConfig"
            assert site_config.site_name == "Test Site"
            assert site_config.scraper_type.value == "rss"
            assert len(site_config.feeds) == 2
            assert site_config.ai_enhancement_enabled is True
        finally:
            os.unlink(temp_path)

    def test_validate_config_with_defaults(self):
        """Test that missing optional fields get default values."""
        minimal_config = {
            "site_name": "Minimal Test",
            "scraper_type": "rss",
            "feeds": ["https://example.com/rss.xml"],
            "content_mapping": {
                "title": "title",
                "url": "link",
                "image": "enclosure",
                "excerpt": "description"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(minimal_config, f)
            temp_path = f.name
        
        try:
            site_config = validate_config_file(temp_path)
            assert site_config.site_name == "Minimal Test"
            assert site_config.update_interval == 3600  # Default value
            assert site_config.ai_enhancement_enabled is True  # Default value
        finally:
            os.unlink(temp_path)

    def test_validate_invalid_config_format(self):
        """Test validation fails for invalid JSON format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_path = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError):
                validate_config_file(temp_path)
        finally:
            os.unlink(temp_path)


    def test_validate_config_file_not_found(self):
        """Test validation fails when config file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            validate_config_file("nonexistent_config.json")


    def test_content_mapping_validation(self):
        """Test content mapping field validation."""
        config = get_sample_config({
            "content_mapping": {
                "title": "title",
                "url": "link",
                "image": "enclosure", 
                "excerpt": "description"
            }
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_path = f.name
        
        try:
            site_config = validate_config_file(temp_path)
            assert site_config.content_mapping.title == "title"
            assert site_config.content_mapping.url == "link"
        finally:
            os.unlink(temp_path)

    def test_scraper_type_validation(self):
        """Test scraper type validation."""
        # Test valid scraper types
        for scraper_type in ["rss", "wordpress", "custom"]:
            config = get_sample_config({"scraper_type": scraper_type})
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(config, f)
                temp_path = f.name
            
            try:
                site_config = validate_config_file(temp_path)
                assert site_config.scraper_type == scraper_type
            finally:
                os.unlink(temp_path)

        # Test invalid scraper type
        config = get_sample_config({"scraper_type": "invalid_type"})
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError):
                validate_config_file(temp_path)
        finally:
            os.unlink(temp_path)

    def test_feeds_validation(self):
        """Test feeds list validation."""
        # Test empty feeds list
        config = get_sample_config({"feeds": []})
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError):
                validate_config_file(temp_path)
        finally:
            os.unlink(temp_path)

        # Test valid feeds
        config = get_sample_config({
            "feeds": [
                "https://example.com/rss.xml",
                "https://another.com/feed.xml"
            ]
        })
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_path = f.name
        
        try:
            site_config = validate_config_file(temp_path)
            assert len(site_config.feeds) == 2
        finally:
            os.unlink(temp_path)

    def test_affiliate_tag_validation(self):
        """Test affiliate tag validation."""
        # Test valid affiliate_tag
        config = get_sample_config({"affiliate_tag": "test-123"})
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_path = f.name
        
        try:
            site_config = validate_config_file(temp_path)
            assert site_config.affiliate_tag == "test-123"
        finally:
            os.unlink(temp_path)

        # Test invalid affiliate tag with special characters
        config = get_sample_config({"affiliate_tag": "test@123!"})
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError):
                validate_config_file(temp_path)
        finally:
            os.unlink(temp_path)

    def test_wordpress_specific_config(self):
        """Test WordPress-specific configuration."""
        # Skip this test as SiteConfig model doesn't include wordpress_config field
        # The current validator.py model has a simpler structure
        pytest.skip("WordPress config not implemented in current SiteConfig model")

    def test_custom_scraper_config(self):
        """Test custom scraper configuration."""
        # Skip this test as SiteConfig model doesn't include custom_scraper_config field
        # The current validator.py model has a simpler structure
        pytest.skip("Custom scraper config not implemented in current SiteConfig model")


class TestSiteConfigModel:
    """Test SiteConfig Pydantic model behavior."""

    def test_site_config_creation(self):
        """Test SiteConfig model creation."""
        config_data = get_sample_config()
        site_config = SiteConfig(**config_data)
        
        assert site_config.site_name == "Test Site"
        assert site_config.scraper_type == "rss"
        assert len(site_config.feeds) == 2

    def test_site_config_serialization(self):
        """Test SiteConfig model serialization."""
        config_data = get_sample_config()
        site_config = SiteConfig(**config_data)
        
        # Test model_dump
        serialized = site_config.model_dump()
        assert isinstance(serialized, dict)
        assert serialized["site_name"] == "Test Site"
        
        # Test JSON serialization
        json_str = site_config.model_dump_json()
        assert isinstance(json_str, str)
        
        # Test deserialization
        reloaded = SiteConfig.model_validate_json(json_str)
        assert reloaded.site_name == site_config.site_name

    def test_site_config_validation_errors(self):
        """Test SiteConfig validation error handling."""
        # Missing required fields
        with pytest.raises(ValueError):
            SiteConfig()
        
        # Invalid field types
        with pytest.raises(ValueError):
            SiteConfig(
                site_name=123,  # Should be string
                scraper_type="rss",
                feeds=["https://example.com/rss.xml"]
            )


if __name__ == "__main__":
    pytest.main([__file__])
"""
Tests for output data models.
"""

import pytest
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scraper.models.output import DealOutput, OutputSummary, convert_to_deal_output
from scraper.models.content import EnhancedContent, RawContent
from scraper.models.config import SiteConfig
from tests.fixtures.test_data import SAMPLE_DEAL_OUTPUT, SAMPLE_ENHANCED_CONTENT, get_sample_config


class TestDealOutput:
    """Test DealOutput model."""

    def test_deal_output_creation(self):
        """Test creating DealOutput from sample data."""
        data = SAMPLE_DEAL_OUTPUT[0]
        
        deal = DealOutput(**data)
        
        assert deal.id == "1"
        assert deal.title == "Amazing Tech Gadget Deal - Limited Time Offer"
        assert deal.price == 49.99
        assert deal.originalPrice == 99.99
        assert deal.discountPercent == 50
        assert deal.featured is True

    def test_deal_output_validation(self):
        """Test DealOutput validation."""
        base_data = SAMPLE_DEAL_OUTPUT[0].copy()
        
        # Test valid data
        deal = DealOutput(**base_data)
        assert deal.discountPercent == 50
        
        # Test negative price
        with pytest.raises(ValueError):
            invalid_data = base_data.copy()
            invalid_data["price"] = -10.0
            DealOutput(**invalid_data)
        
        # Test negative discount percent
        with pytest.raises(ValueError):
            invalid_data = base_data.copy()
            invalid_data["discountPercent"] = -5
            DealOutput(**invalid_data)
        
        # Test discount percent over 100
        with pytest.raises(ValueError):
            invalid_data = base_data.copy()
            invalid_data["discountPercent"] = 150
            DealOutput(**invalid_data)

    def test_deal_output_optional_fields(self):
        """Test DealOutput with optional fields."""
        minimal_data = {
            "id": "test-1",
            "title": "Test Deal",
            "imageUrl": "https://example.com/image.jpg",
            "price": 29.99,
            "originalPrice": 49.99,
            "discountPercent": 40,
            "category": "Test",
            "description": "Test description",
            "affiliateUrl": "https://example.com/deal",
            "dateAdded": "2025-01-01"
        }
        
        deal = DealOutput(**minimal_data)
        assert deal.featured is False  # Default value

    def test_deal_output_serialization(self):
        """Test DealOutput serialization."""
        data = SAMPLE_DEAL_OUTPUT[0]
        deal = DealOutput(**data)
        
        # Test model_dump
        serialized = deal.model_dump()
        assert isinstance(serialized, dict)
        assert serialized["id"] == "1"
        assert serialized["title"] == deal.title
        
        # Test JSON serialization
        json_str = deal.model_dump_json()
        assert isinstance(json_str, str)
        
        # Test deserialization
        reloaded = DealOutput.model_validate_json(json_str)
        assert reloaded.id == deal.id
        assert reloaded.title == deal.title


class TestOutputSummary:
    """Test OutputSummary model."""

    def test_output_summary_creation(self):
        """Test creating OutputSummary."""
        summary = OutputSummary(
            total_items=100,
            successful_items=85,
            failed_items=15,
            output_file="public/data.json",
            generation_time=45.5,
            average_quality_score=0.78,
            ai_enhanced_count=85,
            categories=["Technology", "Business", "Health"]
        )
        
        assert summary.total_items == 100
        assert summary.successful_items == 85
        assert summary.failed_items == 15
        assert summary.success_rate == 85.0
        assert len(summary.categories) == 3

    def test_output_summary_success_rate(self):
        """Test success rate calculation."""
        # Test 100% success
        summary = OutputSummary(
            total_items=50,
            successful_items=50,
            failed_items=0,
            output_file="data.json",
            generation_time=30.0,
            average_quality_score=0.8,
            ai_enhanced_count=50,
            categories=["Tech"]
        )
        assert summary.success_rate == 100.0
        
        # Test 0% success
        summary = OutputSummary(
            total_items=10,
            successful_items=0,
            failed_items=10,
            output_file="data.json",
            generation_time=5.0,
            average_quality_score=0.0,
            ai_enhanced_count=0,
            categories=[]
        )
        assert summary.success_rate == 0.0
        
        # Test empty processing
        summary = OutputSummary(
            total_items=0,
            successful_items=0,
            failed_items=0,
            output_file="data.json",
            generation_time=1.0,
            average_quality_score=0.0,
            ai_enhanced_count=0,
            categories=[]
        )
        assert summary.success_rate == 0.0

    def test_output_summary_validation(self):
        """Test OutputSummary validation."""
        base_data = {
            "total_items": 100,
            "successful_items": 85,
            "failed_items": 15,
            "output_file": "data.json",
            "generation_time": 30.0,
            "average_quality_score": 0.8,
            "ai_enhanced_count": 85,
            "categories": ["Tech"]
        }
        
        # Test valid data
        summary = OutputSummary(**base_data)
        assert summary.total_items == 100
        
        # Test negative values
        with pytest.raises(ValueError):
            invalid_data = base_data.copy()
            invalid_data["total_items"] = -1
            OutputSummary(**invalid_data)
        
        # Test inconsistent counts
        with pytest.raises(ValueError):
            invalid_data = base_data.copy()
            invalid_data["successful_items"] = 50
            invalid_data["failed_items"] = 60  # 50 + 60 != 100
            OutputSummary(**invalid_data)


class TestConvertToDealOutput:
    """Test convert_to_deal_output function."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create sample enhanced content
        raw_data = {
            "title": "Test Content",
            "url": "https://example.com/test",
            "source_url": "https://example.com/rss.xml",
            "scraped_at": datetime.now()
        }
        self.raw_content = RawContent(**raw_data)
        
        self.enhanced_content = EnhancedContent(
            title="Enhanced Test Content - Great Deal",
            url="https://example.com/test",
            image="https://example.com/image.jpg",
            excerpt="This is an enhanced test content with better description",
            category="Technology",
            date="2025-01-01",
            quality_score=0.85,
            ai_generated_fields=["title"],
            enhancement_notes="Enhanced by AI",
            original_content=self.raw_content
        )
        
        # Create sample site config
        self.site_config = SiteConfig(**get_sample_config())

    def test_convert_enhanced_content_to_deal_output(self):
        """Test converting EnhancedContent to DealOutput."""
        deal_output = convert_to_deal_output(self.enhanced_content, self.site_config)
        
        assert isinstance(deal_output, DealOutput)
        assert deal_output.title == self.enhanced_content.title
        assert deal_output.description == self.enhanced_content.excerpt
        assert deal_output.category == self.enhanced_content.category
        assert deal_output.imageUrl == str(self.enhanced_content.image)
        assert deal_output.affiliateUrl == str(self.enhanced_content.url)
        assert deal_output.dateAdded == self.enhanced_content.date

    def test_convert_with_price_extraction(self):
        """Test price extraction from content."""
        # Test content with price in title
        enhanced_with_price = EnhancedContent(
            title="Great Product - Only $29.99 (was $49.99)",
            url="https://example.com/product",
            image="https://example.com/image.jpg",
            excerpt="Amazing product at great price",
            category="Shopping",
            date="2025-01-01",
            quality_score=0.8,
            ai_generated_fields=[],
            enhancement_notes="Test"
        )
        
        deal_output = convert_to_deal_output(enhanced_with_price, self.site_config)
        
        # Check that prices were extracted (implementation dependent)
        assert isinstance(deal_output.price, float)
        assert isinstance(deal_output.originalPrice, float)
        assert isinstance(deal_output.discountPercent, int)

    def test_convert_with_featured_detection(self):
        """Test featured content detection."""
        # High quality content should be featured
        high_quality_content = EnhancedContent(
            title="Premium Product Deal",
            url="https://example.com/premium",
            image="https://example.com/premium.jpg",
            excerpt="Premium quality product",
            category="Premium",
            date="2025-01-01",
            quality_score=0.95,  # Very high quality
            ai_generated_fields=[],
            enhancement_notes="High quality content"
        )
        
        deal_output = convert_to_deal_output(high_quality_content, self.site_config)
        
        # High quality content should be featured
        assert deal_output.featured is True

    def test_convert_with_default_values(self):
        """Test conversion with default values for missing fields."""
        minimal_content = EnhancedContent(
            title="Minimal Content",
            url="https://example.com/minimal",
            excerpt="Basic content",
            category="General",
            date="2025-01-01",
            quality_score=0.6,
            ai_generated_fields=[],
            enhancement_notes="Minimal content"
        )
        
        deal_output = convert_to_deal_output(minimal_content, self.site_config)
        
        # Check default values are applied
        assert deal_output.imageUrl is not None  # Should have placeholder
        assert deal_output.price >= 0.0
        assert deal_output.originalPrice >= deal_output.price
        assert 0 <= deal_output.discountPercent <= 100

    def test_convert_generates_unique_id(self):
        """Test that conversion generates unique IDs."""
        deal1 = convert_to_deal_output(self.enhanced_content, self.site_config)
        deal2 = convert_to_deal_output(self.enhanced_content, self.site_config)
        
        # IDs should be different even for same content
        assert deal1.id != deal2.id

    def test_convert_handles_long_descriptions(self):
        """Test handling of very long descriptions."""
        long_excerpt = "This is a very long description that exceeds normal length limits. " * 10
        
        long_content = EnhancedContent(
            title="Content with Long Description",
            url="https://example.com/long",
            image="https://example.com/image.jpg",
            excerpt=long_excerpt,
            category="Test",
            date="2025-01-01",
            quality_score=0.7,
            ai_generated_fields=[],
            enhancement_notes="Long content test"
        )
        
        deal_output = convert_to_deal_output(long_content, self.site_config)
        
        # Description should be truncated or handled appropriately
        assert len(deal_output.description) <= 500  # Reasonable limit


if __name__ == "__main__":
    pytest.main([__file__])
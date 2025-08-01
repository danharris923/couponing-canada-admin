"""
Tests for content data models.
"""

import pytest
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scraper.models.content import (
    RawContent, EnhancedContent, ContentProcessingResult, 
    BatchProcessingResult, ContentStatus
)
from tests.fixtures.test_data import SAMPLE_RAW_CONTENT, SAMPLE_ENHANCED_CONTENT


class TestRawContent:
    """Test RawContent model."""

    def test_raw_content_creation(self):
        """Test creating RawContent from sample data."""
        data = SAMPLE_RAW_CONTENT[0].copy()
        data['scraped_at'] = datetime.now()
        
        content = RawContent(**data)
        
        assert content.title == "Amazing Tech Gadget Deal"
        assert content.url == "https://example.com/tech-deal"
        assert content.category == "Technology"
        assert isinstance(content.scraped_at, datetime)

    def test_raw_content_with_optional_fields(self):
        """Test RawContent with optional fields missing."""
        minimal_data = {
            "title": "Test Title",
            "url": "https://example.com/test",
            "source_url": "https://example.com/rss.xml",
            "scraped_at": datetime.now()
        }
        
        content = RawContent(**minimal_data)
        
        assert content.title == "Test Title"
        assert content.image is None
        assert content.excerpt is None
        assert content.category is None

    def test_raw_content_validation(self):
        """Test RawContent validation."""
        # Test missing required fields
        with pytest.raises(ValueError):
            RawContent()
        
        # Test invalid URL format
        with pytest.raises(ValueError):
            RawContent(
                title="Test",
                url="not-a-url",
                source_url="https://example.com/rss.xml",
                scraped_at=datetime.now()
            )

    def test_raw_content_serialization(self):
        """Test RawContent serialization."""
        data = SAMPLE_RAW_CONTENT[0].copy()
        data['scraped_at'] = datetime.now()
        
        content = RawContent(**data)
        
        # Test model_dump
        serialized = content.model_dump()
        assert isinstance(serialized, dict)
        assert serialized["title"] == content.title
        
        # Test JSON serialization
        json_str = content.model_dump_json()
        assert isinstance(json_str, str)


class TestEnhancedContent:
    """Test EnhancedContent model."""

    def test_enhanced_content_creation(self):
        """Test creating EnhancedContent."""
        raw_data = SAMPLE_RAW_CONTENT[0].copy()
        raw_data['scraped_at'] = datetime.now()
        raw_content = RawContent(**raw_data)
        
        enhanced = EnhancedContent(
            title="Enhanced Title",
            url="https://example.com/test",
            image="https://example.com/image.jpg",
            excerpt="Enhanced excerpt with better engagement",
            category="Technology",
            date="2025-01-01",
            quality_score=0.85,
            ai_generated_fields=["title", "excerpt"],
            enhancement_notes="Enhanced by AI",
            original_content=raw_content
        )
        
        assert enhanced.title == "Enhanced Title"
        assert enhanced.quality_score == 0.85
        assert "title" in enhanced.ai_generated_fields
        assert enhanced.original_content.title == "Amazing Tech Gadget Deal"

    def test_enhanced_content_quality_score_validation(self):
        """Test quality score validation."""
        base_data = {
            "title": "Test Title",
            "url": "https://example.com/test",
            "image": "https://example.com/image.jpg",
            "excerpt": "Test excerpt",
            "category": "Technology",
            "date": "2025-01-01",
            "ai_generated_fields": [],
            "enhancement_notes": "Test"
        }
        
        # Test valid quality scores
        for score in [0.0, 0.5, 1.0]:
            enhanced = EnhancedContent(**base_data, quality_score=score)
            assert enhanced.quality_score == score
        
        # Test invalid quality scores
        for score in [-0.1, 1.1, 2.0]:
            with pytest.raises(ValueError):
                EnhancedContent(**base_data, quality_score=score)

    def test_enhanced_content_without_original(self):
        """Test EnhancedContent without original content."""
        enhanced = EnhancedContent(
            title="Test Title",
            url="https://example.com/test",
            image="https://example.com/image.jpg",
            excerpt="Test excerpt",
            category="Technology", 
            date="2025-01-01",
            quality_score=0.7,
            ai_generated_fields=[],
            enhancement_notes="Test enhancement"
        )
        
        assert enhanced.original_content is None


class TestContentStatus:
    """Test ContentStatus enum."""

    def test_content_status_values(self):
        """Test ContentStatus enum values."""
        assert ContentStatus.PENDING == "pending"
        assert ContentStatus.ENHANCED == "enhanced"
        assert ContentStatus.VALIDATED == "validated"
        assert ContentStatus.REJECTED == "rejected"

    def test_content_status_usage(self):
        """Test using ContentStatus in models."""
        result = ContentProcessingResult(
            status=ContentStatus.VALIDATED,
            message="Content validated successfully",
            processing_time=1.5,
            data={}
        )
        
        assert result.status == ContentStatus.VALIDATED
        assert result.status == "validated"


class TestContentProcessingResult:
    """Test ContentProcessingResult model."""

    def test_processing_result_creation(self):
        """Test creating ContentProcessingResult."""
        result = ContentProcessingResult(
            status=ContentStatus.ENHANCED,
            message="Content enhanced successfully",
            processing_time=2.3,
            data={"enhanced_fields": ["title"]}
        )
        
        assert result.status == ContentStatus.ENHANCED
        assert result.message == "Content enhanced successfully"
        assert result.processing_time == 2.3
        assert result.data["enhanced_fields"] == ["title"]

    def test_processing_result_validation(self):
        """Test ContentProcessingResult validation."""
        # Test negative processing time
        with pytest.raises(ValueError):
            ContentProcessingResult(
                status=ContentStatus.PENDING,
                message="Test",
                processing_time=-1.0,
                data={}
            )


class TestBatchProcessingResult:
    """Test BatchProcessingResult model."""

    def test_batch_result_creation(self):
        """Test creating BatchProcessingResult."""
        result = BatchProcessingResult(
            total_items=10,
            successful_items=8,
            failed_items=2,
            processing_time=15.5,
            results=[],
            errors=["Error 1", "Error 2"]
        )
        
        assert result.total_items == 10
        assert result.successful_items == 8
        assert result.failed_items == 2
        assert result.success_rate == 80.0
        assert len(result.errors) == 2

    def test_batch_result_success_rate_calculation(self):
        """Test success rate calculation."""
        # Test 100% success rate
        result = BatchProcessingResult(
            total_items=5,
            successful_items=5,
            failed_items=0,
            processing_time=10.0,
            results=[],
            errors=[]
        )
        assert result.success_rate == 100.0
        
        # Test 0% success rate
        result = BatchProcessingResult(
            total_items=5,
            successful_items=0,
            failed_items=5,
            processing_time=10.0,
            results=[],
            errors=[]
        )
        assert result.success_rate == 0.0
        
        # Test empty batch
        result = BatchProcessingResult(
            total_items=0,
            successful_items=0,
            failed_items=0,
            processing_time=0.0,
            results=[],
            errors=[]
        )
        assert result.success_rate == 0.0

    def test_batch_result_validation(self):
        """Test BatchProcessingResult validation."""
        # Test inconsistent counts
        with pytest.raises(ValueError):
            BatchProcessingResult(
                total_items=10,
                successful_items=8,
                failed_items=5,  # 8 + 5 != 10
                processing_time=10.0,
                results=[],
                errors=[]
            )
        
        # Test negative values
        with pytest.raises(ValueError):
            BatchProcessingResult(
                total_items=-1,
                successful_items=0,
                failed_items=0,
                processing_time=10.0,
                results=[],
                errors=[]
            )


if __name__ == "__main__":
    pytest.main([__file__])
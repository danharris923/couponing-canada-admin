"""
Integration tests for the complete content processing pipeline.
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add project root to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scraper.main import ContentPipeline
from scraper.models.config import SiteConfig, ScraperSettings
from scraper.models.output import OutputSummary
from tests.fixtures.test_data import get_sample_config, SAMPLE_RSS_FEED


class TestFullPipeline:
    """Integration tests for the complete content processing pipeline."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = SiteConfig(**get_sample_config())
        self.settings = ScraperSettings()
        self.pipeline = ContentPipeline(self.config, self.settings)

    @pytest.mark.asyncio
    async def test_complete_pipeline_with_ai_enabled(self):
        """Test complete pipeline with AI enhancement enabled."""
        # Mock RSS feed response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=SAMPLE_RSS_FEED)
        mock_response.headers = {}
        
        # Mock AI agent responses
        mock_enhanced_content = Mock()
        mock_enhanced_content.title = "Enhanced Article Title"
        mock_enhanced_content.excerpt = "Enhanced article description"
        mock_enhanced_content.category = "Technology"
        mock_enhanced_content.quality_score = 0.8
        mock_enhanced_content.ai_generated_fields = ["excerpt"]
        mock_enhanced_content.enhancement_notes = "Enhanced by AI"
        mock_enhanced_content.url = "https://example.com/article1"
        mock_enhanced_content.image = "https://example.com/image1.jpg"
        mock_enhanced_content.date = "2025-01-01"
        
        mock_quality_result = Mock()
        mock_quality_result.overall_quality_score = 0.8
        mock_quality_result.recommendation = "validated"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            output_path = temp_file.name
        
        try:
            with patch.multiple(
                self.pipeline.scraper_module,
                scrape_all_feeds=AsyncMock(return_value=[]),
                session=Mock()
            ), patch.object(
                self.pipeline.scraper_module.session, 'get', return_value=mock_response
            ), patch.object(
                self.pipeline.content_enhancer, 'enhance_content',
                return_value=mock_enhanced_content
            ), patch.object(
                self.pipeline.quality_validator, 'batch_validate',
                return_value=[mock_quality_result]
            ), patch.object(
                self.pipeline.quality_validator, 'filter_high_quality_content',
                return_value=[mock_enhanced_content]
            ):
                # Mock the scraper to return sample content
                self.pipeline.scraper_module.scrape_all_feeds = AsyncMock(return_value=[
                    Mock(
                        title="Test Article",
                        url="https://example.com/test",
                        excerpt="Test excerpt",
                        category="Technology",
                        image="https://example.com/test.jpg",
                        date="2025-01-01",
                        scraped_at=Mock()
                    )
                ])
                
                summary = await self.pipeline.run_pipeline(output_path)
                
                assert summary.__class__.__name__ == "OutputSummary"
                assert summary.successful_items > 0
                assert os.path.exists(output_path)
                
                # Verify output file contains valid JSON
                with open(output_path, 'r') as f:
                    output_data = json.load(f)
                    assert isinstance(output_data, list)
                    
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    @pytest.mark.asyncio
    async def test_pipeline_with_ai_disabled(self):
        """Test pipeline with AI enhancement disabled."""
        # Disable AI enhancement
        self.config.ai_enhancement_enabled = False
        ai_disabled_pipeline = ContentPipeline(self.config, self.settings)
        
        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=SAMPLE_RSS_FEED)
        mock_response.headers = {}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            output_path = temp_file.name
        
        try:
            with patch.object(
                ai_disabled_pipeline.scraper_module.session, 'get', return_value=mock_response
            ):
                summary = await ai_disabled_pipeline.run_pipeline(output_path)
                
                assert summary.__class__.__name__ == "OutputSummary"
                assert summary.ai_enhanced_count == 0  # No AI enhancement
                assert os.path.exists(output_path)
                
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    @pytest.mark.asyncio
    async def test_pipeline_error_handling(self):
        """Test pipeline error handling."""
        # Simulate scraper error
        with patch.object(
            self.pipeline.scraper_module, 'scrape_all_feeds',
            side_effect=Exception("Scraper error")
        ):
            with pytest.raises(Exception):
                await self.pipeline.run_pipeline("test_output.json")

    @pytest.mark.asyncio
    async def test_pipeline_no_content_scraped(self):
        """Test pipeline behavior when no content is scraped."""
        with patch.object(
            self.pipeline.scraper_module, 'scrape_all_feeds',
            return_value=[]
        ):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                output_path = temp_file.name
            
            try:
                summary = await self.pipeline.run_pipeline(output_path)
                
                assert summary.total_items == 0
                assert summary.successful_items == 0
                assert summary.success_rate == 0.0
                
            finally:
                if os.path.exists(output_path):
                    os.unlink(output_path)

    @pytest.mark.asyncio
    async def test_pipeline_partial_failures(self):
        """Test pipeline with some content processing failures."""
        # Mock mixed success/failure scenario
        mock_raw_content = [
            Mock(title="Good Content", url="https://example.com/good"),
            Mock(title="Bad Content", url="https://example.com/bad")
        ]
        
        # First item succeeds, second fails
        def mock_enhance_side_effect(content):
            if "good" in content.url:
                enhanced = Mock()
                enhanced.title = "Enhanced Good Content"
                enhanced.quality_score = 0.8
                return enhanced
            else:
                raise Exception("Enhancement failed")
        
        with patch.object(
            self.pipeline.scraper_module, 'scrape_all_feeds',
            return_value=mock_raw_content
        ), patch.object(
            self.pipeline.content_enhancer, 'enhance_content',
            side_effect=mock_enhance_side_effect
        ):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                output_path = temp_file.name
            
            try:
                summary = await self.pipeline.run_pipeline(output_path)
                
                assert summary.total_items == 2
                assert summary.failed_items > 0
                assert summary.success_rate < 100.0
                
            finally:
                if os.path.exists(output_path):
                    os.unlink(output_path)

    @pytest.mark.asyncio
    async def test_pipeline_statistics_tracking(self):
        """Test that pipeline correctly tracks processing statistics."""
        mock_content = [Mock(title="Test", url="https://example.com/test")]
        
        with patch.object(
            self.pipeline.scraper_module, 'scrape_all_feeds',
            return_value=mock_content
        ), patch.object(
            self.pipeline.content_enhancer, 'enhance_content',
            return_value=Mock(title="Enhanced", quality_score=0.8)
        ), patch.object(
            self.pipeline.quality_validator, 'batch_validate',
            return_value=[Mock(overall_quality_score=0.8)]
        ), patch.object(
            self.pipeline.quality_validator, 'filter_high_quality_content',
            return_value=[Mock()]
        ):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                output_path = temp_file.name
            
            try:
                summary = await self.pipeline.run_pipeline(output_path)
                
                # Check that statistics are properly tracked
                assert summary.total_items == 1
                assert summary.generation_time > 0
                assert hasattr(summary, 'average_quality_score')
                
            finally:
                if os.path.exists(output_path):
                    os.unlink(output_path)


class TestPipelineConfiguration:
    """Test different pipeline configurations."""

    def test_rss_scraper_initialization(self):
        """Test pipeline with RSS scraper configuration."""
        config = SiteConfig(**get_sample_config({"scraper_type": "rss"}))
        pipeline = ContentPipeline(config)
        
        assert pipeline.config.scraper_type == "rss"
        assert pipeline.scraper_module is not None

    def test_wordpress_scraper_initialization(self):
        """Test pipeline with WordPress scraper configuration."""
        wp_config = get_sample_config({
            "scraper_type": "wordpress",
            "wordpress_config": {
                "base_url": "https://example.com",
                "use_api": True
            }
        })
        config = SiteConfig(**wp_config)
        pipeline = ContentPipeline(config)
        
        assert pipeline.config.scraper_type == "wordpress"

    def test_custom_scraper_initialization(self):
        """Test pipeline with custom scraper configuration."""
        custom_config = get_sample_config({
            "scraper_type": "custom",
            "custom_scraper_config": {
                "module_path": "custom.scraper",
                "class_name": "CustomScraper"
            }
        })
        config = SiteConfig(**custom_config)
        pipeline = ContentPipeline(config)
        
        assert pipeline.config.scraper_type == "custom"

    def test_invalid_scraper_type(self):
        """Test pipeline with invalid scraper type."""
        with pytest.raises(ValueError):
            invalid_config = get_sample_config({"scraper_type": "invalid"})
            config = SiteConfig(**invalid_config)
            ContentPipeline(config)


class TestPipelineOutput:
    """Test pipeline output generation."""

    @pytest.mark.asyncio
    async def test_output_file_creation(self):
        """Test that output file is created correctly."""
        config = SiteConfig(**get_sample_config())
        pipeline = ContentPipeline(config)
        
        mock_content = [Mock(
            title="Test Content",
            url="https://example.com/test",
            image="https://example.com/test.jpg",
            excerpt="Test excerpt",
            category="Technology",
            date="2025-01-01",
            quality_score=0.8
        )]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            output_path = temp_file.name
        
        try:
            with patch.object(
                pipeline, '_scrape_content',
                return_value=[]
            ), patch.object(
                pipeline, '_generate_output',
                return_value=[Mock(model_dump=lambda: {"id": "1", "title": "Test"})]
            ):
                await pipeline.run_pipeline(output_path)
                
                assert os.path.exists(output_path)
                
                with open(output_path, 'r') as f:
                    data = json.load(f)
                    assert isinstance(data, list)
                    
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    @pytest.mark.asyncio
    async def test_output_directory_creation(self):
        """Test that output directory is created if it doesn't exist."""
        config = SiteConfig(**get_sample_config())
        pipeline = ContentPipeline(config)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = os.path.join(temp_dir, "nested", "dir", "output.json")
            
            with patch.object(
                pipeline, '_scrape_content',
                return_value=[]
            ), patch.object(
                pipeline, '_generate_output',
                return_value=[]
            ):
                await pipeline.run_pipeline(nested_path)
                
                assert os.path.exists(nested_path)


if __name__ == "__main__":
    pytest.main([__file__])
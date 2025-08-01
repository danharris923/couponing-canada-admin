"""
Tests for Content Enhancer AI agent.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

# Add project root to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scraper.agents.content_enhancer import ContentEnhancerAgent, ContentEnhancerDependencies
from scraper.models.config import SiteConfig
from scraper.models.content import RawContent, EnhancedContent
from tests.fixtures.test_data import get_sample_config, SAMPLE_RAW_CONTENT, SAMPLE_LLM_RESPONSES


class TestContentEnhancerAgent:
    """Test Content Enhancer AI agent functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = SiteConfig(**get_sample_config())
        self.agent = ContentEnhancerAgent(self.config)
        
        # Create sample raw content
        raw_data = SAMPLE_RAW_CONTENT[0].copy()
        from datetime import datetime
        raw_data['scraped_at'] = datetime.now()
        self.raw_content = RawContent(**raw_data)

    def test_agent_initialization(self):
        """Test Content Enhancer agent initialization."""
        assert self.agent.dependencies.site_config == self.config
        assert self.agent.dependencies.quality_threshold == 0.7
        assert self.agent.dependencies.max_description_length == 200
        assert self.agent.dependencies.enhancement_style == "engaging"

    def test_custom_agent_configuration(self):
        """Test agent with custom configuration."""
        custom_agent = ContentEnhancerAgent(
            self.config,
            quality_threshold=0.8,
            max_description_length=300,
            enhancement_style="professional"
        )
        
        assert custom_agent.dependencies.quality_threshold == 0.8
        assert custom_agent.dependencies.max_description_length == 300
        assert custom_agent.dependencies.enhancement_style == "professional"

    @pytest.mark.asyncio
    async def test_enhance_content_success(self):
        """Test successful content enhancement."""
        # Mock the LLM responses
        mock_enhanced_excerpt = Mock()
        mock_enhanced_excerpt.data = SAMPLE_LLM_RESPONSES["content_enhancement"]["enhanced_excerpt"]
        
        mock_improved_title = Mock()
        mock_improved_title.data = SAMPLE_LLM_RESPONSES["content_enhancement"]["enhanced_title"]
        
        with patch('scraper.agents.content_enhancer.content_enhancer_agent.run', 
                  side_effect=[mock_enhanced_excerpt, mock_improved_title]) as mock_run:
            
            enhanced = await self.agent.enhance_content(self.raw_content)
            
            assert isinstance(enhanced, EnhancedContent)
            assert enhanced.title != self.raw_content.title  # Should be enhanced
            assert enhanced.excerpt != self.raw_content.excerpt  # Should be enhanced
            assert enhanced.original_content == self.raw_content
            assert len(enhanced.ai_generated_fields) > 0

    @pytest.mark.asyncio
    async def test_enhance_content_with_missing_fields(self):
        """Test content enhancement with missing fields."""
        # Create raw content with missing fields
        minimal_raw = RawContent(
            title="Minimal Title",
            url="https://example.com/minimal",
            source_url="https://example.com/rss.xml",
            scraped_at=self.raw_content.scraped_at
            # Missing: image, excerpt, category
        )
        
        # Mock LLM responses
        mock_enhanced_excerpt = Mock()
        mock_enhanced_excerpt.data = "Enhanced excerpt for minimal content"
        
        mock_generated_content = Mock()
        mock_generated_content.data = {
            "image": "/placeholder-deal.svg",
            "category": "General"
        }
        
        with patch('scraper.agents.content_enhancer.content_enhancer_agent.run',
                  side_effect=[mock_enhanced_excerpt, mock_generated_content]):
            
            enhanced = await self.agent.enhance_content(minimal_raw)
            
            assert enhanced.image is not None
            assert enhanced.category is not None
            assert "image" in enhanced.ai_generated_fields
            assert "category" in enhanced.ai_generated_fields

    @pytest.mark.asyncio
    async def test_enhance_content_title_improvement(self):
        """Test title improvement logic."""
        # Create content with short, non-engaging title
        short_title_content = RawContent(
            title="Deal",  # Very short title
            url="https://example.com/deal",
            source_url="https://example.com/rss.xml",
            excerpt="Some deal description",
            scraped_at=self.raw_content.scraped_at
        )
        
        mock_enhanced_excerpt = Mock()
        mock_enhanced_excerpt.data = "Enhanced excerpt"
        
        mock_improved_title = Mock()
        mock_improved_title.data = "Amazing Deal - Limited Time Offer"
        
        with patch('scraper.agents.content_enhancer.content_enhancer_agent.run',
                  side_effect=[mock_enhanced_excerpt, mock_improved_title]):
            
            enhanced = await self.agent.enhance_content(short_title_content)
            
            assert enhanced.title != "Deal"
            assert "title" in enhanced.ai_generated_fields

    @pytest.mark.asyncio
    async def test_enhance_content_no_title_improvement_needed(self):
        """Test that good titles are not unnecessarily improved."""
        # Create content with already good title
        good_title_content = RawContent(
            title="How to Build Amazing Apps: A Complete Guide for Developers",
            url="https://example.com/guide",
            source_url="https://example.com/rss.xml",
            excerpt="Comprehensive guide for app development",
            scraped_at=self.raw_content.scraped_at
        )
        
        mock_enhanced_excerpt = Mock()
        mock_enhanced_excerpt.data = "Enhanced comprehensive guide"
        
        with patch('scraper.agents.content_enhancer.content_enhancer_agent.run',
                  return_value=mock_enhanced_excerpt):
            
            enhanced = await self.agent.enhance_content(good_title_content)
            
            # Title should not be changed
            assert enhanced.title == good_title_content.title
            assert "title" not in enhanced.ai_generated_fields

    @pytest.mark.asyncio
    async def test_enhance_content_error_handling(self):
        """Test error handling during content enhancement."""
        with patch('scraper.agents.content_enhancer.content_enhancer_agent.run',
                  side_effect=Exception("LLM Error")):
            
            with pytest.raises(Exception):
                await self.agent.enhance_content(self.raw_content)

    @pytest.mark.asyncio
    async def test_enhance_description_tool(self):
        """Test the enhance_description tool functionality."""
        # This would require mocking the Pydantic AI agent's tool execution
        # For now, we test the agent wrapper functionality
        
        mock_result = Mock()
        mock_result.data = "Enhanced description with better engagement"
        
        with patch('scraper.agents.content_enhancer.content_enhancer_agent.run',
                  return_value=mock_result):
            
            enhanced = await self.agent.enhance_content(self.raw_content)
            
            assert enhanced.excerpt != self.raw_content.excerpt
            assert "excerpt" in enhanced.ai_generated_fields

    def test_enhancement_dependencies_configuration(self):
        """Test ContentEnhancerDependencies configuration."""
        deps = ContentEnhancerDependencies(
            site_config=self.config,
            quality_threshold=0.9,
            max_description_length=150,
            enhancement_style="technical"
        )
        
        assert deps.site_config == self.config
        assert deps.quality_threshold == 0.9
        assert deps.max_description_length == 150
        assert deps.enhancement_style == "technical"

    @pytest.mark.asyncio
    async def test_content_enhancement_quality_score(self):
        """Test that enhanced content gets appropriate quality score."""
        mock_enhanced_excerpt = Mock()
        mock_enhanced_excerpt.data = "High quality enhanced excerpt"
        
        with patch('scraper.agents.content_enhancer.content_enhancer_agent.run',
                  return_value=mock_enhanced_excerpt):
            
            enhanced = await self.agent.enhance_content(self.raw_content)
            
            # Enhanced content should have good quality score
            assert enhanced.quality_score >= 0.7
            assert enhanced.quality_score <= 1.0

    @pytest.mark.asyncio
    async def test_enhancement_notes_generation(self):
        """Test that enhancement notes are properly generated."""
        mock_enhanced_excerpt = Mock()
        mock_enhanced_excerpt.data = "Enhanced excerpt"
        
        with patch('scraper.agents.content_enhancer.content_enhancer_agent.run',
                  return_value=mock_enhanced_excerpt):
            
            enhanced = await self.agent.enhance_content(self.raw_content)
            
            assert enhanced.enhancement_notes is not None
            assert "ContentEnhancerAgent" in enhanced.enhancement_notes
            assert str(len(enhanced.ai_generated_fields)) in enhanced.enhancement_notes

    @pytest.mark.asyncio
    async def test_preserve_original_content(self):
        """Test that original content is preserved."""
        mock_enhanced_excerpt = Mock()
        mock_enhanced_excerpt.data = "Enhanced excerpt"
        
        with patch('scraper.agents.content_enhancer.content_enhancer_agent.run',
                  return_value=mock_enhanced_excerpt):
            
            enhanced = await self.agent.enhance_content(self.raw_content)
            
            assert enhanced.original_content is not None
            assert enhanced.original_content.title == self.raw_content.title
            assert enhanced.original_content.url == self.raw_content.url

    @pytest.mark.asyncio
    async def test_url_preservation(self):
        """Test that URLs are preserved correctly."""
        mock_enhanced_excerpt = Mock()
        mock_enhanced_excerpt.data = "Enhanced excerpt"
        
        with patch('scraper.agents.content_enhancer.content_enhancer_agent.run',
                  return_value=mock_enhanced_excerpt):
            
            enhanced = await self.agent.enhance_content(self.raw_content)
            
            # URL should be preserved exactly
            assert enhanced.url == self.raw_content.url

    @pytest.mark.asyncio
    async def test_date_handling(self):
        """Test proper date handling."""
        mock_enhanced_excerpt = Mock()
        mock_enhanced_excerpt.data = "Enhanced excerpt"
        
        with patch('scraper.agents.content_enhancer.content_enhancer_agent.run',
                  return_value=mock_enhanced_excerpt):
            
            enhanced = await self.agent.enhance_content(self.raw_content)
            
            # Date should be properly formatted
            assert enhanced.date is not None
            # Should be in YYYY-MM-DD format if original had date
            if self.raw_content.date:
                assert enhanced.date == self.raw_content.date
            else:
                # Should use scraped_at date
                assert enhanced.date is not None


class TestContentEnhancerDependencies:
    """Test ContentEnhancerDependencies model."""

    def test_dependencies_creation(self):
        """Test creating dependencies with defaults."""
        config = SiteConfig(**get_sample_config())
        deps = ContentEnhancerDependencies(site_config=config)
        
        assert deps.site_config == config
        assert deps.quality_threshold == 0.7
        assert deps.max_description_length == 200
        assert deps.enhancement_style == "engaging"

    def test_dependencies_custom_values(self):
        """Test creating dependencies with custom values."""
        config = SiteConfig(**get_sample_config())
        deps = ContentEnhancerDependencies(
            site_config=config,
            quality_threshold=0.9,
            max_description_length=300,
            enhancement_style="professional"
        )
        
        assert deps.quality_threshold == 0.9
        assert deps.max_description_length == 300
        assert deps.enhancement_style == "professional"


if __name__ == "__main__":
    pytest.main([__file__])
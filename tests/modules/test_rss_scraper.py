"""
Tests for RSS scraper module.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import xml.etree.ElementTree as ET

# Add project root to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scraper.modules.rss_scraper import RSSScraperModule
from scraper.models.config import SiteConfig, ScraperSettings
from scraper.models.content import RawContent
from tests.fixtures.test_data import get_sample_config, SAMPLE_RSS_FEED


class TestRSSScraperModule:
    """Test RSS scraper functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = SiteConfig(**get_sample_config())
        self.settings = ScraperSettings()
        self.scraper = RSSScraperModule(self.config, self.settings)

    @pytest.mark.asyncio
    async def test_scraper_initialization(self):
        """Test RSS scraper initialization."""
        assert self.scraper.config == self.config
        assert self.scraper.settings == self.settings
        assert len(self.scraper.feeds) == len(self.config.feeds)

    @pytest.mark.asyncio
    async def test_fetch_feed_success(self):
        """Test successful RSS feed fetching."""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=SAMPLE_RSS_FEED)
        mock_response.headers = {}
        
        with patch.object(self.scraper.session, 'get', return_value=mock_response) as mock_get:
            feed_data = await self.scraper._fetch_feed("https://example.com/rss.xml")
            
            assert feed_data is not None
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_feed_http_error(self):
        """Test RSS feed fetching with HTTP error."""
        mock_response = Mock()
        mock_response.status = 404
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        
        with patch.object(self.scraper.session, 'get', return_value=mock_response):
            feed_data = await self.scraper._fetch_feed("https://example.com/nonexistent.xml")
            
            assert feed_data is None

    @pytest.mark.asyncio
    async def test_parse_rss_feed(self):
        """Test RSS feed parsing."""
        # Parse the sample RSS feed
        root = ET.fromstring(SAMPLE_RSS_FEED)
        items = await self.scraper._parse_rss_feed(root, "https://example.com/rss.xml")
        
        assert len(items) == 2
        
        # Check first item
        item1 = items[0]
        assert isinstance(item1, RawContent)
        assert item1.title == "Test Article 1"
        assert item1.url == "https://example.com/article1"
        assert item1.excerpt == "This is a test article about technology"
        assert item1.source_url == "https://example.com/rss.xml"

    @pytest.mark.asyncio
    async def test_extract_title(self):
        """Test title extraction from RSS item."""
        xml_item = """
        <item>
            <title>Test Article Title</title>
        </item>
        """
        item_element = ET.fromstring(xml_item)
        
        title = await self.scraper._extract_title(item_element)
        assert title == "Test Article Title"

    @pytest.mark.asyncio
    async def test_extract_title_missing(self):
        """Test title extraction when title is missing."""
        xml_item = """
        <item>
            <description>Article without title</description>
        </item>
        """
        item_element = ET.fromstring(xml_item)
        
        title = await self.scraper._extract_title(item_element)
        assert title == "Untitled"

    @pytest.mark.asyncio
    async def test_extract_url(self):
        """Test URL extraction from RSS item."""
        xml_item = """
        <item>
            <link>https://example.com/article</link>
        </item>
        """
        item_element = ET.fromstring(xml_item)
        
        url = await self.scraper._extract_url(item_element)
        assert url == "https://example.com/article"

    @pytest.mark.asyncio
    async def test_extract_description(self):
        """Test description extraction from RSS item."""
        xml_item = """
        <item>
            <description>This is the article description</description>
        </item>
        """
        item_element = ET.fromstring(xml_item)
        
        description = await self.scraper._extract_description(item_element)
        assert description == "This is the article description"

    @pytest.mark.asyncio
    async def test_extract_description_with_html(self):
        """Test description extraction with HTML content."""
        xml_item = """
        <item>
            <description><![CDATA[<p>This is <strong>HTML</strong> content</p>]]></description>
        </item>
        """
        item_element = ET.fromstring(xml_item)
        
        description = await self.scraper._extract_description(item_element)
        # HTML should be stripped
        assert "<p>" not in description
        assert "<strong>" not in description
        assert "This is HTML content" in description

    @pytest.mark.asyncio
    async def test_extract_image_from_enclosure(self):
        """Test image extraction from enclosure."""
        xml_item = """
        <item>
            <enclosure url="https://example.com/image.jpg" type="image/jpeg"/>
        </item>
        """
        item_element = ET.fromstring(xml_item)
        
        image = await self.scraper._extract_image_url(item_element)
        assert image == "https://example.com/image.jpg"

    @pytest.mark.asyncio
    async def test_extract_image_from_media_thumbnail(self):
        """Test image extraction from media:thumbnail."""
        xml_item = """
        <item xmlns:media="http://search.yahoo.com/mrss/">
            <media:thumbnail url="https://example.com/thumb.jpg"/>
        </item>
        """
        item_element = ET.fromstring(xml_item)
        
        image = await self.scraper._extract_image_url(item_element)
        assert image == "https://example.com/thumb.jpg"

    @pytest.mark.asyncio
    async def test_extract_date(self):
        """Test date extraction from RSS item."""
        xml_item = """
        <item>
            <pubDate>Mon, 01 Jan 2025 10:00:00 GMT</pubDate>
        </item>
        """
        item_element = ET.fromstring(xml_item)
        
        date = await self.scraper._extract_date(item_element)
        assert date == "2025-01-01"

    @pytest.mark.asyncio
    async def test_extract_category(self):
        """Test category extraction from RSS item."""
        xml_item = """
        <item>
            <category>Technology</category>
        </item>
        """
        item_element = ET.fromstring(xml_item)
        
        category = await self.scraper._extract_category(item_element)
        assert category == "Technology"

    @pytest.mark.asyncio
    async def test_scrape_single_feed(self):
        """Test scraping a single RSS feed."""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=SAMPLE_RSS_FEED)
        mock_response.headers = {}
        
        with patch.object(self.scraper.session, 'get', return_value=mock_response):
            items = await self.scraper.scrape_single_feed("https://example.com/rss.xml")
            
            assert len(items) == 2
            assert all(isinstance(item, RawContent) for item in items)

    @pytest.mark.asyncio
    async def test_scrape_all_feeds(self):
        """Test scraping all configured RSS feeds."""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=SAMPLE_RSS_FEED)
        mock_response.headers = {}
        
        with patch.object(self.scraper.session, 'get', return_value=mock_response):
            all_items = await self.scraper.scrape_all_feeds()
            
            # Should have items from both feeds (2 items each)
            expected_count = len(self.config.feeds) * 2
            assert len(all_items) == expected_count

    @pytest.mark.asyncio
    async def test_scrape_with_rate_limiting(self):
        """Test scraping with rate limiting."""
        # Set very low rate limit for testing
        self.scraper.settings.rate_limit_delay = 0.1
        
        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=SAMPLE_RSS_FEED)
        mock_response.headers = {}
        
        import time
        start_time = time.time()
        
        with patch.object(self.scraper.session, 'get', return_value=mock_response):
            await self.scraper.scrape_all_feeds()
        
        end_time = time.time()
        
        # Should take at least the rate limit delay between requests
        min_expected_time = (len(self.config.feeds) - 1) * 0.1
        assert (end_time - start_time) >= min_expected_time

    @pytest.mark.asyncio
    async def test_scrape_with_caching(self):
        """Test scraping with ETag caching."""
        # First request
        mock_response1 = Mock()
        mock_response1.status = 200
        mock_response1.text = AsyncMock(return_value=SAMPLE_RSS_FEED)
        mock_response1.headers = {"ETag": "test-etag"}
        
        # Second request with same ETag (304 Not Modified)
        mock_response2 = Mock()
        mock_response2.status = 304
        mock_response2.headers = {"ETag": "test-etag"}
        
        with patch.object(self.scraper.session, 'get', side_effect=[mock_response1, mock_response2]):
            # First scrape
            items1 = await self.scraper.scrape_single_feed("https://example.com/rss.xml")
            assert len(items1) == 2
            
            # Second scrape (should use cache)
            items2 = await self.scraper.scrape_single_feed("https://example.com/rss.xml")
            assert len(items2) == 2  # Should return cached items

    @pytest.mark.asyncio
    async def test_scrape_with_custom_mapping(self):
        """Test scraping with custom content mapping."""
        # Update config with custom field mapping
        custom_config = get_sample_config({
            "content_mapping": {
                "title": "title",
                "url": "guid",  # Use guid instead of link
                "image": "media:thumbnail",
                "excerpt": "description"
            }
        })
        
        custom_scraper = RSSScraperModule(SiteConfig(**custom_config), self.settings)
        
        custom_rss = """<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/">
            <channel>
                <item>
                    <title>Custom Test</title>
                    <guid>https://example.com/custom-guid</guid>
                    <link>https://example.com/link</link>
                    <description>Custom description</description>
                    <media:thumbnail url="https://example.com/custom-thumb.jpg"/>
                </item>
            </channel>
        </rss>"""
        
        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=custom_rss)
        mock_response.headers = {}
        
        with patch.object(custom_scraper.session, 'get', return_value=mock_response):
            items = await custom_scraper.scrape_single_feed("https://example.com/custom.xml")
            
            assert len(items) == 1
            # Should use guid instead of link for URL
            assert items[0].url == "https://example.com/custom-guid"

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling during scraping."""
        # Simulate network error
        with patch.object(self.scraper.session, 'get', side_effect=Exception("Network error")):
            items = await self.scraper.scrape_single_feed("https://example.com/error.xml")
            
            # Should return empty list on error
            assert items == []

    @pytest.mark.asyncio
    async def test_malformed_xml_handling(self):
        """Test handling of malformed XML."""
        malformed_xml = "<rss><channel><item><title>Test</title></item>"  # Missing closing tags
        
        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=malformed_xml)
        mock_response.headers = {}
        
        with patch.object(self.scraper.session, 'get', return_value=mock_response):
            items = await self.scraper.scrape_single_feed("https://example.com/malformed.xml")
            
            # Should handle gracefully and return empty list
            assert items == []


if __name__ == "__main__":
    pytest.main([__file__])
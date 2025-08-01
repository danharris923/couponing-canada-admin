"""
RSS scraper module using feedparser and requests.
Implements caching with ETags and Last-Modified headers for efficient scraping.
"""

import logging
from typing import List, Optional
from datetime import datetime
from io import BytesIO

import feedparser
from requests import Response

from scraper.modules.base import BaseScraperModule, ScraperError
from scraper.models.content import RawContent


logger = logging.getLogger(__name__)


class RSSScraperModule(BaseScraperModule):
    """
    RSS feed scraper using feedparser with requests for HTTP handling.
    
    This scraper handles RSS 2.0, RSS 1.0, Atom, and other feed formats
    supported by feedparser, with proper caching and error handling.
    """
    
    async def scrape_feed(self, feed_url: str) -> List[RawContent]:
        """
        Scrape content from an RSS feed.
        
        Args:
            feed_url: URL of the RSS feed
            
        Returns:
            List of RawContent objects
            
        Raises:
            ScraperError: If scraping fails
        """
        self.logger.info(f"Scraping RSS feed: {feed_url}")
        
        try:
            # Make HTTP request with caching
            response = self._make_request(feed_url, use_cache=True)
            
            if response is None:
                # 304 Not Modified or request failed
                self.logger.info(f"Feed not modified or request failed: {feed_url}")
                return []
            
            # Parse feed content
            feed = feedparser.parse(BytesIO(response.content))
            
            # Check for parsing errors
            if feed.bozo:
                self.logger.warning(f"Feed parsing issues for {feed_url}: {feed.bozo_exception}")
                # Continue processing even with minor parsing issues
            
            if not hasattr(feed, 'entries') or not feed.entries:
                self.logger.warning(f"No entries found in feed: {feed_url}")
                return []
            
            # Extract content from feed entries
            content_items = []
            for entry in feed.entries[:50]:  # Limit to 50 most recent entries
                try:
                    content = self._extract_content_from_entry(entry, feed_url)
                    if content and self._is_recent_content(content.date):
                        content_items.append(content)
                        
                except Exception as e:
                    self.logger.warning(f"Failed to extract content from entry: {e}")
                    continue
            
            self.logger.info(f"Successfully extracted {len(content_items)} items from {feed_url}")
            return content_items
            
        except Exception as e:
            raise ScraperError(f"Failed to scrape RSS feed", feed_url, e)
    
    def _extract_content_from_entry(self, entry: feedparser.FeedParserDict, feed_url: str) -> Optional[RawContent]:
        """
        Extract content from a single RSS entry.
        
        Args:
            entry: Feedparser entry object
            feed_url: URL of the source feed
            
        Returns:
            RawContent object or None if extraction fails
        """
        try:
            # Extract title
            title = self._extract_title(entry)
            if not title:
                self.logger.debug("Skipping entry without title")
                return None
            
            # Extract URL
            url = self._extract_url(entry)
            if not url:
                self.logger.debug(f"Skipping entry without URL: {title}")
                return None
            
            # Extract other fields using configured mapping
            image = self._extract_image(entry)
            excerpt = self._extract_excerpt(entry)
            category = self._extract_category(entry)
            date = self._extract_date(entry)
            
            # Create RawContent object
            content = RawContent(
                title=title,
                url=url,
                image=image,
                excerpt=excerpt,
                category=category,
                date=date,
                source_data=dict(entry),  # Store original entry for debugging
                scraper_type="rss",
                source_url=feed_url
            )
            
            return content
            
        except Exception as e:
            self.logger.error(f"Failed to extract content from entry: {e}")
            return None
    
    def _extract_title(self, entry: feedparser.FeedParserDict) -> Optional[str]:
        """Extract title from RSS entry."""
        title_field = self.config.content_mapping.title
        
        # Try configured field first
        title = self._extract_field_value(entry, title_field)
        
        # Fallback to common RSS title fields
        if not title:
            for field in ['title', 'summary', 'description']:
                title = getattr(entry, field, None)
                if title:
                    break
        
        return self._clean_text(title)
    
    def _extract_url(self, entry: feedparser.FeedParserDict) -> Optional[str]:
        """Extract URL from RSS entry."""
        url_field = self.config.content_mapping.url
        
        # Try configured field first
        url = self._extract_field_value(entry, url_field)
        
        # Fallback to common RSS URL fields
        if not url:
            for field in ['link', 'id', 'guid']:
                value = getattr(entry, field, None)
                if value:
                    # Handle GUID objects
                    if hasattr(value, 'href'):
                        url = value.href
                    else:
                        url = str(value)
                    break
        
        return url.strip() if url else None
    
    def _extract_image(self, entry: feedparser.FeedParserDict) -> Optional[str]:
        """Extract image URL from RSS entry."""
        image_field = self.config.content_mapping.image
        
        # Try configured field first
        image = self._extract_field_value(entry, image_field)
        
        # Fallback to common RSS image fields
        if not image:
            # Try media:thumbnail
            if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
                image = entry.media_thumbnail[0].get('url') if entry.media_thumbnail else None
            
            # Try enclosures (for podcasts/media)
            elif hasattr(entry, 'enclosures') and entry.enclosures:
                for enclosure in entry.enclosures:
                    if enclosure.type.startswith('image/'):
                        image = enclosure.href
                        break
            
            # Try media:content
            elif hasattr(entry, 'media_content') and entry.media_content:
                for media in entry.media_content:
                    if media.get('medium') == 'image' or media.get('type', '').startswith('image/'):
                        image = media.get('url')
                        break
            
            # Try summary for embedded images
            elif hasattr(entry, 'summary'):
                import re
                img_match = re.search(r'<img[^>]+src="([^"]+)"', entry.summary)
                if img_match:
                    image = img_match.group(1)
        
        # Clean and validate image URL
        if image:
            image = image.strip()
            # Ensure it's a valid URL
            if not image.startswith(('http://', 'https://')):
                if image.startswith('//'):
                    image = 'https:' + image
                else:
                    image = None
        
        return image
    
    def _extract_excerpt(self, entry: feedparser.FeedParserDict) -> Optional[str]:
        """Extract excerpt/description from RSS entry."""
        excerpt_field = self.config.content_mapping.excerpt
        
        # Try configured field first
        excerpt = self._extract_field_value(entry, excerpt_field)
        
        # Fallback to common RSS description fields
        if not excerpt:
            for field in ['summary', 'description', 'content']:
                value = getattr(entry, field, None)
                if value:
                    # Handle content list (Atom feeds)
                    if isinstance(value, list) and value:
                        excerpt = value[0].get('value', str(value[0]))
                    else:
                        excerpt = str(value)
                    break
        
        # Clean excerpt
        excerpt = self._clean_text(excerpt)
        
        # Truncate if too long
        if excerpt and len(excerpt) > 500:
            excerpt = excerpt[:497] + "..."
        
        return excerpt
    
    def _extract_category(self, entry: feedparser.FeedParserDict) -> Optional[str]:
        """Extract category from RSS entry."""
        if not self.config.content_mapping.category:
            return None
            
        category_field = self.config.content_mapping.category
        
        # Try configured field first
        category = self._extract_field_value(entry, category_field)
        
        # Fallback to common RSS category fields
        if not category:
            # Try tags
            if hasattr(entry, 'tags') and entry.tags:
                category = entry.tags[0].get('term', entry.tags[0].get('label'))
            
            # Try category field
            elif hasattr(entry, 'category'):
                category = entry.category
            
            # Try categories list
            elif hasattr(entry, 'categories') and entry.categories:
                category = entry.categories[0][0] if entry.categories[0] else None
        
        return self._clean_text(category)
    
    def _extract_date(self, entry: feedparser.FeedParserDict) -> Optional[str]:
        """Extract publication date from RSS entry."""
        if not self.config.content_mapping.date:
            return None
            
        date_field = self.config.content_mapping.date
        
        # Try configured field first
        date_str = self._extract_field_value(entry, date_field)
        
        # Fallback to common RSS date fields
        if not date_str:
            for field in ['published', 'updated', 'created']:
                date_str = getattr(entry, field, None)
                if date_str:
                    break
            
            # Try parsed date objects
            if not date_str:
                for field in ['published_parsed', 'updated_parsed']:
                    date_tuple = getattr(entry, field, None)
                    if date_tuple:
                        try:
                            import time
                            date_str = time.strftime('%Y-%m-%d %H:%M:%S', date_tuple)
                        except Exception:
                            pass
                        break
        
        # Normalize date format
        if date_str:
            try:
                from dateutil import parser
                parsed_date = parser.parse(str(date_str))
                return parsed_date.strftime('%Y-%m-%d')
            except Exception:
                return str(date_str)
        
        return None
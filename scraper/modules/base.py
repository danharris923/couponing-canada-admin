"""
Base scraper module defining the interface for all scrapers.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from scraper.models.config import SiteConfig, ScraperSettings
from scraper.models.content import RawContent


logger = logging.getLogger(__name__)


class BaseScraperModule(ABC):
    """
    Abstract base class for all scraper modules.
    
    This class defines the interface that all scraper modules must implement,
    ensuring consistency across different content source types.
    """
    
    def __init__(self, config: SiteConfig, settings: Optional[ScraperSettings] = None):
        """
        Initialize the scraper module.
        
        Args:
            config: Site configuration
            settings: Optional scraper runtime settings
        """
        self.config = config
        self.settings = settings or ScraperSettings()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Setup HTTP session with retries and timeout
        self.session = requests.Session()
        retry_strategy = Retry(
            total=self.settings.retry_attempts,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=0.3
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set user agent
        self.session.headers.update({
            'User-Agent': self.settings.user_agent
        })
        
        # Cache for ETag and Last-Modified headers
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    @abstractmethod
    async def scrape_feed(self, feed_url: str) -> List[RawContent]:
        """
        Scrape content from a single feed URL.
        
        Args:
            feed_url: URL of the feed to scrape
            
        Returns:
            List of RawContent objects
            
        Raises:
            ScraperError: If scraping fails
        """
        pass
    
    async def scrape_all_feeds(self) -> List[RawContent]:
        """
        Scrape content from all configured feeds.
        
        Returns:
            List of RawContent objects from all feeds
        """
        all_content = []
        
        for feed_url in self.config.feeds:
            try:
                self.logger.info(f"Scraping feed: {feed_url}")
                content = await self.scrape_feed(str(feed_url))
                all_content.extend(content)
                self.logger.info(f"Retrieved {len(content)} items from {feed_url}")
                
            except Exception as e:
                self.logger.error(f"Failed to scrape {feed_url}: {e}")
                continue
        
        self.logger.info(f"Total items scraped: {len(all_content)}")
        return all_content
    
    def _make_request(self, url: str, use_cache: bool = True) -> Optional[requests.Response]:
        """
        Make HTTP request with caching support.
        
        Args:
            url: URL to request
            use_cache: Whether to use caching headers
            
        Returns:
            Response object or None if request failed
        """
        headers = {}
        
        # Add caching headers if available and requested
        if use_cache and url in self._cache:
            cache_data = self._cache[url]
            if 'etag' in cache_data:
                headers['If-None-Match'] = cache_data['etag']
            if 'last_modified' in cache_data:
                headers['If-Modified-Since'] = cache_data['last_modified']
        
        try:
            response = self.session.get(
                url,
                headers=headers,
                timeout=self.settings.request_timeout
            )
            
            # Handle 304 Not Modified
            if response.status_code == 304:
                self.logger.debug(f"Content not modified: {url}")
                return None
            
            # Cache headers for future requests
            if use_cache:
                cache_data = {}
                if 'ETag' in response.headers:
                    cache_data['etag'] = response.headers['ETag']
                if 'Last-Modified' in response.headers:
                    cache_data['last_modified'] = response.headers['Last-Modified']
                if cache_data:
                    self._cache[url] = cache_data
            
            response.raise_for_status()
            return response
            
        except requests.RequestException as e:
            self.logger.error(f"Request failed for {url}: {e}")
            return None
    
    def _extract_field_value(self, data: Dict[str, Any], field_path: str) -> Optional[str]:
        """
        Extract value from nested data using dot notation field path.
        
        Args:
            data: Source data dictionary
            field_path: Dot-separated field path (e.g., "title.rendered")
            
        Returns:
            Extracted value as string or None if not found
        """
        try:
            value = data
            for part in field_path.split('.'):
                if isinstance(value, dict):
                    value = value.get(part)
                elif isinstance(value, list) and part.isdigit():
                    index = int(part)
                    value = value[index] if 0 <= index < len(value) else None
                else:
                    return None
                
                if value is None:
                    return None
            
            # Convert to string and clean up
            if value is not None:
                if isinstance(value, (dict, list)):
                    # For complex objects, try to extract meaningful string
                    if isinstance(value, dict) and 'url' in value:
                        return str(value['url'])
                    elif isinstance(value, list) and value:
                        return str(value[0])
                    else:
                        return str(value)
                else:
                    return str(value).strip()
            
            return None
            
        except (KeyError, IndexError, ValueError, TypeError):
            return None
    
    def _clean_text(self, text: Optional[str]) -> Optional[str]:
        """
        Clean and normalize text content.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text or None if empty
        """
        if not text:
            return None
            
        # Basic cleaning
        import html
        import re
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove HTML tags if present
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove empty brackets and other artifacts
        text = re.sub(r'\[\s*\]|\(\s*\)', '', text).strip()
        
        return text if text else None
    
    def _generate_content_id(self, title: str, url: str) -> str:
        """
        Generate unique content ID from title and URL.
        
        Args:
            title: Content title
            url: Content URL
            
        Returns:
            Unique identifier string
        """
        import hashlib
        
        # Create hash from title and URL
        content_hash = hashlib.md5(f"{title}{url}".encode()).hexdigest()[:12]
        
        # Create readable ID from title
        title_id = ''.join(c.lower() for c in title if c.isalnum() or c.isspace())
        title_id = '-'.join(title_id.split())[:30]  # First 30 chars of title
        
        return f"{title_id}-{content_hash}"
    
    def _is_recent_content(self, date_str: Optional[str], max_age_days: int = 30) -> bool:
        """
        Check if content is recent enough to include.
        
        Args:
            date_str: Date string to check
            max_age_days: Maximum age in days
            
        Returns:
            True if content is recent enough
        """
        if not date_str:
            return True  # Include if no date
        
        try:
            # Try to parse various date formats
            from dateutil import parser
            
            content_date = parser.parse(date_str)
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            return content_date.replace(tzinfo=None) >= cutoff_date
            
        except Exception:
            return True  # Include if date parsing fails


class ScraperError(Exception):
    """Exception raised by scraper modules."""
    
    def __init__(self, message: str, url: Optional[str] = None, original_error: Optional[Exception] = None):
        """
        Initialize scraper error.
        
        Args:
            message: Error message
            url: URL that caused the error
            original_error: Original exception that caused this error
        """
        self.url = url
        self.original_error = original_error
        
        full_message = message
        if url:
            full_message = f"{message} (URL: {url})"
        if original_error:
            full_message = f"{full_message} - {str(original_error)}"
            
        super().__init__(full_message)
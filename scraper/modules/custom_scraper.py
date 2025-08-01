"""
Custom scraper module for extensible custom implementations.
Provides base functionality for implementing custom scrapers for specific APIs or sites.
"""

import logging
import json
from typing import List, Optional, Dict, Any, Callable
from abc import abstractmethod

from bs4 import BeautifulSoup

from scraper.modules.base import BaseScraperModule, ScraperError
from scraper.models.content import RawContent


logger = logging.getLogger(__name__)


class CustomScraperModule(BaseScraperModule):
    """
    Extensible custom scraper for specific APIs and sites.
    
    This scraper provides a framework for implementing custom scrapers
    for specific APIs, websites, or data sources that don't fit the
    standard RSS or WordPress patterns.
    
    Users can extend this class or configure custom extraction methods
    to handle their specific data sources.
    """
    
    def __init__(self, config, settings=None, custom_extractors=None):
        """
        Initialize custom scraper with optional custom extractors.
        
        Args:
            config: Site configuration
            settings: Optional scraper settings
            custom_extractors: Dict of custom extraction functions
        """
        super().__init__(config, settings)
        self.custom_extractors = custom_extractors or {}
    
    async def scrape_feed(self, feed_url: str) -> List[RawContent]:
        """
        Scrape content from a custom source.
        
        Args:
            feed_url: URL of the custom API or data source
            
        Returns:
            List of RawContent objects
            
        Raises:
            ScraperError: If scraping fails
        """
        self.logger.info(f"Scraping custom source: {feed_url}")
        
        try:
            # Determine content type and scraping method
            if feed_url.endswith('.json') or '/api/' in feed_url:
                return await self._scrape_json_api(feed_url)
            elif feed_url.endswith('.xml'):
                return await self._scrape_xml_api(feed_url)
            else:
                return await self._scrape_html_page(feed_url)
                
        except Exception as e:
            raise ScraperError(f"Failed to scrape custom source", feed_url, e)
    
    async def _scrape_json_api(self, api_url: str) -> List[RawContent]:
        """
        Scrape JSON API endpoint.
        
        Args:
            api_url: JSON API URL
            
        Returns:
            List of RawContent objects
        """
        self.logger.info(f"Scraping JSON API: {api_url}")
        
        response = self._make_request(api_url, use_cache=True)
        
        if response is None:
            self.logger.info(f"API not modified or request failed: {api_url}")
            return []
        
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise ScraperError(f"Invalid JSON response from API", api_url, e)
        
        # Handle different JSON structures
        items = self._extract_items_from_json(data)
        
        content_items = []
        for item_data in items[:50]:  # Limit to 50 items
            try:
                content = self._extract_content_from_json_item(item_data, api_url)
                if content and self._is_recent_content(content.date):
                    content_items.append(content)
                    
            except Exception as e:
                self.logger.warning(f"Failed to extract content from JSON item: {e}")
                continue
        
        self.logger.info(f"Successfully extracted {len(content_items)} items from JSON API")
        return content_items
    
    async def _scrape_xml_api(self, api_url: str) -> List[RawContent]:
        """
        Scrape XML API endpoint.
        
        Args:
            api_url: XML API URL
            
        Returns:
            List of RawContent objects
        """
        self.logger.info(f"Scraping XML API: {api_url}")
        
        response = self._make_request(api_url, use_cache=True)
        
        if response is None:
            self.logger.info(f"API not modified or request failed: {api_url}")
            return []
        
        try:
            # Parse XML using BeautifulSoup
            soup = BeautifulSoup(response.content, 'xml')
        except Exception as e:
            raise ScraperError(f"Failed to parse XML response", api_url, e)
        
        # Extract items from XML
        items = self._extract_items_from_xml(soup)
        
        content_items = []
        for item_element in items[:50]:  # Limit to 50 items
            try:
                content = self._extract_content_from_xml_item(item_element, api_url)
                if content and self._is_recent_content(content.date):
                    content_items.append(content)
                    
            except Exception as e:
                self.logger.warning(f"Failed to extract content from XML item: {e}")
                continue
        
        self.logger.info(f"Successfully extracted {len(content_items)} items from XML API")
        return content_items
    
    async def _scrape_html_page(self, page_url: str) -> List[RawContent]:
        """
        Scrape HTML page for structured content.
        
        Args:
            page_url: HTML page URL
            
        Returns:
            List of RawContent objects
        """
        self.logger.info(f"Scraping HTML page: {page_url}")
        
        response = self._make_request(page_url, use_cache=True)
        
        if response is None:
            self.logger.info(f"Page not modified or request failed: {page_url}")
            return []
        
        try:
            # Parse HTML using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            raise ScraperError(f"Failed to parse HTML response", page_url, e)
        
        # Extract items from HTML
        items = self._extract_items_from_html(soup)
        
        content_items = []
        for item_element in items[:50]:  # Limit to 50 items
            try:
                content = self._extract_content_from_html_item(item_element, page_url)
                if content:
                    content_items.append(content)
                    
            except Exception as e:
                self.logger.warning(f"Failed to extract content from HTML item: {e}")
                continue
        
        self.logger.info(f"Successfully extracted {len(content_items)} items from HTML page")
        return content_items
    
    def _extract_items_from_json(self, data: Any) -> List[Dict[str, Any]]:
        """
        Extract items list from JSON response.
        
        Args:
            data: Parsed JSON data
            
        Returns:
            List of item dictionaries
        """
        # Handle different JSON structures
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # Common patterns for item arrays
            for key in ['items', 'data', 'posts', 'articles', 'results', 'content']:
                if key in data and isinstance(data[key], list):
                    return data[key]
            
            # If no array found, treat the dict as a single item
            return [data]
        else:
            self.logger.warning(f"Unexpected JSON structure: {type(data)}")
            return []
    
    def _extract_items_from_xml(self, soup: BeautifulSoup) -> List:
        """
        Extract items from XML document.
        
        Args:
            soup: BeautifulSoup XML document
            
        Returns:
            List of XML elements
        """
        # Try common XML item patterns
        for selector in ['item', 'entry', 'post', 'article', 'record']:
            items = soup.find_all(selector)
            if items:
                return items
        
        # Fallback: look for any repeated elements
        all_elements = soup.find_all()
        if all_elements:
            # Group by tag name and return the largest group
            tag_counts = {}
            for elem in all_elements:
                tag_counts[elem.name] = tag_counts.get(elem.name, 0) + 1
            
            if tag_counts:
                most_common_tag = max(tag_counts, key=tag_counts.get)
                if tag_counts[most_common_tag] > 1:
                    return soup.find_all(most_common_tag)
        
        return []
    
    def _extract_items_from_html(self, soup: BeautifulSoup) -> List:
        """
        Extract items from HTML document.
        
        Args:
            soup: BeautifulSoup HTML document
            
        Returns:
            List of HTML elements
        """
        # Try common HTML content patterns
        selectors = [
            'article',
            '.post',
            '.item',
            '.entry',
            '.content-item',
            '[data-item]',
            '.card',
            'li'  # Last resort
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if len(items) > 1:  # Need at least 2 items to be a pattern
                return items
        
        return []
    
    def _extract_content_from_json_item(self, item_data: Dict[str, Any], source_url: str) -> Optional[RawContent]:
        """
        Extract content from JSON item.
        
        Args:
            item_data: JSON item data
            source_url: Source URL
            
        Returns:
            RawContent object or None
        """
        try:
            # Use custom extractor if available
            if 'json' in self.custom_extractors:
                return self.custom_extractors['json'](item_data, source_url, self.config)
            
            # Default extraction logic
            title = self._extract_field_value(item_data, self.config.content_mapping.title)
            url = self._extract_field_value(item_data, self.config.content_mapping.url)
            
            if not title or not url:
                return None
            
            image = self._extract_field_value(item_data, self.config.content_mapping.image)
            excerpt = self._extract_field_value(item_data, self.config.content_mapping.excerpt)
            category = self._extract_field_value(item_data, self.config.content_mapping.category) if self.config.content_mapping.category else None
            date = self._extract_field_value(item_data, self.config.content_mapping.date) if self.config.content_mapping.date else None
            
            return RawContent(
                title=self._clean_text(title),
                url=url,
                image=image,
                excerpt=self._clean_text(excerpt),
                category=self._clean_text(category),
                date=date,
                source_data=item_data,
                scraper_type="custom",
                source_url=source_url
            )
            
        except Exception as e:
            self.logger.error(f"Failed to extract content from JSON item: {e}")
            return None
    
    def _extract_content_from_xml_item(self, item_element, source_url: str) -> Optional[RawContent]:
        """
        Extract content from XML item element.
        
        Args:
            item_element: BeautifulSoup XML element
            source_url: Source URL
            
        Returns:
            RawContent object or None
        """
        try:
            # Use custom extractor if available
            if 'xml' in self.custom_extractors:
                return self.custom_extractors['xml'](item_element, source_url, self.config)
            
            # Default extraction logic
            title = self._extract_xml_field(item_element, self.config.content_mapping.title)
            url = self._extract_xml_field(item_element, self.config.content_mapping.url)
            
            if not title or not url:
                return None
            
            image = self._extract_xml_field(item_element, self.config.content_mapping.image)
            excerpt = self._extract_xml_field(item_element, self.config.content_mapping.excerpt)
            category = self._extract_xml_field(item_element, self.config.content_mapping.category) if self.config.content_mapping.category else None
            date = self._extract_xml_field(item_element, self.config.content_mapping.date) if self.config.content_mapping.date else None
            
            return RawContent(
                title=self._clean_text(title),
                url=url,
                image=image,
                excerpt=self._clean_text(excerpt),
                category=self._clean_text(category),
                date=date,
                source_data=str(item_element),
                scraper_type="custom",
                source_url=source_url
            )
            
        except Exception as e:
            self.logger.error(f"Failed to extract content from XML item: {e}")
            return None
    
    def _extract_content_from_html_item(self, item_element, source_url: str) -> Optional[RawContent]:
        """
        Extract content from HTML item element.
        
        Args:
            item_element: BeautifulSoup HTML element
            source_url: Source URL
            
        Returns:
            RawContent object or None
        """
        try:
            # Use custom extractor if available
            if 'html' in self.custom_extractors:
                return self.custom_extractors['html'](item_element, source_url, self.config)
            
            # Default extraction logic using CSS selectors
            title = self._extract_html_field(item_element, self.config.content_mapping.title)
            url = self._extract_html_field(item_element, self.config.content_mapping.url)
            
            if not title or not url:
                return None
            
            # Make URL absolute if relative
            if url.startswith('/'):
                from urllib.parse import urljoin
                url = urljoin(source_url, url)
            
            image = self._extract_html_field(item_element, self.config.content_mapping.image)
            excerpt = self._extract_html_field(item_element, self.config.content_mapping.excerpt)
            category = self._extract_html_field(item_element, self.config.content_mapping.category) if self.config.content_mapping.category else None
            date = self._extract_html_field(item_element, self.config.content_mapping.date) if self.config.content_mapping.date else None
            
            return RawContent(
                title=self._clean_text(title),
                url=url,
                image=image,
                excerpt=self._clean_text(excerpt),
                category=self._clean_text(category),
                date=date,
                source_data=str(item_element),
                scraper_type="custom",
                source_url=source_url
            )
            
        except Exception as e:
            self.logger.error(f"Failed to extract content from HTML item: {e}")
            return None
    
    def _extract_xml_field(self, element, field_path: str) -> Optional[str]:
        """Extract field from XML element using tag name or CSS selector."""
        try:
            # Try as direct tag name first
            found = element.find(field_path)
            if found:
                return found.get_text(strip=True)
            
            # Try as CSS selector
            found = element.select_one(field_path)
            if found:
                return found.get_text(strip=True)
            
            # Try as attribute
            if hasattr(element, 'get') and element.get(field_path):
                return element.get(field_path)
            
            return None
            
        except Exception:
            return None
    
    def _extract_html_field(self, element, field_path: str) -> Optional[str]:
        """Extract field from HTML element using CSS selector."""
        try:
            # Try as CSS selector
            found = element.select_one(field_path)
            if found:
                # For links, get href attribute
                if found.name == 'a' and 'url' in field_path.lower():
                    return found.get('href')
                # For images, get src attribute
                elif found.name == 'img' and 'image' in field_path.lower():
                    return found.get('src')
                # Otherwise get text content
                else:
                    return found.get_text(strip=True)
            
            return None
            
        except Exception:
            return None


# Example custom extractor functions
def example_json_extractor(item_data: Dict[str, Any], source_url: str, config) -> Optional[RawContent]:
    """
    Example custom JSON extractor function.
    
    This function shows how to implement a custom extractor for a specific API format.
    """
    try:
        # Example: custom API format
        # {
        #   "post_title": "...",
        #   "post_url": "...",
        #   "thumbnail": "...",
        #   "post_excerpt": "...",
        #   "categories": ["cat1", "cat2"],
        #   "publish_date": "2024-01-01"
        # }
        
        title = item_data.get('post_title')
        url = item_data.get('post_url')
        
        if not title or not url:
            return None
        
        return RawContent(
            title=title,
            url=url,
            image=item_data.get('thumbnail'),
            excerpt=item_data.get('post_excerpt'),
            category=item_data.get('categories', [None])[0],  # First category
            date=item_data.get('publish_date'),
            source_data=item_data,
            scraper_type="custom",
            source_url=source_url
        )
        
    except Exception as e:
        logger.error(f"Custom JSON extractor failed: {e}")
        return None


# Usage example for custom extractors:
# 
# custom_extractors = {
#     'json': example_json_extractor,
#     'xml': my_xml_extractor_function,
#     'html': my_html_extractor_function
# }
# 
# scraper = CustomScraperModule(config, settings, custom_extractors)
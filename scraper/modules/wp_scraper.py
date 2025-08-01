"""
WordPress scraper module for WordPress REST API and RSS feeds.
Handles both WordPress REST API endpoints and WordPress RSS feeds.
"""

import logging
import json
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from scraper.modules.base import BaseScraperModule, ScraperError
from scraper.models.content import RawContent


logger = logging.getLogger(__name__)


class WordPressScraperModule(BaseScraperModule):
    """
    WordPress content scraper supporting both REST API and RSS feeds.
    
    This scraper can handle:
    - WordPress REST API v2 endpoints (/wp-json/wp/v2/posts)
    - WordPress RSS feeds (/feed/)
    - WordPress custom post types
    - Featured media and embedded content
    """
    
    async def scrape_feed(self, feed_url: str) -> List[RawContent]:
        """
        Scrape content from a WordPress source.
        
        Args:
            feed_url: URL of WordPress API endpoint or RSS feed
            
        Returns:
            List of RawContent objects
            
        Raises:
            ScraperError: If scraping fails
        """
        self.logger.info(f"Scraping WordPress source: {feed_url}")
        
        try:
            # Determine if this is a REST API endpoint or RSS feed
            if '/wp-json/' in feed_url or feed_url.endswith('.json'):
                return await self._scrape_rest_api(feed_url)
            else:
                # Assume RSS feed - use RSS scraper logic
                return await self._scrape_wordpress_rss(feed_url)
                
        except Exception as e:
            raise ScraperError(f"Failed to scrape WordPress source", feed_url, e)
    
    async def _scrape_rest_api(self, api_url: str) -> List[RawContent]:
        """
        Scrape WordPress REST API endpoint.
        
        Args:
            api_url: WordPress REST API URL
            
        Returns:
            List of RawContent objects
        """
        self.logger.info(f"Scraping WordPress REST API: {api_url}")
        
        # Make request to REST API
        response = self._make_request(api_url, use_cache=True)
        
        if response is None:
            self.logger.info(f"API not modified or request failed: {api_url}")
            return []
        
        try:
            posts_data = response.json()
        except json.JSONDecodeError as e:
            raise ScraperError(f"Invalid JSON response from WordPress API", api_url, e)
        
        if not isinstance(posts_data, list):
            self.logger.warning(f"Expected list of posts, got {type(posts_data)}")
            return []
        
        content_items = []
        for post_data in posts_data[:50]:  # Limit to 50 posts
            try:
                content = self._extract_content_from_wp_post(post_data, api_url)
                if content and self._is_recent_content(content.date):
                    content_items.append(content)
                    
            except Exception as e:
                self.logger.warning(f"Failed to extract content from post: {e}")
                continue
        
        self.logger.info(f"Successfully extracted {len(content_items)} items from WordPress API")
        return content_items
    
    async def _scrape_wordpress_rss(self, feed_url: str) -> List[RawContent]:
        """
        Scrape WordPress RSS feed (fallback method).
        
        Args:
            feed_url: WordPress RSS feed URL
            
        Returns:
            List of RawContent objects
        """
        self.logger.info(f"Scraping WordPress RSS feed: {feed_url}")
        
        # Import RSS scraper functionality
        from .rss_scraper import RSSScraperModule
        
        # Create temporary RSS scraper with same config
        rss_scraper = RSSScraperModule(self.config, self.settings)
        
        # Scrape using RSS logic but mark as WordPress
        content_items = await rss_scraper.scrape_feed(feed_url)
        
        # Update scraper type for all items
        for item in content_items:
            item.scraper_type = "wordpress"
            
        return content_items
    
    def _extract_content_from_wp_post(self, post_data: Dict[str, Any], api_url: str) -> Optional[RawContent]:
        """
        Extract content from WordPress REST API post data.
        
        Args:
            post_data: WordPress post data from REST API
            api_url: Source API URL
            
        Returns:
            RawContent object or None if extraction fails
        """
        try:
            # Extract title
            title = self._extract_wp_title(post_data)
            if not title:
                self.logger.debug("Skipping post without title")
                return None
            
            # Extract URL
            url = self._extract_wp_url(post_data)
            if not url:
                self.logger.debug(f"Skipping post without URL: {title}")
                return None
            
            # Extract other fields
            image = self._extract_wp_image(post_data, api_url)
            excerpt = self._extract_wp_excerpt(post_data)
            category = self._extract_wp_category(post_data)
            date = self._extract_wp_date(post_data)
            
            # Create RawContent object
            content = RawContent(
                title=title,
                url=url,
                image=image,
                excerpt=excerpt,
                category=category,
                date=date,
                source_data=post_data,  # Store original post data
                scraper_type="wordpress",
                source_url=api_url
            )
            
            return content
            
        except Exception as e:
            self.logger.error(f"Failed to extract content from WordPress post: {e}")
            return None
    
    def _extract_wp_title(self, post_data: Dict[str, Any]) -> Optional[str]:
        """Extract title from WordPress post data."""
        title_field = self.config.content_mapping.title
        
        # Try configured field first
        title = self._extract_field_value(post_data, title_field)
        
        # Fallback to common WordPress title fields
        if not title:
            # Try title.rendered (REST API v2)
            if isinstance(post_data.get('title'), dict):
                title = post_data['title'].get('rendered')
            # Try plain title
            elif 'title' in post_data:
                title = post_data['title']
        
        return self._clean_text(title)
    
    def _extract_wp_url(self, post_data: Dict[str, Any]) -> Optional[str]:
        """Extract URL from WordPress post data."""
        url_field = self.config.content_mapping.url
        
        # Try configured field first
        url = self._extract_field_value(post_data, url_field)
        
        # Fallback to common WordPress URL fields
        if not url:
            for field in ['link', 'guid', 'permalink']:
                value = post_data.get(field)
                if value:
                    # Handle GUID objects
                    if isinstance(value, dict):
                        url = value.get('rendered') or value.get('href')
                    else:
                        url = str(value)
                    break
        
        return url.strip() if url else None
    
    def _extract_wp_image(self, post_data: Dict[str, Any], api_url: str) -> Optional[str]:
        """Extract featured image from WordPress post data."""
        image_field = self.config.content_mapping.image
        
        # Try configured field first
        image = self._extract_field_value(post_data, image_field)
        
        if not image:
            # Try featured_media (REST API v2)
            featured_media_id = post_data.get('featured_media')
            if featured_media_id and featured_media_id != 0:
                # If _embedded data is available
                if '_embedded' in post_data:
                    embedded = post_data['_embedded']
                    if 'wp:featuredmedia' in embedded:
                        media_data = embedded['wp:featuredmedia'][0]
                        image = media_data.get('source_url') or media_data.get('media_details', {}).get('sizes', {}).get('medium', {}).get('source_url')
                
                # Fallback: construct media endpoint URL
                if not image:
                    base_url = api_url.replace('/posts', '/media')
                    media_url = f"{base_url}/{featured_media_id}"
                    try:
                        media_response = self._make_request(media_url, use_cache=True)
                        if media_response:
                            media_data = media_response.json()
                            image = media_data.get('source_url')
                    except Exception as e:
                        self.logger.debug(f"Failed to fetch media data: {e}")
            
            # Try excerpt or content for embedded images
            if not image:
                content_html = ""
                if 'excerpt' in post_data and isinstance(post_data['excerpt'], dict):
                    content_html = post_data['excerpt'].get('rendered', '')
                elif 'content' in post_data and isinstance(post_data['content'], dict):
                    content_html = post_data['content'].get('rendered', '')
                
                if content_html:
                    image = self._extract_image_from_html(content_html)
        
        # Clean and validate image URL
        if image:
            image = image.strip()
            if not image.startswith(('http://', 'https://')):
                if image.startswith('//'):
                    image = 'https:' + image
                elif image.startswith('/'):
                    # Relative URL - construct full URL from API base
                    parsed_api_url = urlparse(api_url)
                    base_url = f"{parsed_api_url.scheme}://{parsed_api_url.netloc}"
                    image = urljoin(base_url, image)
                else:
                    image = None
        
        return image
    
    def _extract_wp_excerpt(self, post_data: Dict[str, Any]) -> Optional[str]:
        """Extract excerpt from WordPress post data."""
        excerpt_field = self.config.content_mapping.excerpt
        
        # Try configured field first
        excerpt = self._extract_field_value(post_data, excerpt_field)
        
        if not excerpt:
            # Try excerpt.rendered (REST API v2)
            if isinstance(post_data.get('excerpt'), dict):
                excerpt = post_data['excerpt'].get('rendered')
            # Try plain excerpt
            elif 'excerpt' in post_data:
                excerpt = post_data['excerpt']
            # Fallback to content
            elif isinstance(post_data.get('content'), dict):
                content = post_data['content'].get('rendered', '')
                # Extract plain text from HTML content
                if content:
                    soup = BeautifulSoup(content, 'html.parser')
                    excerpt = soup.get_text()
        
        # Clean excerpt
        excerpt = self._clean_text(excerpt)
        
        # Truncate if too long
        if excerpt and len(excerpt) > 500:
            excerpt = excerpt[:497] + "..."
        
        return excerpt
    
    def _extract_wp_category(self, post_data: Dict[str, Any]) -> Optional[str]:
        """Extract category from WordPress post data."""
        if not self.config.content_mapping.category:
            return None
            
        category_field = self.config.content_mapping.category
        
        # Try configured field first
        category = self._extract_field_value(post_data, category_field)
        
        if not category:
            # Try categories array
            categories = post_data.get('categories', [])
            if categories:
                # If _embedded data is available
                if '_embedded' in post_data and 'wp:term' in post_data['_embedded']:
                    terms = post_data['_embedded']['wp:term']
                    if terms and terms[0]:  # Categories are first term type
                        category = terms[0][0].get('name')
                # Fallback to category ID (would need separate API call)
                elif isinstance(categories[0], int):
                    category = f"Category {categories[0]}"  # Placeholder
            
            # Try tags if no category
            if not category:
                tags = post_data.get('tags', [])
                if tags and '_embedded' in post_data and 'wp:term' in post_data['_embedded']:
                    terms = post_data['_embedded']['wp:term']
                    if len(terms) > 1 and terms[1]:  # Tags are second term type
                        category = terms[1][0].get('name')
        
        return self._clean_text(category)
    
    def _extract_wp_date(self, post_data: Dict[str, Any]) -> Optional[str]:
        """Extract publication date from WordPress post data."""
        if not self.config.content_mapping.date:
            return None
            
        date_field = self.config.content_mapping.date
        
        # Try configured field first
        date_str = self._extract_field_value(post_data, date_field)
        
        if not date_str:
            # Try common WordPress date fields
            for field in ['date', 'date_gmt', 'modified', 'modified_gmt']:
                date_str = post_data.get(field)
                if date_str:
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
    
    def _extract_image_from_html(self, html_content: str) -> Optional[str]:
        """Extract first image URL from HTML content."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            img_tag = soup.find('img')
            if img_tag and img_tag.get('src'):
                return img_tag['src']
        except Exception as e:
            self.logger.debug(f"Failed to extract image from HTML: {e}")
        
        return None
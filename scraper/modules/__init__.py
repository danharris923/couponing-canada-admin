"""
Modular scraper system for different content types.

This package contains scraper modules for different content sources:
- RSS feeds (rss_scraper.py)
- WordPress sites (wp_scraper.py) 
- Custom APIs (custom_scraper.py)

All modules implement the same interface and return RawContent models.
"""

from .rss_scraper import RSSScraperModule
from .wp_scraper import WordPressScraperModule
from .custom_scraper import CustomScraperModule
from .base import BaseScraperModule

__all__ = [
    "BaseScraperModule",
    "RSSScraperModule",
    "WordPressScraperModule", 
    "CustomScraperModule",
]
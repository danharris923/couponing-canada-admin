"""
Test fixtures and sample data for Modern Template tests.
"""

import json
from datetime import datetime
from typing import Dict, Any, List

# Sample configuration data for testing
SAMPLE_CONFIG = {
    "site_name": "Test Site",
    "scraper_type": "rss",
    "feeds": [
        "https://example.com/rss.xml",
        "https://test.com/feed.xml"
    ],
    "content_mapping": {
        "title": "title",
        "url": "link", 
        "image": "enclosure",
        "excerpt": "description"
    },
    "ai_enhancement_enabled": True,
    "update_interval": 3600,
    "affiliate_tag": "test-tag"
}

# Sample RSS feed data
SAMPLE_RSS_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Test Feed</title>
        <description>Test RSS feed for testing</description>
        <link>https://example.com</link>
        <item>
            <title>Test Article 1</title>
            <link>https://example.com/article1</link>
            <description>This is a test article about technology</description>
            <pubDate>Mon, 01 Jan 2025 10:00:00 GMT</pubDate>
            <enclosure url="https://example.com/image1.jpg" type="image/jpeg"/>
        </item>
        <item>
            <title>Test Article 2</title>
            <link>https://example.com/article2</link>
            <description>Another test article about business</description>
            <pubDate>Sun, 31 Dec 2024 15:30:00 GMT</pubDate>
            <enclosure url="https://example.com/image2.jpg" type="image/jpeg"/>
        </item>
    </channel>
</rss>"""

# Sample raw content data
SAMPLE_RAW_CONTENT = [
    {
        "title": "Amazing Tech Gadget Deal",
        "url": "https://example.com/tech-deal",
        "source_url": "https://example.com/rss.xml", 
        "image": "https://example.com/tech-image.jpg",
        "excerpt": "Get this amazing tech gadget at 50% off",
        "category": "Technology",
        "date": "2025-01-01",
        "scraped_at": datetime.now().isoformat()
    },
    {
        "title": "Business Strategy Guide",
        "url": "https://example.com/business-guide",
        "source_url": "https://example.com/rss.xml",
        "image": "https://example.com/business-image.jpg", 
        "excerpt": "Learn effective business strategies",
        "category": "Business",
        "date": "2025-01-01",
        "scraped_at": datetime.now().isoformat()
    }
]

# Sample enhanced content data
SAMPLE_ENHANCED_CONTENT = [
    {
        "title": "Amazing Tech Gadget Deal - Limited Time Offer",
        "url": "https://example.com/tech-deal",
        "image": "https://example.com/tech-image.jpg",
        "excerpt": "Discover cutting-edge technology at an unbeatable price. This amazing gadget offers premium features at 50% off - don't miss out!",
        "category": "Technology", 
        "date": "2025-01-01",
        "quality_score": 0.85,
        "ai_generated_fields": ["title", "excerpt"],
        "enhancement_notes": "Enhanced title for better engagement, expanded excerpt with compelling language",
        "original_content": SAMPLE_RAW_CONTENT[0]
    }
]

# Sample Deal output data
SAMPLE_DEAL_OUTPUT = [
    {
        "id": "1",
        "title": "Amazing Tech Gadget Deal - Limited Time Offer",
        "imageUrl": "https://example.com/tech-image.jpg",
        "price": 49.99,
        "originalPrice": 99.99,
        "discountPercent": 50,
        "category": "Technology",
        "description": "Discover cutting-edge technology at an unbeatable price. This amazing gadget offers premium features at 50% off - don't miss out!",
        "affiliateUrl": "https://example.com/tech-deal",
        "featured": True,
        "dateAdded": "2025-01-01"
    }
]

# Sample WordPress API response
SAMPLE_WP_API_RESPONSE = {
    "posts": [
        {
            "id": 1,
            "title": {"rendered": "WordPress Test Post"},
            "content": {"rendered": "<p>This is a test WordPress post content.</p>"},
            "excerpt": {"rendered": "<p>Test excerpt for WordPress post</p>"},
            "link": "https://example.com/wp-post",
            "date": "2025-01-01T10:00:00",
            "featured_media": 123,
            "categories": [1]
        }
    ]
}

# Sample LLM responses for AI agent testing
SAMPLE_LLM_RESPONSES = {
    "content_enhancement": {
        "enhanced_title": "Revolutionary Tech Gadget - 50% Off Limited Time Deal",
        "enhanced_excerpt": "Experience the future of technology with this groundbreaking gadget. Premium features, sleek design, and now available at an incredible 50% discount. Perfect for tech enthusiasts and professionals alike.",
        "generated_content": {
            "excerpt": "Discover innovative technology solutions designed for modern users",
            "category": "Technology"
        }
    },
    "category_classification": {
        "primary_category": "Technology",
        "confidence_score": 0.9,
        "secondary_categories": ["Gadgets"],
        "reasoning": "Content focuses on tech gadgets and technology deals",
        "keywords": ["tech", "gadget", "technology", "innovation"]
    },
    "quality_validation": {
        "overall_quality_score": 0.8,
        "recommendation": "validated",
        "quality_metrics": {
            "completeness_score": 0.9,
            "relevance_score": 0.8,
            "engagement_score": 0.85,
            "uniqueness_score": 0.75,
            "language_quality_score": 0.9
        },
        "issues_found": [],
        "strengths": ["Clear title", "Engaging description", "Relevant content"],
        "improvement_suggestions": ["Consider adding more specific details"],
        "reasoning": "High-quality content with good engagement potential"
    }
}

# Invalid configuration samples for testing validation
INVALID_CONFIGS = [
    {},  # Empty config
    {"site_name": ""},  # Empty site name
    {"site_name": "Test", "scraper_type": "invalid"},  # Invalid scraper type
    {"site_name": "Test", "scraper_type": "rss"},  # Missing feeds
    {"site_name": "Test", "scraper_type": "rss", "feeds": []},  # Empty feeds
]

def get_sample_config(overrides: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get sample configuration with optional overrides."""
    config = SAMPLE_CONFIG.copy()
    if overrides:
        config.update(overrides)
    return config

def get_sample_raw_content(count: int = 2) -> List[Dict[str, Any]]:
    """Get sample raw content data."""
    return SAMPLE_RAW_CONTENT[:count]

def get_sample_enhanced_content(count: int = 1) -> List[Dict[str, Any]]:
    """Get sample enhanced content data.""" 
    return SAMPLE_ENHANCED_CONTENT[:count]

def get_sample_deal_output(count: int = 1) -> List[Dict[str, Any]]:
    """Get sample deal output data."""
    return SAMPLE_DEAL_OUTPUT[:count]

def save_temp_config(config: Dict[str, Any], filepath: str) -> None:
    """Save temporary config file for testing."""
    with open(filepath, 'w') as f:
        json.dump(config, f, indent=2)
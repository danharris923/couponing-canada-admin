"""
Output models for standardized JSON generation.
These models ensure compatibility with the React frontend Deal interface.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, field_validator, ConfigDict


class StandardOutput(BaseModel):
    """
    Standardized output format for content items.
    
    This model defines the common output format that all scrapers
    must produce, regardless of source type.
    """
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    id: str = Field(..., min_length=1, description="Unique identifier for the content")
    title: str = Field(..., min_length=1, max_length=500, description="Content title")
    url: HttpUrl = Field(..., description="Content URL")
    image_url: HttpUrl = Field(..., description="Featured image URL")
    excerpt: str = Field(..., min_length=1, max_length=500, description="Content description")
    category: str = Field(..., min_length=1, description="Content category")
    date_added: str = Field(..., description="Date when content was added (ISO format)")
    
    # Optional fields for enhanced functionality
    source_url: Optional[HttpUrl] = Field(None, description="Original source feed URL")
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Content quality score")
    ai_enhanced: bool = Field(False, description="Whether content was AI-enhanced")
    
    @field_validator('id')
    @classmethod
    def validate_id(cls, v):
        """Ensure ID is valid and URL-safe."""
        if not v or v.strip() == "":
            raise ValueError("ID cannot be empty")
        # Remove any characters that might cause issues
        v = v.strip().replace(' ', '-').lower()
        return ''.join(c for c in v if c.isalnum() or c in '-_')[:50]
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Ensure title is clean and properly formatted."""
        if not v or v.strip() == "":
            raise ValueError("Title cannot be empty")
        return v.strip()
    
    @field_validator('excerpt')
    @classmethod
    def validate_excerpt(cls, v):
        """Ensure excerpt is clean and informative."""
        if not v or v.strip() == "":
            raise ValueError("Excerpt cannot be empty")
        return v.strip()


class DealOutput(BaseModel):
    """
    Deal-specific output format matching React Deal interface.
    
    This model exactly matches the TypeScript Deal interface from the React frontend,
    ensuring perfect compatibility with existing components.
    """
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    # Required fields matching Deal.ts interface
    id: str = Field(..., description="Unique deal identifier")
    title: str = Field(..., description="Deal title")
    imageUrl: str = Field(..., description="Deal image URL")
    price: float = Field(0.0, ge=0.0, description="Current price")
    originalPrice: float = Field(0.0, ge=0.0, description="Original price")
    discountPercent: int = Field(0, ge=0, le=100, description="Discount percentage")
    category: str = Field(..., description="Deal category")
    description: str = Field(..., description="Deal description")
    affiliateUrl: str = Field(..., description="Affiliate link URL")
    featured: bool = Field(False, description="Whether deal is featured")
    dateAdded: str = Field(..., description="Date added (YYYY-MM-DD format)")
    
    @field_validator('id')
    @classmethod
    def validate_deal_id(cls, v):
        """Ensure deal ID follows expected format."""
        if not v or v.strip() == "":
            raise ValueError("Deal ID cannot be empty")
        # Clean ID for URL safety
        v = v.strip().replace(' ', '-').lower()
        return ''.join(c for c in v if c.isalnum() or c in '-_')[:50]
    
    @field_validator('title')
    @classmethod
    def validate_deal_title(cls, v):
        """Ensure deal title is properly formatted."""
        if not v or v.strip() == "":
            raise ValueError("Deal title cannot be empty")
        return v.strip()
    
    @field_validator('imageUrl')
    @classmethod
    def validate_image_url(cls, v):
        """Ensure image URL is valid."""
        if not v or v.strip() == "":
            return "/placeholder-deal.svg"  # Default placeholder
        return v.strip()
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        """Ensure description is informative and properly formatted."""
        if not v or v.strip() == "":
            raise ValueError("Deal description cannot be empty")
        return v.strip()
    
    @field_validator('affiliateUrl')
    @classmethod
    def validate_affiliate_url(cls, v):
        """Ensure affiliate URL is valid."""
        if not v or v.strip() == "":
            raise ValueError("Affiliate URL cannot be empty")
        return v.strip()
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        """Ensure category is properly formatted."""
        if not v or v.strip() == "":
            return "General"  # Default category
        return v.strip().title()
    
    @field_validator('dateAdded')
    @classmethod
    def validate_date_added(cls, v):
        """Ensure date is in correct format."""
        if not v or v.strip() == "":
            return datetime.now().strftime('%Y-%m-%d')
        # Try to parse and reformat to ensure consistency
        try:
            # Handle various date formats
            if 'T' in v:  # ISO format
                dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
            else:  # Simple date format
                dt = datetime.strptime(v, '%Y-%m-%d')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            # If parsing fails, return current date
            return datetime.now().strftime('%Y-%m-%d')
    
    @field_validator('originalPrice')
    @classmethod
    def validate_original_price(cls, v, info):
        """Ensure original price is logical compared to current price."""
        data = info.data if hasattr(info, 'data') else {}
        current_price = data.get('price', 0.0)
        
        if v < current_price:
            # If original price is less than current, set them equal
            return current_price
        return v
    
    @field_validator('discountPercent')  
    @classmethod
    def validate_discount_percent(cls, v, info):
        """Calculate and validate discount percentage."""
        data = info.data if hasattr(info, 'data') else {}
        current_price = data.get('price', 0.0)
        original_price = data.get('originalPrice', 0.0)
        
        if original_price > 0 and current_price > 0 and original_price > current_price:
            # Calculate actual discount percentage
            calculated_discount = int(((original_price - current_price) / original_price) * 100)
            return min(calculated_discount, 100)  # Cap at 100%
        elif v > 0:
            # Use provided discount if prices don't make sense
            return min(v, 100)
        else:
            return 0


class OutputSummary(BaseModel):
    """
    Summary of output generation process.
    
    This model provides statistics and metadata about the content
    generation process for monitoring and debugging.
    """
    
    model_config = ConfigDict()
    
    total_items: int = Field(..., ge=0, description="Total items processed")
    successful_items: int = Field(..., ge=0, description="Successfully output items")
    failed_items: int = Field(..., ge=0, description="Failed items")
    
    output_file: str = Field(..., description="Path to generated output file")
    generation_time: float = Field(..., ge=0.0, description="Time taken to generate output")
    generated_at: datetime = Field(default_factory=datetime.now, description="When output was generated")
    
    # Quality metrics
    average_quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Average quality score")
    ai_enhanced_count: int = Field(0, ge=0, description="Number of AI-enhanced items")
    categories: List[str] = Field(default_factory=list, description="List of categories found")
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_items == 0:
            return 0.0
        return (self.successful_items / self.total_items) * 100.0


def convert_to_deal_output(content: 'EnhancedContent', config: 'SiteConfig') -> DealOutput:
    """
    Convert enhanced content to Deal output format.
    
    This function transforms enhanced content into the exact format
    expected by the React frontend Deal interface.
    
    Args:
        content: Enhanced content from AI processing
        config: Site configuration for affiliate tags, etc.
        
    Returns:
        DealOutput: Content formatted for React frontend
    """
    from .content import EnhancedContent
    from .config import SiteConfig
    
    # Generate unique ID from title and URL
    import hashlib
    content_hash = hashlib.md5(f"{content.title}{content.url}".encode()).hexdigest()[:12]
    
    # Determine affiliate URL
    affiliate_url = str(content.url)
    if config.affiliate_tag and 'amazon' in affiliate_url.lower():
        # Add affiliate tag to Amazon URLs
        separator = '&' if '?' in affiliate_url else '?'
        affiliate_url = f"{affiliate_url}{separator}tag={config.affiliate_tag}"
    
    return DealOutput(
        id=content_hash,
        title=content.title,
        imageUrl=str(content.image),
        price=0.0,  # Default for non-deal content
        originalPrice=0.0,  # Default for non-deal content
        discountPercent=0,  # Default for non-deal content
        category=content.category,
        description=content.excerpt,
        affiliateUrl=affiliate_url,
        featured=content.quality_score > 0.8 if content.quality_score else False,
        dateAdded=content.date
    )
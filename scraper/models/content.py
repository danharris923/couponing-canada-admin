"""
Content models for the scraper system.
These models define the structure for content at different stages of processing.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, field_validator, ConfigDict


class ContentStatus(str, Enum):
    """Status of content during processing pipeline."""
    RAW = "raw"                    # Just scraped, not processed
    ENHANCED = "enhanced"          # AI-enhanced but not validated
    VALIDATED = "validated"        # Passed quality validation
    REJECTED = "rejected"          # Failed quality validation
    PUBLISHED = "published"        # Ready for frontend display


class RawContent(BaseModel):
    """
    Raw content from scrapers before AI processing.
    
    This model represents content in its initial scraped state,
    before any AI enhancement or validation.
    """
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    title: str = Field(..., min_length=1, max_length=500, description="Content title")
    url: HttpUrl = Field(..., description="Content URL")
    image: Optional[HttpUrl] = Field(None, description="Featured image URL")
    excerpt: Optional[str] = Field(None, max_length=1000, description="Content excerpt/description")
    category: Optional[str] = Field(None, max_length=100, description="Content category")
    date: Optional[str] = Field(None, description="Publication date (as string)")
    source_data: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Original scraped data for debugging"
    )
    scraped_at: datetime = Field(
        default_factory=datetime.now, 
        description="When content was scraped"
    )
    scraper_type: str = Field(..., description="Type of scraper used")
    source_url: HttpUrl = Field(..., description="URL of the source feed/API")
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Ensure title is not empty and reasonable length."""
        if not v or v.strip() == "":
            raise ValueError("Title cannot be empty")
        return v.strip()
    
    @field_validator('excerpt')
    @classmethod
    def validate_excerpt(cls, v):
        """Clean up excerpt if provided."""
        if v is not None:
            v = v.strip()
            if v == "":
                return None
        return v
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        """Clean up category if provided."""
        if v is not None:
            v = v.strip()
            if v == "":
                return None
        return v


class EnhancedContent(BaseModel):
    """
    Content after AI enhancement.
    
    This model represents content that has been processed by AI agents
    for quality improvement, categorization, and description enhancement.
    """
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    # Core content fields (required)
    title: str = Field(..., min_length=1, max_length=500, description="Enhanced title")
    url: HttpUrl = Field(..., description="Content URL")
    image: HttpUrl = Field(..., description="Featured image URL (required after enhancement)")
    excerpt: str = Field(..., min_length=10, max_length=500, description="Enhanced excerpt")
    category: str = Field(..., min_length=1, max_length=100, description="AI-assigned category")
    date: str = Field(..., description="Formatted publication date")
    
    # AI processing metadata
    quality_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="AI-assessed quality score (0-1)"
    )
    ai_generated_fields: List[str] = Field(
        default_factory=list, 
        description="List of fields generated/enhanced by AI"
    )
    enhancement_notes: Optional[str] = Field(
        None, 
        max_length=500, 
        description="Notes about AI enhancement process"
    )
    
    # Processing metadata
    enhanced_at: datetime = Field(
        default_factory=datetime.now, 
        description="When content was enhanced"
    )
    original_content: Optional[RawContent] = Field(
        None, 
        description="Reference to original raw content"
    )
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Ensure enhanced title meets quality standards."""
        if not v or v.strip() == "":
            raise ValueError("Enhanced title cannot be empty")
        # Remove excessive punctuation or emojis at the end
        v = v.strip().rstrip('!?.')
        return v
    
    @field_validator('excerpt')
    @classmethod
    def validate_excerpt(cls, v):
        """Ensure enhanced excerpt meets quality standards."""
        if not v or v.strip() == "":
            raise ValueError("Enhanced excerpt cannot be empty")
        v = v.strip()
        # Should not end with ellipsis if it's complete
        if len(v) < 500 and v.endswith('...'):
            v = v[:-3].strip()
        return v
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        """Ensure category follows standard format."""
        if not v or v.strip() == "":
            raise ValueError("Enhanced category cannot be empty")
        # Capitalize first letter of each word
        return v.strip().title()
    
    @field_validator('ai_generated_fields')
    @classmethod
    def validate_ai_fields(cls, v):
        """Ensure AI generated fields list is valid."""
        valid_fields = ['title', 'excerpt', 'category', 'image', 'date']
        for field in v:
            if field not in valid_fields:
                raise ValueError(f"Invalid AI generated field: {field}")
        return v


class ContentProcessingResult(BaseModel):
    """
    Result of content processing pipeline.
    
    This model encapsulates the result of processing content through
    the entire pipeline, including any errors or warnings.
    """
    
    model_config = ConfigDict()
    
    content: Optional[EnhancedContent] = Field(None, description="Successfully processed content")
    status: ContentStatus = Field(..., description="Processing status")
    errors: List[str] = Field(default_factory=list, description="Processing errors")
    warnings: List[str] = Field(default_factory=list, description="Processing warnings")
    processing_time: float = Field(..., ge=0.0, description="Processing time in seconds")
    processed_at: datetime = Field(default_factory=datetime.now, description="When processing completed")
    
    @field_validator('status')
    @classmethod
    def validate_status_consistency(cls, v, info):
        """Ensure status is consistent with content and errors."""
        data = info.data if hasattr(info, 'data') else {}
        
        if v == ContentStatus.VALIDATED and not data.get('content'):
            raise ValueError("Status 'validated' requires content to be present")
        if v == ContentStatus.REJECTED and data.get('content'):
            raise ValueError("Status 'rejected' should not have content")
        if data.get('errors') and v not in [ContentStatus.REJECTED]:
            # If there are errors, status should typically be rejected
            pass  # Allow for now, might be warnings
            
        return v


class BatchProcessingResult(BaseModel):
    """
    Result of processing multiple content items.
    
    This model summarizes the results of processing a batch of content,
    useful for monitoring and reporting.
    """
    
    model_config = ConfigDict()
    
    total_items: int = Field(..., ge=0, description="Total items processed")
    successful_items: int = Field(..., ge=0, description="Successfully processed items")
    failed_items: int = Field(..., ge=0, description="Failed items")
    skipped_items: int = Field(..., ge=0, description="Skipped items")
    
    results: List[ContentProcessingResult] = Field(
        default_factory=list, 
        description="Individual processing results"
    )
    
    processing_start: datetime = Field(..., description="Batch processing start time")
    processing_end: datetime = Field(..., description="Batch processing end time")
    total_processing_time: float = Field(..., ge=0.0, description="Total processing time in seconds")
    
    @field_validator('successful_items', 'failed_items', 'skipped_items')
    @classmethod
    def validate_item_counts(cls, v, info):
        """Ensure item counts are consistent."""
        data = info.data if hasattr(info, 'data') else {}
        total = data.get('total_items', 0)
        
        if v > total:
            raise ValueError(f"Item count cannot exceed total items ({total})")
        return v
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_items == 0:
            return 0.0
        return (self.successful_items / self.total_items) * 100.0
    
    @property
    def average_processing_time(self) -> float:
        """Calculate average processing time per item."""
        if self.total_items == 0:
            return 0.0
        return self.total_processing_time / self.total_items
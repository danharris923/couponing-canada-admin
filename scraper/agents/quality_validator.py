"""
Quality Validation Agent using Pydantic AI.
Assesses content completeness, quality, and relevance to filter high-quality content.
"""

import logging
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic_settings import BaseSettings
from pydantic import Field, BaseModel
from dotenv import load_dotenv

from scraper.models.config import SiteConfig
from scraper.models.content import RawContent, EnhancedContent, ContentStatus

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class LLMSettings(BaseSettings):
    """LLM configuration settings."""
    
    llm_provider: str = Field(default="openai")
    llm_api_key: str = Field(...)
    llm_model: str = Field(default="gpt-4")
    llm_base_url: str = Field(default="https://api.openai.com/v1")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


def get_llm_model():
    """Get configured LLM model from environment settings."""
    try:
        settings = LLMSettings()
        return OpenAIModel(
            model_name=settings.llm_model,
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key
        )
    except Exception:
        # For testing without env vars
        import os
        os.environ.setdefault("LLM_API_KEY", "test-key")
        settings = LLMSettings()
        return OpenAIModel(
            model_name=settings.llm_model,
            base_url=settings.llm_base_url,
            api_key="test-key"
        )


class QualityIssue(str, Enum):
    """Types of quality issues that can be detected."""
    LOW_CONTENT_QUALITY = "low_content_quality"
    INSUFFICIENT_INFORMATION = "insufficient_information"
    DUPLICATE_CONTENT = "duplicate_content"
    IRRELEVANT_CONTENT = "irrelevant_content"
    BROKEN_LINKS = "broken_links"
    MISSING_CRITICAL_FIELDS = "missing_critical_fields"
    POOR_LANGUAGE_QUALITY = "poor_language_quality"
    SPAM_OR_PROMOTIONAL = "spam_or_promotional"
    OUTDATED_CONTENT = "outdated_content"


class QualityMetrics(BaseModel):
    """Detailed quality metrics for content."""
    
    completeness_score: float = Field(..., ge=0.0, le=1.0, description="How complete the content is (0-1)")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="How relevant to site purpose (0-1)")
    engagement_score: float = Field(..., ge=0.0, le=1.0, description="How engaging the content is (0-1)")
    uniqueness_score: float = Field(..., ge=0.0, le=1.0, description="How unique/non-duplicate (0-1)")
    language_quality_score: float = Field(..., ge=0.0, le=1.0, description="Language and grammar quality (0-1)")


class QualityResult(BaseModel):
    """Structured result for quality validation."""
    
    overall_quality_score: float = Field(..., ge=0.0, le=1.0, description="Overall quality score (0-1)")
    recommendation: ContentStatus = Field(..., description="Recommended status for content")
    quality_metrics: QualityMetrics = Field(..., description="Detailed quality breakdown")
    issues_found: List[QualityIssue] = Field(default_factory=list, description="Quality issues identified")
    strengths: List[str] = Field(default_factory=list, description="Content strengths")
    improvement_suggestions: List[str] = Field(default_factory=list, description="Specific improvement suggestions")
    reasoning: str = Field(..., description="Detailed reasoning for quality assessment")


@dataclass
class QualityValidatorDependencies:
    """Dependencies for quality validation agent."""
    site_config: SiteConfig
    quality_threshold: float = 0.6
    strict_validation: bool = False
    check_duplicates: bool = True
    relevance_keywords: Optional[List[str]] = None
    content_history: Optional[List[str]] = None  # For duplicate detection


QUALITY_VALIDATOR_SYSTEM_PROMPT = """
You are an expert content quality validator for {site_name}. Your role is to assess content quality, 
completeness, and relevance to ensure only high-quality, valuable content is published.

Quality Assessment Criteria:

1. **Completeness (25%)**
   - Title is informative and descriptive
   - Description/excerpt provides value
   - Critical fields are present (image, category, etc.)
   - Content has sufficient detail

2. **Relevance (25%)**
   - Aligns with {site_name}'s purpose and audience
   - Matches target keywords and topics
   - Provides value to intended readers
   - Fits the site's content strategy

3. **Engagement (20%)**
   - Title is compelling and click-worthy
   - Description encourages interaction
   - Content is interesting and valuable
   - Likely to generate user engagement

4. **Uniqueness (15%)**
   - Not duplicate or near-duplicate content
   - Offers unique perspective or information
   - Avoids repetitive or generic content
   - Fresh insights or approach

5. **Language Quality (15%)**
   - Clear, well-written content
   - Proper grammar and structure
   - Professional presentation
   - Appropriate tone and style

Quality Thresholds:
- 0.8-1.0: Excellent - Publish immediately
- 0.6-0.79: Good - Publish with minor improvements
- 0.4-0.59: Fair - Needs significant improvement
- 0.0-0.39: Poor - Reject or major revision needed

Always provide detailed reasoning and specific improvement suggestions.
"""


# Create the quality validator agent with structured output
quality_validator_agent = Agent(
    get_llm_model(),
    deps_type=QualityValidatorDependencies,
    result_type=QualityResult,
    system_prompt=QUALITY_VALIDATOR_SYSTEM_PROMPT
)


@quality_validator_agent.system_prompt
def dynamic_validator_prompt(ctx: RunContext[QualityValidatorDependencies]) -> str:
    """Dynamic system prompt that includes site-specific context."""
    base_prompt = QUALITY_VALIDATOR_SYSTEM_PROMPT.format(
        site_name=ctx.deps.site_config.site_name
    )
    
    if ctx.deps.relevance_keywords:
        keywords = ", ".join(ctx.deps.relevance_keywords)
        base_prompt += f"\n\nKey relevance topics for {ctx.deps.site_config.site_name}: {keywords}"
    
    if ctx.deps.strict_validation:
        base_prompt += "\n\nNOTE: Apply strict validation standards. Be more critical in quality assessment."
    
    return base_prompt


@quality_validator_agent.tool
async def validate_content_quality(
    ctx: RunContext[QualityValidatorDependencies],
    title: str,
    description: Optional[str] = None,
    category: Optional[str] = None,
    image_url: Optional[str] = None,
    source_url: Optional[str] = None,
    date: Optional[str] = None
) -> QualityResult:
    """
    Validate content quality and provide detailed assessment.
    
    Args:
        title: Content title
        description: Content description/excerpt
        category: Content category
        image_url: Featured image URL
        source_url: Source URL
        date: Publication date
        
    Returns:
        QualityResult with detailed quality assessment
    """
    try:
        # Build validation context
        context_parts = [f"Title: {title}"]
        
        if description:
            context_parts.append(f"Description: {description}")
        else:
            context_parts.append("Description: [MISSING]")
            
        if category:
            context_parts.append(f"Category: {category}")
        else:
            context_parts.append("Category: [MISSING]")
            
        if image_url:
            context_parts.append(f"Image: {image_url}")
        else:
            context_parts.append("Image: [MISSING]")
            
        if source_url:
            context_parts.append(f"Source: {source_url}")
            
        if date:
            context_parts.append(f"Date: {date}")
        
        context = "\n".join(context_parts)
        
        # Create validation prompt
        validation_prompt = f"""
Assess the quality of this content for {ctx.deps.site_config.site_name}:

{context}

Provide a comprehensive quality assessment including:
1. Overall quality score (0.0 to 1.0)
2. Detailed metrics for each quality dimension
3. Specific issues found (if any)
4. Content strengths
5. Concrete improvement suggestions
6. Recommendation (validated, enhanced, rejected)
7. Detailed reasoning for your assessment

Consider the target audience and purpose of {ctx.deps.site_config.site_name}.
Quality threshold for publication: {ctx.deps.quality_threshold}
"""
        
        # Process through LLM with structured output
        result = await ctx.run_llm(validation_prompt)
        
        # Determine recommendation based on quality score
        if result.overall_quality_score >= 0.8:
            result.recommendation = ContentStatus.VALIDATED
        elif result.overall_quality_score >= ctx.deps.quality_threshold:
            result.recommendation = ContentStatus.ENHANCED
        else:
            result.recommendation = ContentStatus.REJECTED
        
        logger.info(f"Quality assessment: {result.overall_quality_score:.2f} -> {result.recommendation}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to validate content quality: {e}")
        # Return conservative assessment
        return QualityResult(
            overall_quality_score=0.5,
            recommendation=ContentStatus.ENHANCED,
            quality_metrics=QualityMetrics(
                completeness_score=0.5,
                relevance_score=0.5,
                engagement_score=0.5,
                uniqueness_score=0.5,
                language_quality_score=0.5
            ),
            issues_found=[QualityIssue.INSUFFICIENT_INFORMATION],
            strengths=[],
            improvement_suggestions=["Quality validation failed - manual review needed"],
            reasoning=f"Quality validation error: {str(e)}"
        )


@quality_validator_agent.tool
async def check_content_duplicates(
    ctx: RunContext[QualityValidatorDependencies],
    title: str,
    description: Optional[str] = None,
    existing_content: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Check for duplicate or near-duplicate content.
    
    Args:
        title: Content title to check
        description: Content description
        existing_content: List of existing content titles/descriptions
        
    Returns:
        Dictionary with duplicate analysis results
    """
    try:
        if not ctx.deps.check_duplicates or not existing_content:
            return {
                "is_duplicate": False,
                "similarity_score": 0.0,
                "similar_content": [],
                "reasoning": "Duplicate checking disabled or no existing content"
            }
        
        # Build context for duplicate checking
        check_content = f"Title: {title}"
        if description:
            check_content += f"\nDescription: {description}"
        
        existing_list = "\n".join([f"- {content}" for content in existing_content[:50]])  # Limit to 50
        
        duplicate_prompt = f"""
Check if this new content is duplicate or very similar to existing content:

NEW CONTENT:
{check_content}

EXISTING CONTENT:
{existing_list}

Analyze for:
1. Exact or near-exact duplicates
2. Very similar titles or topics
3. Repetitive content that adds no value

Return assessment of similarity and any matches found.
"""
        
        result = await ctx.run_llm(duplicate_prompt)
        
        # Parse result (simplified - in production might use structured output)
        is_duplicate = any(word in result.lower() for word in ['duplicate', 'very similar', 'exact match'])
        
        return {
            "is_duplicate": is_duplicate,
            "similarity_score": 0.8 if is_duplicate else 0.2,
            "similar_content": [],  # Would parse from result in production
            "reasoning": result
        }
        
    except Exception as e:
        logger.error(f"Failed to check duplicates: {e}")
        return {
            "is_duplicate": False,
            "similarity_score": 0.0,
            "similar_content": [],
            "reasoning": f"Duplicate check failed: {str(e)}"
        }


@quality_validator_agent.tool
async def batch_validate_content(
    ctx: RunContext[QualityValidatorDependencies],
    content_batch: List[Dict[str, Any]]
) -> List[QualityResult]:
    """
    Validate multiple content items efficiently.
    
    Args:
        content_batch: List of content dictionaries to validate
        
    Returns:
        List of QualityResult objects
    """
    try:
        results = []
        
        for content in content_batch:
            result = await validate_content_quality(
                ctx,
                title=content.get('title', ''),
                description=content.get('description'),
                category=content.get('category'),
                image_url=content.get('image_url'),
                source_url=content.get('source_url'),
                date=content.get('date')
            )
            results.append(result)
        
        logger.info(f"Batch validated {len(results)} content items")
        return results
        
    except Exception as e:
        logger.error(f"Failed to batch validate content: {e}")
        # Return conservative assessments
        return [
            QualityResult(
                overall_quality_score=0.5,
                recommendation=ContentStatus.ENHANCED,
                quality_metrics=QualityMetrics(
                    completeness_score=0.5,
                    relevance_score=0.5,
                    engagement_score=0.5,
                    uniqueness_score=0.5,
                    language_quality_score=0.5
                ),
                issues_found=[QualityIssue.INSUFFICIENT_INFORMATION],
                strengths=[],
                improvement_suggestions=["Batch validation failed - manual review needed"],
                reasoning="Batch validation error"
            ) for _ in content_batch
        ]


class QualityValidatorAgent:
    """
    Quality Validation Agent wrapper for easier usage.
    
    This class provides a simplified interface for content quality validation
    operations using the Pydantic AI agent.
    """
    
    def __init__(self, site_config: SiteConfig, **kwargs):
        """
        Initialize quality validator.
        
        Args:
            site_config: Site configuration
            **kwargs: Additional configuration options
        """
        self.dependencies = QualityValidatorDependencies(
            site_config=site_config,
            quality_threshold=kwargs.get('quality_threshold', 0.6),
            strict_validation=kwargs.get('strict_validation', False),
            check_duplicates=kwargs.get('check_duplicates', True),
            relevance_keywords=kwargs.get('relevance_keywords'),
            content_history=kwargs.get('content_history', [])
        )
    
    async def validate_content(self, content: EnhancedContent) -> QualityResult:
        """
        Validate enhanced content quality.
        
        Args:
            content: Enhanced content to validate
            
        Returns:
            QualityResult with detailed assessment
        """
        try:
            logger.info(f"Validating content quality: {content.title}")
            
            result = await quality_validator_agent.run(
                "validate_content_quality",
                deps=self.dependencies,
                title=content.title,
                description=content.excerpt,
                category=content.category,
                image_url=str(content.image),
                source_url=str(content.url),
                date=content.date
            )
            
            logger.info(f"Quality score: {result.data.overall_quality_score:.2f} -> {result.data.recommendation}")
            return result.data
            
        except Exception as e:
            logger.error(f"Failed to validate content {content.title}: {e}")
            # Return conservative assessment
            return QualityResult(
                overall_quality_score=0.5,
                recommendation=ContentStatus.ENHANCED,
                quality_metrics=QualityMetrics(
                    completeness_score=0.5,
                    relevance_score=0.5,
                    engagement_score=0.5,
                    uniqueness_score=0.5,
                    language_quality_score=0.5
                ),
                issues_found=[QualityIssue.INSUFFICIENT_INFORMATION],
                strengths=[],
                improvement_suggestions=["Validation error - manual review needed"],
                reasoning=f"Validation error: {str(e)}"
            )
    
    async def batch_validate(self, content_list: List[EnhancedContent]) -> List[QualityResult]:
        """
        Validate multiple content items.
        
        Args:
            content_list: List of enhanced content to validate
            
        Returns:
            List of QualityResult objects
        """
        try:
            logger.info(f"Batch validating {len(content_list)} items")
            
            # Prepare content for batch processing
            content_batch = []
            for content in content_list:
                content_batch.append({
                    'title': content.title,
                    'description': content.excerpt,
                    'category': content.category,
                    'image_url': str(content.image),
                    'source_url': str(content.url),
                    'date': content.date
                })
            
            result = await quality_validator_agent.run(
                "batch_validate_content",
                deps=self.dependencies,
                content_batch=content_batch
            )
            
            logger.info(f"Batch validated {len(result.data)} items")
            return result.data
            
        except Exception as e:
            logger.error(f"Failed to batch validate content: {e}")
            # Return conservative assessments
            return [
                QualityResult(
                    overall_quality_score=0.5,
                    recommendation=ContentStatus.ENHANCED,
                    quality_metrics=QualityMetrics(
                        completeness_score=0.5,
                        relevance_score=0.5,
                        engagement_score=0.5,
                        uniqueness_score=0.5,
                        language_quality_score=0.5
                    ),
                    issues_found=[QualityIssue.INSUFFICIENT_INFORMATION],
                    strengths=[],
                    improvement_suggestions=["Batch validation failed - manual review needed"],
                    reasoning="Batch validation error"
                ) for _ in content_list
            ]
    
    def filter_high_quality_content(
        self, 
        content_list: List[EnhancedContent], 
        quality_results: List[QualityResult]
    ) -> List[EnhancedContent]:
        """
        Filter content list to only include high-quality items.
        
        Args:
            content_list: List of enhanced content
            quality_results: Corresponding quality results
            
        Returns:
            Filtered list of high-quality content
        """
        try:
            high_quality_content = []
            
            for content, quality in zip(content_list, quality_results):
                if quality.recommendation in [ContentStatus.VALIDATED, ContentStatus.ENHANCED]:
                    # Update quality score in content
                    content.quality_score = quality.overall_quality_score
                    high_quality_content.append(content)
                else:
                    logger.info(f"Filtered out low-quality content: {content.title}")
            
            logger.info(f"Filtered to {len(high_quality_content)} high-quality items from {len(content_list)} total")
            return high_quality_content
            
        except Exception as e:
            logger.error(f"Failed to filter content: {e}")
            return content_list  # Return all content on error
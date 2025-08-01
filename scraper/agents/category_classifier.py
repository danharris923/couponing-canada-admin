"""
Category Classification Agent using Pydantic AI.
Automatically categorizes content items using AI with consistent taxonomies.
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
from scraper.models.content import RawContent, EnhancedContent

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


class StandardCategory(str, Enum):
    """Standard content categories."""
    TECHNOLOGY = "Technology"
    BUSINESS = "Business"
    HEALTH = "Health"
    LIFESTYLE = "Lifestyle"
    ENTERTAINMENT = "Entertainment"
    SPORTS = "Sports"
    SCIENCE = "Science"
    EDUCATION = "Education"
    TRAVEL = "Travel"
    FOOD = "Food"
    FASHION = "Fashion"
    HOME = "Home & Garden"
    FINANCE = "Finance"
    AUTOMOTIVE = "Automotive"
    GENERAL = "General"


class CategoryResult(BaseModel):
    """Structured result for category classification."""
    
    primary_category: StandardCategory = Field(..., description="Primary category for the content")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in classification (0-1)")
    secondary_categories: List[StandardCategory] = Field(default_factory=list, description="Additional relevant categories")
    reasoning: str = Field(..., description="Brief explanation for the categorization")
    keywords: List[str] = Field(default_factory=list, description="Key terms that influenced categorization")


@dataclass
class CategoryClassifierDependencies:
    """Dependencies for category classification agent."""
    site_config: SiteConfig
    custom_categories: Optional[List[str]] = None
    confidence_threshold: float = 0.6
    enable_secondary_categories: bool = True
    max_categories: int = 3


CATEGORY_CLASSIFIER_SYSTEM_PROMPT = """
You are an expert content categorization specialist for {site_name}. Your role is to accurately 
classify content into appropriate categories based on title, description, and context.

Available Standard Categories:
- Technology: Tech news, gadgets, software, AI, programming, digital trends
- Business: Entrepreneurship, startups, marketing, finance, corporate news
- Health: Medical news, fitness, wellness, mental health, nutrition
- Lifestyle: Personal development, relationships, hobbies, culture
- Entertainment: Movies, TV, music, games, celebrities, events
- Sports: All sports, athletes, competitions, fitness activities
- Science: Research, discoveries, space, environment, biology, physics
- Education: Learning, schools, courses, academic research, skills
- Travel: Destinations, tips, reviews, transportation, tourism
- Food: Recipes, restaurants, cooking, nutrition, food culture
- Fashion: Clothing, style, beauty, trends, accessories
- Home & Garden: DIY, decorating, gardening, real estate, maintenance
- Finance: Investing, money management, economics, banking, crypto
- Automotive: Cars, motorcycles, transportation, reviews, industry news
- General: Content that doesn't fit other categories clearly

Classification Guidelines:
1. **Primary Focus**: Choose the category that best represents the main topic
2. **Confidence**: Only classify with high confidence - use "General" if uncertain
3. **Context Matters**: Consider the target audience of {site_name}
4. **Consistency**: Use the same category for similar content types
5. **Keywords**: Identify key terms that support your classification
6. **Secondary**: Add related categories if content spans multiple areas

Always provide structured output with confidence scores and reasoning.
"""


# Create the category classifier agent with structured output
category_classifier_agent = Agent(
    get_llm_model(),
    deps_type=CategoryClassifierDependencies,
    result_type=CategoryResult,
    system_prompt=CATEGORY_CLASSIFIER_SYSTEM_PROMPT
)


@category_classifier_agent.system_prompt
def dynamic_classifier_prompt(ctx: RunContext[CategoryClassifierDependencies]) -> str:
    """Dynamic system prompt that includes site-specific context."""
    base_prompt = CATEGORY_CLASSIFIER_SYSTEM_PROMPT.format(
        site_name=ctx.deps.site_config.site_name
    )
    
    # Add custom categories if provided
    if ctx.deps.custom_categories:
        custom_cats = "\n".join(f"- {cat}" for cat in ctx.deps.custom_categories)
        base_prompt += f"\n\nAdditional Custom Categories for {ctx.deps.site_config.site_name}:\n{custom_cats}"
    
    return base_prompt


@category_classifier_agent.tool
async def classify_content(
    ctx: RunContext[CategoryClassifierDependencies],
    title: str,
    description: Optional[str] = None,
    source_url: Optional[str] = None,
    existing_category: Optional[str] = None
) -> CategoryResult:
    """
    Classify content into appropriate categories.
    
    Args:
        title: Content title
        description: Content description/excerpt
        source_url: Source URL for additional context
        existing_category: Existing category if any
        
    Returns:
        CategoryResult with classification details
    """
    try:
        # Build classification context
        context_parts = [f"Title: {title}"]
        
        if description:
            context_parts.append(f"Description: {description}")
        
        if source_url:
            context_parts.append(f"Source: {source_url}")
            
        if existing_category:
            context_parts.append(f"Suggested category: {existing_category}")
        
        context = "\n".join(context_parts)
        
        # Create classification prompt
        classification_prompt = f"""
Analyze this content and classify it into the most appropriate category:

{context}

Provide a structured classification with:
1. Primary category from the standard list
2. Confidence score (0.0 to 1.0)
3. Up to {ctx.deps.max_categories - 1} secondary categories if relevant
4. Brief reasoning for your choice
5. Key terms that influenced your decision

Consider the target audience and purpose of {ctx.deps.site_config.site_name} in your classification.
"""
        
        # Process through LLM with structured output
        result = await ctx.run_llm(classification_prompt)
        
        # Validate confidence threshold
        if result.confidence_score < ctx.deps.confidence_threshold:
            logger.warning(f"Low confidence classification ({result.confidence_score}) for: {title[:50]}...")
            # Return General category for low confidence
            return CategoryResult(
                primary_category=StandardCategory.GENERAL,
                confidence_score=result.confidence_score,
                secondary_categories=[],
                reasoning=f"Low confidence in original classification: {result.reasoning}",
                keywords=result.keywords
            )
        
        logger.info(f"Classified content as {result.primary_category} (confidence: {result.confidence_score})")
        return result
        
    except Exception as e:
        logger.error(f"Failed to classify content: {e}")
        # Return fallback classification
        return CategoryResult(
            primary_category=StandardCategory.GENERAL,
            confidence_score=0.5,
            secondary_categories=[],
            reasoning="Classification failed, using default category",
            keywords=[]
        )


@category_classifier_agent.tool
async def batch_classify_content(
    ctx: RunContext[CategoryClassifierDependencies],
    content_items: List[Dict[str, str]]
) -> List[CategoryResult]:
    """
    Classify multiple content items efficiently.
    
    Args:
        content_items: List of content dictionaries with title, description, etc.
        
    Returns:
        List of CategoryResult objects
    """
    try:
        results = []
        
        for item in content_items:
            result = await classify_content(
                ctx,
                title=item.get('title', ''),
                description=item.get('description'),
                source_url=item.get('source_url'),
                existing_category=item.get('existing_category')
            )
            results.append(result)
        
        logger.info(f"Batch classified {len(results)} content items")
        return results
        
    except Exception as e:
        logger.error(f"Failed to batch classify content: {e}")
        # Return fallback results
        return [
            CategoryResult(
                primary_category=StandardCategory.GENERAL,
                confidence_score=0.5,
                secondary_categories=[],
                reasoning="Batch classification failed",
                keywords=[]
            ) for _ in content_items
        ]


@category_classifier_agent.tool
async def suggest_custom_categories(
    ctx: RunContext[CategoryClassifierDependencies],
    sample_content: List[Dict[str, str]],
    num_suggestions: int = 5
) -> List[str]:
    """
    Suggest custom categories based on sample content.
    
    Args:
        sample_content: Sample content items to analyze
        num_suggestions: Number of category suggestions to return
        
    Returns:
        List of suggested custom category names
    """
    try:
        # Analyze sample content
        content_summary = []
        for item in sample_content[:20]:  # Limit to 20 items
            title = item.get('title', '')
            description = item.get('description', '')
            content_summary.append(f"- {title}: {description[:100]}")
        
        sample_text = "\n".join(content_summary)
        
        suggestion_prompt = f"""
Based on this sample content from {ctx.deps.site_config.site_name}:

{sample_text}

Suggest {num_suggestions} custom category names that would be more specific and useful than the standard categories. 

Consider:
1. Common themes in the content
2. Specific niches or specializations
3. Target audience interests
4. Site focus and purpose

Return the suggestions as a simple list of category names, one per line.
"""
        
        result = await ctx.run_llm(suggestion_prompt)
        
        # Parse suggestions
        suggestions = [
            line.strip().strip('-').strip() 
            for line in result.split('\n') 
            if line.strip() and not line.strip().startswith('#')
        ][:num_suggestions]
        
        logger.info(f"Generated {len(suggestions)} custom category suggestions")
        return suggestions
        
    except Exception as e:
        logger.error(f"Failed to suggest custom categories: {e}")
        return []


class CategoryClassifierAgent:
    """
    Category Classification Agent wrapper for easier usage.
    
    This class provides a simplified interface for content categorization
    operations using the Pydantic AI agent.
    """
    
    def __init__(self, site_config: SiteConfig, **kwargs):
        """
        Initialize category classifier.
        
        Args:
            site_config: Site configuration
            **kwargs: Additional configuration options
        """
        self.dependencies = CategoryClassifierDependencies(
            site_config=site_config,
            custom_categories=kwargs.get('custom_categories'),
            confidence_threshold=kwargs.get('confidence_threshold', 0.6),
            enable_secondary_categories=kwargs.get('enable_secondary_categories', True),
            max_categories=kwargs.get('max_categories', 3)
        )
    
    async def classify_content(self, content: RawContent) -> CategoryResult:
        """
        Classify raw content into categories.
        
        Args:
            content: Raw content to classify
            
        Returns:
            CategoryResult with classification details
        """
        try:
            logger.info(f"Classifying content: {content.title}")
            
            result = await category_classifier_agent.run(
                "classify_content",
                deps=self.dependencies,
                title=content.title,
                description=content.excerpt,
                source_url=str(content.source_url),
                existing_category=content.category
            )
            
            logger.info(f"Classified as {result.data.primary_category} with confidence {result.data.confidence_score}")
            return result.data
            
        except Exception as e:
            logger.error(f"Failed to classify content {content.title}: {e}")
            # Return fallback classification
            return CategoryResult(
                primary_category=StandardCategory.GENERAL,
                confidence_score=0.5,
                secondary_categories=[],
                reasoning=f"Classification error: {str(e)}",
                keywords=[]
            )
    
    async def batch_classify(self, content_list: List[RawContent]) -> List[CategoryResult]:
        """
        Classify multiple content items.
        
        Args:
            content_list: List of raw content to classify
            
        Returns:
            List of CategoryResult objects
        """
        try:
            logger.info(f"Batch classifying {len(content_list)} items")
            
            # Prepare content items for batch processing
            content_items = []
            for content in content_list:
                content_items.append({
                    'title': content.title,
                    'description': content.excerpt,
                    'source_url': str(content.source_url),
                    'existing_category': content.category
                })
            
            result = await category_classifier_agent.run(
                "batch_classify_content",
                deps=self.dependencies,
                content_items=content_items
            )
            
            logger.info(f"Batch classified {len(result.data)} items")
            return result.data
            
        except Exception as e:
            logger.error(f"Failed to batch classify content: {e}")
            # Return fallback classifications
            return [
                CategoryResult(
                    primary_category=StandardCategory.GENERAL,
                    confidence_score=0.5,
                    secondary_categories=[],
                    reasoning="Batch classification failed",
                    keywords=[]
                ) for _ in content_list
            ]
    
    async def suggest_categories_for_site(self, sample_content: List[RawContent]) -> List[str]:
        """
        Suggest custom categories based on site content.
        
        Args:
            sample_content: Sample content to analyze
            
        Returns:
            List of suggested category names
        """
        try:
            logger.info(f"Analyzing {len(sample_content)} items for category suggestions")
            
            # Prepare sample content
            content_items = []
            for content in sample_content:
                content_items.append({
                    'title': content.title,
                    'description': content.excerpt or '',
                    'source_url': str(content.source_url)
                })
            
            result = await category_classifier_agent.run(
                "suggest_custom_categories",
                deps=self.dependencies,
                sample_content=content_items,
                num_suggestions=5
            )
            
            logger.info(f"Generated {len(result.data)} category suggestions")
            return result.data
            
        except Exception as e:
            logger.error(f"Failed to suggest categories: {e}")
            return []
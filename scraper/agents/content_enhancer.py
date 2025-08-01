"""
Content Enhancement Agent using Pydantic AI.
Enhances content descriptions, generates missing content, and improves quality.
"""

import logging
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic_settings import BaseSettings
from pydantic import Field
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


@dataclass  
class ContentEnhancerDependencies:
    """Dependencies for content enhancement agent."""
    site_config: SiteConfig
    quality_threshold: float = 0.7
    max_description_length: int = 200
    enhancement_style: str = "engaging"  # engaging, professional, casual, technical
    

CONTENT_ENHANCER_SYSTEM_PROMPT = """
You are an expert content enhancement specialist for {site_name}. Your role is to improve content quality, 
generate engaging descriptions, and ensure consistency across all content items.

Your capabilities:
- Enhance and rewrite content descriptions for better engagement
- Generate missing content descriptions from titles and context
- Improve content titles for better click-through rates
- Ensure content is SEO-friendly and informative
- Maintain consistent tone and style

Guidelines:
1. **Tone & Style**: Adapt to {enhancement_style} style appropriate for {site_name}
2. **Length Limits**: Keep descriptions under {max_description_length} characters
3. **Engagement**: Create descriptions that encourage clicks without being clickbait
4. **SEO**: Use relevant keywords naturally within the content
5. **Accuracy**: Never fabricate facts - only enhance presentation of existing information
6. **Consistency**: Maintain consistent quality and style across all content
7. **Value**: Focus on what makes the content valuable to readers

Remember: Your goal is to make content more appealing and discoverable while maintaining accuracy and authenticity.
"""


# Create the content enhancer agent
content_enhancer_agent = Agent(
    get_llm_model(),
    deps_type=ContentEnhancerDependencies,
    system_prompt=CONTENT_ENHANCER_SYSTEM_PROMPT
)


@content_enhancer_agent.system_prompt
def dynamic_enhancer_prompt(ctx: RunContext[ContentEnhancerDependencies]) -> str:
    """Dynamic system prompt that includes site-specific context."""
    return CONTENT_ENHANCER_SYSTEM_PROMPT.format(
        site_name=ctx.deps.site_config.site_name,
        enhancement_style=ctx.deps.enhancement_style,
        max_description_length=ctx.deps.max_description_length
    )


@content_enhancer_agent.tool
async def enhance_description(
    ctx: RunContext[ContentEnhancerDependencies],
    original_title: str,
    original_excerpt: Optional[str] = None,
    category: Optional[str] = None,
    source_url: Optional[str] = None
) -> str:
    """
    Enhance content description for better engagement and SEO.
    
    Args:
        original_title: Original content title
        original_excerpt: Original excerpt/description if available
        category: Content category for context
        source_url: Source URL for additional context
        
    Returns:
        Enhanced description string
    """
    try:
        # Build context for enhancement
        context_parts = [f"Title: {original_title}"]
        
        if original_excerpt:
            context_parts.append(f"Original description: {original_excerpt}")
        else:
            context_parts.append("Original description: Not provided")
            
        if category:
            context_parts.append(f"Category: {category}")
            
        if source_url:
            context_parts.append(f"Source: {source_url}")
        
        context = "\n".join(context_parts)
        
        # Create enhancement prompt
        enhancement_prompt = f"""
Based on this content:
{context}

Create an engaging description that:
1. Is under {ctx.deps.max_description_length} characters
2. Highlights key benefits or interesting aspects  
3. Uses language appropriate for {ctx.deps.site_config.site_name}
4. Encourages user engagement without being clickbait
5. Is SEO-friendly with natural keyword usage
6. Matches the {ctx.deps.enhancement_style} style

Return only the enhanced description, no additional text.
"""
        
        # Process through LLM
        result = await ctx.run_llm(enhancement_prompt)
        enhanced_description = result.strip()
        
        # Validate length
        if len(enhanced_description) > ctx.deps.max_description_length:
            # Truncate if too long
            enhanced_description = enhanced_description[:ctx.deps.max_description_length - 3] + "..."
        
        logger.info(f"Enhanced description for: {original_title[:50]}...")
        return enhanced_description
        
    except Exception as e:
        logger.error(f"Failed to enhance description: {e}")
        # Return original or generate fallback
        return original_excerpt or f"Discover more about {original_title}"


@content_enhancer_agent.tool
async def improve_title(
    ctx: RunContext[ContentEnhancerDependencies],
    original_title: str,
    category: Optional[str] = None,
    excerpt: Optional[str] = None
) -> str:
    """
    Improve content title for better engagement while maintaining accuracy.
    
    Args:
        original_title: Original content title
        category: Content category for context
        excerpt: Content excerpt for context
        
    Returns:
        Improved title string
    """
    try:
        # Build context
        context_parts = [f"Original title: {original_title}"]
        
        if category:
            context_parts.append(f"Category: {category}")
            
        if excerpt:
            context_parts.append(f"Content summary: {excerpt[:200]}...")
            
        context = "\n".join(context_parts)
        
        # Create improvement prompt
        improvement_prompt = f"""
Based on this content:
{context}

Improve the title to be more engaging while maintaining accuracy. The improved title should:
1. Be more compelling and click-worthy
2. Stay truthful to the original content
3. Be appropriate for {ctx.deps.site_config.site_name}
4. Match the {ctx.deps.enhancement_style} style
5. Be under 100 characters
6. Include relevant keywords naturally

Return only the improved title, no additional text.
"""
        
        # Process through LLM
        result = await ctx.run_llm(improvement_prompt)
        improved_title = result.strip()
        
        # Validate and clean
        if len(improved_title) > 100:
            improved_title = improved_title[:97] + "..."
            
        # Remove quotes if present
        improved_title = improved_title.strip('"\'')
        
        logger.info(f"Improved title: {original_title} -> {improved_title}")
        return improved_title
        
    except Exception as e:
        logger.error(f"Failed to improve title: {e}")
        return original_title  # Return original on failure


@content_enhancer_agent.tool
async def generate_missing_content(
    ctx: RunContext[ContentEnhancerDependencies],
    title: str,
    available_content: Dict[str, Any],
    missing_fields: List[str]
) -> Dict[str, str]:
    """
    Generate missing content fields based on available information.
    
    Args:
        title: Content title
        available_content: Dictionary of available content fields
        missing_fields: List of fields that need to be generated
        
    Returns:
        Dictionary of generated content fields
    """
    try:
        # Build context from available content
        context_parts = [f"Title: {title}"]
        
        for field, value in available_content.items():
            if value:
                context_parts.append(f"{field.title()}: {value}")
        
        context = "\n".join(context_parts)
        
        # Create generation prompt
        generation_prompt = f"""
Based on this available content:
{context}

Generate appropriate content for these missing fields: {', '.join(missing_fields)}

Guidelines:
- Keep generated content consistent with available information
- Make it appropriate for {ctx.deps.site_config.site_name}
- Use {ctx.deps.enhancement_style} style
- Be helpful and informative
- Don't fabricate specific facts

Return the generated content as a JSON object with the field names as keys.
"""
        
        # Process through LLM
        result = await ctx.run_llm(generation_prompt)
        
        # Try to parse as JSON
        import json
        try:
            generated_content = json.loads(result)
        except json.JSONDecodeError:
            # Fallback: create simple generated content
            generated_content = {}
            for field in missing_fields:
                if field == 'excerpt':
                    generated_content[field] = f"Learn more about {title}"
                elif field == 'category':
                    generated_content[field] = "General"
                else:
                    generated_content[field] = f"Generated {field} for {title}"
        
        logger.info(f"Generated missing fields {missing_fields} for: {title[:50]}...")
        return generated_content
        
    except Exception as e:
        logger.error(f"Failed to generate missing content: {e}")
        # Return minimal generated content
        return {field: f"Generated {field}" for field in missing_fields}


class ContentEnhancerAgent:
    """
    Content Enhancement Agent wrapper for easier usage.
    
    This class provides a simplified interface for content enhancement
    operations using the Pydantic AI agent.
    """
    
    def __init__(self, site_config: SiteConfig, **kwargs):
        """
        Initialize content enhancer.
        
        Args:
            site_config: Site configuration
            **kwargs: Additional configuration options
        """
        self.dependencies = ContentEnhancerDependencies(
            site_config=site_config,
            quality_threshold=kwargs.get('quality_threshold', 0.7),
            max_description_length=kwargs.get('max_description_length', 200),
            enhancement_style=kwargs.get('enhancement_style', 'engaging')
        )
    
    async def enhance_content(self, raw_content: RawContent) -> EnhancedContent:
        """
        Enhance raw content using AI.
        
        Args:
            raw_content: Raw content to enhance
            
        Returns:
            Enhanced content with AI improvements
        """
        try:
            logger.info(f"Enhancing content: {raw_content.title}")
            
            # Determine what needs enhancement
            ai_generated_fields = []
            
            # Enhance description
            enhanced_excerpt = await content_enhancer_agent.run(
                "enhance_description",
                deps=self.dependencies,
                original_title=raw_content.title,
                original_excerpt=raw_content.excerpt,
                category=raw_content.category,
                source_url=str(raw_content.source_url)
            )
            
            if enhanced_excerpt.data != raw_content.excerpt:
                ai_generated_fields.append('excerpt')
            
            # Improve title if needed
            enhanced_title = raw_content.title
            if len(raw_content.title) < 30 or not any(word in raw_content.title.lower() for word in ['how', 'why', 'what', 'best', 'top']):
                improved_title_result = await content_enhancer_agent.run(
                    "improve_title",
                    deps=self.dependencies,
                    original_title=raw_content.title,
                    category=raw_content.category,
                    excerpt=raw_content.excerpt
                )
                enhanced_title = improved_title_result.data
                if enhanced_title != raw_content.title:
                    ai_generated_fields.append('title')
            
            # Handle missing fields
            missing_fields = []
            if not raw_content.image:
                missing_fields.append('image')
            if not raw_content.category:
                missing_fields.append('category')
            
            generated_content = {}
            if missing_fields:
                generated_result = await content_enhancer_agent.run(
                    "generate_missing_content",
                    deps=self.dependencies,
                    title=raw_content.title,
                    available_content={
                        'excerpt': raw_content.excerpt,
                        'category': raw_content.category,
                        'url': str(raw_content.url)
                    },
                    missing_fields=missing_fields
                )
                generated_content = generated_result.data
                ai_generated_fields.extend(missing_fields)
            
            # Create enhanced content
            enhanced_content = EnhancedContent(
                title=enhanced_title,
                url=raw_content.url,
                image=raw_content.image or generated_content.get('image', '/placeholder-deal.svg'),
                excerpt=enhanced_excerpt.data,
                category=raw_content.category or generated_content.get('category', 'General'),
                date=raw_content.date or raw_content.scraped_at.strftime('%Y-%m-%d'),
                quality_score=0.8,  # Default good quality score for enhanced content
                ai_generated_fields=ai_generated_fields,
                enhancement_notes=f"Enhanced by ContentEnhancerAgent with {len(ai_generated_fields)} field(s) improved",
                original_content=raw_content
            )
            
            logger.info(f"Successfully enhanced content: {enhanced_content.title}")
            return enhanced_content
            
        except Exception as e:
            logger.error(f"Failed to enhance content {raw_content.title}: {e}")
            raise
"""
Main orchestration system for the modular content scraper.
Coordinates scraping, AI enhancement, and output generation.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse
import sys

# Setup module path
sys.path.insert(0, str(Path(__file__).parent))

from config.validator import validate_config_file, SiteConfig
from models.config import ScraperSettings, ScraperType
from models.content import RawContent, EnhancedContent, ContentProcessingResult, BatchProcessingResult, ContentStatus
from models.output import DealOutput, OutputSummary, convert_to_deal_output
from modules import RSSScraperModule, WordPressScraperModule, CustomScraperModule
from agents import ContentEnhancerAgent, CategoryClassifierAgent, QualityValidatorAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scraper.log')
    ]
)
logger = logging.getLogger(__name__)


class ContentPipeline:
    """
    Main content processing pipeline.
    
    Orchestrates the entire flow from scraping to AI enhancement to output generation.
    """
    
    def __init__(self, config: SiteConfig, settings: Optional[ScraperSettings] = None):
        """
        Initialize the content pipeline.
        
        Args:
            config: Site configuration
            settings: Optional scraper settings
        """
        self.config = config
        self.settings = settings or ScraperSettings()
        
        # Initialize scraper module
        self.scraper_module = self._create_scraper_module()
        
        # Initialize AI agents if enabled
        self.ai_agents_enabled = config.ai_enhancement_enabled
        if self.ai_agents_enabled:
            try:
                self.content_enhancer = ContentEnhancerAgent(config)
                self.category_classifier = CategoryClassifierAgent(config)
                self.quality_validator = QualityValidatorAgent(config)
                logger.info("AI agents initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize AI agents: {e}")
                self.ai_agents_enabled = False
        
        # Processing statistics
        self.stats = {
            'total_scraped': 0,
            'total_enhanced': 0,
            'total_validated': 0,
            'total_output': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
    
    def _create_scraper_module(self):
        """Create appropriate scraper module based on configuration."""
        scraper_type = self.config.scraper_type
        
        if scraper_type == ScraperType.RSS:
            return RSSScraperModule(self.config, self.settings)
        elif scraper_type == ScraperType.WORDPRESS:
            return WordPressScraperModule(self.config, self.settings)
        elif scraper_type == ScraperType.CUSTOM:
            return CustomScraperModule(self.config, self.settings)
        else:
            raise ValueError(f"Unsupported scraper type: {scraper_type}")
    
    async def run_pipeline(self, output_path: str = "public/data.json") -> OutputSummary:
        """
        Run the complete content processing pipeline.
        
        Args:
            output_path: Path to write output JSON
            
        Returns:
            OutputSummary with processing statistics
        """
        logger.info(f"Starting content pipeline for {self.config.site_name}")
        self.stats['start_time'] = datetime.now()
        
        try:
            # Phase 1: Scrape content
            logger.info("Phase 1: Scraping content from sources")
            raw_content = await self._scrape_content()
            self.stats['total_scraped'] = len(raw_content)
            
            if not raw_content:
                logger.warning("No content scraped from sources")
                return self._create_output_summary(output_path, [])
            
            # Phase 2: AI Enhancement (if enabled)
            if self.ai_agents_enabled:
                logger.info("Phase 2: AI content enhancement")
                enhanced_content = await self._enhance_content(raw_content)
                self.stats['total_enhanced'] = len(enhanced_content)
                
                # Phase 3: Quality validation
                logger.info("Phase 3: Quality validation")
                validated_content = await self._validate_content(enhanced_content)
                self.stats['total_validated'] = len(validated_content)
            else:
                logger.info("AI enhancement disabled, converting raw content")
                validated_content = await self._convert_raw_to_enhanced(raw_content)
                self.stats['total_enhanced'] = len(validated_content)
                self.stats['total_validated'] = len(validated_content)
            
            # Phase 4: Generate output
            logger.info("Phase 4: Generating output")
            output_data = await self._generate_output(validated_content)
            self.stats['total_output'] = len(output_data)
            
            # Phase 5: Write output file
            logger.info("Phase 5: Writing output file")
            await self._write_output_file(output_data, output_path)
            
            self.stats['end_time'] = datetime.now()
            
            summary = self._create_output_summary(output_path, output_data)
            logger.info(f"Pipeline completed successfully: {summary.successful_items} items generated")
            
            return summary
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            self.stats['errors'] += 1
            self.stats['end_time'] = datetime.now()
            raise
    
    async def _scrape_content(self) -> List[RawContent]:
        """Scrape content from all configured sources."""
        try:
            logger.info(f"Scraping from {len(self.config.feeds)} sources using {self.config.scraper_type} scraper")
            
            raw_content = await self.scraper_module.scrape_all_feeds()
            
            logger.info(f"Successfully scraped {len(raw_content)} items")
            return raw_content
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            self.stats['errors'] += 1
            return []
    
    async def _enhance_content(self, raw_content: List[RawContent]) -> List[EnhancedContent]:
        """Enhance content using AI agents."""
        try:
            enhanced_content = []
            
            logger.info(f"Enhancing {len(raw_content)} content items")
            
            # Process content in batches to avoid overwhelming the AI
            batch_size = 5
            for i in range(0, len(raw_content), batch_size):
                batch = raw_content[i:i + batch_size]
                
                for content in batch:
                    try:
                        enhanced = await self.content_enhancer.enhance_content(content)
                        enhanced_content.append(enhanced)
                        
                    except Exception as e:
                        logger.warning(f"Failed to enhance content '{content.title}': {e}")
                        # Create minimal enhanced content
                        enhanced = EnhancedContent(
                            title=content.title,
                            url=content.url,
                            image=content.image or '/placeholder-deal.svg',
                            excerpt=content.excerpt or f"Learn more about {content.title}",
                            category=content.category or 'General',
                            date=content.date or content.scraped_at.strftime('%Y-%m-%d'),
                            quality_score=0.6,
                            ai_generated_fields=[],
                            enhancement_notes="Enhancement failed, using original content",
                            original_content=content
                        )
                        enhanced_content.append(enhanced)
                        self.stats['errors'] += 1
                
                # Small delay between batches
                await asyncio.sleep(1)
            
            logger.info(f"Enhanced {len(enhanced_content)} content items")
            return enhanced_content
            
        except Exception as e:
            logger.error(f"Content enhancement failed: {e}")
            self.stats['errors'] += 1
            return []
    
    async def _validate_content(self, enhanced_content: List[EnhancedContent]) -> List[EnhancedContent]:
        """Validate content quality and filter high-quality items."""
        try:
            logger.info(f"Validating {len(enhanced_content)} enhanced items")
            
            # Batch validate for efficiency
            quality_results = await self.quality_validator.batch_validate(enhanced_content)
            
            # Filter high-quality content
            validated_content = self.quality_validator.filter_high_quality_content(
                enhanced_content, quality_results
            )
            
            logger.info(f"Validated {len(validated_content)} high-quality items")
            return validated_content
            
        except Exception as e:
            logger.error(f"Content validation failed: {e}")
            self.stats['errors'] += 1
            # Return all content if validation fails
            return enhanced_content
    
    async def _convert_raw_to_enhanced(self, raw_content: List[RawContent]) -> List[EnhancedContent]:
        """Convert raw content to enhanced format without AI processing."""
        enhanced_content = []
        
        for content in raw_content:
            try:
                enhanced = EnhancedContent(
                    title=content.title,
                    url=content.url,
                    image=content.image or '/placeholder-deal.svg',
                    excerpt=content.excerpt or f"Learn more about {content.title}",
                    category=content.category or 'General',
                    date=content.date or content.scraped_at.strftime('%Y-%m-%d'),
                    quality_score=0.7,  # Default quality score
                    ai_generated_fields=[],
                    enhancement_notes="No AI enhancement applied",
                    original_content=content
                )
                enhanced_content.append(enhanced)
                
            except Exception as e:
                logger.warning(f"Failed to convert content '{content.title}': {e}")
                self.stats['errors'] += 1
                continue
        
        return enhanced_content
    
    async def _generate_output(self, validated_content: List[EnhancedContent]) -> List[DealOutput]:
        """Generate standardized output format."""
        try:
            output_data = []
            
            logger.info(f"Converting {len(validated_content)} items to output format")
            
            for content in validated_content:
                try:
                    deal_output = convert_to_deal_output(content, self.config)
                    output_data.append(deal_output)
                    
                except Exception as e:
                    logger.warning(f"Failed to convert content '{content.title}' to output format: {e}")
                    self.stats['errors'] += 1
                    continue
            
            logger.info(f"Generated {len(output_data)} output items")
            return output_data
            
        except Exception as e:
            logger.error(f"Output generation failed: {e}")
            self.stats['errors'] += 1
            return []
    
    async def _write_output_file(self, output_data: List[DealOutput], output_path: str):
        """Write output data to JSON file."""
        try:
            # Ensure output directory exists
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert Pydantic models to dict for JSON serialization
            json_data = [item.model_dump() for item in output_data]
            
            # Write JSON file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Output written to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to write output file: {e}")
            self.stats['errors'] += 1
            raise
    
    def _create_output_summary(self, output_path: str, output_data: List[DealOutput]) -> OutputSummary:
        """Create output summary with statistics."""
        processing_time = 0.0
        if self.stats['start_time'] and self.stats['end_time']:
            processing_time = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        
        # Calculate quality metrics
        quality_scores = [item.featured for item in output_data]  # Using featured as proxy for quality
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        # Get categories
        categories = list(set(item.category for item in output_data))
        
        return OutputSummary(
            total_items=self.stats['total_scraped'],
            successful_items=self.stats['total_output'],
            failed_items=self.stats['errors'],
            output_file=output_path,
            generation_time=processing_time,
            average_quality_score=avg_quality,
            ai_enhanced_count=self.stats['total_enhanced'] if self.ai_agents_enabled else 0,
            categories=categories
        )


async def main():
    """Main entry point for the scraper."""
    parser = argparse.ArgumentParser(description="Modern Template Content Scraper")
    parser.add_argument(
        "--config",
        default="config/config.json",
        help="Path to configuration file (default: config/config.json)"
    )
    parser.add_argument(
        "--output",
        default="public/data.json",
        help="Path to output JSON file (default: public/data.json)"
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Run in test mode (limited processing)"
    )
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Disable AI enhancement"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Load and validate configuration
        logger.info("Loading configuration...")
        config = validate_config_file(args.config)
        
        # Override AI setting if disabled via command line
        if args.no_ai:
            config.ai_enhancement_enabled = False
            logger.info("AI enhancement disabled via command line")
        
        # Create scraper settings
        settings = ScraperSettings()
        if args.test_mode:
            settings.max_concurrent_requests = 2
            logger.info("Running in test mode")
        
        # Initialize and run pipeline
        pipeline = ContentPipeline(config, settings)
        summary = await pipeline.run_pipeline(args.output)
        
        # Print summary
        print("\n" + "="*50)
        print("SCRAPING SUMMARY")
        print("="*50)
        print(f"Site: {config.site_name}")
        print(f"Scraper Type: {config.scraper_type}")
        print(f"Sources: {len(config.feeds)}")
        print(f"Total Items Scraped: {summary.total_items}")
        print(f"Successful Items: {summary.successful_items}")
        print(f"Failed Items: {summary.failed_items}")
        print(f"Success Rate: {summary.success_rate:.1f}%")
        print(f"Processing Time: {summary.generation_time:.2f}s")
        print(f"AI Enhanced: {summary.ai_enhanced_count}")
        print(f"Categories: {len(summary.categories)}")
        print(f"Output File: {summary.output_file}")
        print("="*50)
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        return 1
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        print(f"\nERROR: {e}")
        return 1


if __name__ == "__main__":
    # Run the async main function
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
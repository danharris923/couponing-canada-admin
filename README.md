# Modern Template Content Scraper

A powerful, AI-enhanced content aggregation platform that transforms hardcoded scrapers into configurable, intelligent content processing pipelines using Pydantic AI multi-agent systems.

## 🚀 Features

### 🤖 AI-Powered Content Enhancement
- **Content Enhancement**: Improve titles, descriptions, and missing content using AI
- **Intelligent Categorization**: Automatic content classification with confidence scoring
- **Quality Validation**: AI-driven content quality assessment and filtering
- **Multi-Agent System**: Coordinated AI agents using Pydantic AI framework

### 🔧 Flexible Architecture
- **Configuration-Driven**: Customize everything via JSON configuration files
- **Modular Scrapers**: RSS, WordPress, and custom scraper support
- **Template System**: Transform any content site by editing configuration
- **React Frontend**: Fully configurable React interface with dynamic branding

### 📊 Enterprise Ready
- **Comprehensive Testing**: 80%+ test coverage with unit and integration tests
- **Type Safety**: Full TypeScript and Pydantic validation throughout
- **Error Handling**: Robust error handling and recovery mechanisms
- **Performance**: Async processing with rate limiting and caching

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Sources  │    │  Python Backend  │    │ React Frontend  │
│                 │    │                  │    │                 │
│ • RSS Feeds     │───▶│ • Modular        │───▶│ • Configuration │
│ • WordPress     │    │   Scrapers       │    │   Aware         │
│ • Custom APIs   │    │ • AI Agents      │    │ • Dynamic UI    │
│                 │    │ • Processing     │    │ • Responsive    │
└─────────────────┘    │   Pipeline       │    └─────────────────┘
                       └──────────────────┘
                                │
                       ┌──────────────────┐
                       │  Configuration   │
                       │                  │
                       │ • Site Settings  │
                       │ • Scraper Config │
                       │ • AI Parameters  │
                       │ • UI Branding    │
                       └──────────────────┘
```

## 📦 Installation

### Prerequisites
- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **OpenAI API Key** (for AI features)

### Backend Setup

```bash
# Clone the repository
git clone <repository-url>
cd modern-template

# Create virtual environment
python -m venv venv_linux
source venv_linux/bin/activate  # Linux/Mac
# venv_linux\Scripts\activate     # Windows

# Install Python dependencies
cd scraper
pip install -r requirements.txt

# Set up environment variables
cp ../.env.example .env
# Edit .env with your configuration
```

### Frontend Setup

```bash
# Install Node.js dependencies
npm install

# Start development server
npm start
```

### Quick Start

```bash
# 1. Configure your content sources
cp config/config.example.json config/config.json
# Edit config/config.json with your settings

# 2. Set up AI credentials
echo "LLM_API_KEY=your_openai_api_key_here" >> .env

# 3. Run the scraper
cd scraper
python main.py --config ../config/config.json

# 4. Start the frontend
cd ..
npm start
```

## ⚙️ Configuration

### Backend Configuration (`config/config.json`)

```json
{
  "site_name": "My Content Site",
  "scraper_type": "rss",
  "feeds": [
    "https://example.com/rss.xml"
  ],
  "content_mapping": {
    "title": "title",
    "url": "link",
    "image": "enclosure",
    "excerpt": "description"
  },
  "ai_enhancement_enabled": true,
  "quality_threshold": 0.6
}
```

### Frontend Configuration (`public/config.json`)

```json
{
  "siteName": "My Content Site",
  "tagline": "Discover Amazing Content",
  "colors": {
    "primary": "#10B981",
    "primaryHover": "#059669"
  },
  "navigation": {
    "showHome": true,
    "showDeals": true,
    "showAbout": true
  },
  "content": {
    "dataFile": "/data.json",
    "showFeaturedSidebar": true,
    "searchPlaceholder": "Search content..."
  }
}
```

### Environment Variables (`.env`)

```bash
# Required: AI Configuration
LLM_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-4
LLM_PROVIDER=openai

# Optional: Performance Settings
MAX_CONCURRENT_REQUESTS=10
RATE_LIMIT_RPS=2
QUALITY_THRESHOLD=0.6

# Optional: Site Settings
SITE_NAME=My Content Site
AI_ENHANCEMENT_ENABLED=true
```

## 🎯 Usage

### Basic Content Scraping

```bash
# Scrape content with default settings
python scraper/main.py

# Use custom configuration
python scraper/main.py --config config/my-site.json

# Output to custom location
python scraper/main.py --output public/my-data.json

# Run without AI enhancement
python scraper/main.py --no-ai
```

### Advanced Usage

```bash
# Test mode (limited processing)
python scraper/main.py --test-mode

# Verbose logging
python scraper/main.py --verbose

# Custom environment file
python scraper/main.py --env-file .env.production
```

### Frontend Customization

1. **Update Site Branding**: Edit `public/config.json`
2. **Customize Colors**: Modify the `colors` section
3. **Configure Navigation**: Update `navigation` settings
4. **Change Data Source**: Set `content.dataFile` path

## 🤖 AI Agents

### Content Enhancer
Improves content quality and engagement:
- **Title Enhancement**: Makes titles more compelling
- **Description Generation**: Creates engaging descriptions
- **Missing Content**: Fills in missing fields intelligently

### Category Classifier  
Automatically categorizes content:
- **15+ Standard Categories**: Technology, Business, Health, etc.
- **Custom Categories**: Define your own classification system
- **Confidence Scoring**: Only accept high-confidence classifications

### Quality Validator
Ensures content meets quality standards:
- **Multi-Dimensional Scoring**: Completeness, relevance, engagement
- **Duplicate Detection**: Identifies and filters duplicate content
- **Quality Thresholds**: Configurable quality requirements

## 🔧 Development

### Project Structure

```
modern-template/
├── config/                 # Configuration files
│   ├── config.example.json # Backend configuration template
│   └── validator.py        # Configuration validation
├── scraper/               # Python backend
│   ├── agents/           # AI agents
│   ├── models/           # Pydantic data models
│   ├── modules/          # Scraper modules
│   └── main.py           # Main orchestration
├── src/                  # React frontend
│   ├── components/       # React components
│   ├── hooks/           # Custom hooks
│   └── types/           # TypeScript types
├── tests/               # Comprehensive test suite
└── public/              # Static assets and config
```

### Adding Custom Scrapers

1. **Create Scraper Module**:
```python
# scraper/modules/my_scraper.py
from .base import BaseScraperModule

class MyCustomScraper(BaseScraperModule):
    async def scrape_single_feed(self, url: str):
        # Implement your scraping logic
        pass
```

2. **Update Configuration**:
```json
{
  "scraper_type": "custom",
  "custom_scraper_config": {
    "module_path": "modules.my_scraper",
    "class_name": "MyCustomScraper"
  }
}
```

### Extending AI Agents

```python
# Add custom tools to existing agents
@content_enhancer_agent.tool
async def my_custom_tool(ctx: RunContext, content: str) -> str:
    # Custom AI processing logic
    return enhanced_content
```

## 🧪 Testing

### Run All Tests

```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Run all tests
python run_tests.py

# Run with coverage
python run_tests.py --coverage --html-coverage
```

### Test Categories

```bash
# Unit tests only
python run_tests.py --unit

# Integration tests only  
python run_tests.py --integration

# Skip slow tests
python run_tests.py --fast

# Skip AI-dependent tests
python run_tests.py --no-ai
```

### Writing Tests

```python
import pytest
from scraper.models.content import RawContent

class TestMyFeature:
    def test_basic_functionality(self):
        """Test basic feature functionality."""
        # Test implementation
        assert True
    
    @pytest.mark.asyncio
    async def test_async_functionality(self):
        """Test async feature functionality."""
        result = await my_async_function()
        assert result is not None
```

## 🚀 Deployment

### Production Deployment

1. **Backend Setup**:
```bash
# Install production dependencies
pip install -r scraper/requirements.txt

# Set production environment
export ENVIRONMENT=production
export LLM_API_KEY=your_production_api_key

# Run scraper (consider using cron for scheduling)
python scraper/main.py --config config/production.json
```

2. **Frontend Deployment**:
```bash
# Build for production
npm run build

# Deploy to static hosting (Vercel, Netlify, etc.)
# The build/ directory contains all static assets
```

### Docker Deployment

```bash
# Build and run with Docker
docker-compose up --build

# Or run individual services
docker run -d -p 3000:3000 modern-template-frontend
docker run -d modern-template-scraper
```

### Automation

Set up automated scraping:

```bash
# Add to crontab for hourly scraping
0 * * * * cd /path/to/modern-template && python scraper/main.py
```

## 📚 API Documentation

### Scraper API

#### `ContentPipeline`
Main orchestration class for content processing.

```python
from scraper.main import ContentPipeline
from scraper.models.config import SiteConfig

config = SiteConfig(**config_data)
pipeline = ContentPipeline(config)
summary = await pipeline.run_pipeline("output.json")
```

#### Configuration Models

```python
from scraper.models.config import SiteConfig, ScraperSettings

# Site configuration
config = SiteConfig(
    site_name="My Site",
    scraper_type="rss",
    feeds=["https://example.com/rss.xml"]
)

# Scraper settings
settings = ScraperSettings(
    max_concurrent_requests=10,
    rate_limit_delay=0.5
)
```

#### Content Models

```python
from scraper.models.content import RawContent, EnhancedContent

# Raw scraped content
raw = RawContent(
    title="Article Title",
    url="https://example.com/article",
    source_url="https://example.com/rss.xml"
)

# AI-enhanced content
enhanced = EnhancedContent(
    title="Enhanced Article Title",
    excerpt="AI-generated description...",
    quality_score=0.85,
    ai_generated_fields=["excerpt"]
)
```

## 🛠️ Troubleshooting

### Common Issues

#### Configuration Errors
```bash
# Validate configuration
python config/validator.py config/config.json

# Common fixes:
# - Check JSON syntax
# - Verify required fields
# - Validate URLs and file paths
```

#### AI Agent Errors
```bash
# Check API key
echo $LLM_API_KEY

# Test AI connectivity
python -c "from scraper.agents.content_enhancer import get_llm_model; print(get_llm_model())"

# Common fixes:
# - Verify API key is correct
# - Check rate limits
# - Ensure internet connectivity
```

#### Scraping Issues
```bash
# Test RSS feed accessibility
curl -I https://your-feed-url.com/rss.xml

# Check scraper logs
python scraper/main.py --verbose

# Common fixes:
# - Verify feed URLs are accessible
# - Check content mapping configuration
# - Review rate limiting settings
```

#### Frontend Issues
```bash
# Check configuration loading
curl http://localhost:3000/config.json

# Verify data file
curl http://localhost:3000/data.json

# Common fixes:
# - Ensure config.json is valid
# - Check data file path in config
# - Verify all required config fields
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python scraper/main.py --verbose

# Run tests in debug mode
python run_tests.py --verbose -s

# Check configuration
python -c "from config.validator import validate_config_file; print(validate_config_file('config/config.json'))"
```

### Performance Issues

```bash
# Reduce concurrent requests
export MAX_CONCURRENT_REQUESTS=5

# Increase rate limiting
export RATE_LIMIT_RPS=1

# Disable AI enhancement for testing
python scraper/main.py --no-ai
```

## 🤝 Contributing

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/modern-template.git
cd modern-template

# Set up development environment
python -m venv venv_linux
source venv_linux/bin/activate
pip install -r scraper/requirements.txt
pip install -r tests/requirements.txt

# Install pre-commit hooks
pre-commit install
```

### Code Standards

- **Python**: Follow PEP 8, use type hints, format with Black
- **TypeScript**: Use strict mode, proper interfaces, format with Prettier
- **Testing**: Maintain 80%+ coverage, write tests for new features
- **Documentation**: Update README and docstrings for changes

### Pull Request Process

1. Create feature branch from `main`
2. Write tests for new functionality
3. Ensure all tests pass: `python run_tests.py`
4. Update documentation as needed
5. Submit pull request with clear description

### Reporting Issues

Please include:
- **Configuration**: Your config files (sanitized)
- **Environment**: Python version, OS, Node.js version
- **Error Messages**: Full error output
- **Steps to Reproduce**: Minimal example

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Pydantic AI**: For the excellent AI agent framework
- **OpenAI**: For providing the underlying language models
- **React Community**: For the robust frontend framework
- **FastAPI & Pydantic**: For excellent Python API tools

## 📞 Support

- **Documentation**: [CONFIG_GUIDE.md](CONFIG_GUIDE.md)
- **Testing Guide**: [tests/README.md](tests/README.md)
- **Issues**: [GitHub Issues](https://github.com/yourorg/modern-template/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourorg/modern-template/discussions)

---

**Built with ❤️ using React, Python, and AI**
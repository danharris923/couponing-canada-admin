# Testing Framework

This directory contains comprehensive tests for the Modern Template Content Scraper system. The testing framework includes unit tests, integration tests, and utilities for testing all components of the system.

## Test Structure

```
tests/
├── README.md                    # This file
├── requirements.txt             # Testing dependencies
├── __init__.py                  # Test package initialization
├── fixtures/                    # Test data and fixtures
│   └── test_data.py            # Sample data for tests
├── config/                      # Configuration validation tests
│   └── test_validator.py       # Config validation tests
├── models/                      # Pydantic model tests
│   ├── test_content.py         # Content model tests
│   └── test_output.py          # Output model tests
├── modules/                     # Scraper module tests
│   └── test_rss_scraper.py     # RSS scraper tests
├── agents/                      # AI agent tests
│   └── test_content_enhancer.py # Content enhancer tests
└── integration/                 # Full pipeline tests
    └── test_full_pipeline.py   # End-to-end tests
```

## Test Categories

### Unit Tests
- **Configuration Tests**: Validate configuration loading and validation
- **Model Tests**: Test Pydantic models for data validation and serialization
- **Module Tests**: Test individual scraper modules (RSS, WordPress, Custom)
- **Agent Tests**: Test AI agents with mocked LLM responses

### Integration Tests
- **Pipeline Tests**: Test complete content processing pipeline
- **Error Handling**: Test system behavior under various failure conditions
- **Configuration Integration**: Test different scraper configurations

## Running Tests

### Quick Start

```bash
# Install testing dependencies
pip install -r tests/requirements.txt

# Run all tests
python run_tests.py

# Run with coverage
python run_tests.py --coverage
```

### Test Runner Options

The `run_tests.py` script provides various options:

```bash
# Run specific test categories
python run_tests.py --unit                # Unit tests only
python run_tests.py --integration         # Integration tests only

# Run specific tests
python run_tests.py --file test_validator # Specific test file
python run_tests.py --function test_config_validation # Specific function

# Skip slow or external tests
python run_tests.py --fast               # Skip slow tests
python run_tests.py --no-ai             # Skip AI-dependent tests
python run_tests.py --no-network        # Skip network tests

# Coverage and reporting
python run_tests.py --coverage          # Terminal coverage report
python run_tests.py --html-coverage     # HTML coverage report

# Utilities
python run_tests.py --install-deps      # Install dependencies
python run_tests.py --clean            # Clean test artifacts
python run_tests.py --verbose          # Verbose output
```

### Direct Pytest Usage

You can also run pytest directly:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=scraper --cov-report=html

# Run specific test file
pytest tests/config/test_validator.py

# Run tests matching pattern
pytest -k "test_config"

# Run with specific markers
pytest -m "unit and not slow"
```

## Test Markers

Tests are marked with the following categories:

- `unit`: Unit tests for individual components
- `integration`: Integration tests for full pipeline
- `slow`: Tests that may take longer to run
- `ai_required`: Tests requiring actual AI/LLM API access
- `network`: Tests requiring network access

## Mock Strategy

### Configuration Tests
- Mock file system operations
- Test various configuration scenarios
- Validate error handling

### Model Tests
- Test data validation
- Test serialization/deserialization
- Test edge cases and invalid data

### Module Tests
- Mock HTTP responses for RSS feeds
- Mock external API calls
- Test different content formats

### Agent Tests
- Mock LLM API responses
- Test structured output validation
- Test error handling and fallbacks

### Integration Tests
- Mock external dependencies
- Test complete data flow
- Test error propagation

## Test Data

Test fixtures are provided in `fixtures/test_data.py`:

- `SAMPLE_CONFIG`: Valid configuration examples
- `SAMPLE_RSS_FEED`: Mock RSS feed data
- `SAMPLE_RAW_CONTENT`: Example scraped content
- `SAMPLE_ENHANCED_CONTENT`: Example AI-enhanced content
- `SAMPLE_LLM_RESPONSES`: Mock AI agent responses
- `INVALID_CONFIGS`: Invalid configuration examples

## Writing New Tests

### Unit Test Example

```python
import pytest
from scraper.models.content import RawContent

class TestRawContent:
    def test_content_creation(self):
        """Test creating RawContent from valid data."""
        content = RawContent(
            title="Test Title",
            url="https://example.com/test",
            source_url="https://example.com/rss.xml",
            scraped_at=datetime.now()
        )
        
        assert content.title == "Test Title"
        assert content.url == "https://example.com/test"
    
    def test_content_validation(self):
        """Test content validation."""
        with pytest.raises(ValueError):
            RawContent(url="invalid-url")
```

### Async Test Example

```python
import pytest

class TestAsyncFunction:
    @pytest.mark.asyncio
    async def test_async_operation(self):
        """Test async function."""
        result = await some_async_function()
        assert result is not None
```

### Mock Test Example

```python
from unittest.mock import Mock, patch

class TestWithMocks:
    @patch('module.external_call')
    def test_with_mock(self, mock_external):
        """Test with mocked external dependency."""
        mock_external.return_value = "mocked_result" 
        
        result = function_that_calls_external()
        
        assert result == "expected_result"
        mock_external.assert_called_once()
```

## Coverage Goals

The test suite aims for:
- **Overall Coverage**: 80%+ line coverage
- **Unit Tests**: 90%+ coverage for core logic
- **Integration Tests**: Cover all major user workflows
- **Error Handling**: Test all exception paths

## Continuous Integration

For CI/CD pipelines, use:

```bash
# Fast test suite (no external dependencies)
python run_tests.py --fast --no-ai --no-network --coverage

# Full test suite (with external dependencies)
python run_tests.py --coverage
```

## Test Environment Variables

Tests use these environment variables:

- `TEST_MODE=true`: Enables test mode in application
- `LLM_API_KEY=test-key`: Mock API key for AI tests
- `PYTHONPATH=.`: Ensures imports work correctly

## Common Issues

### Import Errors
- Ensure `PYTHONPATH` includes project root
- Install all dependencies: `pip install -r tests/requirements.txt`

### Async Test Issues
- Use `@pytest.mark.asyncio` for async tests
- Install `pytest-asyncio`: `pip install pytest-asyncio`

### Mock Issues
- Patch the correct import path
- Use `return_value` for simple mocks, `side_effect` for complex behavior
- Remember to patch where the function is used, not where it's defined

### Coverage Issues
- Ensure all code paths are tested
- Use `--cov-report=html` to see detailed coverage
- Add `# pragma: no cover` for untestable code only

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure tests cover both success and failure cases
3. Add appropriate test markers
4. Update test documentation if needed
5. Ensure tests pass in CI environment

## Performance Testing

For performance testing of the scraper:

```bash
# Time test execution
time python run_tests.py --integration

# Profile test execution
python -m pytest --profile

# Memory usage testing
python -m pytest --memprof
```

## Debugging Tests

```bash
# Run with debugging output
python run_tests.py --verbose -s

# Drop into debugger on failure
pytest --pdb

# Debug specific test
pytest tests/config/test_validator.py::TestConfigValidator::test_valid_config -s -v
```
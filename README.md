# Web Scraper with LLM

Simple web scraper that uses LLM (Large Language Model) to extract structured data from web pages. Instead of traditional CSS selectors or XPath, it uses natural language instructions to identify and extract content.

## Features

- Uses DeepSeek LLM for intelligent content extraction
- Returns data in structured JSON format
- Configurable schema for desired data structure
- Saves results with timestamps

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment:
```bash
# Create .env file with
DEEPSEEK_API_KEY=your-api-key-here
```

3. Use the scraper:
```python
scraper = CourseScraper()
courses = await scraper.scrape_courses(url)
```

## Example

**main.py**

```python
# Define schema for desired data
schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "code": {"type": "string"},
            "name": {"type": "string"},
            "credits": {"type": "number"}
        }
    }
}

# Extract data using natural language instructions
extractor = LLMExtractionStrategy(
    instruction="Extract course code, name and credits",
    schema=schema
)
```

Results are saved automatically in the `results` directory.

## Requirements

All required packages are listed in `requirements.txt`. Use it to ensure you have all dependencies installed.
# Web Scraper with LLM

Simple web scraper that uses LLM (Large Language Model) to extract structured data from web pages. Instead of traditional CSS selectors or XPath, it uses natural language instructions to identify and extract content.

## Features

- Uses DeepSeek LLM for intelligent content extraction
- Returns data in structured JSON format
- Configurable schema for desired data structure
- Saves results with timestamps
- Supports web store product data extraction (web_store_scraper.py)

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
# For course data
scraper = CourseScraper()
courses = await scraper.scrape_courses(url)

# For web store products
scraper = SmartScraper()
products = await scraper.scrape_with_schema(
    url="your-product-url",
    instructions="Find product name, price, and features",
    schema=product_schema
)
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

**web_store_scraper.py**

```python
# Example product schema
product_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "price": {"type": "string"},
        "features": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}

# Initialize and use the scraper
scraper = SmartScraper()
results = await scraper.scrape_with_schema(
    url="your-product-url",
    instructions="Find the product name, price, and list of features",
    schema=product_schema
)
```

main.py results are saved automatically in the `results` directory.

## Requirements

All required packages are listed in `requirements.txt`. Use it to ensure you have all dependencies installed.

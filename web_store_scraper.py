import asyncio
import json
import os
from typing import Any, Dict

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class SmartScraper:
    def __init__(self, api_token: str = None):
        print("Initializing SmartScraper...")
        """
        Initialize scraper with DeepSeek API.
        Args:
            api_token: DeepSeek API token. If None, retrieves DEEPSEEK_API_KEY from .env file.
        """
        self.api_token = api_token or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_token:
            raise ValueError(
                "DeepSeek API token is required. Add it to .env file or pass directly.")
        # 3. Configure browser settings
        self.browser_config = BrowserConfig(
            headless=True,
            java_script_enabled=True
        )

    async def scrape_with_schema(
        self,
        url: str,
        instructions: str,
        schema: Dict[str, Any]
    ) -> Dict:
        """
        Scrapes the page and returns data in JSON format.
        """
        # LLM extraction strategy with DeepSeek
        extraction_strategy = LLMExtractionStrategy(
            provider="deepseek/deepseek-chat",     # Use chat model
            api_token=self.api_token,              # API token for DeepSeek
            extraction_type="schema",              # Want schema-formatted output
            schema=schema,                         # JSON schema
            instruction=instructions,              # Instructions for extraction
            chunk_token_threshold=2000,            # Smaller chunks
            overlap_rate=0.1,                      # 10% overlap between chunks
            verbose=True                           # Show debug info
        )

        crawler_config = CrawlerRunConfig(
            extraction_strategy=extraction_strategy,
            word_count_threshold=1,
            remove_overlay_elements=True
        )

        try:
            async with AsyncWebCrawler(config=self.browser_config) as crawler:
                print("Scraping URL:", url)
                result = await crawler.arun(url=url, config=crawler_config)

                if not result.success:
                    return {"error": result.error_message}

                return json.loads(result.extracted_content)

        except Exception as e:
            return {"error": str(e)}


async def main():
    # Example schema for product information
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

    scraper = SmartScraper()  # Automatically fetches from .env file

    results = await scraper.scrape_with_schema(
        url="https://www.adidas.com/us/handball-spezial-shoes/JS0241.html?pr=taxonomy_rr&slot=2&rec=mt",
        instructions="Find the product name, price, and list of features",
        schema=product_schema
    )

    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
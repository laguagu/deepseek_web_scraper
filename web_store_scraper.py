import asyncio
import json
import os
from typing import Any, Dict

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from dotenv import load_dotenv

# Ladataan .env tiedosto
load_dotenv()


class SmartScraper:
    def __init__(self, api_token: str = None):
        print("Initializing SmartScraper...")
        """
        Initialisoi scraper DeepSeek API:lla.
        Args:
            api_token: DeepSeek API token. Jos None, hakee DEEPSEEK_API_KEY .env tiedostosta.
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
        Scrapee sivun ja palauttaa datan JSON muodossa.
        """
        # LLM extraction strategy DeepSeekillä
        extraction_strategy = LLMExtractionStrategy(
            provider="deepseek/deepseek-chat",     # Käytetään chat-mallia
            api_token=self.api_token,              # API token DeepSeekille
            extraction_type="schema",              # Halutaan schema-muotoinen output
            schema=schema,                         # JSON schema
            instruction=instructions,              # Ohjeet extractioon
            chunk_token_threshold=2000,            # Pienemmät chunkit
            overlap_rate=0.1,                      # 10% overlap chunkkien välillä
            verbose=True                           # Näytetään debug infoa
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
    # Esimerkki schema tuotetiedoille
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

    scraper = SmartScraper()  # Hakee automaattisesti .env tiedostosta

    results = await scraper.scrape_with_schema(
        url="https://www.adidas.com/us/handball-spezial-shoes/JS0241.html?pr=taxonomy_rr&slot=2&rec=mt",
        instructions="Etsi tuotteen nimi, hinta ja ominaisuudet listana",
        schema=product_schema
    )

    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path

from crawl4ai import (AsyncWebCrawler, BrowserConfig, CacheMode,
                      CrawlerRunConfig)
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from dotenv import load_dotenv

load_dotenv()

class CourseScraper:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in .env file")

        self.browser = BrowserConfig(
            headless=True,
            java_script_enabled=True
        )
        
        # Conver JSON schema for course data
        self.schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "name": {"type": "string"},
                    "credits": {"type": "number"},
                    "category": {"type": "string"},
                    "mandatory": {"type": "boolean"},
                    "description": {"type": "string"}
                },
                "required": ["code", "name", "credits"]
            }
        }

    def save_json(self, data, url: str):
        """Saves the extracted data to a JSON file"""
        Path("results").mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"course_catalog_{timestamp}.json"

        # Extract courses from data in list format
        courses = data if isinstance(data, list) else data.get("courses", [])
        
        data_to_save = {
            "metadata": {
                "url": url,
                "timestamp": timestamp,
                "course_count": len(courses)
            },
            "results": {
                "courses": courses
            }
        }

        path = Path("results") / filename
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)
        print(f"Saved to: {path}")
        return courses

    async def scrape_courses(self, url: str):
        """Scraping courses from the given URL"""
        print(f"Scraping courses from: {url}")
        
        extractor = LLMExtractionStrategy(
            provider="deepseek/deepseek-chat",
            api_token=self.api_key,
            schema=self.schema,
            extraction_type="schema",
            verbose=True,
            instruction="""
            Extract a list of courses from the page. For each course include:
               - Course code (e.g., COM001HH1A)
               - Course name
               - Credits (number)
               - Category/group name
               - Mandatory status (true if mandatory/"valitaan kaikki", false if optional)
               - Description (if available)
            
            Return the data as a JSON array where each item represents a course.
            
            Notes:
            - Keep original language (Finnish/English) as found
            - Convert credit strings to numbers (e.g., "5 op" → 5)
            - Mark courses as mandatory (true) if they are required
            """,
            chunk_token_threshold=2000,
            overlap_rate=0.1,
            extra_args={
                "temperature": 0.1,
                "max_tokens": 4000 # Remove this if answers are missing content
            }
        )

        config = CrawlerRunConfig(
            extraction_strategy=extractor,
            remove_overlay_elements=True,
            cache_mode=CacheMode.BYPASS,
            page_timeout=30000
        )

        try:
            async with AsyncWebCrawler(config=self.browser) as crawler:
                result = await crawler.arun(url=url, config=config)

                if not result.success:
                    print(f"Error: {result.error_message}")
                    return {"error": result.error_message}

                # parse JSON
                data = json.loads(result.extracted_content)
                
                # Save courses
                courses = self.save_json(data, url)
                
                print(f"Successfully scraped {len(courses)} courses")
                return courses

        except Exception as e:
            print(f"Error during scraping: {str(e)}")
            return {"error": str(e)}

async def main():
    url = "https://opinto-opas.haaga-helia.fi/fi/131320/fi/131354/TRATI22/year/2024"

    scraper = CourseScraper()
    
    try:
        courses = await scraper.scrape_courses(url)
        if isinstance(courses, list):  # Check if there are courses
            print(f"\nTotal courses: {len(courses)}")
            print("\nExample courses:")
            for course in courses[:3]:
                print(
                    f"- {course['name']} ({course['code']}) {course['credits']} ECTS"
                    f" {'[Mandatory]' if course.get('mandatory') else ''}"
                )
        elif isinstance(courses, dict) and "error" in courses:
            print("Error:", courses["error"])
        else:
            print("Unexpected response format")
            
    except Exception as e:
        print(f"Failed to process URL: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
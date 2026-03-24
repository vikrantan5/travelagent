from firecrawl import FirecrawlApp
import os
from agno.tools import tool
from loguru import logger
from config.logger import logger_hook

# Make Firecrawl optional
FIRECRAWL_KEY = os.getenv("FIRECRAWL_API_KEY")

if FIRECRAWL_KEY:
    try:
        app = FirecrawlApp(api_key=FIRECRAWL_KEY)
        logger.info("Firecrawl initialized successfully.")
    except Exception as e:
        logger.warning(f"Firecrawl initialization failed: {e}")
        app = None
else:
    logger.warning("FIRECRAWL_API_KEY not provided. Firecrawl disabled.")
    app = None


@tool(
    name="scrape_website",
    description="Scrape a website and return the markdown content.",
    tool_hooks=[logger_hook],
)
def scrape_website(url: str) -> str:
    """Scrape a website and return markdown content."""
    
    if app is None:
        return (
            f"# Website Content\n"
            f"Unable to scrape {url} - Firecrawl not configured."
        )

    try:
        status = app.scrape_url(
            url,
            formats=["markdown"],
            wait_for=30000,
            timeout=60000,
        )
        return status.markdown
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return f"# Website Content\nError scraping {url}: {str(e)}"
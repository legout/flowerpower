# Key Considerations / Safety Protocols
*   **API Key Security:** Emphasize secure handling of the `FIRECRAWL_API_KEY`.
*   **Extraction Modes:** Understand the difference between `markdown` (default) and `llm-extraction` (requires schema).
*   **Crawl vs. Scrape:** Use `/scrape` for single URLs, `/crawl` for discovering and scraping multiple URLs from a starting point.
*   **Job Status:** Crawl jobs are asynchronous. Status needs to be checked separately or via webhook.
*   **Cost:** Be mindful that Firecrawl is a paid service; configure crawls efficiently.
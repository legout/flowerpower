# 6. Context / Knowledge Base & Key Concepts

## Context Pointers (Refer to `../context/` directory)
*   **Crawl4AI Documentation:** Consult `crawl4ai-docs.md` (if available) for package documentation.
*   **Python `asyncio` basics:** Consult `asyncio-concepts.md` (if available) for async programming concepts.
*   **Web Crawling Best Practices:** Consult `crawling-best-practices.md` (if available) for ethical and efficient crawling guidelines.
*   **Browser Automation Concepts:** Consult `browser-automation.md` (if available) for headless browser concepts.
*   **HTML/CSS Selectors:** Consult `html-css-selectors.md` (if available) for content extraction patterns.

## Key Concepts Reminder:
*   **`crawl4ai`:** Python library for asynchronous web crawling.
*   **`AsyncWebCrawler`:** Main class. Takes URLs and `CrawlerOptions`. `run()` method starts crawl.
*   **`CrawlerOptions`:** Configures strategy (`bfs`/`dfs`), depth, limit, concurrency, delay, user-agent, proxy, SSL verification.
*   **`Filters`:** Defines `url_filters` (regex patterns), `content_filters`, `url_boundary`. Can be chained.
*   **`BrowserOptions`:** Configures headless mode, browser type (`chromium`, `firefox`, `webkit`), page options (viewport, headers, storage state).
*   **`Extractor`:** (Implicit) Handles content extraction (often default behavior extracts main content).
*   **Result:** `crawler.run()` returns list of `CrawledData` objects containing URL, content, metadata.
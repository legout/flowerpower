# 4. Key Considerations / Safety Protocols

*   **Rate Limiting & Delays:** Configure appropriate delays (`CrawlerOptions(delay=...)`) to avoid overloading target servers.
*   **User-Agent:** Set a descriptive user-agent string (`CrawlerOptions(user_agent=...)`).
*   **Robots.txt:** Be aware of `robots.txt` rules (though `crawl4ai` might handle basic checks, confirm behavior if critical).
*   **Resource Management:** Configure browser options and concurrency (`CrawlerOptions(concurrency=...)`) appropriately to manage local resources.
*   **Error Handling:** Implement `try...except` blocks around `crawler.run()` and during result processing.
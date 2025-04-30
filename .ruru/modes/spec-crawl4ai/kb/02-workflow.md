# 2. Workflow / Operational Steps

1.  **Receive Task & Initialize Plan:** Get assignment (Task ID `[TaskID]`), requirements (target URLs/domains, depth, filters, extraction needs, output format/location) from requesting mode. **Guidance:** Log goal internally (no project journal logging for assistants).
2.  **Analyze & Plan:** Review requirements. Plan `crawl4ai` configuration:
    *   Crawler: `AsyncWebCrawler(urls=..., crawler_options=...)`
    *   Strategy: `CrawlerOptions(strategy='bfs'/'dfs', depth=..., limit=...)`
    *   Filtering: `Filters(url_filters=[...], content_filters=[...], url_boundary=...)`
    *   Browser: `BrowserOptions(headless=True, browser_type='chromium', ...)`, potentially `page_options` for viewport, etc.
    *   Extraction: Plan how to process results from `crawler.run()`.
    *   Use `ask_followup_question` to clarify requirements with the requester if needed.
3.  **Implement Script:** Write Python script (`.py`) using `crawl4ai`. Configure `AsyncWebCrawler` with planned options. Implement logic to process/save results. Use `write_to_file`.
4.  **Consult Resources:** Use `browser` or context base (see `06-context-and-concepts.md`) to consult `crawl4ai` documentation if needed.
5.  **Prepare Execution:** Formulate the `execute_command` to run the script (e.g., `python path/to/your_crawler.py`).
6.  **Report Plan & Await Execution:** Use `attempt_completion` to:
    *   Present the generated Python script content.
    *   Present the planned `execute_command`.
    *   Request approval to execute the command.
    *   *(Wait for user/coordinator to execute the command and provide results)*
7.  **Report Results:** Once results are provided by the user/coordinator, use `attempt_completion` again to:
    *   Summarize the outcome (success/failure, number of pages crawled, errors encountered).
    *   Provide path to output files if applicable.
    *   Report any issues encountered or potential escalations needed.
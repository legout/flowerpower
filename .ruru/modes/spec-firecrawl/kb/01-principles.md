# General Operational Principles
*   **API Focus:** Primarily interact with the Firecrawl API (v0) using `execute_command` with `curl` or potentially official client libraries if available and installed.
*   **Configuration:** Accurately configure crawl/scrape parameters based on user requirements (URL, crawler options, page options, extractor options).
*   **Security:** Ensure the Firecrawl API key (`FIRECRAWL_API_KEY`) is handled securely (passed via environment or secure mechanism, **never hardcoded**).
*   **Tool Usage:** Use tools iteratively. Analyze requirements. Use `write_to_file` only if generating complex request payloads or processing scripts. Use `execute_command` for `curl` API calls. Use `ask_followup_question` for missing critical info (URL, API key source, extraction schema). Ensure access to all tool groups.
*   **Respect Service Limits:** Be aware of potential Firecrawl API rate limits or usage quotas (inform user if relevant).
# Workflow / Operational Steps
1.  **Receive Task & Initialize Plan:** Get assignment (Task ID `[TaskID]`), requirements (URL(s), crawl/scrape mode, extraction needs, API key source) from requesting mode. **Guidance:** Log goal internally.
2.  **Analyze & Plan API Call:** Determine endpoint (`/crawl` or `/scrape`). Plan JSON payload parameters (`url`, `crawlerOptions`, `pageOptions`, `extractorOptions`). Use `ask_followup_question` to clarify requirements with requester.
3.  **Construct Payload & Command:** Create JSON payload. Formulate `execute_command` using `curl`:
    *   Scrape: `curl -X POST https://api.firecrawl.dev/v0/scrape -H "Authorization: Bearer $FIRECRAWL_API_KEY" -H "Content-Type: application/json" -d '{"url": "...", "pageOptions": {...}, "extractorOptions": {...}}'`
    *   Crawl: `curl -X POST https://api.firecrawl.dev/v0/crawl -H "Authorization: Bearer $FIRECRAWL_API_KEY" -H "Content-Type: application/json" -d '{"url": "...", "crawlerOptions": {...}, "pageOptions": {...}}'` (Note: Crawl returns a job ID).
    *   **(Ensure `$FIRECRAWL_API_KEY` is set in the execution environment)**
4.  **Report Plan & Await Execution:** Use `attempt_completion` to present the planned `curl` command and JSON payload. Request approval to execute. *(Wait for user/coordinator to execute and provide results)*.
5.  **Process Results & Report:**
    *   Receive API response (JSON) from user/coordinator.
    *   **Scrape:** Extract `data` (Markdown or structured JSON) from the response.
    *   **Crawl:** Extract `jobId` from the response. Inform requester about the job ID and that they need to check status or webhook. (Optionally, if instructed, prepare subsequent API calls to check job status: `GET /crawl/{jobId}`).
    *   Use `attempt_completion` to report the outcome (success/failure, extracted data snippet or job ID, errors). Escalate API errors or limitations.
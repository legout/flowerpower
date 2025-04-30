# 1. General Operational Principles

*   **Crawl Ethically:** Be mindful of `robots.txt`, rate limits, and website terms of service. Implement appropriate delays and user-agent strings.
*   **Efficiency:** Design crawlers to be efficient with resources (network, CPU, memory). Use filtering effectively to avoid unnecessary requests.
*   **Robustness:** Implement proper error handling for network issues, timeouts, and unexpected page structures.
*   **Tool Usage:** Use tools iteratively. Analyze requirements carefully. Use `write_to_file` for scripts. Use `execute_command` to run scripts. Use `ask_followup_question` for missing critical info (target sites, specific filters). Ensure access to all tool groups specified in the mode definition.
*   **Focus:** Concentrate on implementing the crawling logic using `crawl4ai`. Escalate tasks related to complex data processing, infrastructure, or advanced anti-bot circumvention.
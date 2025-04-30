# 5. Error Handling

*   Handle common crawling errors (network timeouts, HTTP errors, parsing errors) within the script if possible.
*   Log errors effectively during the crawl.
*   Report significant errors or inability to complete the crawl back to the requester.
*   Report tool errors or persistent blockers via `attempt_completion`.
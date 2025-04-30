+++
id = "DEV-GOLANG-KB-LOOKUP-V1"
title = "Golang Developer: Rule - KB Lookup Trigger"
context_type = "rules"
scope = "Mode-specific knowledge base access conditions"
target_audience = ["dev-golang"]
granularity = "ruleset"
status = "active"
last_updated = "2025-04-26" # Based on current date
# version = "1.0"
related_context = [".ruru/modes/dev-golang/kb/"]
tags = ["rules", "kb-lookup", "golang", "dev-golang"]
# relevance = ""
template_schema_doc = ".ruru/templates/toml-md/16_ai_rule.README.md"
+++

# Rule: Knowledge Base Lookup Trigger

**Objective:** To ensure the mode leverages its dedicated Knowledge Base (KB) effectively before resorting to general knowledge or external searches.

**Rule:**

1.  **Prioritize KB:** Before attempting to answer a query, generate code, or make a decision based on general knowledge, **MUST** first check if relevant information exists within the mode-specific Knowledge Base located at:
    *   `.ruru/modes/dev-golang/kb/`
2.  **Lookup Condition:** Perform a KB lookup if the user's request or the current task involves:
    *   Specific Golang libraries, frameworks, or tools mentioned in the KB.
    *   Established patterns, best practices, or architectural decisions documented in the KB.
    *   Configuration details or project standards relevant to Golang development within this project.
    *   Troubleshooting common Golang-related issues documented in the KB.
3.  **Effective KB Usage (Golang Specific):**
    *   **Concurrency:** Prioritize KB files in `concurrency/` when dealing with goroutines, channels, mutexes, or race conditions.
    *   **Best Practices & Style:** Consult `best-practices/` for idiomatic Go code style, effective error handling patterns (explicit error checks), and project structure conventions.
    *   **Testing:** Refer to `testing/` for guidance on unit testing (`testing` package), table-driven tests, benchmarking (`go test -bench`), and mocking strategies.
    *   **Standard Library:** Check for specific guidance on using standard library packages like `net/http`, `encoding/json`, `io`, `os`, etc., if available in the KB.
    *   **Tooling:** Look for information on `go mod` (dependency management), `go build`, `go test`, `pprof` (profiling), etc., in relevant KB sections.
4.  **Synthesize Information:** If relevant KB documents are found, synthesize the information from them to formulate the response or guide the action. Clearly indicate when information is derived from the KB.
5.  **Proceed if No KB Match:** If a thorough check reveals no relevant information in the KB, proceed using general knowledge or other approved methods (like external search tools, if permitted by other rules).

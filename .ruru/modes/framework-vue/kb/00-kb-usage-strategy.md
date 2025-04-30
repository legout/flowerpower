+++
id = "KB-USAGE-STRATEGY-FRAMEWORK-VUE-V1"
title = "Knowledge Base Usage Strategy (framework-vue)"
context_type = "documentation"
scope = "internal_kb_usage"
status = "active"
last_updated = "2025-04-27" # Use current date
tags = ["kb", "strategy", "documentation", "framework-vue"]
related_context = [".ruru/modes/framework-vue/kb/README.md"]
template_schema_doc = ".ruru/templates/toml-md/18_kb_usage_strategy.README.md" # Assuming this template exists
relevance = "Defines how the framework-vue mode should prioritize and utilize its KB."
+++

# Knowledge Base Usage Strategy for `framework-vue`

## 1. Prioritization

1.  **Specific Rules (`.roo/rules-framework-vue/`):** Always prioritize specific rules defined for this mode.
2.  **Context7 KB (`kb/context7/`):** Use as the primary source for detailed Vue.js concepts, API details, and code examples derived from the official documentation. Start searches within the relevant subdirectories identified in `kb/context7/_index.json` or the summary rule (`.roo/rules-framework-vue/05-context7-summary.md`).
3.  **Local KB (`kb/local_docs/`, if exists):** Consult for project-specific overrides, conventions, or supplementary information not covered by Context7.
4.  **General Rules (`.roo/rules/`):** Apply general workspace rules when mode-specific or KB information is not available.
5.  **Mode's Core Knowledge:** Use internal knowledge as a last resort or for synthesis.

## 2. Querying Strategy

*   When needing specific Vue.js information, formulate queries targeting the `kb/context7/` directory structure (e.g., "Find information on computed properties in `kb/context7/guide/essentials/`").
*   Use the `kb/context7/source_info.json` to understand the origin and approximate recency of the Context7 data.
*   If project-specific details are needed, query `kb/local_docs/`.

## 3. Maintenance

*   The Context7 KB is updated via the `WF-CONTEXT7-REFRESH-001.md` workflow.
*   Local KB requires manual updates or specific enrichment workflows.

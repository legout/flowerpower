+++
id = "util-writer-kb-lookup"
title = "KB Lookup Rule for util-writer"
context_type = "rules"
scope = "Mode-specific knowledge base access"
target_audience = ["util-writer"]
granularity = "rule"
status = "active"
last_updated = "2025-04-19"
# version = "1.0"
# related_context = []
tags = ["kb", "knowledge-base", "lookup", "util-writer"]
# relevance = "High"
target_mode_slug = "util-writer"
kb_directory = ".ruru/modes/util-writer/kb/"
+++

# Knowledge Base Lookup Rule

**Objective:** Ensure consistent and informed responses by leveraging dedicated knowledge resources.

**Rule:** Before responding to any user request or performing a task, **ALWAYS** consult the contents of your dedicated Knowledge Base (KB) directory located at: `.ruru/modes/util-writer/kb/`.

**Procedure:**

1.  **Identify Need:** Recognize when the user's request or the task at hand might benefit from specific guidelines, examples, preferred methods, or contextual information related to your function as `util-writer`.
2.  **Access KB:** Systematically review the files within the `.ruru/modes/util-writer/kb/` directory. Pay attention to filenames and READMEs to quickly locate relevant documents.
3.  **Prioritize KB:** Information, instructions, or constraints found within your KB **supersede** your general knowledge or previously learned patterns. Adhere to the guidance provided in the KB.
4.  **Apply Knowledge:** Integrate the information retrieved from the KB into your reasoning process and response generation. If the KB specifies a particular format, tool, or approach, use it.
5.  **Acknowledge Gaps (If Any):** If the KB does not contain relevant information for the specific request, proceed using your general knowledge and best judgment, but be mindful that the KB is the primary source of truth for your operational guidelines.

**Rationale:** Your KB contains curated information tailored to your specific role and responsibilities within this project. Consulting it ensures you operate according to established standards, best practices, and project-specific requirements, even if the directory is currently sparse or empty. Consistent KB checks are crucial for maintaining alignment as the project evolves.
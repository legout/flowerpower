+++
id = "KB-LOOKUP-DESIGN-THREEJS"
title = "KB Lookup Rule: design-threejs"
context_type = "rules"
scope = "Mode-specific knowledge base access"
target_audience = ["design-threejs"]
granularity = "rule"
status = "active"
last_updated = "2025-04-19" # Using today's date
# version = ""
# related_context = []
tags = ["kb-lookup", "design-threejs", "knowledge-base", "design", "3d", "threejs", "webgl", "graphics", "frontend", "visualization"]
# relevance = ""
target_mode_slug = "design-threejs"
kb_directory = ".ruru/modes/design-threejs/kb"
+++

# Knowledge Base (KB) Lookup Rule

**Applies To:** `design-threejs` mode

**Rule:**

Before attempting a task, **ALWAYS** consult the dedicated Knowledge Base (KB) directory for this mode located at:

`{{kb_directory}}`

**Procedure:**

1.  **Identify Keywords:** Determine the key concepts, tools, or procedures relevant to the current task (e.g., Three.js concepts, WebGL, 3D modeling, rendering, animation, shaders, scene setup, performance optimization).
2.  **Scan KB:** Review the filenames and content within the `{{kb_directory}}` for relevant documents (e.g., principles, workflows, examples, code snippets, best practices, common issues, performance tips). Pay special attention to `README.md` if it exists.
3.  **Apply Knowledge:** Integrate relevant information from the KB into your task execution plan and response. Reference specific KB documents if applicable.
4.  **If KB is Empty/Insufficient:** If the KB doesn't contain relevant information, proceed using your core capabilities and general knowledge about Three.js and 3D graphics, but note the potential knowledge gap.

**Rationale:** This ensures the `design-threejs` mode leverages specialized, curated knowledge for consistent and effective operation, promoting maintainability and allowing for future knowledge expansion specific to Three.js development.
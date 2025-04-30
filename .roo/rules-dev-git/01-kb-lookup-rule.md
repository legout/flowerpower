# Rule: Consult Knowledge Base

Before proceeding with the task, review the KB README (`.ruru/modes/dev-git/kb/README.md`) which summarizes available documents and their size (line count).
Assess the relevance of each listed document to the current task based on its summary.
Estimate the potential benefit vs. the context cost (line count) of reading relevant documents.
**Limit:** If the total estimated lines to read for *multiple* relevant files exceeds ~1000 lines (adjust threshold as needed), consider if all are truly necessary. If unsure, use `ask_followup_question` to confirm with the user which specific files to read or suggest refining the task.
If you are confident a document is highly relevant and the cost is acceptable (or confirmed by user), read it using `read_file`.
Incorporate information from read documents into your response or actions.
If no relevant documents are found or deemed worth the cost, proceed using your general knowledge.
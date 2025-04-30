# Collaboration & Escalation

## Collaboration

*   **Primary Interaction:** You primarily receive requests from `roo-commander` or other specialist modes needing contextual information.
*   **Reporting:** You report synthesized summaries back to the requesting mode using `attempt_completion`.

## Escalation

*   **Ambiguous Queries:** If a received query is unclear, lacks sufficient detail to identify sources, or is too broad to provide a concise summary, use the `ask_followup_question` tool to request clarification from the calling mode. Provide specific suggestions for how the query could be improved (e.g., "Please specify the Task ID", "Which decision topic are you interested in?").
*   **Missing Critical Sources:** If source documents explicitly requested or deemed critical for answering the query (based on `03-source-prioritization.md`) cannot be read (e.g., file not found, access error), clearly state this limitation in your final summary using the `*(Note: ...)*` format. Do not attempt to guess the missing information.
*   **Systemic Issues:** If you consistently encounter issues accessing core project directories (`.tasks`, `.decisions`, etc.), escalate this observation to `roo-commander` as it might indicate a broader problem.
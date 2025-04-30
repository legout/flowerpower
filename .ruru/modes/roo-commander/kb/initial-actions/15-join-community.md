+++
# --- Basic Metadata ---
id = "KB-ROO-CMD-INIT-15-COMMUNITY"
title = "KB: Initial Action - Join the Roo Commander Community"
status = "active"
created_date = "2025-04-22"
updated_date = "2025-04-22"
version = "1.0"
tags = ["kb", "roo-commander", "workflow", "initialization", "community", "discord", "help", "support", "contribution"]

# --- Ownership & Context ---
owner = "Roo Commander"
related_docs = [
    ".roo/rules-roo-commander/02-initialization-workflow-rule.md",
    "README.md" # Project README might have links/info
]
related_templates = []

# --- Workflow Specific Fields ---
objective = "Provide the user with information about the Roo Commander community (Discord), its purpose, and a link to join."
scope = "This procedure is executed by Roo Commander immediately after the user selects the 'Join the Roo Commander Community (Discord)' option."
roles = ["Coordinator (Roo Commander)", "User"]
trigger = "User selection of '🐾 Join the Roo Commander Community (Discord)'."
success_criteria = [
    "Coordinator successfully presents information about the community and the Discord link.",
    "User receives the information and link."
]
failure_criteria = [
    "Coordinator fails to present the information (e.g., missing link in configuration/prompt)."
]

# --- Integration ---
acqa_applicable = false # Information delivery
pal_validated = false # Needs validation
validation_notes = "Simple procedure, needs testing with actual link."

# --- AI Interaction Hints (Optional) ---
context_type = "workflow_step_details"
target_audience = ["roo-commander"]
granularity = "informational"
+++

# KB: Initial Action - Join the Roo Commander Community

## 1. Objective 🎯
*   To inform the user about the Roo Commander community, its purpose (support, discussion, contribution), and provide a direct link to the Discord server.

## 2. Roles & Responsibilities 👤
*   **Coordinator (Roo Commander):** Presents the community information and Discord link.
*   **User:** Receives the information and link.

## 3. Procedure Steps 🪜

*   **Step 1: Present Community Information & Link (Coordinator Task)**
    *   **Description:** Provide a pre-defined message about the community and the Discord invitation link.
    *   **Inputs:** User selected "🐾 Join the Roo Commander Community...".
    *   **Tool:** `attempt_completion` (followed by `ask_followup_question` to prompt next action).
    *   **Procedure:**
        1.  Formulate the response message. **Note:** The Discord link MUST be kept up-to-date here or loaded from a configuration.
            ```markdown
            That's great! Connecting with the community is a fantastic way to get help, share ideas, see examples, and contribute to the evolution of Roo Commander.

            **Why Join?**
            *   Get support and ask questions.
            *   Discuss workflows and share custom modes/rules.
            *   See how others are using Roo Commander.
            *   Stay updated on the latest developments and features.
            *   Contribute feedback and ideas.

            **Discord Server:**
            You can join the official Roo Commander Discord server here:
            [https://discord.gg/ESaJBnw7As](https://discord.gg/ESaJBnw7As)

            We look forward to seeing you there!

            What would you like to do now in this workspace? *(Present the initial 16 options again via `ask_followup_question` or await next user prompt)*
            ```
        2.  Send the information using `attempt_completion`.
        3.  *(Self-Correction/Refinement):* Immediately follow up with `ask_followup_question` presenting the standard 16 initial options to guide the user's next action within the workspace.
    *   **Outputs:** Community information and link presented to the user. User prompted for next action.
    *   **Error Handling:** If the Discord link is missing or known to be invalid, report "Sorry, I don't have the current community link available right now."

## 4. Postconditions ✅
*   The user has been informed about the community and provided with the Discord link.
*   The user has been prompted for their next action within the workspace.
*   The Coordinator's responsibility for *this specific initial action* is complete.

## 5. Rationale / Notes 🤔
*   Provides a direct and helpful way for users to connect with the wider community.
*   Keeps the community information consistent by defining it within this KB procedure.
*   Ensures the user is prompted for their next *workspace* action after receiving the community information.
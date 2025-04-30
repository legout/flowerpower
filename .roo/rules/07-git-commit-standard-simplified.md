+++
id = "RULE-GIT-COMMIT-STD-SIMPLE-V1"
title = "Standard: Git Commit Message Format"
context_type = "rules"
scope = "Formatting standard for all Git commit messages"
target_audience = ["all"] # Especially modes initiating commits
granularity = "standard"
status = "active"
last_updated = "2025-04-22"
tags = ["rules", "git", "commit", "standard", "conventional-commits", "traceability", "mdtm"]
related_context = [".roo/rules/04-mdtm-workflow-initiation.md"] # Link to MDTM rule
template_schema_doc = ".ruru/templates/toml-md/16_ai_rule.README.md"
relevance = "High: Enforces commit consistency and traceability"
+++

# Standard: Git Commit Message Format

**Objective:** Ensure Git commits are informative, consistent, and traceable.

**Rule:**

1.  **Format:** All commit messages MUST use the [Conventional Commits](https://www.conventionalcommits.org/) format (`type(scope): subject`).
2.  **Footer:** A footer section **MUST** be present.
    *   If the commit relates to specific MDTM task(s) (identified by IDs like `TASK-...`), use `Refs: [TaskID]`. Multiple `Refs:` lines are allowed.
    *   If no specific MDTM task applies (confirm if unsure), use `Refs: General`.
3.  **Delegation:** When delegating a commit to `dev-git`, provide the *complete, fully formatted message string*, including type, subject, optional body, and the mandatory footer. `dev-git` MUST use the exact string provided.
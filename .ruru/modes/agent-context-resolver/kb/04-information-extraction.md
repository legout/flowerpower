# Information Extraction Guidelines

These guidelines help in efficiently extracting key information from common project artifact types found in the standard hidden directories (`.tasks`, `.decisions`, `.planning`, etc.).

## MDTM Task Files (`.ruru/tasks/**/*.md`)

*   **Primary Goal:** Look for the `title` field in the TOML frontmatter. Also check for `## Goal` or `## Description` sections.
*   **Current Status:** Check the `status` field in the TOML frontmatter (e.g., `status = "🟡 To Do"`).
*   **Assignee:** Check the `assigned_to` field in the TOML frontmatter.
*   **Blockers:** Scan for `## Blockers`, `## Issues`, or keywords like "blocked", "waiting for". Check if `status` is `"⚪ Blocked"`.
*   **Recent Activity:** Look for dated entries or `## Log` sections. Check `updated_date` in TOML.
*   **Next Steps:** Scan for `## Next Steps` or concluding remarks.
*   **Related Items:** Check `depends_on` and `related_docs` arrays in TOML.

## Architecture Decision Records (ADRs) (`.ruru/decisions/*.md`)

*   **Decision:** Look for `## Decision` or `## Resolution`.
*   **Date:** Check filename or metadata (e.g., `Date:` field).
*   **Status:** Look for a `Status:` field (e.g., `Proposed`, `Accepted`, `Superseded`).
*   **Context/Problem:** Read `## Context` or `## Problem Statement`.
*   **Options:** Look for `## Options Considered`.
*   **Justification/Consequences:** Read `## Rationale`, `## Justification`, `## Consequences`.

## Planning Documents (`.ruru/planning/*.md`)

*   **Overall Vision/Goals:** Look for introductions, `## Goals`, `## Vision`.
*   **Roadmap/Phases:** Scan for timelines, phases, quarters, milestones.
*   **Requirements:** Look for requirement IDs, user stories, functional descriptions.
*   **Architecture Overview:** Check for high-level component descriptions, links to diagrams/ADRs.

## General Tips

*   **Use Standard Emojis:** Leverage 🎯, 📄, 💡, 🧱, ➡️ as defined in `05-summary-templates.md`.
*   **Scan Headings:** Use Markdown headings (`##`, `###`) for navigation.
*   **Focus on Query:** Extract only information directly relevant to the query.
*   **Cite Sources:** Always mention the source file (`(from [filepath])`).
*   **Be Concise:** Summarize briefly using bullet points.
*   **Note Missing Info:** Explicitly state if relevant information or files are missing/unreadable.
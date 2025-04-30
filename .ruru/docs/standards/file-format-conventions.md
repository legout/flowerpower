+++
# --- Metadata ---
id = "STANDARD-FILE-FORMAT-CONVENTIONS-V1"
title = "Standard: Roo Commander File Format Conventions (TOML+MD vs Pure TOML)"
status = "active"
created_date = "2025-04-24"
updated_date = "2025-04-24"
version = "1.0"
tags = ["standard", "documentation", "file-format", "toml", "markdown", "convention", "design-decision", "architecture"]
related_docs = [
    ".roo/rules/01-standard-toml-md-format.md",
    ".ruru/templates/synthesis-task-sets/README.md"
]
audience = ["developers", "contributors", "architects", "ai-modes"]
# --- Document Specific Fields ---
objective = "To clarify and justify the use of different file extensions (`.md` vs `.toml`) based on the primary content type within the Roo Commander project."
scope = "Applies to all configuration, rule, mode, KB, and template files within the `.roo` and `.ruru` directories."
+++

# Standard: Roo Commander File Format Conventions

## 1. Abstract

This document outlines the standard conventions for file extensions within the Roo Commander project, specifically addressing files containing TOML data. It establishes **two primary patterns**: files combining TOML frontmatter with a primary Markdown body use the `.md` extension, while files containing *only* TOML configuration data use the standard `.toml` extension. This distinction prioritizes semantic accuracy and tooling compatibility over pure visual consistency of extensions.

## 2. Introduction

The Roo Commander system relies heavily on structured configuration and knowledge files. These files often need to be both **machine-readable** (for parsing by the Roo Code engine and AI modes) and **human-readable** (for development, maintenance, and understanding). TOML provides excellent machine readability and good human readability for configuration, while Markdown excels at human-readable documentation and structured text.

To effectively manage these different needs, the project employs specific file format conventions.

## 3. The Two Primary Patterns

### 3.1. Pattern 1: TOML Frontmatter + Markdown Body (`.md` extension)

*   **Description:** This pattern is used for files where the **primary content is intended as human-readable text, documentation, or instructions**, but which also require **structured metadata** for processing by the system or AI.
*   **Format:**
    *   The file begins with a TOML block enclosed in triple-plus delimiters (`+++`). This block contains key-value pairs defining metadata (e.g., `id`, `title`, `tags`, `status`, mode `role`, tool lists).
    *   Following the closing `+++` delimiter is the main content of the file, written in standard **Markdown**.
*   **Extension:** `.md`
*   **Rationale:** The `.md` extension is used because **Markdown is the primary content format**. The TOML block acts as *frontmatter* providing metadata *about* the Markdown content. This aligns with common conventions in static site generators and documentation systems (like Jekyll, Hugo, Docusaurus).
*   **Examples:**
    *   Rule files (`.roo/rules/**/*.md`, `.roo/rules-roo-commander/**/*.md`)
    *   Mode definition files (`.ruru/modes/**/*.mode.md`)
    *   Knowledge Base documents (`.ruru/modes/**/kb/*.md`)
    *   Planning documents (`.ruru/planning/**/*.md`)
    *   Architecture Decision Records (`.ruru/decisions/*.md`)

### 3.2. Pattern 2: Pure TOML Configuration (`.toml` extension)

*   **Description:** This pattern is used for files where the **entire content is TOML data**, serving purely as configuration input for a process or system component. There is **no associated Markdown body**.
*   **Format:** The entire file contains only valid TOML syntax (key-value pairs, tables, arrays of tables). No `+++` delimiters are typically needed unless embedding within another system that specifically requires them (which is not the standard for these files in Roo).
*   **Extension:** `.toml`
*   **Rationale:** Using the `.toml` extension is the **standard, universally recognized convention** for files containing TOML data. It provides:
    *   **Semantic Accuracy:** Clearly signals the file's content type is purely TOML.
    *   **Tooling Compatibility:** Ensures compatibility with standard TOML parsers, linters, validators, schema checkers, and editor syntax highlighters without requiring custom configurations.
    *   **Clarity:** Avoids confusion about whether Markdown content is expected.
*   **Examples:**
    *   Synthesis Task Set definitions (`.ruru/templates/synthesis-task-sets/*.toml`)
    *   *(Potential Future)* Global system settings, complex tool configurations (if JSON like `mcp.json` were migrated to TOML).

## 4. Justification for Distinction vs. Universal `.md`

While using `.md` for *all* files containing TOML might seem visually consistent initially, it introduces significant drawbacks for files that are *purely* configuration:

*   **Semantic Ambiguity:** Using `.md` for a `.toml`-only file misrepresents its primary content type.
*   **Tooling Friction:** Standard TOML tools may not recognize or correctly process `.md` files without specific workarounds. This increases technical debt and hinders the adoption of standard validation practices.
*   **Violation of Established Pattern:** It breaks the project's own established pattern where `.md` implies the presence of a Markdown body following `+++` delimiters.

Therefore, the project prioritizes **semantic accuracy and standard tooling compatibility** by using the `.toml` extension for pure TOML files, even though it introduces a second extension alongside `.md` within the configuration/knowledge structure. This distinction clearly signals the *nature* of the file's content (metadata + documentation vs. pure configuration).

## 5. Conclusion

Adhering to these two patterns ensures clarity, maintainability, and compatibility within the Roo Commander ecosystem:

*   Use `.md` with `+++` TOML frontmatter for documents combining metadata and Markdown content.
*   Use `.toml` for files containing only TOML configuration data.

This standard facilitates both human understanding and robust machine processing of the project's configuration and knowledge assets.
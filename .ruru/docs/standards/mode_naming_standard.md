+++
id = "STD-MODE-NAMING-V1"
title = "Mode Naming Standard"
context_type = "standard"
scope = "Defines the standard format for naming Roo modes (slug, display name, emoji)"
target_audience = ["all"] # Anyone creating or proposing new modes
granularity = "detailed"
status = "active"
last_updated = "2025-04-25" # Use current date
tags = ["modes", "naming", "standard", "documentation", "emoji", "slug"]
related_context = [
    ".ruru/modes/roo-commander/kb/available-modes-summary.md",
    ".ruru/workflows/WF-NEW-MODE-CREATION-001.md" # Assumed workflow for creating modes
    ]
template_schema_doc = ".ruru/templates/toml-md/16_ai_rule.README.md"
relevance = "High: Ensures consistency and discoverability of modes"
+++

# Mode Naming Standard

## 1. Purpose

This document defines the standard naming convention for all Roo modes. Adhering to this standard ensures:
*   **Consistency:** Modes are named using a predictable pattern.
*   **Discoverability:** Modes can be easily found and understood based on their name.
*   **Clarity:** The name reflects the mode's category, function, and specialty.
*   **Uniqueness:** Avoids conflicts and ambiguity, especially with emojis.

## 2. Components of a Mode Name

Each mode has three key naming components defined in its `.mode.md` file:

1.  **Slug (`slug`):** A unique, machine-readable identifier used internally and for switching modes (e.g., `dev-react`).
2.  **Display Name (`name`):** A human-readable name shown in interfaces, including an emoji (e.g., `⚛️ React Specialist`).
3.  **Emoji:** A single Unicode emoji character used in the display name for quick visual identification.

## 3. Slug (`slug`) Format

*   **Structure:** `category-topic` or `type-specialty`
*   **Case:** Strictly **lowercase**.
*   **Separator:** Use a hyphen (`-`) to separate the category/type from the topic/specialty.
*   **Characters:** Use only lowercase letters (`a-z`), numbers (`0-9`), and hyphens (`-`). Avoid spaces or other special characters.
*   **Standard Categories/Types:** Use one of the following established prefixes:
    *   `core`: Foundational system modes.
    *   `manager`: Modes responsible for coordination and process management.
    *   `lead`: Modes coordinating specific domains (backend, frontend, etc.).
    *   `agent`: Automated assistants performing specific background tasks.
    *   `spec`: Specialists focused on a specific external tool, API, or service (e.g., `spec-openai`).
    *   `framework`: Specialists for specific programming frameworks (e.g., `framework-react`).
    *   `design`: Specialists for UI/UX design tools or principles (e.g., `design-tailwind`).
    *   `data`: Specialists for database technologies or data handling (e.g., `data-mongo`).
    *   `infra`: Specialists for infrastructure management (e.g., `infra-compose`).
    *   `edge`: Specialists for edge computing platforms (e.g., `edge-workers`).
    *   `test`: Specialists for testing methodologies (e.g., `test-e2e`).
    *   `util`: General utility or helper modes (e.g., `util-refactor`).
    *   `auth`: Specialists for authentication services (e.g., `auth-clerk`).
    *   `baas`: Specialists for Backend-as-a-Service platforms (e.g., `baas-supabase`).
    *   `cloud`: Specialists for specific cloud providers (e.g., `cloud-aws`).
    *   `cms`: Specialists for Content Management Systems (e.g., `cms-wordpress`).
    *   `dev`: General development roles or language-specific specialists (e.g., `dev-react`, `dev-git`).
    *   `prime`: High-privilege modes for direct system modification.
*   **Topic/Specialty:** A concise, descriptive identifier for the mode's specific focus (e.g., `react`, `context-resolver`, `aws`, `writer`, `fixer`).

## 4. Display Name (`name`) Format

*   **Structure:** `Emoji Category/Type Topic/Specialty`
*   **Case:** **Title Case** (e.g., "React Specialist", "Technical Writer", "Backend Lead").
*   **Emoji:** See Section 5 below. Must be the first part of the name, followed by a single space.
*   **Category/Type:** The capitalized version of the category/type used in the slug (e.g., "Framework", "Util", "Lead"). For `dev-` slugs, often omitted or implied (e.g., "React Specialist" not "Dev React Specialist"). Use judgment for clarity.
*   **Topic/Specialty:** The capitalized, human-friendly version of the topic/specialty from the slug (e.g., "React Specialist", "Context Resolver", "AWS Architect").

## 5. Emoji Guidelines

*   **Uniqueness:** Each **new** mode **MUST** use a unique Unicode emoji character that is not already assigned to another mode.
*   **Relevance:** The emoji should visually represent the mode's function, domain, or technology as closely as possible.
*   **Visibility:** Choose emojis that render reliably across common platforms.
*   **Finding Emojis:** Resources like [Emojipedia](https://emojipedia.org/) can be helpful for finding suitable and unique emojis.
*   **Currently Used Emojis (as of 2025-04-25):** The following emojis are already in use and **MUST NOT** be reused for *new* modes:
    👑, 🏗️, 🚦, 📦, 📋, ⚙️, 🗄️, 🎨, 🚀, 🖥️, 💎, 🛡️, 🗜️, 🕵️, 📖, 🩹, 🌐, ⏱️, 🕷️, 🚒, 🤗, 🎱, 🅰️, 🧑‍🚀, 🐍, 💨, 🧪, 🛠️, 🐘, 💿, 🔥, 💚, ✨, 🐜, 🅱️, 📊, 🧩, 🧊, 🔄, 🔍, 🍃, 🐬, 💾, 🐳, ⚡, 🎭, 🔗, ♿, 🎯, 🌱, 🔧, ♻️, 👀, 🤔, 🧑‍💻, 🔷, ✍️, 🔑, 🧯, 🔐, 🦸, ☁️, 🌎, 🇼, 🔌, 📏, 🩺, 🦕, ⚛️, 🚜, 🐹, ✒️
    *(Note: Some historical duplicates exist (e.g., 🏗️, 🎨, 🚀). These should ideally be resolved over time, but the primary rule is **no new duplicates**.)*

## 6. Examples

| Slug                     | Display Name                     | Category/Type | Topic/Specialty   | Emoji | Notes                                    |
| :----------------------- | :------------------------------- | :------------ | :---------------- | :---- | :--------------------------------------- |
| `roo-commander`          | 👑 Roo Commander                 | `roo`         | `commander`       | 👑    | Special case                             |
| `lead-backend`           | ⚙️ Backend Lead                  | `lead`        | `backend`         | ⚙️    | Standard Lead format                     |
| `agent-context-resolver` | 📖 Context Resolver              | `agent`       | `context-resolver`| 📖    | Standard Agent format                    |
| `framework-react`        | ⚛️ React Specialist              | `framework`   | `react`           | ⚛️    | Framework specialist, common name format |
| `util-writer`            | ✍️ Technical Writer              | `util`        | `writer`          | ✍️    | Utility mode, descriptive name           |
| `spec-openai`            | 🎱 OpenAI Specialist             | `spec`        | `openai`          | 🎱    | Specific external service specialist     |
| `design-tailwind`        | 💨 Tailwind CSS Specialist       | `design`      | `tailwind`        | 💨    | Design tool specialist                   |
| `dev-git`                | 🦕 Git Manager                   | `dev`         | `git`             | 🦕    | Development utility                      |

## 7. Process for New Modes

When proposing or creating a new mode, ensure its naming adheres strictly to this standard. Refer to the workflow document `WF-NEW-MODE-CREATION-001.md` (if available) for the full process of mode creation and approval, which includes verifying compliance with this naming standard.
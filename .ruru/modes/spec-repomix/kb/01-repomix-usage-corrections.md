+++
id = "KB-REPOMIX-USAGE-CORRECTIONS-V1"
title = "Repomix Usage Corrections (Config & CLI)"
context_type = "knowledge"
scope = "Correct usage of repomix config file and CLI flags"
target_audience = ["MODE-SPEC-REPOMIX"]
granularity = "specific-corrections"
status = "active"
last_updated = "2025-04-27" # Use current date
tags = ["kb", "repomix", "configuration", "cli", "schema", "flags", "correction"]
related_context = ["repomix documentation"] # Assumed external context
template_schema_doc = ".ruru/templates/toml-md/14_kb_article.README.md"
relevance = "Critical: Corrects known errors in tool usage"
+++

# Repomix Usage Corrections

This document outlines critical corrections for using the `repomix` tool based on observed errors.

## 1. Configuration File (`repomix.config.json`) Schema

**Error:** The `output` field was incorrectly specified as a string.
**Correction:** The `output` field **MUST** be an **object** containing `path` and `format` keys.

**Incorrect Example:**
```json
{
  "output": "my-output-file.md"
}
```

**Correct Example:**
```json
{
  "output": {
    "path": "my-output-file.md",
    "format": "markdown" // Or "xml", "text"
  }
}
```
*   Ensure the `output` field is structured as an object.
*   Valid `format` values include `"markdown"`, `"xml"`, `"text"`.

## 2. Command-Line Interface (CLI) Flags

**Error:** The `--format` flag was used to specify the output format (e.g., `--format markdown`).
**Correction:** The correct flag to specify the output format/style is **`--style`**.

**Incorrect Command:**
```bash
repomix . --format markdown -o output.md
```

**Correct Command:**
```bash
repomix . --style markdown -o output.md
```
*   Use `--style [format]` (e.g., `--style markdown`) instead of `--format [format]`.

**Adherence to these corrections is crucial for successful `repomix` execution.**
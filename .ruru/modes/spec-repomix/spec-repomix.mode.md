+++
# --- Core Identification (Required) ---
id = "MODE-SPEC-REPOMIX" # << REQUIRED >>
name = "🧬 Repomix Specialist" # << REQUIRED >>
version = "1.0.0" # << REQUIRED >> Initial version

# --- Classification & Hierarchy (Required) ---
classification = "Specialist" # << REQUIRED >>
domain = "utility" # << REQUIRED >> Specializes in a specific tool
# sub_domain = "repository-packaging" # << OPTIONAL >>

# --- Description (Required) ---
summary = "Specialist in using the `repomix` tool to package repository content for LLM context." # << REQUIRED >>

# --- Base Prompting (Required) ---
system_prompt = """
You are Roo 🧬 Repomix Specialist. Your primary role is to utilize the `repomix` command-line tool effectively to package code repositories into formats suitable for Large Language Models (LLMs).

Key Responsibilities:
- Execute `repomix` commands to process local and remote repositories.
- Configure `repomix` using `repomix.config.json` or command-line options.
- Select appropriate output formats (XML, Markdown, plain text) based on requirements.
- Apply filters and other options to customize the packaging process.
- Generate initial configuration files using `repomix --init`.

Operational Guidelines:
- Consult and prioritize guidance, best practices, and project-specific information found in the Knowledge Base (KB) located in `.ruru/modes/spec-repomix/kb/`. Use the KB README to assess relevance and the KB lookup rule for guidance on context ingestion.
- Use tools iteratively and wait for confirmation.
- Prioritize precise file modification tools (`apply_diff`, `search_and_replace`) over `write_to_file` for existing files.
- Use `read_file` to confirm content before applying diffs if unsure.
- Execute CLI commands using `execute_command`, explaining clearly.
- Escalate tasks outside core expertise to appropriate specialists via the lead or coordinator.
""" # << REQUIRED >>

# --- Tool Access (Optional - Defaults to standard set if omitted) ---
# If omitted, assumes access to: ["read", "edit", "browser", "command", "mcp"]
# allowed_tool_groups = ["read", "edit", "command"] # Example: Specify if different from default

# --- File Access Restrictions (Optional - Defaults to allow all if omitted) ---
# [file_access]
# read_allow = ["**/*.py", ".docs/**"] # Example: Glob patterns for allowed read paths
# write_allow = ["**/*.py"] # Example: Glob patterns for allowed write paths

# --- Metadata (Optional but Recommended) ---
[metadata]
tags = ["repomix", "cli", "llm-context", "repository-packaging", "utility"] # << RECOMMENDED >> Lowercase, descriptive tags
categories = ["Utility", "AI Integration", "Development Tools"] # << RECOMMENDED >> Broader functional areas
delegate_to = ["other-mode-slug"] # << OPTIONAL >> Modes this mode might delegate specific sub-tasks to
escalate_to = ["lead-mode-slug", "architect-mode-slug"] # << OPTIONAL >> Modes to escalate complex issues or broader concerns to
reports_to = ["lead-mode-slug", "roo-commander"] # << OPTIONAL >> Modes this mode typically reports completion/status to
documentation_urls = [ # << OPTIONAL >> Links to relevant external documentation
  "https://example.com/docs"
]
context_files = [ # << OPTIONAL >> Relative paths to key context files within the workspace
  # ".ruru/docs/standards/coding_style.md"
]
context_urls = [] # << OPTIONAL >> URLs for context gathering (less common now with KB)

# --- Custom Instructions Pointer (Optional) ---
# Specifies the location of the Knowledge Base directory.
custom_instructions_dir = "kb" # << RECOMMENDED >> Should point to the Knowledge Base directory

# --- Mode-Specific Configuration (Optional) ---
# [config]
# key = "value" # Add any specific configuration parameters the mode might need
+++

# 🧬 Repomix Specialist - Mode Documentation

**Executive Summary**

Based on the available official documentation (primarily the GitHub repository README, associated documentation website `repomix.com`, command-line help, and PyPI page for the Python port), the `yamadashy/repomix` CLI tool is well-documented regarding its core purpose, installation, basic usage, command-line options, filtering, and output formats (XML, Markdown, Plain Text). It is designed to package entire code repositories into a single file optimized for consumption by Large Language Models (LLMs). Documentation covers both local and remote repository processing. Configuration via file (`repomix.config.json`) is also documented, including global and local scope. Some advanced concepts like code compression and security checks are mentioned. Explicit "best practices" are not extensively detailed but can be inferred from usage examples. Documentation gaps exist regarding detailed internal mechanisms beyond high-level descriptions and explicit version compatibility matrices (though the tool is actively developed).

**1. Core Concepts**

`repomix` is a command-line utility designed to consolidate the contents of a software repository (either local or remote) into a single file [1, 6, 7]. The primary goal is to create an "AI-friendly" output that can be easily fed into Large Language Models (LLMs) like Claude, ChatGPT, Gemini, etc., for tasks such as code review, refactoring, documentation generation, or general analysis [1, 4, 6]. It processes the codebase, respects ignore files (`.gitignore`), performs security checks, and formats the output [1, 6].

**2. Principles**

Based on the documentation, the underlying principles appear to be:

*   **AI Optimization:** Formatting output specifically for better comprehension by LLMs, including introductory explanations and structured formats like XML [1, 6, 11].
*   **Simplicity:** Offering a straightforward command-line interface for common use cases (`npx repomix`) [1, 4].
*   **Customization:** Providing options for filtering, output formatting, and configuration to tailor the output [1, 6, 8].
*   **Context Awareness:** Being Git-aware (respecting `.gitignore`) and providing options to include repository structure and file summaries [1, 6, 9].
*   **Security:** Integrating checks to prevent accidental inclusion of sensitive data [1, 6, 7].
*   **Efficiency:** Offering features like code compression (`--compress`) to manage token limits for LLMs [1, 8, 9].

**3. Best Practices (Inferred)**

While not explicitly labeled as "Best Practices," the documentation suggests the following approaches:

*   **Start Simple:** Use `npx repomix` for quick, installation-free use in a project directory [1, 5].
*   **Configure for Consistency:** Use a `repomix.config.json` file (created via `repomix --init`) for project-specific settings like includes/excludes and output preferences [5, 6, 9].
*   **Leverage `.gitignore`:** Rely on existing `.gitignore` files for standard exclusions, as `repomix` respects them by default [1, 9]. Add project-specific exclusions to `.repomixignore` or use `--ignore` flags [9].
*   **Choose Appropriate Output Format:** Use XML (`--style xml`, default) for potentially better parsing by AI like Claude, or Markdown/Plain Text (`--style markdown`/`--style plain`) as needed [1, 5, 8, 11].
*   **Use Compression for Large Repos:** Employ the `--compress` flag when dealing with large codebases to reduce token count while preserving key structures [1, 8, 9].
*   **Utilize Remote Processing:** Analyze public repositories directly using the `--remote` flag without manual cloning [1, 5, 8].
*   **Review Security:** Be aware of the integrated security checks (using Secretlint in the Node.js version, detect-secrets in the Python version) but understand their limitations [1, 6, 7].

**4. Key Functionalities**

*   **Repository Packing:** Combines files from a specified directory or an entire repository into one output file [1, 4].
*   **Filtering:** Includes/excludes files based on glob patterns, `.gitignore`, `.repomixignore`, and default patterns [1, 8, 9].
*   **Output Formatting:** Generates output in XML, Markdown, or Plain Text formats [1, 5, 8, 11].
*   **Remote Repository Processing:** Clones and processes public Git repositories directly via URL or shorthand (`user/repo`) [1, 5, 8]. Supports specifying branches/tags/commits [8].
*   **Configuration Management:** Supports configuration via CLI flags, local `repomix.config.json`, and global configuration files [2, 8, 9]. CLI flags generally override file configurations [2].
*   **Security Scanning:** Integrates tools to detect potential secrets (API keys, credentials) and prevent their inclusion [1, 6, 7]. Can be disabled (`--no-security-check` in Python version) [6].
*   **Code Compression:** Uses Tree-sitter (Node.js version) to intelligently extract key code elements (signatures, etc.) reducing token count [1, 8, 9].
*   **Token Counting:** Provides token counts for files and the repository (useful for LLM context limits) [1, 6].
*   **Metadata Inclusion:** Can optionally include directory structure, file summaries, and line numbers in the output [1, 8].
*   **MCP Server:** Can run as a Model Context Protocol (MCP) server for integration with AI assistants like Cursor [7, 15].

**5. Configuration**

*   **Initialization:** A configuration file can be created using `repomix --init` [1, 5, 6].
*   **File Name:** The default local configuration file is `repomix.config.json` in the project root [5, 6, 9].
*   **Global Configuration:** A global configuration file can be created with `repomix --init --global` [9].
    *   Location (macOS/Linux): `~/.config/repomix/repomix.config.json` [9].
    *   Location (Windows): `%LOCALAPPDATA%\\Repomix\\repomix.config.json` [9].
*   **Custom Path:** A custom configuration file path can be specified using `-c` or `--config <path>` [1, 8].
*   **Format:** The configuration file uses JSON format [6, 9].
*   **Key Options (documented in `repomix.config.json`) [6, 9]:**
    *   `output`: Controls output settings like `filePath`, `style` (xml, markdown, plain), `compress`, `headerText`, `instructionFilePath`, `fileSummary`, `directoryStructure`, `removeComments`, `removeEmptyLines`, `showLineNumbers`, `copyToClipboard`, `includeEmptyDirectories`.
    *   `output.git`: Controls Git-based sorting (`sortByChanges`, `sortByChangesMaxCommits`).
    *   `include`: Array of glob patterns for files to include.
    *   `ignore`: Controls ignore settings like `useGitignore`, `useDefaultPatterns`, `customPatterns` (array of glob patterns).
    *   `security`: Controls security checks (`enableSecurityCheck`).
*   **Priority:** Configuration settings are merged, with command-line options typically overriding file settings [2, 9]. Ignore pattern priority is documented as: CLI > `.repomixignore` > `.gitignore` / `.git/info/exclude` > Default patterns [9].

**6. Command-Line Options**

The CLI provides extensive options, documented via `--help` and on the documentation site [1, 8]. Key options include:

*   **Basic:**
    *   `-v, --version`: Show version [8].
*   **Output Control:**
    *   `-o, --output <file>`: Specify output file name [1, 8].
    *   `--style <type>`: Set output format (`xml`, `markdown`, `plain`) [1, 5, 8]. Default is `xml` [8].
    *   `--parsable-style`: Ensure output strictly follows the chosen format's schema [1, 8].
    *   `--compress`: Enable intelligent code compression [1, 8].
    *   `--output-show-line-numbers`: Add line numbers to output [1, 8].
    *   `--copy`: Copy output to clipboard [1, 8].
    *   `--no-file-summary`, `--no-directory-structure`, `--no-files`: Disable specific output sections [1, 8].
    *   `--remove-comments`, `--remove-empty-lines`: Modify content [8].
    *   `--header-text <text>`, `--instruction-file-path <path>`: Add custom content to the header [3, 8].
    *   `--include-empty-directories`: Include empty directories in output [3, 8].
*   **Filtering:**
    *   `--include <patterns>`: Comma-separated list of include glob patterns [1, 8].
    *   `-i, --ignore <patterns>`: Comma-separated list of additional ignore glob patterns [1, 8].
    *   `--no-gitignore`: Disable use of `.gitignore` files [1, 3, 8].
    *   `--no-default-patterns`: Disable default ignore patterns [1, 3, 8].
*   **Remote Repositories:**
    *   `--remote <url>`: Process a remote Git repository (URL or `user/repo` format) [1, 5, 8].
    *   `--remote-branch <name>`: Specify branch, tag, or commit hash for remote repo [3, 8].
*   **Configuration:**
    *   `-c, --config <path>`: Path to custom config file [1, 8].
    *   `--init`: Create a config file (`repomix.config.json`) [1, 5, 8].
    *   `--global`: Use global config (used with `--init`) [1, 9].
*   **Security (Python version specific flag shown):**
    *   `--no-security-check`: Disable security checks [6]. (Node.js version uses config file) [9].
*   **Other:**
    *   `--verbose`: Enable verbose logging [6, 8].
    *   `--quiet`: Disable stdout output [8].
    *   `--mcp`: Run as MCP server [7].

**7. Filtering**

Filtering determines which files are included in the output:

*   **Include Patterns:** Specified via `--include <patterns>` (CLI) or `include` array (config file). Uses glob patterns [1, 8, 9].
*   **Ignore Patterns:** Specified via:
    *   `--ignore <patterns>` (CLI) [1, 8].
    *   `customPatterns` array in `ignore` section (config file) [9].
    *   `.repomixignore` file in the project root [9].
    *   `.gitignore` and `.git/info/exclude` files (can be disabled with `--no-gitignore` or `useGitignore: false` in config) [1, 8, 9].
    *   Default internal ignore patterns (can be disabled with `--no-default-patterns` or `useDefaultPatterns: false` in config) [1, 3, 8, 9]. Includes common patterns like `node_modules/**`, `.git/**` [9].
*   **Priority:** As mentioned in Configuration, CLI ignores take precedence, followed by `.repomixignore`, then `.gitignore`, then defaults [9].
*   **Path Matching:** Uses `fnmatch` (Python version) or similar glob matching, supporting special characters [2, 3].

**8. Handling Local and Remote Repositories**

*   **Local Repositories:**
    *   By default, `repomix` runs in the current working directory [1, 5].
    *   A specific local directory can be provided as an argument: `repomix path/to/directory` [5, 7].
    *   It scans the specified directory recursively, applying filtering rules to find relevant files [2].
*   **Remote Repositories:**
    *   The `--remote <url>` flag is used [1, 5, 8].
    *   The URL can be a full Git repository URL (e.g., `https://github.com/yamadashy/repomix`) or a shorthand (`yamadashy/repomix`) [5].
    *   It supports URLs pointing to specific branches, tags, or commits (e.g., `https://github.com/user/repo/tree/branch-name`) [3, 5, 8].
    *   The `--remote-branch <name>` flag can explicitly specify a branch, tag, or commit hash [8].
    *   When processing a remote repository, `repomix` clones it into a temporary directory, processes it, and then cleans up the temporary directory [2].

**9. Output Formats**

`repomix` explicitly supports three output formats, selectable via the `--style <type>` flag or the `output.style` configuration option [1, 5, 6, 8, 11]:

1.  **XML (`--style xml`):**
    *   This is the default format [8, 11].
    *   It wraps file content and metadata in XML tags [1, 6].
    *   Documentation suggests this format is potentially better parsed by AI models like Claude [1, 11].
    *   The `--parsable-style` flag ensures properly escaped XML [3, 8].
2.  **Markdown (`--style markdown`):**
    *   Formats the output using Markdown syntax, typically using code blocks for file content [5, 6, 8, 11].
    *   The `--parsable-style` flag dynamically adjusts code block delimiters to avoid conflicts [3, 8].
3.  **Plain Text (`--style plain`):**
    *   Outputs the content as plain text with separators between files [5, 6, 8, 11].
    *   Includes an AI-oriented explanation header [1, 6].

**10. Code Examples**

*   **Basic Usage (Current Directory, XML Output):**
    ```bash
    # Run without installation (uses latest version)
    npx repomix

    # Or, if installed globally
    repomix
    ```
    *Explanation:* This command processes the current directory, respects `.gitignore`, uses default filters, and outputs to `repomix-output.xml` (default filename changed over time, check current default) [1, 5, 8].

*   **Specify Output File and Format (Markdown):**
    ```bash
    repomix -o project_packed.md --style markdown
    ```
    *Explanation:* Processes the current directory, outputs to `project_packed.md` in Markdown format [5, 8].

*   **Process Remote Repository (Specific Branch):**
    ```bash
    repomix --remote yamadashy/repomix --remote-branch main --style plain -o repomix_main.txt
    ```
    *Explanation:* Clones the `main` branch of the `yamadashy/repomix` repository, processes it, and outputs to `repomix_main.txt` in plain text format [5, 8].

*   **Filtering Example (Include/Exclude):**
    ```bash
    repomix --include "src/**/*.js,*.md" --ignore "**/test/**,*.log"
    ```
    *Explanation:* Processes the current directory, including only `.js` files within `src` and Markdown files at any level, while excluding anything under `test` directories and any `.log` files [5, 8].

*   **Configuration File Example (`repomix.config.json`):**
    ```json
    {
      "output": {
        "filePath": "ai_context.xml",
        "style": "xml",
        "compress": true,
        "fileSummary": true,
        "directoryStructure": true
      },
      "include": [
        "src/**/*",
        "docs/**/*.md"
      ],
      "ignore": {
        "useGitignore": true,
        "useDefaultPatterns": true,
        "customPatterns": [
          "**/node_modules/**",
          "**/*.test.js",
          "temp/"
        ]
      },
      "security": {
        "enableSecurityCheck": true
      }
    }
    ```
    *Explanation:* This configuration specifies XML output to `ai_context.xml`, enables compression, includes file summary and directory structure. It includes files in `src` and Markdown files in `docs`. It uses `.gitignore` and default ignores, plus custom ignores for `node_modules`, test files, and `temp/`. Security checks are enabled [6, 9]. Run `repomix` in the same directory as this file.

**11. Boundary of Documentation**

*   The primary documentation sources are the GitHub repository (`yamadashy/repomix`), specifically the `README.md`, the linked documentation website (`repomix.com`), command-line help (`--help`), and the PyPI page for the Python port [1, 5, 6, 8].
*   Documentation thoroughly covers the tool's purpose, installation, usage, CLI options, configuration file structure, filtering mechanisms, output formats, and remote repository handling [1, 5, 6, 8, 9].
*   Detailed internal implementation logic (e.g., exact algorithms for compression or security scanning beyond mentioning the libraries used) is generally not documented, though some code structure overview exists in related articles or specific documentation files [2, 3].
*   Explicit version compatibility matrices are not provided, but the tool is under active development, implying recent versions are recommended [1, 3].
*   While security features are mentioned, the exact rulesets or limitations of the underlying tools (Secretlint, detect-secrets) are not detailed within the `repomix` documentation itself [1, 6, 9]. Users would need to consult the documentation for those specific libraries for full details.
*   Performance benchmarks or detailed scaling characteristics are not documented.

**12. Documentation References**

*   **Primary Sources (Node.js version):**
    *   [1] GitHub Repository (`yamadashy/repomix`): `https://github.com/yamadashy/repomix` (Includes README.md)
    *   [5] Official Documentation Website: `https://repomix.com/`
    *   [8] Command Line Options Documentation: `https://repomix.com/docs/cli-options`
    *   [9] Configuration Documentation: `https://repomix.com/docs/configuration`
    *   [11] Output Formats Documentation: `https://repomix.com/docs/output-formats`
    *   [3] `repomix-instruction.md` (for AI assistance): `https://github.com/yamadashy/repomix/blob/main/repomix-instruction.md`
    *   [7] Playbooks MCP Server Documentation: `https://playbooks.developer-service.io/servers/repomix`
    *   [15] MagicSlides MCP Server Documentation: `https://magicslides.app/mcp-servers/repomix/`
    *   [18] Repomix MCP Client Overview: `https://mcp.anysphere.co/clients/repomix`
    *   [12] Homebrew Formulae: `https://formulae.brew.sh/formula/repomix`
    *   [16] Yarn Package Info: `https://yarnpkg.com/package/repomix`
    *   [19] NPM Package Info: `https://www.npmjs.com/package/repomix`
*   **Python Port:**
    *   [6] PyPI Page (`repomix` Python version): `https://pypi.org/project/repomix/`
*   **Related Articles/Discussions (Contextual):**
    *   [2] DEV Community Article (Code Explanation): `https://dev.to/dteamtop/code-explanation-repomix-codebase-packaging-for-ai-consumption-4g4l`
    *   [4] DEV Community Article (Author's Introduction): `https://dev.to/yamadashy/i-made-repomix-a-tool-for-seamless-coding-with-claude-ai-2k6k`
    *   [10] Zenn Article (Author's Story, Japanese): `https://zenn.dev/yamadashy/articles/repomix-oss-journey`
    *   [13] Trendshift Article (Mentions Repomix): `https://trendshift.io/tools/ask-ai`
    *   [14] Flox Blog Post (Using Repomix): `https://flox.dev/blog/fun-package-friday-repomix`
    *   [17] Reddit Discussion (Mentions Features): `https://www.reddit.com/r/ChatGPTCoding/comments/1apz80c/is_repomix_safe/`
## Description

The 🧬 Repomix Specialist is an expert in using the `repomix` command-line tool. Its primary function is to package the contents of code repositories (both local directories and remote GitHub repositories) into a single, structured file. This output is specifically optimized for consumption by Large Language Models (LLMs), providing them with comprehensive codebase context in a condensed format.

## Capabilities

[List the specific tasks and abilities this mode possesses. Use bullet points.]

*   Execute the core `repomix [path]` command to package repositories.
*   Specify output files using `-o` or `--output`.
*   Control the output format (`--format`) choosing between `xml`, `markdown`, or `plain` text.
*   Process both local filesystem paths and (presumably) remote GitHub repository URLs.
*   Initialize a `repomix.config.json` file using `repomix --init`.
*   Utilize settings defined within `repomix.config.json` to guide the packaging process (e.g., applying filters, defining structure).

## Workflow & Usage Examples

[Describe the typical high-level workflow the mode follows. Provide 2-3 concrete usage examples in `prompt` blocks demonstrating how to invoke the mode.]

**General Workflow:**

1.  Receive instructions specifying the target repository (local path or remote URL) and desired output options (file name, format, specific configurations/filters).
2.  Determine if a `repomix.config.json` exists or needs to be created (`repomix --init`).
3.  Construct the appropriate `repomix` command with necessary options.
4.  Execute the command using the `execute_command` tool.
5.  Report the path to the generated output file or any errors encountered.

**Usage Examples:**

**Example 1: Package Current Directory as Markdown**

```prompt
Use repomix to package the current project directory into a Markdown file named 'project-context.md'.
```
*Expected Action:* Executes `repomix . --format markdown -o project-context.md`.

**Example 2: Initialize Configuration**

```prompt
Create a default repomix configuration file in the current directory.
```
*Expected Action:* Executes `repomix --init`.

**Example 3: Package Specific Local Path**

```prompt
Package the repository at '/home/user/projects/my-app' into an XML file named 'my-app-context.xml'.
```
*Expected Action:* Executes `repomix /home/user/projects/my-app --format xml -o my-app-context.xml`.

## Limitations

[Clearly define the boundaries of the mode's expertise. What tasks does it *not* do? When should it escalate or delegate?]

*   Does not interpret the *content* of the packaged repository, only structures it.
*   Relies on the `repomix` tool being correctly installed and accessible in the environment.
*   Specific syntax for advanced filtering or handling remote repositories beyond basic invocation might require further research or KB population, as initial context was limited.
*   Cannot provide details on *how* to install `repomix` itself based on current context.
*   Does not manage Git operations (cloning, pulling) unless explicitly instructed as part of a multi-step process coordinated externally.

## Rationale / Design Decisions

[Explain *why* this mode exists and the key decisions behind its design, capabilities, and limitations. How does it fit into the overall system?]

*   **Rationale:** LLMs require comprehensive context to understand and reason about codebases effectively. `repomix` provides a standardized way to package this context, overcoming limitations of manually feeding files or dealing with context window constraints. This specialist mode ensures consistent and correct application of the `repomix` tool.
*   **Design:** Focused solely on the execution and configuration of the `repomix` CLI tool. Assumes the tool itself handles the complexities of repository parsing and formatting.
*   **Fit:** Acts as a utility specialist, invoked by coordinators or other modes when LLM context generation from a repository is needed.
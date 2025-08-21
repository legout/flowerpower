You are tasked with creating clear, concise, and professional documentation for my Python library/framework using both Quarto and MkDocs with Material theme. 

No project structure or examples exist yet, so you must set up both documentation systems and generate all content. The documentation should be user-friendly, leveraging each tool's features for polished HTML output. Read the `README.md` file and the codebase in `src/flowerpower` to understand the library's details, especially for the API section. Follow these instructions:

### Objectives
1. **Clarity**: Write accessible explanations for new and experienced users.
2. **Comprehensiveness**: Cover setup, installation, quickstart, API, examples, and contributing.
3. **Tool Features**: Use markdown, code blocks, and cross-references for HTML output in both systems.
4. **Codebase Analysis**: Use `README.md` and the codebase in `src/flowerpower` to inform content, foundationally for the API section.

### Requirements

#### Project Structure
```
docs/
├── quarto/
│   ├── _quarto.yml
│   ├── index.qmd
│   ├── installation.qmd
│   ├── quickstart.qmd
│   ├── architecture.qmd
│   ├── examples.qmd
│   ├── advanced.qmd
│   ├── contributing.qmd
│   └── api/
│       └── *.qmd files
└── mkdocs/
  ├── mkdocs.yml
  ├── docs/
  │   ├── index.md
  │   ├── installation.md
  │   ├── quickstart.md
  │   ├── architecture.md
  │   ├── examples.md
  │   ├── advanced.md
  │   ├── contributing.md
  │   └── api/
  │       └── *.md files
  └── requirements.txt
```

#### 1. Quarto Setup (`docs/quarto/`):
   - Create a new Quarto project using `quarto create project website`.
   - Organize content into `.qmd` files: `index.qmd`, `installation.qmd`, `quickstart.qmd`, `architecture.qmd`, `examples.qmd`, `advanced.qmd`, `contributing.qmd`.
   - Configure `_quarto.yml` for intuitive navigation, HTML output (use `cosmo` theme, enable search).
   - Create an `api/` folder for API documentation files.

#### 2. MkDocs Setup (`docs/mkdocs/`):
   - Initialize MkDocs project with Material theme.
   - Configure `mkdocs.yml` with Material theme, navigation, search, and code highlighting.
   - Organize content into `.md` files in `docs/` subfolder: `index.md`, `installation.md`, `quickstart.md`, `architecture.md`, `examples.md`, `advanced.md`, `contributing.md`.
   - Create a `docs/api/` folder for API documentation files.
   - Include `requirements.txt` with `mkdocs-material` and other needed plugins.

### Content Sections (Identical for Both Systems):
   - **Home Page (`index.qmd`/`index.md`)**:
   - Introduce the library based on `README.md` (purpose, key features).
   - Include a "Get Started" link to quickstart page.
   - Add a badge/link to GitHub or PyPI (if applicable).
   - Include a summary of key features or concepts.
   - Highlight any important usage notes or caveats.
   - **Installation (`installation.qmd`/`installation.md`)**:
   - Provide `pip` installation steps and prerequisites (e.g., Python version). Mention `uv` and `pixi`
   - Include troubleshooting tips for common issues.
   - **Quickstart (`quickstart.qmd`/`quickstart.md`)**:
   - Create a simple, hypothetical example based on `README.md` or the examples in `examples/` to demonstrate core functionality.
   - Use executable code blocks (Quarto: `{python}`, MkDocs: syntax highlighting).
   - Include explanations for each step.
   - Provide links to relevant API documentation or examples.
   - **Architecture Overview (`architecture.qmd`/`architecture.md`)**:
   - Explain the library's architecture, inspired by `README.md`.
   - Include diagrams or flowcharts if necessary (use each tool's diagram features).
   - Discuss key components and their interactions.
   - **Examples (`examples.qmd`/`examples.md`)**:
   - Create some hypothetical examples based on the examples in `examples/`.
   - Use code blocks and write explanations for each step in plain text.
   - **Advanced Usage (`advanced.qmd`/`advanced.md`)**:
   - Highlight advanced features or configurations inferred from the codebase in `src/flowerpower`.
   - Include performance tips or integrations.
   - Discuss potential use cases or scenarios.
   - Include troubleshooting tips for common issues.
   - **API Reference (`api/*.qmd`/`api/*.md`)**:
   - Analyze the codebase in `src/flowerpower` and `README.md` to document all public classes, functions, and methods.
   - Organize into separate files per module/class.
   - Use tables or callouts for parameters, returns, and exceptions.
   - Include code snippets and cross-references.
   - **Contributing (`contributing.qmd`/`contributing.md`)**:
   - Summarize how to contribute (issues, pull requests).
   - Reference development setup from `README.md` if available.

### Tool-Specific Features:

#### Quarto Features:
   - Use executable `{python}` code blocks.
   - Use callout blocks (`::: {.callout-note}`) for tips/warnings.
   - Add table of contents for each `.qmd` file.
   - Configure `_quarto.yml` for HTML output only.
   - Theme-toggle: Enable dark/light mode switching.
   - Include a footer with copyright and license information.
   - Add a "Back to top" button for easier navigation.
   - Place GitHub and PyPI badges/links prominently (e.g., right navigation bar).
   - Use Quarto's built-in search functionality.
   - Create menus for the API documentation.

#### MkDocs Material Features:
   - Use Material theme admonitions (`!!! note`) for tips/warnings.
   - Configure navigation in `mkdocs.yml`.
   - Use Material's code highlighting and copy buttons.
   - Enable search and other Material theme features.
   - Include a footer with copyright and license information.
   - Add a "Back to top" button for easier navigation.
   - Place GitHub and PyPI badges/links prominently (e.g., right navigation bar).
   - Create menus for the API documentation.

### Styling and Tone:
   - Use a friendly, professional tone.
   - Format code and variables consistently (e.g., `function_name()`).
   - Ensure accessibility (e.g., alt text for visuals).

### Output and Testing:
   - **Quarto**: Render documentation as HTML using `quarto render` from `docs/quarto/`.
   - **MkDocs**: Serve documentation using `mkdocs serve` from `docs/mkdocs/`.
   - Test code blocks and navigation for correctness in both systems.
   - Optimize visuals for fast loading.

### Deliverables
- Complete Quarto project in `docs/quarto/` with `.qmd` files and `_quarto.yml`.
- Complete MkDocs project in `docs/mkdocs/` with `.md` files and `mkdocs.yml`.
- API documentation in both `docs/quarto/api/` and `docs/mkdocs/docs/api/`.
- Brief report summarizing structure and assumptions for both systems.
- Instructions for rendering and deploying both documentation systems (e.g., GitHub Pages).

### Assumptions
- The codebase in `src/flowerpower`, examples in `examples/` and `README.md` are available for reference.
- If specific details are unclear, include placeholders and note where clarification is needed.
- Both documentation systems should have identical content, adapted to each tool's syntax and features.

### Notes
- Prioritize modularity for future updates in both systems.
- Do not generate PDF output.
- Use latest features of both Quarto and MkDocs Material (as of August 2025).
- Ensure consistent navigation and structure between both documentation systems.

Please proceed with generating both documentation systems based on these instructions. If you need clarification, let me know!
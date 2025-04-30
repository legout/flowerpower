+++
id = "kb-available-modes-summary"
title = "Available Modes Summary"
context_type = "summary"
target_audience = ["roo-commander"]
status = "generated"
last_generated = "2025-04-25"
+++

# Available Modes Summary

This document provides a summary of available specialist modes for delegation.

## Roo Commander
- **roo-commander** (👑 Roo Commander): Highest-level coordinator for software development projects, managing goals, delegation, and project state.

## Core Modes
- **core-architect** (🏗️ Technical Architect): Designs and oversees high-level system architecture, making strategic technology decisions that align with business goals and technical requirements. Responsible for establishing the technical vision, selecting appropriate technologies, evaluating architectural trade-offs, addressing non-functional requirements, and ensuring technical coherence across the project. Acts as the primary technical decision-maker and advisor for complex system design challenges.

## Manager Modes
- **manager-onboarding** (🚦 Project Onboarding): Handles initial user interaction, determines project scope (new/existing), delegates discovery/requirements gathering, coordinates basic setup, and delegates tech initialization.
- **manager-product** (📦 Product Manager): A strategic director-level mode responsible for defining and executing product vision, strategy, and roadmap. Translates business goals and user needs into actionable product requirements, coordinates with technical teams, and ensures product success through data-driven decision making.
- **manager-project** (📋 Project Manager (MDTM)): Manages project features/phases using the TOML-based Markdown-Driven Task Management (MDTM) system, breaking down work, delegating tasks, tracking status, and reporting progress. Operates primarily within the `.ruru/tasks/` directory.

## Lead Modes
- **lead-backend** (⚙️ Backend Lead): Coordinates backend development (APIs, logic, data integration), manages workers, ensures quality, security, performance, and architectural alignment.
- **lead-db** (🗄️ Database Lead): Coordinates database tasks (schema design, migrations, query optimization, security), manages workers, ensures data integrity and performance.
- **lead-design** (🎨 Design Lead): Coordinates design tasks (UI, diagrams), manages design workers, ensures quality and consistency, and reports progress to Directors.
- **lead-devops** (🚀 DevOps Lead): Coordinates DevOps tasks (CI/CD, infra, containers, monitoring, deployment), manages workers, ensures operational stability and efficiency.
- **lead-frontend** (🖥️ Frontend Lead): Coordinates frontend development tasks, manages frontend workers, ensures code quality, performance, and adherence to design/architecture.
- **lead-qa** (💎 QA Lead): The QA Lead is responsible for coordinating and overseeing all quality assurance activities within the project. They ensure that software releases meet quality standards by planning, delegating, and monitoring testing efforts. They receive features ready for testing or high-level quality objectives from Directors (e.g., Project Manager) or other Leads (e.g., Frontend Lead, Backend Lead) and translate them into actionable testing tasks for the QA Worker modes. Their primary goals are to ensure thorough test coverage, facilitate effective bug detection and reporting, assess product quality, and communicate quality-related risks.
- **lead-security** (🛡️ Security Lead): Coordinates security strategy, risk management, compliance, incident response, and manages security specialists.

## Agent Modes
- **agent-context-condenser** (🗜️ Context Condenser): Generates dense, structured summaries (Condensed Context Indices) from technical documentation sources for embedding into other modes' instructions.
- **agent-context-discovery** (🕵️ Discovery Agent): Specialized assistant for exploring the project workspace, analyzing files, and retrieving context.
- **agent-context-resolver** (📖 Context Resolver): Specialist in reading project documentation (task logs, decision records, planning files) to provide concise, accurate summaries of the current project state. Acts as the primary information retrieval and synthesis service for other modes.
- **agent-file-repair** (🩹 File Repair Specialist): Attempts to fix corrupted or malformed text files (such as source code, JSON, YAML, configs) by addressing common issues like encoding errors, basic syntax problems, truncation, and invalid characters.
- **agent-mcp-manager** (🛠️ MCP Manager Agent): Guides the user through installing, configuring, and potentially managing MCP servers interactively.
- **agent-research** (🌐 Research & Context Builder): Researches topics using web sources, code repositories, and local files, evaluates sources, gathers data, and synthesizes findings into structured summaries with citations.
- **agent-session-summarizer** (⏱️ Session Summarizer): Reads project state artifacts (task logs, plans) to generate a concise handover summary.

## Specialist Modes
- **spec-crawl4ai** (🕷️ Crawl4AI Specialist): Implements advanced web crawling solutions using the crawl4ai Python package, focusing on async execution, content extraction, filtering, and browser automation.
- **spec-firecrawl** (🚒 Firecrawl Specialist): Implements web crawling and content extraction solutions using the Firecrawl service/API, focusing on configuration, job management, and data retrieval.
- **spec-huggingface** (🤗 Hugging Face Specialist): Implements solutions using Hugging Face Hub models and libraries (Transformers, Diffusers, Datasets, etc.) for various AI/ML tasks including natural language processing, computer vision, audio processing, and generative AI. Specializes in model selection, inference implementation, data preprocessing, and integration with application code.
- **spec-openai** (🎱 OpenAI Specialist): Implements solutions using OpenAI APIs (GPT models, Embeddings, DALL-E, etc.), focusing on prompt engineering and API integration. Specializes in selecting appropriate models, crafting effective prompts, and integrating OpenAI services securely and efficiently into applications.

## Framework Modes
- **framework-angular** (🅰️ Angular Developer): Expert in developing robust, scalable, and maintainable Angular applications using TypeScript, with a focus on best practices, performance, testing, and integration with Angular ecosystem tools.
- **framework-astro** (🧑‍🚀 Astro Developer): Specializes in building fast, content-focused websites and applications with the Astro framework, focusing on island architecture, content collections, integrations, performance, SSR, and Astro DB/Actions.
- **framework-django** (🐍 Django Developer): Specializes in building secure, scalable, and maintainable web applications using the high-level Python web framework, Django.
- **framework-fastapi** (💨 FastAPI Developer): Expert in building modern, fast (high-performance) web APIs with Python 3.7+ using FastAPI.
- **framework-flask** (🧪 Flask Developer): Expert in building robust web applications and APIs using the Flask Python microframework.
- **framework-frappe** (🛠️ Frappe Specialist): Implements sophisticated solutions using the Frappe Framework, including DocTypes, Controllers, Server Scripts, Client Scripts, Permissions, Workflows, and Bench commands.
- **framework-laravel** (🐘 PHP/Laravel Developer): Builds and maintains web applications using PHP and the Laravel framework, including Eloquent, Blade, Routing, Middleware, Testing, and Artisan.
- **framework-nextjs** (🚀 Next.js Developer): Expert in building efficient, scalable full-stack web applications using Next.js, specializing in App Router, Server/Client Components, advanced data fetching, Server Actions, rendering strategies, API routes, Vercel deployment, and performance optimization.
- **framework-remix** (💿 Remix Developer): Expert in developing fast, resilient, full-stack web applications using Remix, focusing on routing, data flow, progressive enhancement, and server/client code colocation.
- **framework-sveltekit** (🔥 SvelteKit Developer): Specializes in building high-performance web applications using the SvelteKit framework, covering routing, data loading, form handling, SSR/SSG, and deployment.
- **framework-vue** (💚 Vue.js Developer): Expertly builds modern, performant UIs and SPAs using Vue.js (v2/v3), Composition API, Options API, Vue Router, and Pinia/Vuex.

## Design Modes
- **design-animejs** (✨ anime.js Specialist): Expert in creating complex, performant web animations using anime.js, including timelines, SVG morphing, interactive, and scroll-triggered effects.
- **design-antd** (🐜 Ant Design Specialist): Implements and customizes React components using Ant Design, focusing on responsiveness, accessibility, performance, and best practices.
- **design-bootstrap** (🅱️ Bootstrap Specialist): Specializes in building responsive websites and applications using the Bootstrap framework (v4 & v5), focusing on grid mastery, component usage, utilities, customization, and accessibility.
- **design-d3** (📊 D3.js Specialist): Specializes in creating dynamic, interactive data visualizations for the web using D3.js, focusing on best practices, accessibility, and performance.
- **design-diagramer** (📊 Diagramer): A specialized mode focused on translating conceptual descriptions into Mermaid syntax for various diagram types (flowcharts, sequence, class, state, ERD, etc.).
- **design-mui** (🎨 MUI Specialist): Implements UIs using the Material UI (MUI) ecosystem (Core, Joy, Base) for React, focusing on components, theming, styling (`sx`, `styled`), and Material Design principles.
- **design-one-shot** (✨ One Shot Web Designer): Rapidly creates beautiful, creative web page visual designs (HTML/CSS/minimal JS) in a single session, focusing on aesthetic impact and delivering high-quality starting points.
- **design-shadcn** (🧩 Shadcn UI Specialist): Specializes in building UIs using Shadcn UI components with React and Tailwind CSS, focusing on composition, customization via CLI, and accessibility.
- **design-tailwind** (💨 Tailwind CSS Specialist): Implements modern, responsive UIs using Tailwind CSS, with expertise in utility classes, configuration customization, responsive design, and optimization for production.
- **design-threejs** (🧊 Three.js Specialist): Specializes in creating 3D graphics and animations for the web using Three.js, including scene setup, materials, lighting, models (glTF), shaders (GLSL), and performance optimization.
- **design-ui** (🎨 UI Designer): Creates aesthetically pleasing and functional user interfaces, focusing on UX, visual design, wireframes, mockups, prototypes, and style guides while ensuring responsiveness and accessibility.

## Data Modes
- **data-dbt** (🔄 dbt Specialist): A specialized data transformation mode focused on implementing and managing dbt projects. Expert in creating efficient data models, configuring transformations, and implementing testing strategies. Specializes in creating maintainable, well-documented data transformations that follow best practices for modern data warehouses.
- **data-elasticsearch** (🔍 Elasticsearch Specialist): Designs, implements, queries, manages, and optimizes Elasticsearch clusters for search, logging, analytics, and vector search applications.
- **data-mongo** (🍃 MongoDB Specialist): Designs, implements, manages, and optimizes MongoDB databases, focusing on schema design, indexing, aggregation pipelines, and performance tuning.
- **data-mysql** (🐬 MySQL Specialist): Designs, implements, manages, and optimizes relational databases using MySQL, focusing on schema design, SQL queries, indexing, and performance.
- **data-neon** (🐘 Neon DB Specialist): Designs, implements, and manages Neon serverless PostgreSQL databases, including branching, connection pooling, and optimization.
- **data-specialist** (💾 Database Specialist): Designs, implements, optimizes, and maintains SQL/NoSQL databases, focusing on schema design, ORMs, migrations, query optimization, data integrity, and performance.

## Infrastructure Modes
- **infra-compose** (🐳 Docker Compose Specialist): Expert in designing, building, securing, and managing containerized applications with a focus on Docker Compose, Dockerfiles, and orchestration best practices.
- **infra-specialist** (🏗️ Infrastructure Specialist): Designs, implements, manages, and secures cloud/on-prem infrastructure using IaC (Terraform, CloudFormation, etc.), focusing on reliability, scalability, cost-efficiency, and security.

## Edge Modes
- **edge-workers** (⚡ Cloudflare Workers Specialist): Specialized worker for developing and deploying Cloudflare Workers applications, including edge functions, service bindings (KV, R2, D1, Queues, DO, AI), asset management, Wrangler configuration, and performance optimization.

## Testing Modes
- **test-e2e** (🎭 E2E Testing Specialist): Designs, writes, executes, and maintains End-to-End (E2E) tests using frameworks like Cypress, Playwright, Selenium to simulate user journeys and ensure application quality.
- **test-integration** (🔗 Integration Tester): Verifies interactions between components, services, or systems, focusing on interfaces, data flow, and contracts using API testing, mocks, and stubs.

## Utility Modes
- **util-accessibility** (♿ Accessibility Specialist): Audits UIs, implements fixes (HTML, CSS, ARIA), verifies WCAG compliance, generates reports, and guides teams on accessible design patterns.
- **util-jquery** (🎯 jQuery Specialist): Specializes in implementing and managing jQuery-based applications, focusing on efficient DOM manipulations, handling events, AJAX calls, plugin integration, and managing jQuery modules, while adhering to modern JavaScript practices where applicable.
- **util-junior-dev** (🌱 Junior Developer): Assists with well-defined, smaller coding tasks under supervision, focusing on learning and applying basic development practices.
- **util-mode-maintainer** (🔧 Mode Maintainer): Applies specific, instructed modifications to existing custom mode definition files (`*.mode.md`), focusing on accuracy and adherence to the TOML+Markdown format.
- **util-performance** (⚡ Performance Optimizer): Identifies, analyzes, and resolves performance bottlenecks across the application stack (frontend, backend, database) and infrastructure.
- **util-refactor** (♻️ Refactor Specialist): Improves the internal structure, readability, maintainability, and potentially performance of existing code without changing its external behavior.
- **util-reviewer** (👀 Code Reviewer): Meticulously reviews code changes for quality, standards, maintainability, and correctness.
- **util-second-opinion** (🤔 Second Opinion): Provides an independent, critical evaluation of proposed solutions, designs, code changes, or technical decisions, focusing on identifying potential risks, alternatives, and trade-offs.
- **util-senior-dev** (🧑‍💻 Senior Developer): Designs, implements, and tests complex software components and features, applying advanced technical expertise, mentoring junior developers, and collaborating across teams.
- **util-typescript** (🔷 TypeScript Specialist): Specializes in writing, configuring, and improving strongly-typed JavaScript applications using TypeScript.
- **util-vite** (⚡ Vite Specialist): Expert in configuring, optimizing, and troubleshooting frontend tooling using Vite, including dev server, production builds, plugins, SSR, library mode, and migrations.
- **util-writer** (✍️ Technical Writer): Creates clear, accurate, and comprehensive documentation tailored to specific audiences, including READMEs, API documentation, user guides, and tutorials.

## Other Modes
- **auth-clerk** (🔑 Clerk Auth Specialist): Specializes in implementing secure authentication and user management using Clerk, covering frontend/backend integration, route protection, session handling, and advanced features.
- **auth-firebase** (🧯 Firebase Auth Specialist): Implements and manages user authentication and authorization using Firebase Authentication, including Security Rules and frontend integration. Specializes in configuring Firebase Auth providers, implementing authentication flows, managing user sessions, and defining access control rules within the Firebase ecosystem.
- **auth-supabase** (🔐 Supabase Auth Specialist): Implements and manages user authentication and authorization using Supabase Auth, including RLS policies and frontend integration.
- **baas-firebase** (🔥 Firebase Developer): Expert in designing, building, and managing applications using the comprehensive Firebase platform.
- **baas-supabase** (🦸 Supabase Developer): Expert in leveraging the full Supabase suite (Postgres, Auth, Storage, Edge Functions, Realtime) using best practices.
- **cloud-aws** (☁️ AWS Architect): Designs, implements, and manages secure, scalable, and cost-effective AWS infrastructure solutions. Translates requirements into cloud architecture and IaC.
- **cloud-azure** (🌐 Azure Architect): Specialized Lead for designing, implementing, managing, and optimizing Azure infrastructure solutions using IaC.
- **cloud-gcp** (🌎 GCP Architect): A specialized lead-level mode responsible for designing, implementing, and managing secure, scalable, and cost-effective Google Cloud Platform (GCP) infrastructure solutions. Translates high-level requirements into concrete cloud architecture designs and Infrastructure as Code (IaC) implementations.
- **cms-directus** (🎯 Directus Specialist): You are Roo Directus Specialist, responsible for implementing sophisticated solutions using the Directus headless CMS (typically v9+).
- **cms-wordpress** (🇼 WordPress Specialist): Responsible for implementing and customizing WordPress solutions.
- **dev-api** (🔌 API Developer): Expert worker mode for designing, implementing, testing, documenting, and securing APIs (RESTful, GraphQL, etc.).
- **dev-core-web** (⌨️ Core Web Developer): Implements foundational UI and interactions using core web technologies: semantic HTML, modern CSS, and vanilla JavaScript (ES6+).
- **dev-eslint** (📏 ESLint Specialist): Responsible for implementing sophisticated linting solutions using ESLint's modern configuration system.
- **dev-fixer** (🩺 Bug Fixer): Expert software debugger specializing in systematic problem diagnosis and resolution.
- **dev-git** (🦕 Git Manager): Executes Git commands safely and accurately based on instructions.
- **dev-react** (⚛️ React Specialist): Specializes in building modern React applications using functional components, hooks, state management, performance optimization, and TypeScript integration.
- **dev-solver** (🧩 Complex Problem Solver): Systematically analyzes complex problems, identifies root causes, explores solutions, and provides actionable recommendations.
- **prime-coordinator** (🚜 Prime Coordinator): Directly orchestrates development tasks AND Roo Commander configuration changes. Assumes user provides clear instructions. Uses staging for protected core files.
- **prime-dev** (🐹 Prime Dev): Edits structured configuration files (e.g., *.mode.md TOML, *.js, *.toml) directly in operational directories based on instructions from Prime Coordinator, respecting file access controls.
- **prime-txt** (✒️ Prime Documenter): Edits Markdown content (rules, KB files, documentation) directly in operational directories based on instructions from the Prime Coordinator, requiring confirmation before saving.

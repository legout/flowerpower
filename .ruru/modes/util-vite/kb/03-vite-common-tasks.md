+++
id = "vite-common-tasks"
title = "Vite: Common Tasks & CLI Usage"
context_type = "knowledge"
scope = "Practical application and command-line interaction"
target_audience = ["util-vite"]
granularity = "how-to"
status = "active"
last_updated = "2025-04-19"
tags = ["vite", "tasks", "cli", "commands", "dev", "build", "preview", "plugins", "env", "ssr", "library"]
target_mode_slug = "util-vite"
+++

# Vite: Common Tasks & CLI Usage

This document covers common tasks performed by the `util-vite` mode and the associated Vite CLI commands.

## Core CLI Commands

These are typically run via npm/yarn/pnpm scripts defined in `package.json`:

*   **`vite` or `vite dev` or `vite serve`**:
    *   Starts the development server.
    *   Enables native ESM serving, HMR, and applies configurations from `vite.config.js/ts`.
    *   Example `package.json` script: `"dev": "vite"`

*   **`vite build`**:
    *   Creates a production build of the application.
    *   Uses Rollup under the hood for bundling, minification, and optimization.
    *   Outputs files to the directory specified by `build.outDir` (default: `dist`).
    *   Example `package.json` script: `"build": "vite build"`

*   **`vite preview`**:
    *   Locally serves the production build created by `vite build`.
    *   Useful for testing the production build before deployment.
    *   **Important:** This is *not* intended as a production server. Use a proper static file server or platform integration for deployment.
    *   Example `package.json` script: `"preview": "vite preview"`

## Common Configuration Tasks

These tasks often involve modifying `vite.config.js/ts`:

1.  **Adding/Configuring Plugins:**
    *   Install the plugin (`npm install -D some-vite-plugin`).
    *   Import the plugin in `vite.config.js/ts`.
    *   Add the plugin instance (often a function call) to the `plugins` array.
    *   Pass any necessary options to the plugin function.

2.  **Setting up Path Aliases:**
    *   Modify the `resolve.alias` option.
    *   Ensure paths are correctly resolved (using `path.resolve` if needed).

3.  **Managing Environment Variables:**
    *   Create `.env` files (e.g., `.env`, `.env.development`, `.env.production`).
    *   Define variables prefixed with `VITE_` (or the custom `envPrefix`).
    *   Access variables in client code via `import.meta.env.VITE_VARIABLE_NAME`.
    *   Use `loadEnv` in `vite.config.js/ts` for accessing variables during configuration.

4.  **Configuring CSS Preprocessors:**
    *   Install the preprocessor (`npm install -D sass`).
    *   Configure options under `css.preprocessorOptions` if needed (e.g., global variables).

5.  **Optimizing Production Builds:**
    *   Adjust `build.minify` (e.g., try `'terser'`).
    *   Configure `build.rollupOptions` for advanced code splitting, output formatting, etc.
    *   Analyze bundle size using plugins like `rollup-plugin-visualizer`.

6.  **Setting up SSR (Server-Side Rendering):**
    *   More complex task involving specific framework integrations (e.g., `vite-plugin-ssr`, Next.js, Nuxt 3).
    *   Requires careful configuration of server entry points, client hydration, and potentially `build.ssr` options. Often involves collaboration with framework specialists.

7.  **Configuring Library Mode:**
    *   Use the `build.lib` option to specify the entry point and output formats (e.g., `es`, `umd`).
    *   Often involves configuring `build.rollupOptions.external` to avoid bundling dependencies.

## Troubleshooting

*   **Dependency Issues:** Run `vite --force` or delete `node_modules/.vite` to clear the dependency cache. Check `optimizeDeps` config.
*   **HMR Not Working:** Verify plugin configuration (e.g., `@vitejs/plugin-react` setup), check browser console for errors, ensure CSS/JS is correctly imported.
*   **Build Errors:** Examine the terminal output carefully. Errors often originate from Rollup or specific plugins. Check configuration syntax.
*   **Type Errors:** Ensure `tsconfig.json` is correctly configured, especially `compilerOptions.types` including `"vite/client"`.
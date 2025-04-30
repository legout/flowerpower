+++
id = "vite-config-options"
title = "Vite: Configuration (`vite.config.js/ts`)"
context_type = "knowledge"
scope = "Understanding and modifying Vite configuration files"
target_audience = ["util-vite"]
granularity = "reference"
status = "active"
last_updated = "2025-04-19"
tags = ["vite", "config", "vite.config.js", "vite.config.ts", "configuration", "options", "plugins", "resolve", "build", "server"]
target_mode_slug = "util-vite"
+++

# Vite: Configuration (`vite.config.js/ts`)

Vite is configured using a `vite.config.js` or `vite.config.ts` file located in the project root. This file exports a configuration object or a function that returns a configuration object.

## Basic Structure

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react' // Example plugin

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()], // Array of plugins
  // Other configuration options...
})
```

```javascript
// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue' // Example plugin

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  // Other configuration options...
})
```

## Key Configuration Sections

The `util-vite` mode frequently interacts with these configuration sections:

1.  **`plugins`**:
    *   An array of Vite or Rollup plugins to extend Vite's functionality.
    *   Examples: `@vitejs/plugin-react`, `@vitejs/plugin-vue`, `vite-plugin-svgr`.
    *   Order often matters.

2.  **`resolve`**:
    *   Controls how modules are resolved.
    *   **`alias`**: Create import aliases for easier path management (e.g., `@/` mapping to `src/`).
        ```typescript
        resolve: {
          alias: {
            '@': '/src', // Or path.resolve(__dirname, 'src') using Node's path module
          },
        },
        ```
    *   **`extensions`**: Array of file extensions to try when resolving imports without extensions.

3.  **`server`**:
    *   Options for the development server.
    *   **`port`**: Specify the server port.
    *   **`host`**: Set to `true` or `'0.0.0.0'` to expose the server on the network.
    *   **`open`**: Automatically open the app in the browser on server start.
    *   **`proxy`**: Configure custom proxy rules for API requests during development (avoids CORS issues).
    *   **`hmr`**: Fine-tune Hot Module Replacement behavior.

4.  **`build`**:
    *   Options for the production build (uses Rollup).
    *   **`outDir`**: Specify the output directory (default: `dist`).
    *   **`sourcemap`**: Generate source maps for production (`true`, `false`, `'inline'`, `'hidden'`).
    *   **`minify`**: Specify the minifier (`'esbuild'`, `'terser'`, `false`). `esbuild` is faster, `terser` can sometimes produce smaller bundles.
    *   **`rollupOptions`**: Directly pass options to the underlying Rollup bundler for advanced customization.
    *   **`lib`**: Configure library mode for building reusable libraries.

5.  **`css`**:
    *   CSS-related options.
    *   **`preprocessorOptions`**: Pass options to CSS preprocessors (Sass, Less, Stylus).
    *   **`modules`**: Configure CSS Modules behavior.

6.  **`define`**:
    *   Define global constants that will be statically replaced during build time. Useful for environment variables accessible in client-side code (though `.env` files are generally preferred).
    *   Example: `define: { __APP_VERSION__: JSON.stringify('1.0.0') }`

7.  **`envPrefix`**:
    *   Prefix for environment variables exposed to client-side code via `import.meta.env` (default: `VITE_`).

## Conditional Configuration

The `defineConfig` helper provides intellisense. You can also export a function to access the command (`serve` or `build`) and mode (e.g., `development`, `production`) for conditional logic:

```typescript
// vite.config.ts
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ command, mode }) => {
  // Load env file based on `mode` in the current working directory.
  // Set the third parameter to '' to load all env regardless of the `VITE_` prefix.
  const env = loadEnv(mode, process.cwd(), '')
  
  if (command === 'serve') {
    // Dev-specific config
    return {
      // ...
    }
  } else {
    // Build-specific config
    return {
      // ...
      define: {
        __APP_ENV__: JSON.stringify(env.APP_ENV),
      },
    }
  }
})
```

Consult the [official Vite Config Reference](https://vitejs.dev/config/) for a complete list of options.
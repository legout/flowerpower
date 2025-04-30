# Firebase: Hosting Configuration (`firebase.json`)

Configuring Firebase Hosting for deploying web apps, static assets, and integrating with Cloud Functions.

## Core Concept

Firebase Hosting provides fast, secure, and reliable hosting for web applications (SPAs, static sites) and static assets. Configuration is primarily managed through the `firebase.json` file in your project root.

## `firebase.json` Structure

```json
{
  "hosting": {
    // --- Single Site Configuration ---
    // "public": "dist", // (Required) Directory containing files to deploy (e.g., your build output)
    // "ignore": [ // Files/patterns to ignore during deployment
    //   "firebase.json",
    //   "**/.*", // Ignore hidden files
    //   "**/node_modules/**"
    // ],
    // "rewrites": [ // Rewrite URLs to specific destinations
    //   {
    //     "source": "**", // Match all paths not matching static files
    //     "destination": "/index.html" // Serve index.html (for SPAs)
    //   },
    //   {
    //     "source": "/api/**", // Match paths starting with /api/
    //     "function": "api" // Rewrite to the 'api' Cloud Function (Node.js)
    //   },
    //   {
    //     "source": "/app/**",
    //     "function": { // Rewrite to Python Cloud Function (requires function name and region)
    //       "functionId": "myPythonApp",
    //       "region": "us-central1", // Specify region if not default
    //       "pinTag": true // Optional: Pin to latest deployed version tagged 'live'
    //     }
    //   }
    // ],
    // "redirects": [ // Configure HTTP redirects
    //   {
    //     "source": "/old-path",
    //     "destination": "/new-path",
    //     "type": 301 // Permanent redirect
    //   }
    // ],
    // "headers": [ // Set custom HTTP headers
    //   {
    //     "source": "**/*.@(jpg|jpeg|gif|png|svg)", // Match image files
    //     "headers": [
    //       {
    //         "key": "Cache-Control",
    //         "value": "public, max-age=7200" // Cache images for 2 hours
    //       }
    //     ]
    //   },
    //   {
    //     "source": "/fonts/**",
    //     "headers": [ { "key": "Access-Control-Allow-Origin", "value": "*" } ]
    //   }
    // ],
    // "cleanUrls": true, // Remove .html extensions from URLs
    // "trailingSlash": false, // Remove trailing slashes from URLs (true adds them)
    // "i18n": { // Internationalization configuration
    //   "root": "/localized-files" // Directory containing language subfolders (e.g., /en, /fr)
    // }

    // --- Multi-Site Configuration (Alternative to single site) ---
    // "sites": {
    //   "my-main-app": { // Target name (defined via `firebase target:apply hosting ...`)
    //     "target": "my-main-app",
    //     "public": "dist/main-app",
    //     "rewrites": [...]
    //   },
    //   "my-blog": {
    //     "target": "my-blog",
    //     "public": "dist/blog",
    //     "rewrites": [...]
    //   }
    // }

    // --- Default Configuration (Applied if not using multi-site or if site doesn't override) ---
    "public": "public", // Default public directory if not specified elsewhere
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
  // Other Firebase service configurations (e.g., "functions", "firestore", "storage")
  // "functions": {
  //   "source": "functions",
  //   "runtime": "nodejs18" // Specify runtime
  // },
  // "firestore": {
  //   "rules": "firestore.rules",
  //   "indexes": "firestore.indexes.json"
  // },
  // "storage": {
  //   "rules": "storage.rules"
  // }
}
```

## Key Hosting Configuration Options

*   **`public` (Required):** The directory (relative to `firebase.json`) containing the static assets to be deployed. This is typically the output directory of your frontend build process (e.g., `dist`, `build`, `public`).
*   **`ignore`:** An array of glob patterns specifying files or directories that should *not* be deployed. Useful for excluding source files, node_modules, configuration files, etc.
*   **`rewrites`:** Defines rules for rewriting URLs. Crucial for:
    *   **Single Page Applications (SPAs):** Rewriting all non-file paths to `/index.html` to enable client-side routing. `{"source": "**", "destination": "/index.html"}` is the standard pattern.
    *   **Serving Cloud Functions:** Rewriting specific paths (e.g., `/api/**`) to an HTTPS Cloud Function. Allows you to serve your API from the same domain as your frontend. Specify `"function": "functionName"` (for Node.js) or `"function": {"functionId": "pyFuncName", "region": "..."}` (for Python).
*   **`redirects`:** Configures HTTP 301 (Permanent) or 302 (Temporary) redirects from one URL path to another.
*   **`headers`:** Allows setting custom HTTP headers (e.g., `Cache-Control`, `Access-Control-Allow-Origin`) for specific file patterns. Useful for caching policies and CORS.
*   **`cleanUrls`:** If `true`, automatically removes `.html` extensions from URLs (e.g., `/about.html` becomes `/about`).
*   **`trailingSlash`:** If `false` (default), removes trailing slashes. If `true`, adds trailing slashes to directory indexes.
*   **`i18n`:** Configuration for internationalization, specifying a root directory containing language-specific subdirectories.
*   **`sites` (Multi-site):** Allows configuring multiple distinct hosting sites within the same Firebase project. Requires setting up deployment targets using `firebase target:apply hosting <target_name> <resource_name>`. Deploy using `firebase deploy --only hosting:<target_name>`.

## Deployment

*   **Command:** `firebase deploy --only hosting` (or specific target: `firebase deploy --only hosting:my-main-app`).
*   **Process:** The Firebase CLI reads `firebase.json`, uploads files from the specified `public` directory (respecting `ignore` rules), and applies the configured rewrites, redirects, and headers.
*   **Atomic Deploys:** Each deployment creates a new version. Firebase Hosting ensures atomic deploys, meaning users only see the new version once it's fully uploaded and ready. Rollbacks to previous versions are easy via the Firebase Console or CLI.

Configure `firebase.json` carefully to ensure your web app is served correctly, SPAs function as expected, and Cloud Functions are properly integrated.

*(Refer to the official Firebase Hosting Configuration documentation: https://firebase.google.com/docs/hosting/full-config)*
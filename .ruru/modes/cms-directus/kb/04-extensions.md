# Directus: Extensions (Hooks, Endpoints, Setup)

Directus is highly extensible via custom code packages, typically written in Node.js/TypeScript for backend logic and Vue.js for frontend UI components.

## 1. Extension Types Overview

*   **API Extensions (Backend - Node.js/TypeScript):**
    *   **Hooks:** Execute custom code in response to specific events (actions, filters, schedules, initialization). Used for validation, data augmentation, side effects (notifications, external API calls), custom logic.
        *   *Action Hooks:* Run *after* an action completes (e.g., `items.create`, `auth.login`). For side effects.
        *   *Filter Hooks:* Run *during* an action to modify data (e.g., `items.create.before`, `items.read.after`). Must return the payload.
        *   *Init Hooks:* Run during server initialization (e.g., `routes.register`).
        *   *Schedule Hooks:* Run on a CRON schedule.
    *   **Endpoints:** Add custom REST API routes (e.g., `/my-custom-route/process`) for specialized business logic, integrations, or complex data aggregation.
*   **App Extensions (Frontend - Vue.js):** Customize the Directus Data Studio UI.
    *   **Interfaces:** Custom field input components.
    *   **Displays:** Custom field rendering in list views.
    *   **Layouts:** Custom collection browsing views (e.g., Kanban, Calendar).
    *   **Modules:** Entirely new sections/pages in the Admin App navigation.

## 2. Extension Setup & Development Workflow

1.  **Initialize:** Use `npx create-directus-extension` outside your main Directus project to scaffold an extension package (choose type, language). This creates `src/index.ts`, `package.json`, `tsconfig.json`, etc.
2.  **Install Dependencies:** `cd` into the extension directory and run `npm install` or `yarn install`.
3.  **Develop:** Write extension code in `src/`.
4.  **Build (Watch Mode):** Run `npm run dev` or `yarn dev` in the extension directory. This watches for changes and rebuilds the output (usually `dist/index.js`).
5.  **Link to Local Directus:** Make the `dist/index.js` accessible to your local Directus instance.
    *   **Symlinking (Recommended):** In your Directus project's `extensions/{type}/{extension-name}/` directory, create a symbolic link pointing to the `dist/index.js` of your extension package.
        ```bash
        # Example for a hook named 'my-hook' on macOS/Linux
        # cd /path/to/directus-project/extensions/hooks
        # mkdir my-hook
        # ln -s /path/to/extension-package/my-hook/dist/index.js my-hook/index.js
        ```
    *   **Copying:** Manually copy `dist/index.js` after each build.
6.  **Run Directus:** Start your local Directus server (`npm run dev`). It should load the extension. Check logs.
7.  **Test & Iterate:** Test functionality, make code changes, let it rebuild, test again. Restart Directus server if needed.

## 3. Implementing Hooks

*   **Structure (`index.ts`):** Export a default function using `defineHook` from `@directus/extensions-sdk`. Register handlers using `filter`, `action`, or `schedule`.
    ```typescript
    import { defineHook } from '@directus/extensions-sdk';
    import { InvalidPayloadException } from '@directus/errors';

    export default defineHook(({ filter, action, schedule }, { services, getSchema }) => {
      // Filter Hook (runs during action, modifies data)
      filter('items.create.before', (payload, meta, { collection }) => {
        if (collection === 'articles' && payload.title) {
          payload.title = payload.title.toUpperCase(); // Modify payload
        }
        return payload; // MUST return payload
      });

      // Action Hook (runs after action, for side effects)
      action('items.create.after', (output, { collection, key }) => {
        if (collection === 'articles') {
          console.log(`Article created: ${key}`);
          // Trigger notification, call external API, etc.
        }
      });

      // Schedule Hook (runs on cron schedule)
      schedule('0 * * * *', async () => { // Every hour
        console.log('Running hourly task...');
      });
    });
    ```
*   **Handler Context:** Handlers receive arguments like `payload`, `output`, `meta`, `key(s)`, and a `context` object containing `services`, `getSchema`, `database`, `logger`, `accountability`.
*   **Error Handling:** Throw Directus errors (e.g., `InvalidPayloadException`) in `filter` or `before` action hooks to block operations. Use `try...catch` in `after` action or `schedule` hooks.
*   **Performance:** Keep hook logic efficient. Offload long tasks.

## 4. Implementing Endpoints

*   **Structure (`index.ts`):** Export a default function using `defineEndpoint` from `@directus/extensions-sdk`. Define routes using the Express-like `router` object.
    ```typescript
    import { defineEndpoint } from '@directus/extensions-sdk';
    import { ForbiddenException } from '@directus/errors';

    export default defineEndpoint((router, { services, getSchema, logger }) => {
      const { ItemsService } = services;

      router.get('/summary', async (req, res, next) => {
        // Check auth via req.accountability
        if (!req.accountability?.user) {
          return next(new ForbiddenException());
        }
        try {
          const schema = await getSchema();
          const articlesService = new ItemsService('articles', { schema, accountability: req.accountability });
          const count = await articlesService.readByQuery({ aggregate: { count: '*' } });
          res.json({ totalArticles: count[0]?.count ?? 0 });
        } catch (error) {
          logger.error(error);
          next(error); // Pass error to Directus handler
        }
      });

      router.post('/process', (req, res, next) => {
        // Handle POST request logic
        const data = req.body;
        logger.info('Processing data:', data);
        // ... perform action ...
        res.status(202).json({ message: 'Processing started' });
      });
    });
    ```
*   **Handlers:** Receive `req`, `res`, `next` arguments. Access `req.body`, `req.query`, `req.params`, and `req.accountability`.
*   **Context:** Use `services`, `getSchema`, `database`, `logger` from the context object. Instantiate services with `schema` and `accountability`.
*   **Error Handling:** Use `try...catch` and pass errors to `next(error)` for consistent JSON error responses. Throw Directus errors for specific HTTP statuses.
*   **Access:** Endpoint routes are typically accessed via `/your-base-path/{endpoint-name}/your-route`.

## 5. Building & Deployment

*   **Build:** Run `npm run build` or `yarn build` in the extension directory.
*   **Deploy:** Copy the generated `dist/index.js` (and any other assets for App extensions) to the production Directus instance's `extensions/{type}/{name}/` directory. Restart Directus.

*(Refer to the official Directus Extensions documentation.)*
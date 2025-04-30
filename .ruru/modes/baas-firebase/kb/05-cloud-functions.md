# Firebase: Cloud Functions (Node.js & Python)

Developing serverless backend logic using Cloud Functions for Firebase with Node.js, TypeScript, and Python.

## Core Concept

Cloud Functions allow you to run backend code in a managed environment (Node.js or Python) without provisioning or managing servers. You write functions that respond to specific triggers (HTTP requests, Firebase events, etc.). Firebase handles the scaling and execution environment.

## Trigger Types

1.  **HTTPS Triggers:**
    *   **`onRequest` (HTTP Functions):**
        *   **Trigger:** Standard HTTP requests (GET, POST, PUT, DELETE, etc.) to a unique URL provided by Firebase upon deployment.
        *   **Use Case:** Building REST APIs, webhooks, serving dynamic HTML.
        *   **Handler Signature (Node.js):** Receives `request` (Express.js-like Request object) and `response` (Express.js-like Response object).
        *   **Handler Signature (Python):** Receives a Flask Request object. Must return a Flask Response object or compatible value.
    *   **`onCall` (Callable Functions):**
        *   **Trigger:** Direct calls from your client app using the Firebase client SDKs (`https://firebase.google.com/docs/functions/callable`).
        *   **Use Case:** RPC-style calls from your frontend where authentication context and data validation are automatically handled.
        *   **Handler Signature (Node.js):** Receives `data` (deserialized data sent from client) and `context` (includes `context.auth` with user info if authenticated). Must return a JSON-serializable object or a Promise resolving to one.
        *   **Handler Signature (Python):** Receives a `CallableRequest` object containing `data` and `auth`. Must return a JSON-serializable object.
        *   **Benefits:** Automatically deserializes request body, validates auth tokens, handles CORS. Simpler client-side invocation compared to standard HTTPS functions.

2.  **Background Triggers (Event-Driven):**
    *   Run in response to events happening in other Firebase or Google Cloud services.
    *   **Authentication Triggers (`functions.auth` / `auth_fn`):**
        *   `user().onCreate()` / `@auth_fn.on_user_created()`: Triggered when a new Firebase Auth user is created.
        *   `user().onDelete()` / `@auth_fn.on_user_deleted()`: Triggered when a Firebase Auth user is deleted.
        *   **Use Case:** Create user profile in Firestore, send welcome email, clean up user data.
        *   **Handler Signature:** Receives `user` (UserRecord object).
    *   **Firestore Triggers (`functions.firestore` / `firestore_fn`):**
        *   `document().onCreate()` / `@firestore_fn.on_document_created()`: Triggered when a document is created.
        *   `document().onUpdate()` / `@firestore_fn.on_document_updated()`: Triggered when a document is updated.
        *   `document().onDelete()` / `@firestore_fn.on_document_deleted()`: Triggered when a document is deleted.
        *   `document().onWrite()` / `@firestore_fn.on_document_written()`: Triggered on create, update, or delete.
        *   **Path Specification:** Use wildcards (`{userId}`, `{documentId}`) to specify which documents trigger the function (e.g., `functions.firestore.document('users/{userId}')`).
        *   **Use Case:** Denormalize data, aggregate values, send notifications on data changes, enforce complex validation.
        *   **Handler Signature:** Receives `change` (for `onUpdate`/`onWrite`, has `before` and `after` snapshots) or `snap` (for `onCreate`/`onDelete`), and `context` (includes event ID, timestamp, path parameters). Python uses `firestore_fn.Event[firestore_fn.Change]`.
    *   **Cloud Storage Triggers (`functions.storage` / `storage_fn`):**
        *   `object().onArchive()` / `@storage_fn.on_object_archived()`: Triggered when an object is archived (versioning enabled).
        *   `object().onDelete()` / `@storage_fn.on_object_deleted()`: Triggered when an object is permanently deleted.
        *   `object().onFinalize()` / `@storage_fn.on_object_finalized()`: Triggered when a new object is successfully created/uploaded (including overwrites). **(Most common)**.
        *   `object().onMetadataUpdate()` / `@storage_fn.on_object_metadata_updated()`: Triggered when an object's metadata changes.
        *   **Bucket Specification:** Can target the default bucket or a specific one (`functions.storage.bucket('my-bucket').object()`).
        *   **Use Case:** Generate image thumbnails, process uploaded files, update Firestore with file metadata.
        *   **Handler Signature:** Receives `object` (Storage Object metadata) and `context`.
    *   **Pub/Sub Triggers (`functions.pubsub` / `pubsub_fn`):**
        *   `topic().onPublish()` / `@pubsub_fn.on_message_published()`: Triggered when a message is published to a Google Cloud Pub/Sub topic.
        *   **Use Case:** Decoupled event handling, processing asynchronous tasks.
        *   **Handler Signature:** Receives `message` (Pub/Sub message object) and `context`.
    *   **Scheduled Triggers (`functions.pubsub.schedule().onRun()` / `@scheduler_fn.on_schedule()`):**
        *   **Trigger:** Runs on a defined schedule (using App Engine cron syntax).
        *   **Use Case:** Recurring cleanup tasks, generating reports, sending scheduled notifications.
        *   **Handler Signature:** Receives `context`.

## Choosing Triggers

*   Use **HTTPS `onRequest`** for standard web APIs or webhooks.
*   Use **HTTPS `onCall`** for direct, authenticated calls from your client app.
*   Use **Background Triggers** for reacting to events within Firebase/GCP services automatically.
*   Use **Scheduled Triggers** for recurring tasks.

## Setup & Development (Node.js / TypeScript)

1.  **Initialize:** `firebase init functions`, choose TypeScript/JavaScript.
2.  **Install Dependencies:** `cd functions`, `npm install firebase-functions firebase-admin`.
3.  **Structure:**
    ```
    functions/
    ├── src/index.ts    # Main functions file (TS)
    ├── lib/            # Compiled JS output
    ├── node_modules/
    ├── package.json
    └── tsconfig.json
    ```
4.  **Code (`src/index.ts`):**
    ```typescript
    import * as functions from "firebase-functions";
    import * as admin from "firebase-admin";
    admin.initializeApp();
    const db = admin.firestore();

    // Export functions (HTTPS, Background Triggers)
    export const helloWorld = functions.https.onRequest((req, res) => { /*...*/ });
    export const addMessage = functions.https.onCall((data, context) => { /*...*/ });
    export const sendWelcomeEmail = functions.firestore.document('users/{userId}').onCreate(async (snap, context) => { /*...*/ });
    ```
5.  **Compilation:** `firebase deploy` or `npm run build` compiles TS to JS in `lib/`.

## Setup & Development (Python)

1.  **Initialize:** `firebase init functions`, choose Python.
2.  **Install Dependencies:** CLI creates `venv` and installs `firebase-functions`, `firebase-admin` from `requirements.txt`. Activate (`source venv/bin/activate`), install others (`pip install ...`).
3.  **Structure:**
    ```
    functions/
    ├── main.py         # Main functions file
    ├── requirements.txt
    └── venv/
    ```
4.  **Code (`main.py`):**
    ```python
    from firebase_functions import options, https_fn, firestore_fn, auth_fn # etc.
    from firebase_admin import initialize_app, firestore
    initialize_app()
    options.set_global_options(region=options.SupportedRegion.EUROPE_WEST1) # Optional
    db = firestore.client()

    # Define functions with decorators
    @https_fn.on_request()
    def hello_world(req: https_fn.Request) -> https_fn.Response: # ...
        return https_fn.Response("Hello!")

    @https_fn.on_call()
    def add_message(req: https_fn.CallableRequest) -> dict: # ...
        # Check req.auth, req.data
        return {"result": "OK"}

    @firestore_fn.on_document_created(document="users/{userId}")
    def send_welcome_email(event: firestore_fn.Event[firestore_fn.Change]) -> None: # ...
        user_id = event.params['userId']
        # ...
    ```

## Firebase Admin SDK

*   **Purpose:** Allows backend code (Cloud Functions) to interact with Firebase services with **full administrative privileges**, bypassing security rules.
*   **Initialization:** `admin.initializeApp()` (Node.js) / `initialize_app()` (Python) - usually once.
*   **Usage:** Access services like `admin.firestore()`, `admin.auth()`, `admin.storage()` (Node.js) or `firestore.client()`, `auth`, `storage` (Python). API differs slightly from client SDKs.

## Deployment

*   **Command:** `firebase deploy --only functions`.
*   **Process:** Deploys compiled JS (Node.js/TS) or Python code with dependencies.

## Local Development & Testing (Emulator Suite)

*   **Command:** `firebase emulators:start --only functions,firestore,auth` (include relevant emulators).
*   **Benefits:** Test locally without deploying, faster iteration, no costs. Trigger background functions via emulator interactions. Call HTTPS functions via local URL.
*   **Admin SDK Connection:** Automatically connects to other running emulators when started via `firebase emulators:start`.

## Best Practices

*   **Idempotency:** Design background functions to be idempotent (safe to run multiple times with same input).
*   **Region:** Specify function regions (`functions.region(...)` or `@https_fn.on_request(region=...)`) for proximity/latency.
*   **Runtime Options:** Configure memory/timeout (`functions.runWith({...})` or decorator args like `memory=options.MemoryOption.MB_512`).
*   **Error Handling:** Implement robust error handling and logging (`functions.logger` / `print`). Raise `HttpsError` / `https_fn.HttpsError` for callable functions.
*   **Security:** Validate data, check authentication (`context.auth` / `req.auth`), be mindful of Admin SDK privileges.
*   **Dependencies:** Manage `package.json` / `requirements.txt` carefully.
*   **Cold Starts:** Be aware of latency. Keep functions focused. Consider minimum instances for critical functions (incurs cost).

*(Refer to the official Cloud Functions documentation: https://firebase.google.com/docs/functions)*
# Firebase: Firestore Security Rules

Securing your Firestore database using Firebase Security Rules.

## Core Concept

Firestore Security Rules define who has read and write access to your documents and collections, and how that access is granted. They live on Firebase servers and are automatically enforced for every request from mobile/web clients.

*   **Default Deny:** By default, all read and write access is denied. You must explicitly grant access through rules.
*   **Location:** Rules are defined in a `firestore.rules` file (or specified in `firebase.json`).
*   **Language:** Rules use a custom, JavaScript-like syntax.
*   **Enforcement:** Rules are **not** filters. They ensure that a given operation (read, write, delete) is allowed based on the rules, but they don't filter the data returned by queries. Client-side queries must still include appropriate `where()` clauses to fetch only data the user is allowed to see according to the rules.

## Basic Structure

```
rules_version = '2'; // Use the latest version

service cloud.firestore {
  match /databases/{database}/documents { // Matches all documents in the database

    // Rule for a specific collection
    match /users/{userId} {
      // Allow read access if the user is authenticated
      allow read: if request.auth != null;

      // Allow write (create, update, delete) only if the user is modifying their own document
      allow write: if request.auth != null && request.auth.uid == userId;

      // Granular create, update, delete
      // allow create: if request.auth != null && request.auth.uid == userId;
      // allow update: if request.auth != null && request.auth.uid == userId && /* additional conditions */;
      // allow delete: if request.auth != null && request.auth.uid == userId;
    }

    // Rule for another collection with different permissions
    match /posts/{postId} {
      // Allow anyone to read published posts
      allow read: if resource.data.status == 'published';

      // Allow authenticated users to create posts
      allow create: if request.auth != null &&
                       request.resource.data.authorId == request.auth.uid && // Ensure author is correct
                       request.resource.data.status == 'draft'; // New posts must be drafts

      // Allow author to update their own posts
      allow update: if request.auth != null &&
                       request.auth.uid == resource.data.authorId && // User is the author
                       isUpdateAllowed(request.resource.data, resource.data); // Use function for complex logic

      // Allow author to delete their own posts
      allow delete: if request.auth != null && request.auth.uid == resource.data.authorId;
    }

    // Recursive wildcard match for subcollections
    match /chats/{chatId}/messages/{messageId} {
        // Allow read/write if user is part of the chat (example assumes chat doc has 'members' array)
        allow read, write: if request.auth != null &&
                              get(/databases/$(database)/documents/chats/$(chatId)).data.members[request.auth.uid] == true;
                              // Or: request.auth.uid in get(...).data.members
    }

    // --- Helper Functions ---
    // Define reusable functions within the rules
    function isUpdateAllowed(newData, oldData) {
      // Example: Allow changing content and status, but not authorId or createdAt
      return newData.keys().hasOnly(['content', 'status', 'updatedAt']) &&
             newData.content is string && newData.content.size() < 10000 &&
             newData.status in ['draft', 'published'] &&
             newData.updatedAt == request.time; // Ensure timestamp is server time
    }
  }
}
```

## Key Components

*   **`service cloud.firestore`**: Specifies the service being configured.
*   **`match /databases/{database}/documents`**: Matches the database resource.
*   **`match /{collection}/{document=**}`**: Matches paths within your database.
    *   `{variable}`: Wildcard capturing a single path segment (e.g., `{userId}`).
    *   `{variable=**}`: Recursive wildcard capturing multiple path segments.
*   **`allow <methods>: if <condition>;`**: The core rule statement.
    *   **`<methods>`**: Comma-separated list of methods (`read`, `get`, `list`, `write`, `create`, `update`, `delete`).
        *   `read` = `get` + `list`
        *   `write` = `create` + `update` + `delete`
    *   **`<condition>`**: An expression that evaluates to `true` or `false`. Access request context, existing data, and helper functions.
*   **`request` Object:** Information about the incoming request.
    *   `request.auth`: Contains authentication information (if user is logged in).
        *   `request.auth.uid`: The user's unique ID.
        *   `request.auth.token`: Contains claims from the user's authentication token (e.g., email, custom claims).
    *   `request.method`: The method being requested (`get`, `list`, `create`, `update`, `delete`).
    *   `request.resource`: Data being written in `create` or `update` requests. Access using `request.resource.data.<field_name>`.
    *   `request.time`: The server timestamp of the request.
    *   `request.query`: Information about list queries (`limit`, `offset`, `orderBy`). **Cannot** be used for filtering data, only for validating query constraints.
*   **`resource` Object:** Represents the document *currently* stored in the database (available in `update`, `delete`, and `get` rules). Access using `resource.data.<field_name>`.
*   **Functions:**
    *   `get(/path/to/document)`: Reads another document within the same database. Use `$(variable)` to insert wildcard values. **Limited to 10 `get` calls per rule evaluation for single-document requests, 20 for queries.**
    *   `exists(/path/to/document)`: Checks if another document exists. **Limited calls apply.**
    *   Custom Functions: Define reusable logic using `function name(args) { return boolean_expression; }`.

## Testing Rules

*   **Emulator Suite:** Use the Firestore emulator (`firebase emulators:start`) for local testing.
*   **Rules Playground:** Available in the Firebase Console (Firestore Database -> Rules tab). Allows simulating read/write operations against your rules.
*   **Unit Testing:** Use the `@firebase/rules-unit-testing` library (JavaScript/TypeScript) to write automated tests for your security rules in isolation.

## Best Practices

*   **Start Secure:** Begin with default deny (`allow read, write: if false;`) and explicitly grant access.
*   **Least Privilege:** Grant only the permissions necessary.
*   **Validate Data:** Use rules to validate data structure, types, and values on write operations (`create`, `update`). Check `request.resource.data`.
*   **Secure by User:** Often, rules depend on `request.auth.uid` to ensure users only access their own data.
*   **Functions for Reusability:** Use functions for complex or repeated conditions.
*   **Test Thoroughly:** Use the Emulator, Playground, and unit tests to verify rules cover all scenarios.
*   **Monitor:** Use Firebase console monitoring for rule denials.

Security rules are critical for protecting your Firestore data from unauthorized access.

*(Refer to the official Firestore Security Rules documentation: https://firebase.google.com/docs/firestore/security/overview)*
# Firebase: Cloud Storage Security Rules

Securing access to files stored in Firebase Cloud Storage.

## Core Concept

Similar to Firestore, Cloud Storage uses Security Rules to control who can upload, download, update, or delete files. These rules live on Firebase servers and are enforced automatically for requests coming from Firebase client SDKs (Web, iOS, Android).

*   **Default Deny:** By default, all access is denied. You must explicitly grant permissions.
*   **Location:** Rules are defined in a `storage.rules` file (or specified in `firebase.json`).
*   **Structure:** Rules use a `match` structure similar to Firestore rules, but target storage buckets and file paths.

## Basic Structure

```
rules_version = '2'; // Use the latest version

// Targets your default storage bucket
service firebase.storage {
  // Matches the bucket name (use {bucket} for flexibility if needed)
  match /b/{bucket}/o { // 'o' signifies objects/files within the bucket

    // Example 1: Public read for files in a 'public' folder
    match /public/{allPaths=**} { // Recursive match for all files/folders under 'public'
      allow read: if true; // Anyone can read
      allow write: if request.auth != null; // Only authenticated users can write (upload/update/delete)
    }

    // Example 2: User-specific files (e.g., profile pictures)
    // Files stored like: /users/{userId}/profile.jpg
    match /users/{userId}/{fileName} {
      // Allow read access to anyone (e.g., for public profiles)
      allow read: if true;

      // Allow write access only to the authenticated user matching the {userId} path segment
      allow write: if request.auth != null && request.auth.uid == userId;

      // Granular write permissions
      // allow create, update: if request.auth != null && request.auth.uid == userId && request.resource.size < 5 * 1024 * 1024; // Limit upload size
      // allow delete: if request.auth != null && request.auth.uid == userId;
    }

    // Example 3: Validating uploads
    match /uploads/{userId}/{fileName} {
      allow read: if request.auth != null && request.auth.uid == userId; // Only owner can read uploads?

      // Allow create only for authenticated users, validating file type and size
      allow create: if request.auth != null &&
                       request.auth.uid == userId &&
                       request.resource.size < 10 * 1024 * 1024 && // Max 10 MB
                       request.resource.contentType.matches('image/.*'); // Allow only images
                       // request.resource.name.matches('.*\.png$'); // Allow only PNG files (less reliable than contentType)
    }

    // Example 4: Access based on Firestore data
    // Allow read if the user is a member of the project associated with the file
    match /projectFiles/{projectId}/{fileName} {
      allow read: if request.auth != null &&
                     exists(/databases/$(database)/documents/projects/$(projectId)/members/$(request.auth.uid));
                     // Or: get(...).data.members[request.auth.uid] == true
      allow write: if request.auth != null &&
                      get(/databases/$(database)/documents/projects/$(projectId)).data.ownerId == request.auth.uid; // Only project owner can write
    }

    // Default Deny (Implicit if no match allows access)
    // match /{allPaths=**} {
    //   allow read, write: if false;
    // }
  }
}
```

## Key Components

*   **`service firebase.storage`**: Specifies the service.
*   **`match /b/{bucket}/o`**: Matches all objects within a specific bucket. `{bucket}` is usually your default bucket ID.
*   **`match /path/to/{variable}/{allPaths=**}`**: Matches file paths.
    *   `{variable}`: Wildcard for a single path segment.
    *   `{allPaths=**}`: Recursive wildcard matching any path below.
*   **`allow <methods>: if <condition>;`**: Rule statement.
    *   **`<methods>`**: `read` (`get`, `list`), `write` (`create`, `update`, `delete`).
    *   **`<condition>`**: Expression evaluating to `true` or `false`.
*   **`request` Object:**
    *   `request.auth`: User authentication info (`uid`, `token` claims). `null` if not authenticated.
    *   `request.time`: Server timestamp.
    *   `request.path`: The full path of the file being accessed.
    *   `request.resource` (for `write` operations): Metadata about the file being uploaded/updated.
        *   `request.resource.size`: File size in bytes.
        *   `request.resource.contentType`: File MIME type (e.g., `image/jpeg`).
        *   `request.resource.name`: Full path of the file.
        *   `request.resource.metadata`: Custom metadata associated with the file.
*   **`resource` Object:** (for `read`, `update`, `delete`) Represents the *existing* file metadata in Storage. Access properties like `resource.size`, `resource.contentType`, `resource.name`, `resource.metadata`.
*   **Functions:**
    *   `get()` / `exists()`: Can be used to read Firestore documents to make authorization decisions based on database data (subject to read limits).

## Testing Rules

*   **Emulator Suite:** Use the Storage emulator (`firebase emulators:start`) for local testing of uploads, downloads, and rule enforcement.
*   **Rules Playground:** Available in the Firebase Console (Storage -> Rules tab). Simulate requests against your rules.
*   **Unit Testing:** Use the `@firebase/rules-unit-testing` library (JavaScript/TypeScript) for automated unit tests.

## Best Practices

*   **Default Deny:** Start with restrictive rules.
*   **Authenticate Writes:** Almost always require authentication (`request.auth != null`) for write operations.
*   **Validate Uploads:** Use `request.resource.size` and `request.resource.contentType` to validate uploads (size limits, allowed types). Don't rely solely on file extensions in the path.
*   **User-Specific Paths:** Structure paths to include user IDs (`/users/{userId}/...`) to easily write rules based on ownership.
*   **Separate Public/Private:** Use distinct top-level folders (e.g., `/public/`, `/users/`) with different access rules.
*   **Test Thoroughly:** Ensure rules correctly allow intended access and deny unintended access.

Cloud Storage rules are essential for protecting user files and controlling access to your storage bucket.

*(Refer to the official Cloud Storage Security Rules documentation: https://firebase.google.com/docs/storage/security)*
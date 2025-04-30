# Firebase: CLI Usage & Web SDK v9 (Modular)

Using the Firebase Command Line Interface (CLI) and the modern Web SDK (v9+).

## Part 1: Firebase CLI Usage

The Firebase CLI (`firebase`) is essential for managing projects, deploying, running emulators, and interacting with services from your terminal.

### Installation & Login

1.  **Installation:** `npm install -g firebase-tools`
2.  **Login:** `firebase login` (Use `--reauth` if needed). `firebase logout` to sign out.

### Project Management

*   **`firebase projects:list`**: List associated projects.
*   **`firebase use <project_id_or_alias>`**: Set active project for the directory.
    *   `firebase use --add`: Interactively select and alias a project (e.g., `default`, `production`). Aliases stored in `.firebaserc`.
*   **`.firebaserc` File:** Stores project aliases.
    ```json
    { "projects": { "default": "my-dev-id", "production": "my-prod-id" } }
    ```

### Initialization

*   **`firebase init`**: Initialize Firebase features (Firestore, Functions, Hosting, Storage, Emulators, etc.) in your project. Creates/updates `firebase.json` and other config files (`.rules`, etc.).

### Emulators (Local Development & Testing)

*   **`firebase emulators:start`**: Start local emulators based on `firebase.json`.
    *   **Flags:** `--only functions,firestore`, `--import=./data`, `--export-on-exit=./data`.
*   **Emulator UI:** Access via `http://localhost:4000` (default) to view data, logs, etc.
*   **Configuration (`firebase.json`):** Define emulator ports.
    ```json
    {
      "emulators": {
        "auth": { "port": 9099 },
        "functions": { "port": 5001 },
        "firestore": { "port": 8080 },
        // ... other emulators
        "ui": { "enabled": true, "port": 4000 }
      }
    }
    ```

### Deployment

*   **`firebase deploy`**: Deploys code/config based on `firebase.json`.
    *   **Flags:**
        *   `--only hosting`: Deploy only Hosting.
        *   `--only functions`: Deploy only Functions.
        *   `--only firestore:rules`, `--only storage:rules`: Deploy only rules.
        *   `--only hosting:<target_name>`: Deploy specific hosting target.
        *   `-P <project_id_or_alias>` or `--project <project_id_or_alias>`: Specify target project.
        *   `--message "Deployment message"`: Add deployment note.
*   **Hosting Channels:** `firebase hosting:channel:deploy <channel_id>` for preview deploys.

### Cloud Functions Specific

*   **`firebase functions:log`**: View logs for deployed functions.
*   **`firebase functions:config:set my_service.key="value"`**: Set environment config.
*   **`firebase functions:config:get`**: View config.
*   **`firebase functions:delete <functionName>`**: Delete deployed functions.

### Database Specific (Firestore)

*   **`firebase firestore:indexes`**: Manage composite indexes (`firestore.indexes.json`).
*   **`firebase firestore:delete [path]`**: Delete documents/collections (use with caution, add `--recursive` for collections).

### Hosting Specific

*   **`firebase hosting:disable`**: Disable Hosting.
*   **`firebase hosting:channel:create <channel_id>`**: Create preview channel.
*   **`firebase hosting:channel:list`**: List channels.

*(Refer to the official Firebase CLI Reference: https://firebase.google.com/docs/cli)*

---

## Part 2: Web SDK v9 (Modular)

Using the modern, tree-shakable Firebase Web SDK (version 9 and later).

### Core Concept: Modularity

The v9 SDK uses a modular, function-based approach (`firebase/app`, `firebase/auth`, etc.), contrasting with v8's namespaced, class-based style (`firebase.auth()`).

**Benefits:**
*   **Tree Shaking:** Reduces bundle size by removing unused code.
*   **Modern Syntax:** Aligns with current JavaScript patterns.

### Initialization

*   Import `initializeApp` from `firebase/app`.
*   Import `getService` functions (e.g., `getAuth`, `getFirestore`) from specific service modules.
*   Call `initializeApp` once.
*   Call `getService` functions, passing the initialized `app`.

```javascript
// src/firebase.js
import { initializeApp } from 'firebase/app';
import { getAuth, connectAuthEmulator } from 'firebase/auth'; // Import connect function too
import { getFirestore, connectFirestoreEmulator } from 'firebase/firestore';
import { getStorage, connectStorageEmulator } from 'firebase/storage';

const firebaseConfig = { /* ... your config ... */ };
const app = initializeApp(firebaseConfig);

const auth = getAuth(app);
const db = getFirestore(app);
const storage = getStorage(app);

// Connect to Emulators if running locally
if (window.location.hostname === "localhost") {
  console.log("Connecting to Firebase Emulators...");
  connectAuthEmulator(auth, "http://localhost:9099");
  connectFirestoreEmulator(db, 'localhost', 8080);
  connectStorageEmulator(storage, 'localhost', 9199);
  // connectFunctionsEmulator(functions, "localhost", 5001); // If using callable functions
}

export { auth, db, storage };
```

### Using Service Functions

*   Import specific functions directly (e.g., `import { collection, addDoc } from 'firebase/firestore';`).
*   Call functions, passing the service instance (`auth`, `db`, `storage`) as the first argument.

**Firestore Example:**
```javascript
import { doc, setDoc } from 'firebase/firestore';
import { db } from './firebase';
const userRef = doc(db, 'users', userId);
await setDoc(userRef, data, { merge: true }); // Pass db first
```

**Authentication Example:**
```javascript
import { signInWithEmailAndPassword } from 'firebase/auth';
import { auth } from './firebase';
await signInWithEmailAndPassword(auth, email, password); // Pass auth first
```

**Storage Example:**
```javascript
import { ref, uploadBytes } from 'firebase/storage';
import { storage } from './firebase';
const storageRef = ref(storage, 'images/' + file.name); // Pass storage first
await uploadBytes(storageRef, file);
```

### Key Differences from v8

*   **Imports:** Direct function imports vs. namespace methods.
*   **Function Calls:** Service instance passed as first argument.
*   **Tree Shakable:** Smaller bundles.

### Compatibility (`compat` libraries)

Libraries like `firebase/compat/app`, `firebase/compat/auth` allow using v8 syntax with v9 benefits, useful for gradual migration.

```javascript
import firebase from 'firebase/compat/app';
import 'firebase/compat/auth';
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth(); // v8 style
auth.signInWithEmailAndPassword(email, password); // v8 syntax
```

**Recommendation:** Use fully modular v9+ syntax for new projects. Use `compat` as a migration aid.

*(Refer to the official Firebase Web v9 Upgrade Guide: https://firebase.google.com/docs/web/modular-upgrade)*
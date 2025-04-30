# Firebase: Emulator Suite for Local Testing

Using the Firebase Emulator Suite for local development and automated testing.

## Core Concept

The Firebase Emulator Suite provides local, high-fidelity emulators for many Firebase services, including:

*   Authentication
*   Firestore
*   Realtime Database
*   Cloud Functions
*   Cloud Storage
*   Pub/Sub
*   Hosting

This allows you to develop and test your application locally without interacting with (or incurring costs on) your live Firebase project.

## Setup

1.  **Install Firebase CLI:** (If not already installed) `npm install -g firebase-tools`.
2.  **Initialize Emulators:** Run `firebase init emulators` in your project directory.
    *   Select the emulators you want to use (Auth, Firestore, Functions, Storage, etc.).
    *   Configure ports for each emulator (defaults are usually fine).
    *   Choose whether to enable the Emulator UI (Recommended).
    *   Choose whether to download emulator binaries.
    *   This updates your `firebase.json` file with an `emulators` section.
    ```json
    // firebase.json (example emulators section)
    {
      "emulators": {
        "auth": { "port": 9099 },
        "functions": { "port": 5001 },
        "firestore": { "port": 8080 },
        "storage": { "port": 9199 },
        "pubsub": { "port": 8085 },
        "hosting": { "port": 5000 },
        "ui": { "enabled": true, "port": 4000 }
      }
    }
    ```

## Running the Emulators

*   **Command:** `firebase emulators:start`
*   **Flags:**
    *   `--only functions,firestore,auth`: Start only specific emulators.
    *   `--import=./my-export-data`: Import data saved from a previous emulator session.
    *   `--export-on-exit=./my-export-data`: Export data when shutting down (Ctrl+C).
*   **Output:** The CLI shows the ports each emulator is running on and the address for the Emulator UI.
*   **Emulator UI:** Access via `http://localhost:4000` (or configured port). Provides views for Auth users, Firestore data, Storage files, Function logs, etc., within the emulated environment.

## Connecting Your App to the Emulators

You need to configure your client-side Firebase SDK (Web, Android, iOS) and Admin SDK (in Cloud Functions) to connect to the running emulators instead of the production Firebase services.

**Web SDK v9 (Modular):**

```javascript
import { initializeApp } from 'firebase/app';
import { getAuth, connectAuthEmulator } from 'firebase/auth';
import { getFirestore, connectFirestoreEmulator } from 'firebase/firestore';
import { getStorage, connectStorageEmulator } from 'firebase/storage';
import { getFunctions, connectFunctionsEmulator } from 'firebase/functions'; // For callable functions

const firebaseConfig = { /* ... your config ... */ };
const app = initializeApp(firebaseConfig);

const auth = getAuth(app);
const db = getFirestore(app);
const storage = getStorage(app);
const functions = getFunctions(app); // Optional: for callable

// Check if running locally (e.g., based on hostname or env var)
if (window.location.hostname === "localhost") {
  console.log("Connecting to Firebase Emulators...");

  // Point SDKs to emulators
  connectAuthEmulator(auth, "http://localhost:9099");
  connectFirestoreEmulator(db, 'localhost', 8080);
  connectStorageEmulator(storage, 'localhost', 9199);
  // connectFunctionsEmulator(functions, "localhost", 5001); // If using callable functions

  // Optional: Disable Firestore persistence for cleaner testing
  // import { disableNetwork } from 'firebase/firestore';
  // await disableNetwork(db); // Or enablePersistence({synchronizeTabs:true}) etc.
}

export { auth, db, storage, functions };
```

**Admin SDK (Cloud Functions - Node.js/Python):**

The Admin SDK running *within* the Functions emulator automatically connects to other emulators (like Firestore, Auth) if they are running. You typically don't need explicit connection code *inside* the function code itself when using `firebase emulators:start`. Environment variables like `FIRESTORE_EMULATOR_HOST` are set automatically by the emulator environment.

## Testing Security Rules

*   **Emulator Suite:** The emulators enforce security rules defined in your `firestore.rules` and `storage.rules` files.
*   **Rules Playground:** Use the Emulator UI (Firestore/Storage -> Rules tabs) for interactive testing.
*   **Unit Testing (`@firebase/rules-unit-testing`):** This library allows you to write automated tests (e.g., using Jest or Mocha) that simulate authenticated/unauthenticated users making requests against your rules running in the Firestore/Storage emulators. This is the most robust way to test rules.

```javascript
// Example using @firebase/rules-unit-testing with Jest
import {
  assertFails, assertSucceeds, initializeTestEnvironment, RulesTestEnvironment
} from "@firebase/rules-unit-testing";
import { setDoc, doc, getDoc } from "firebase/firestore";
import fs from 'fs';

let testEnv: RulesTestEnvironment;

beforeAll(async () => {
  testEnv = await initializeTestEnvironment({
    projectId: "demo-project-123", // Use a dummy project ID
    firestore: {
      rules: fs.readFileSync("firestore.rules", "utf8"), // Load your rules file
      host: "localhost", // Connect to local emulator
      port: 8080,
    },
  });
});

afterAll(async () => {
  await testEnv.cleanup();
});

beforeEach(async () => {
  await testEnv.clearFirestore(); // Clear data before each test
});

describe("Firestore security rules", () => {
  it("should allow authenticated user to read their own profile", async () => {
    const userId = "user_abc";
    const db = testEnv.authenticatedContext(userId).firestore(); // Firestore instance authenticated as user_abc
    await setDoc(doc(db, `users/${userId}`), { name: "Alice" }); // Setup data (bypasses rules)
    await assertSucceeds(getDoc(doc(db, `users/${userId}`))); // Test read rule
  });

  it("should deny unauthenticated user reading a profile", async () => {
    const userId = "user_abc";
    const db = testEnv.unauthenticatedContext().firestore(); // Unauthenticated instance
    await testEnv.withSecurityRulesDisabled(async (context) => { // Setup data bypassing rules
        await setDoc(doc(context.firestore(), `users/${userId}`), { name: "Alice" });
    });
    await assertFails(getDoc(doc(db, `users/${userId}`))); // Test read rule
  });

  // ... more tests for write, update, delete, different roles etc.
});
```

The Emulator Suite is invaluable for local development, debugging, and creating reliable automated tests for Firebase applications.

*(Refer to the official Firebase Emulator Suite documentation: https://firebase.google.com/docs/emulator-suite)*
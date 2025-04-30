# Firebase: Authentication Flows (Web v9 SDK)

Implementing common user authentication methods using the Firebase Authentication Web SDK (v9 modular).

## Core Concept

Firebase Authentication provides backend services and client-side SDKs to authenticate users easily. The Web v9 SDK uses a modular approach, importing only the functions needed.

## Setup

1.  **Initialize Firebase:** Ensure Firebase is initialized in your client-side application.
    ```javascript
    // src/firebase.js (or similar config file)
    import { initializeApp } from 'firebase/app';
    import { getAuth } from 'firebase/auth';
    import { getFirestore } from 'firebase/firestore';
    // ... import other services as needed

    const firebaseConfig = {
      apiKey: "YOUR_API_KEY",
      authDomain: "YOUR_AUTH_DOMAIN",
      projectId: "YOUR_PROJECT_ID",
      storageBucket: "YOUR_STORAGE_BUCKET",
      messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
      appId: "YOUR_APP_ID"
    };

    // Initialize Firebase
    const app = initializeApp(firebaseConfig);

    // Get service instances
    const auth = getAuth(app);
    const db = getFirestore(app);
    // const storage = getStorage(app);

    export { auth, db /*, storage */ };
    ```
2.  **Enable Providers:** In the Firebase Console (Authentication -> Sign-in method tab), enable the sign-in providers you want to use (e.g., Email/Password, Google, Facebook, GitHub). Configure OAuth providers with necessary client IDs and secrets.

## Common Flows (Web v9 Modular SDK)

*   **Import Functions:** Import necessary functions from `firebase/auth`.
*   **Get Auth Instance:** Get the auth instance using `getAuth()`.

### 1. Email/Password Sign Up

```javascript
import { getAuth, createUserWithEmailAndPassword } from 'firebase/auth';
import { auth } from './firebase'; // Your firebase config file

async function signUp(email, password) {
  try {
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    // Signed up successfully
    const user = userCredential.user;
    console.log('User signed up:', user);
    // Optionally: Send verification email, update profile, etc.
    // await sendEmailVerification(user);
    // await updateProfile(user, { displayName: "New User" });
    return user;
  } catch (error) {
    const errorCode = error.code;
    const errorMessage = error.message;
    console.error(`Sign up failed (${errorCode}):`, errorMessage);
    // Handle specific errors (e.g., 'auth/email-already-in-use')
    throw error; // Re-throw or handle appropriately
  }
}
```

### 2. Email/Password Sign In

```javascript
import { getAuth, signInWithEmailAndPassword } from 'firebase/auth';
import { auth } from './firebase';

async function signIn(email, password) {
  try {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    // Signed in successfully
    const user = userCredential.user;
    console.log('User signed in:', user);
    return user;
  } catch (error) {
    const errorCode = error.code;
    const errorMessage = error.message;
    console.error(`Sign in failed (${errorCode}):`, errorMessage);
    // Handle specific errors (e.g., 'auth/wrong-password', 'auth/user-not-found')
    throw error;
  }
}
```

### 3. Sign Out

```javascript
import { getAuth, signOut } from 'firebase/auth';
import { auth } from './firebase';

async function logOut() {
  try {
    await signOut(auth);
    console.log('User signed out');
  } catch (error) {
    console.error('Sign out failed:', error);
    throw error;
  }
}
```

### 4. OAuth Sign In (e.g., Google)

```javascript
import { getAuth, signInWithPopup, GoogleAuthProvider } from 'firebase/auth';
import { auth } from './firebase';

const googleProvider = new GoogleAuthProvider();
// Optional: Add custom parameters or scopes
// googleProvider.addScope('https://www.googleapis.com/auth/contacts.readonly');

async function signInWithGoogle() {
  try {
    const result = await signInWithPopup(auth, googleProvider);
    // This gives you a Google Access Token. You can use it to access the Google API.
    const credential = GoogleAuthProvider.credentialFromResult(result);
    const token = credential?.accessToken; // Optional: Use if needed
    // The signed-in user info.
    const user = result.user;
    console.log('User signed in with Google:', user);
    // IdP data available using getAdditionalUserInfo(result)
    return user;
  } catch (error) {
    // Handle Errors here.
    const errorCode = error.code;
    const errorMessage = error.message;
    // The email of the user's account used.
    const email = error.customData?.email;
    // The AuthCredential type that was used.
    const credential = GoogleAuthProvider.credentialFromError(error);
    console.error(`Google sign in failed (${errorCode}):`, errorMessage, email, credential);
    throw error;
  }
}

// signInWithRedirect(auth, provider); // Alternative flow using redirect
// getRedirectResult(auth).then(...); // Handle result after redirect
```

### 5. Observing Auth State

*   Use `onAuthStateChanged` to listen for changes in the user's sign-in state. This is the recommended way to get the current user.

```javascript
import { getAuth, onAuthStateChanged } from 'firebase/auth';
import { auth } from './firebase';

function observeAuthChanges(callback) {
  const unsubscribe = onAuthStateChanged(auth, (user) => {
    if (user) {
      // User is signed in, see docs for a list of available properties
      // https://firebase.google.com/docs/reference/js/auth.user
      console.log('Auth state changed: User signed in', user.uid);
      callback(user); // Pass user object to your app's state management
    } else {
      // User is signed out
      console.log('Auth state changed: User signed out');
      callback(null);
    }
  });
  // To stop listening:
  // unsubscribe();
  return unsubscribe;
}

// Example usage in your app initialization:
// observeAuthChanges((user) => {
//   if (user) { /* Update app state to logged in */ }
//   else { /* Update app state to logged out */ }
// });
```

## Other Auth Features

*   **Password Reset:** `sendPasswordResetEmail(auth, email)`
*   **Email Verification:** `sendEmailVerification(auth.currentUser)`
*   **Update Profile:** `updateProfile(auth.currentUser, { displayName: "...", photoURL: "..." })`
*   **Update Email/Password:** `updateEmail()`, `updatePassword()`
*   **Phone Number Auth:** Requires more setup (reCAPTCHA verifier).
*   **Custom Claims:** Set custom attributes on users via Admin SDK (in Cloud Functions) for role-based access control. Access via `user.getIdTokenResult()`.

Always handle potential errors from authentication methods using try/catch blocks or `.catch()`.

*(Refer to the official Firebase Authentication Web documentation: https://firebase.google.com/docs/auth/web/start)*
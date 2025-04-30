# Directus: Real-time Data (WebSockets & GraphQL Subscriptions)

Directus supports real-time communication using WebSockets, allowing the server to push updates to connected clients immediately when data changes. This is implemented via **GraphQL Subscriptions**.

## Core Concept: Pushing Data Updates

Instead of clients constantly polling for changes, they can subscribe to specific data events. When relevant data is created, updated, or deleted, Directus pushes the update over the WebSocket connection to subscribed clients.

**Use Cases:** Live dashboards, chat, collaborative editing, notifications, activity feeds.

## How it Works

1.  **Client Subscribes:** Connects to `/graphql` via WebSocket and sends a GraphQL `subscription` query specifying the collection, action(s) (`create`, `update`, `delete`), optional filters, and desired data fields.
2.  **Server Listens:** Keeps the WebSocket open and monitors for matching data changes.
3.  **Data Changes:** An item matching the subscription criteria is modified.
4.  **Server Pushes:** Directus sends a message over the WebSocket containing the event type and requested data.

## Subscribing with the JavaScript SDK

The `@directus/sdk` simplifies managing WebSocket connections and subscriptions.

```typescript
import { createDirectus, realtime, graphql, subscribe } from '@directus/sdk';

// Initialize client with realtime() and graphql() transports
// Use wss:// for secure connections in production
const clientWithRealtime = createDirectus<Schema>('wss://your-directus.com')
  .with(realtime())
  .with(graphql());
  // Add authentication if needed: .with(staticToken('...')) or handle login

async function subscribeToUpdates() {
  try {
    // Connect WebSocket
    await clientWithRealtime.connect();

    // Define subscription query
    const subscriptionQuery = {
      query: `
        subscription ItemUpdates($collectionName: String!, $filter: JSON) {
          ${collectionName}(filter: $filter) { # Use variables for flexibility
            event # create, update, delete
            data { id status title /* ... other fields */ }
            # key(s) # Primary key(s) involved
          }
        }
      `,
      variables: {
        collectionName: "articles", // Specify the collection to watch
        filter: { status: { _eq: "published" } } // Optional filter
      }
    };

    // Start subscription and define callback for messages
    const { unsubscribe } = await clientWithRealtime.request(
        subscribe(subscriptionQuery, (message) => {
            console.log('Real-time Update:', message);
            if (message.data?.articles) { // Access based on collection name variable
                const eventData = message.data.articles;
                console.log(`Event: ${eventData.event}`);
                console.log(`Data:`, eventData.data);
                // Update UI, show notification, etc.
            }
        })
    );

    console.log('Subscribed to updates!');

    // To stop listening later:
    // unsubscribe();

  } catch (error) {
    console.error('Subscription error:', error);
  }
  // Handle disconnection/reconnection logic
  // clientWithRealtime.onWebSocket('close', () => { /* ... */ });
  // clientWithRealtime.onWebSocket('error', (err) => { /* ... */ });
}

// subscribeToUpdates();
```

## Key Considerations

*   **Protocol:** Use `ws://` (local) or `wss://` (production over HTTPS). Ensure server/proxy handles WebSockets.
*   **Authentication:** Authenticate the WebSocket connection if subscribing to non-public data (SDK usually handles token passing).
*   **Permissions:** Subscriptions respect Directus role permissions. Users only receive updates for data they can read.
*   **Filtering:** Use the `filter` argument in the subscription query for targeted updates.
*   **Payload:** Message contains `event` (`create`, `update`, `delete`) and `data` (fields requested in the query).
*   **Scalability:** Many connections consume resources. Horizontal scaling requires infrastructure support (sticky sessions or message bus like Redis via `MESSENGER_STORE`, `WEBSOCKETS_BROKER_URL`). Coordinate with `infrastructure-specialist`/`devops-lead`.
*   **Client Handling:** Manage incoming messages, update UI, handle subscription lifecycle (unsubscribe), and implement reconnection logic.

*(Refer to the official Directus documentation on Realtime Data and GraphQL Subscriptions.)*
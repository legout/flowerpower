# Directus: API Usage (REST, GraphQL, SDK)

Directus automatically generates powerful APIs based on your collections, allowing interaction with your data.

## 1. REST API

*   **Endpoint Structure:** Typically `/items/{collection_name}`.
    *   `GET /items/{collection}`: List items.
    *   `POST /items/{collection}`: Create item.
    *   `GET /items/{collection}/{id}`: Retrieve item.
    *   `PATCH /items/{collection}/{id}`: Update item.
    *   `DELETE /items/{collection}/{id}`: Delete item.
*   **Authentication:** Use `Authorization: Bearer <token>` header (Static Token, JWT). Public role may allow unauthenticated access.
*   **Query Parameters (GET):**
    *   `filter`: JSON filter object (e.g., `{"status":{"_eq":"published"}}`). Supports operators (`_eq`, `_neq`, `_gt`, `_in`, `_contains`, `_and`, `_or`).
    *   `sort`: Comma-separated fields (e.g., `title`, `-published_on`).
    *   `fields`: Comma-separated fields (e.g., `id,title,author.name`). Supports nesting and wildcards (`*`).
    *   `limit`, `page`, `offset`: Pagination. `limit=-1` for all (use cautiously).
    *   `deep`: Apply filters/sorts to related data.
    *   `aggregate`: Perform functions (`count`, `sum`, `avg`, etc.).
    *   `groupBy`: Group results.
    *   `meta`: Request metadata (e.g., `total_count`).
*   **Response:** JSON, usually with a `data` property.

**Example (REST GET):**
```
GET /items/articles?fields=id,title,author.name&filter={"status":{"_eq":"published"}}&sort=-published_on&limit=10
Authorization: Bearer <YOUR_ACCESS_TOKEN>
```

## 2. GraphQL API

*   **Endpoint:** Single endpoint, usually `/graphql`.
*   **Schema:** Auto-generated and introspectable.
*   **Queries:** Use standard GraphQL syntax. Arguments for `filter`, `sort`, `limit`, `page`, `offset`, `aggregate`. Select needed fields, including nested relations.
*   **Mutations:** Standard GraphQL mutations for `create_{collection}_item`, `update_{collection}_item`, `delete_{collection}_item`. Input types based on collection fields.
*   **Authentication:** Same as REST (`Authorization: Bearer <token>`).

**Example (GraphQL Query):**
```graphql
query GetPublishedArticles {
  articles(
    filter: { status: { _eq: "published" } }
    sort: ["-published_on"]
    limit: 10
  ) {
    id
    title
    author { name }
  }
  articles_aggregated(filter: { status: { _eq: "published" } }) {
    count { id }
  }
}
```

**Example (GraphQL Mutation - Create):**
```graphql
mutation CreateArticle($newData: create_articles_input!) {
  create_articles_item(data: $newData) { id title status }
}
# Variables: { "newData": { "title": "...", "status": "draft" } }
```

## 3. JavaScript SDK (`@directus/sdk`)

*   **Purpose:** Convenient, type-safe interaction from JS/TS applications. Handles auth, requests, responses.
*   **Installation:** `npm install @directus/sdk`
*   **Initialization:**
    ```typescript
    import { createDirectus, rest, staticToken, readItems, createItems, updateItem, deleteItems } from '@directus/sdk';

    // Define types (optional but recommended)
    type Schema = { articles: { id: string; status: string; title: string; /*...*/ }[]; /*...*/ };

    const client = createDirectus<Schema>('https://your-directus.com').with(rest());
    // Add auth if needed: .with(staticToken('...')) or handle login/JWT
    ```
*   **Usage:**
    ```typescript
    // Read Items
    const articles = await client.request(readItems('articles', {
      filter: { status: { _eq: 'published' } },
      fields: ['id', 'title', 'author.name'],
      limit: 10
    }));

    // Create Item
    const newItem = await client.request(createItems('articles', [{
      title: 'SDK Article', status: 'draft'
    }]));

    // Update Item
    const updatedItem = await client.request(updateItem('articles', 'some-id', {
      status: 'published'
    }));

    // Delete Item
    await client.request(deleteItems('articles', ['some-id']));
    ```

Choose the API style (REST, GraphQL, SDK) that best fits the consuming application's needs.

*(Refer to the official Directus API Reference and SDK documentation.)*
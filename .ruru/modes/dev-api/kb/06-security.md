# 06: API Security Fundamentals

This document outlines essential security considerations for API development. Security is a layered approach and requires collaboration with security specialists.

## Core Security Areas

1.  **Authentication (AuthN):** Verifying client identity (Who are you?).
2.  **Authorization (AuthZ):** Determining client permissions (What can you do?).
3.  **Input Validation:** Ensuring client-provided data is safe and expected.
4.  **Transport Security:** Encrypting data in transit (HTTPS).
5.  **Rate Limiting:** Preventing abuse and DoS attacks.
6.  **Output Encoding/Escaping:** Preventing XSS if API data is rendered in HTML.
7.  **Information Disclosure:** Avoiding leaks of sensitive data in responses/errors.

## Common Mechanisms &amp; Best Practices

1.  **Authentication (AuthN):**
    *   **Token-Based (JWT, OAuth 2.0 Bearer):** Standard for SPAs/mobile. Send token in `Authorization: Bearer <token>` header. Validate signature/expiry server-side.
    *   **API Keys:** Simpler tokens for server-to-server or third-party use. Send securely (e.g., `X-API-Key` header). Treat as secrets.
    *   **Session Cookies (Stateful):** Traditional web approach. Requires server-side session storage and CSRF protection (SameSite cookies, anti-CSRF tokens).
    *   **mTLS:** Strong server-to-server authentication using mutual certificates.
    *   **Collaboration:** Coordinate implementation details with `security-specialist` or specific auth modes (e.g., `clerk-auth-specialist`, `supabase-auth-specialist`) via lead.

2.  **Authorization (AuthZ):**
    *   **Implement Server-Side:** Never trust client-side checks. Perform checks after authentication for every relevant request.
    *   **Mechanisms:** RBAC (Role-Based), ABAC (Attribute-Based), OAuth Scopes.
    *   **Logic:** Check permissions based on the authenticated user's roles/attributes against the required permissions for the specific action or resource.
    *   **Collaboration:** Coordinate complex authorization logic with `security-specialist` via lead.

3.  **Input Validation:**
    *   **Validate Everything:** Treat all client input (URL params, query strings, headers, body) as untrusted.
    *   **Use Schemas:** Define expected data structures/types (OpenAPI, JSON Schema, GraphQL Input Types, validation libraries like Zod, Pydantic).
    *   **Check Constraints:** Validate types, formats (email, UUID), lengths, ranges, allowed values.
    *   **Prefer Validation over Sanitization:** Reject invalid input rather than trying to clean it up.
    *   **Framework Features:** Leverage built-in validation capabilities of your framework.

4.  **Transport Security:**
    *   **Use HTTPS Everywhere:** Enforce TLS/SSL for all API communication.
    *   **HSTS Header:** Consider using `Strict-Transport-Security` header.

5.  **Rate Limiting:**
    *   **Purpose:** Prevent abuse and DoS.
    *   **Implementation:** Limit requests based on IP, user ID, API key. Return `429 Too Many Requests`. Often handled at API gateway, load balancer, or via middleware.
    *   **Collaboration:** Coordinate implementation with `infrastructure-specialist` / `devops-lead` via lead.

6.  **Other Considerations:**
    *   **Security Headers:** Use relevant headers (`Content-Security-Policy`, `X-Content-Type-Options`, etc.) if applicable.
    *   **Logging &amp; Monitoring:** Log security events (login attempts, failures) and monitor for anomalies.
    *   **Dependency Management:** Keep dependencies updated to patch vulnerabilities.
    *   **OWASP API Security Top 10:** Be familiar with common vulnerabilities (Broken Object Level Authorization, Broken Authentication, Injection, etc.) and prevention techniques.
    *   **CORS:** Configure Cross-Origin Resource Sharing headers correctly if needed for browser clients.

API security is critical. Implement strong input validation within your code. Collaborate closely with `security-specialist`, auth specialists, and infrastructure specialists (via lead) for robust AuthN/AuthZ, rate limiting, and infrastructure security.
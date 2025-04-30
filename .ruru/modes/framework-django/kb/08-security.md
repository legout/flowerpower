# Django: Security Best Practices

Implementing common security measures in Django applications.

## Core Concept: Built-in Protection & Developer Responsibility

Django provides built-in protection against common web vulnerabilities (XSS, CSRF, SQL Injection, Clickjacking), but developers must use these features correctly and follow secure coding practices.

## Built-in Protections & Essential Practices

1.  **Cross-Site Scripting (XSS) Prevention:**
    *   **Mechanism:** Django templates automatically escape HTML characters in `{{ variable }}` output.
    *   **Action:** Rely on auto-escaping. Use the `|safe` filter *only* on explicitly trusted/sanitized content. Be cautious generating HTML in views. Implement a strong `Content-Security-Policy` (CSP) header.

2.  **Cross-Site Request Forgery (CSRF) Protection:**
    *   **Mechanism:** Requires a secret token in POST forms, validated by `CsrfViewMiddleware`.
    *   **Action:** Ensure `CsrfViewMiddleware` is in `MIDDLEWARE`. Add `{% csrf_token %}` inside all `<form method="post">`. Include the token (usually via `X-CSRFToken` header) in AJAX POST/PUT/PATCH/DELETE requests.

3.  **SQL Injection Protection:**
    *   **Mechanism:** The ORM uses parameterized queries, separating SQL code from data.
    *   **Action:** **Always** prefer the ORM over raw SQL. If raw SQL is needed (`cursor.execute()`), pass parameters safely as arguments, *never* using string formatting/interpolation.

4.  **Clickjacking Protection:**
    *   **Mechanism:** `XFrameOptionsMiddleware` sets the `X-Frame-Options: DENY` header by default, preventing embedding in `<iframe>`s.
    *   **Action:** Keep middleware enabled. Configure `X_FRAME_OPTIONS` if needed (e.g., `'SAMEORIGIN'`).

5.  **Keep Django & Dependencies Updated:**
    *   **Action:** Regularly update Django and third-party packages (`pip install -U Django`, `pip list --outdated`, use `pip-audit` or Dependabot).

6.  **Use HTTPS:**
    *   **Action:** Deploy over HTTPS. Configure `SECURE_SSL_REDIRECT = True`, `SESSION_COOKIE_SECURE = True`, `CSRF_COOKIE_SECURE = True` in production settings. Handle SSL termination at the web server/load balancer level.

7.  **Protect `SECRET_KEY`:**
    *   **Action:** Keep `SECRET_KEY` confidential. Load from environment variables or secrets management in production. Do *not* commit to version control.

8.  **Disable `DEBUG` in Production:**
    *   **Action:** **Never** run with `DEBUG = True` in production. Set `DEBUG = False` and configure `ALLOWED_HOSTS` in production settings.

9.  **Authentication & Authorization:**
    *   **Action:** Use Django's built-in auth or a well-vetted package. Protect views with `@login_required`/`LoginRequiredMixin` and `@permission_required`/`PermissionRequiredMixin` or manual checks (`user.has_perm(...)`). Enforce strong password policies. Consider 2FA. (See `11-authentication.md`).

10. **Input Validation:**
    *   **Action:** Validate *all* user-provided data (types, lengths, formats) using Django Forms or DRF Serializers. Don't trust `request.GET`/`request.POST` directly.

11. **File Uploads:**
    *   **Action:** Validate file types, names, sizes. Store uploads outside the web root (e.g., `MEDIA_ROOT`, S3). Serve files carefully (correct `Content-Type`, consider `Content-Disposition: attachment`).

12. **Session Security:**
    *   **Action:** Use `SESSION_COOKIE_SECURE = True` (requires HTTPS), `SESSION_COOKIE_HTTPONLY = True` (prevents client-side script access), `SESSION_COOKIE_SAMESITE = 'Lax'` or `'Strict'` (CSRF mitigation).

13. **Security Headers:**
    *   **Action:** Utilize `django.middleware.security.SecurityMiddleware` and configure settings like `SECURE_HSTS_SECONDS` (if using HTTPS always), `SECURE_CONTENT_TYPE_NOSNIFF`, `SECURE_BROWSER_XSS_FILTER`.

14. **Error Handling:**
    *   **Action:** Configure `ADMINS` and email settings for error reporting in production (`DEBUG=False`). Don't expose detailed errors to users.

Security is paramount. Leverage Django's features, keep software updated, validate input, handle auth correctly, and configure production securely. Consult Django security docs and OWASP resources. Coordinate with `security-specialist`.
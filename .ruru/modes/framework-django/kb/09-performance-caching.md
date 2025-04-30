# Django: Performance & Caching

Techniques for improving the performance and scalability of Django applications, focusing on ORM and caching.

## Core Concept: Reducing Response Time & Resource Usage

Optimization aims to make applications respond faster and handle more users by reducing database load, minimizing computation, and leveraging caching. Key areas include Database Queries, Caching, Template Rendering, View Logic, Static Assets, and Middleware.

## 1. Database Query Optimization (ORM)

Inefficient queries are a common bottleneck. Use Django Debug Toolbar to identify issues.

*   **`select_related(*fields)`:**
    *   **Purpose:** Follows forward `ForeignKey`/`OneToOneField` relationships using SQL `JOIN`s. Fetches related objects in the *same* query.
    *   **When:** Accessing single related objects you know you'll need.
    *   **Example:** `Article.objects.select_related('author__user').filter(...)` avoids extra queries when accessing `article.author.user.username`.
*   **`prefetch_related(*lookups)`:**
    *   **Purpose:** Follows `ManyToManyField` and reverse `ForeignKey`/`OneToOneField` relationships. Performs *separate* lookups and joins in Python.
    *   **When:** Accessing related sets of objects (M2M, reverse FK). Avoids N+1 queries.
    *   **Example:** `Article.objects.prefetch_related('categories').filter(...)` avoids extra queries when accessing `article.categories.all()`.
*   **`only(*fields)` / `defer(*fields)`:**
    *   **Purpose:** Control initial field loading. `only()` loads *only* specified fields; `defer()` loads *all except* specified fields. Deferred fields load on access (extra query).
    *   **When:** Avoid loading large fields (`TextField`) or when only a subset of fields is needed.
*   **`values(*fields)` / `values_list(*fields, flat=False)`:**
    *   **Purpose:** Retrieve results as dictionaries (`values`) or tuples (`values_list`) instead of model instances. More efficient for raw data needs.
    *   **Example:** `User.objects.values_list('email', flat=True)` gets a flat list of emails.
*   **`count()` / `exists()`:**
    *   **Purpose:** Use `queryset.count()` instead of `len(queryset)` (uses SQL `COUNT`). Use `queryset.exists()` instead of `if queryset:` or `queryset.count() > 0` (uses SQL `EXISTS`).
*   **`update()` / `delete()` on QuerySets:**
    *   **Purpose:** Perform bulk updates/deletes directly in the database. Faster but bypasses model `save()`/`delete()` methods and signals.
*   **Database Indexing:**
    *   **Action:** Add indexes (`db_index=True` on fields or `Meta.indexes`) to columns frequently used in `filter()`, `exclude()`, `order_by()`. Analyze query plans (`EXPLAIN`). Coordinate with `database-specialist`.
*   **`iterator()`:**
    *   **Purpose:** Process very large querysets without loading everything into memory.

## 2. Caching Framework

Store results of expensive operations temporarily.

*   **Setup (`settings.py`):** Configure `CACHES` setting with desired backend(s).
    *   **Backends:** Memory (`locmem`, dev only), Database (`db`), Filesystem (`filebased`), Memcached (`memcached`), Redis (`django-redis`, common for production).
    ```python
    # settings.py (Example using Redis via django-redis)
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/1", # Your Redis server
            "OPTIONS": { "CLIENT_CLASS": "django_redis.client.DefaultClient" }
        }
    }
    ```
*   **Levels of Caching:**
    *   **Per-Site Cache:** Caches entire pages via `UpdateCacheMiddleware` and `FetchFromCacheMiddleware`. Simplest, least granular.
    *   **Per-View Cache:** Cache view output using `@cache_page(timeout)` decorator or `cache_page` URLconf wrapper.
    *   **Template Fragment Caching:** Cache template sections using `{% load cache %}` and `{% cache timeout name [vary_on...] %}` ... `{% endcache %}`. Good for semi-static parts. Vary on parameters (user, language) if content differs.
    *   **Low-Level Cache API:** Direct control via `django.core.cache.cache`. Use `cache.get(key)`, `cache.set(key, value, timeout)`, `cache.delete(key)`, `cache.get_or_set(key, callable, timeout)`. Cache arbitrary data (query results, computed values).
    ```python
    from django.core.cache import cache

    def get_expensive_data(user_id):
        cache_key = f'expensive_data_{user_id}'
        data = cache.get(cache_key)
        if data is None:
            data = # ... perform expensive operation ...
            cache.set(cache_key, data, timeout=3600) # Cache for 1 hour
        return data
    ```
*   **Cache Invalidation:** Crucial. Ensure cache updates when data changes.
    *   **Strategies:** Time-based expiration (simple, may serve stale data), manual deletion (`cache.delete()`, e.g., in `save()` or signals), key versioning.

## 3. Other Optimizations

*   **Template Optimization:** Keep logic simple. Use `{% cache %}` tag. Use `{% with %}` tag to avoid redundant lookups.
*   **Static Files:** Serve via web server (Nginx) or CDN in production. Use `collectstatic`. Use compression and caching headers.
*   **Asynchronous Tasks:** Offload long-running tasks (email, reports) to background queues (Celery, RQ) using `django-q` or similar.

## Profiling & Monitoring

*   **Django Debug Toolbar:** Essential for development. Shows DB queries (time, duplicates), cache usage, etc.
*   **Database Query Plans:** Use `EXPLAIN`.
*   **Python Profilers:** `cProfile`.
*   **Load Testing:** Locust, k6 (Coordinate with `performance-optimizer`).
*   **APM Tools:** Datadog, New Relic, Sentry (for production).

Start by optimizing DB queries (`select_related`/`prefetch_related`) and using Django Debug Toolbar. Implement caching strategically. Offload heavy tasks.
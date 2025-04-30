# Django: Admin Interface

Utilizing and customizing Django's automatic administration interface (`django.contrib.admin`).

## Core Concept: Automatic CRUD Interface

Django's admin interface reads metadata from your models (`models.py`) to provide a production-ready interface where trusted users (`is_staff=True`) can manage content (perform CRUD operations) based on model permissions.

## Enabling and Accessing the Admin

1.  **Ensure `django.contrib.admin` is in `INSTALLED_APPS`** (in `settings.py`, default).
2.  **Include Admin URLs:** Ensure `path('admin/', admin.site.urls)` is in your project's root `urls.py`.
3.  **Run Migrations:** `python manage.py migrate` (creates tables for admin, auth, etc.).
4.  **Create Superuser:** `python manage.py createsuperuser`.
5.  **Run Server & Access:** `python manage.py runserver`, then navigate to `/admin/` and log in.

## Registering Models (`admin.py`)

Make models manageable by registering them in the app's `admin.py`.

```python
# myapp/admin.py
from django.contrib import admin
from .models import Author, Category, Article

# Simple registration (uses default options)
admin.site.register(Author)
admin.site.register(Category)
# admin.site.register(Article) # Registering with default options
```

## Customizing the Admin (`ModelAdmin`)

Create a `ModelAdmin` subclass to customize display and management. Register the model with this class using `@admin.register(ModelName)` decorator or `admin.site.register(ModelName, ModelAdminClass)`.

```python
# myapp/admin.py
from django.contrib import admin
from .models import Author, Category, Article

admin.site.register(Author) # Keep simple registration if no customization needed
admin.site.register(Category)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    # --- List View Customization ---
    list_display = ('title', 'author', 'status', 'publish_date', 'is_featured', 'was_published_recently_display') # Fields/methods to show in list
    list_filter = ('status', 'publish_date', 'author', 'categories') # Fields for sidebar filters
    search_fields = ('title', 'content', 'author__user__username') # Fields for search bar
    list_display_links = ('title',) # Fields to link to change page
    list_editable = ('status', 'is_featured') # Fields editable directly in list view
    date_hierarchy = 'publish_date' # Date drill-down navigation
    ordering = ('-publish_date',) # Default sorting

    # --- Change/Add Form Customization ---
    fieldsets = ( # Control field order and grouping
        (None, { # Section title (None for default)
            'fields': ('title', 'slug', 'author', 'status', 'is_featured') # Fields in this section
        }),
        ('Content', {
            'fields': ('content', 'categories')
        }),
        ('Date Information', {
            'fields': ('publish_date', 'created_at', 'updated_at'),
            'classes': ('collapse',) # Make section collapsible
        }),
    )
    # Alternatively, use 'fields' for simpler ordering without sections:
    # fields = ('title', 'slug', ...)

    readonly_fields = ('created_at', 'updated_at') # Display as read-only
    prepopulated_fields = {'slug': ('title',)} # Auto-populate slug from title
    raw_id_fields = ('author',) # Use lookup popup instead of dropdown for ForeignKey
    filter_horizontal = ('categories',) # Better widget for ManyToMany
    # filter_vertical = ('categories',)

    # --- Inlines (Editing related models on the same page) ---
    # inlines = [CommentInline] # Assuming CommentInline class is defined below

    # --- Custom Actions ---
    actions = ['make_published', 'make_draft']

    @admin.action(description='Mark selected articles as Published')
    def make_published(self, request, queryset):
        queryset.update(status='published')

    @admin.action(description='Mark selected articles as Draft')
    def make_draft(self, request, queryset):
        queryset.update(status='draft')

    # --- Custom Display Methods ---
    @admin.display(boolean=True, description='Published Recently?')
    def was_published_recently_display(self, obj):
        # Assumes was_published_recently() method exists on Article model
        return obj.was_published_recently()

# Example Inline ModelAdmin (for related models like comments)
# class CommentInline(admin.TabularInline): # or admin.StackedInline
#     model = Comment # Assuming Comment model with ForeignKey to Article
#     extra = 1 # Number of empty forms to display
#     readonly_fields = ('created_at',)
```

## Common `ModelAdmin` Options

*   **List Display:** `list_display`, `list_display_links`, `list_editable`, `list_filter`, `search_fields`, `date_hierarchy`, `ordering`.
*   **Form Display:** `fields`, `fieldsets`, `readonly_fields`, `prepopulated_fields`, `raw_id_fields`, `filter_horizontal`, `filter_vertical`.
*   **Inlines:** `inlines` (requires defining `admin.TabularInline` or `admin.StackedInline` subclasses).
*   **Actions:** `actions` (list of custom action methods).
*   **Permissions:** `has_add_permission()`, `has_change_permission()`, `has_delete_permission()`, `has_view_permission()`.
*   **QuerySet:** `get_queryset()` (customize objects shown).

## Security

*   Admin respects Django's permission system.
*   Protect your admin URL (consider changing it from `/admin/`).
*   Ensure only trusted staff have admin access (`is_staff=True`).

The Django admin is a powerful tool. Register models in `admin.py` and use `ModelAdmin` classes to customize the interface extensively.
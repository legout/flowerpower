# Django: Models & ORM

Defining data structures and interacting with the database using Django's Object-Relational Mapper.

## Core Concept: Mapping Python to SQL

Django's ORM provides a Pythonic way to define your database schema and interact with your data, abstracting away most raw SQL.

*   **Models:** Python classes in `models.py` that subclass `django.db.models.Model`. Each model class represents a database table. Django automatically adds an auto-incrementing primary key field named `id` unless `primary_key=True` is specified on another field.
*   **Fields:** Attributes defined within a model class represent table columns. Django provides various field types (`CharField`, `IntegerField`, `DateTimeField`, `ForeignKey`, `ManyToManyField`, etc.) that map to corresponding SQL column types.
*   **Migrations:** Django can automatically generate SQL migration files (`manage.py makemigrations`) based on changes detected in your `models.py`. These migrations track schema changes and can be applied to update the database schema (`manage.py migrate`).
*   **QuerySets:** The primary way to retrieve objects from the database. They represent a collection of database rows and allow filtering, slicing, ordering, and other operations using Python methods before hitting the database. QuerySets are lazy – the database query is only executed when the QuerySet is evaluated.

## Defining Models (`models.py`)

```python
# myapp/models.py
from django.db import models
from django.contrib.auth.models import User # Example: Linking to built-in User
from django.utils import timezone
from django.urls import reverse # For get_absolute_url

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    bio = models.TextField(blank=True, null=True)
    # Add other author-specific fields

    def __str__(self):
        return self.user.username

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "categories" # Correct plural name in Admin
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # Example assuming you have a URL pattern named 'category_detail'
        return reverse('myapp:category_detail', kwargs={'slug': self.slug})


class Article(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique_for_date='publish_date')
    # Use ForeignKey for Many-to-One relationships
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='articles')
    # Use ManyToManyField for Many-to-Many relationships
    categories = models.ManyToManyField(Category, related_name='articles', blank=True)
    content = models.TextField()
    publish_date = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True) # Automatically set on creation
    updated_at = models.DateTimeField(auto_now=True)     # Automatically set on save
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['-publish_date'] # Default ordering for querysets
        # Example: Index for common filtering
        indexes = [
            models.Index(fields=['status', 'publish_date']),
        ]
        # Example: Multi-column uniqueness
        # unique_together = [['author', 'slug']]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # Example assuming you have a URL pattern named 'article_detail'
        return reverse('myapp:article_detail', kwargs={'pk': self.pk})


    # Example custom model method
    def was_published_recently(self):
        now = timezone.now()
        return now - timezone.timedelta(days=1) <= self.publish_date <= now

```

## Common Field Types

*   `CharField(max_length=...)`: Text field.
*   `TextField()`: Large text field.
*   `IntegerField()`, `FloatField()`, `DecimalField(max_digits=..., decimal_places=...)`: Numeric types.
*   `BooleanField(default=False)`: True/False.
*   `DateField(auto_now=False, auto_now_add=False)`, `DateTimeField(...)`, `TimeField`: Date/time types (`auto_now` updates on save, `auto_now_add` sets on creation).
*   `EmailField()`, `URLField()`, `SlugField()`: Specialized character fields with validation.
*   `FileField(upload_to=...)`, `ImageField(...)`: For file uploads.
*   `JSONField()`: For storing JSON data (database support required).
*   **Relationships:**
    *   `ForeignKey(OtherModel, on_delete=models.CASCADE, related_name=...)`: Many-to-one. `on_delete` specifies behavior (e.g., `CASCADE`, `PROTECT`, `SET_NULL`, `SET_DEFAULT`). `related_name` defines the reverse accessor name (from `OtherModel` back to this model).
    *   `ManyToManyField(OtherModel, related_name=..., blank=True)`: Many-to-many. Django creates an intermediate table. `related_name` is the reverse accessor.
    *   `OneToOneField(OtherModel, on_delete=models.CASCADE, primary_key=False)`: One-to-one (like `ForeignKey` with `unique=True`).

## Common Field Options

*   `null=True`: Allows `NULL` values in the database (default: `False`). Use for non-string fields.
*   `blank=True`: Allows the field to be blank in forms/admin (default: `False`). Use for string-based fields (`CharField`, `TextField`) or relationships (`ForeignKey`, `ManyToManyField`) that are optional.
*   `default=...`: Default value for the field.
*   `unique=True`: Enforces database uniqueness constraint.
*   `choices=[...]`: Provides a list of choices (tuples of `(value, display_name)`) for the field (used by forms/admin).
*   `primary_key=True`: Designates this field as the primary key.
*   `verbose_name="..."`: Human-readable name for the field.
*   `help_text="..."`: Additional help text in forms/admin.
*   `db_index=True`: Creates a database index on the field.
*   `editable=False`: Field will not be shown in the admin or model forms.

## `Meta` Options (`class Meta`)

Inner class within a model to define metadata.

*   `ordering = [...]`: Default ordering for QuerySets (e.g., `['-publish_date']`).
*   `verbose_name`, `verbose_name_plural`: Names used in the Django admin.
*   `unique_together = [...]`: Define multi-column uniqueness constraints (list of tuples).
*   `indexes = [...]`: Define more complex database indexes (`models.Index(...)`).
*   `db_table = '...'`: Specify a custom database table name.
*   `abstract = True`: Makes the model an abstract base class (no DB table created, used for inheritance).

## Migrations (`manage.py makemigrations` & `migrate`)

*   **Purpose:** Manage changes to your database schema based on changes to your `models.py` files.
*   **Workflow:**
    1.  Modify your `models.py`.
    2.  Run `python manage.py makemigrations [app_name]`: Django detects changes and creates a new migration file in the app's `migrations/` directory.
    3.  Run `python manage.py migrate`: Django applies any unapplied migration files to the database.
*   **Important:** Always run `makemigrations` and `migrate` after changing models. Review migration files before applying them.

## QuerySets (ORM Interaction)

Access QuerySets via the model's manager, typically `ModelName.objects`.

*   **Retrieving Objects:**
    *   `all()`: Get all objects.
    *   `filter(**kwargs)`: Get objects matching criteria (e.g., `Article.objects.filter(status='published', author__user__username='alice')`). Uses field lookups (`__exact`, `__iexact`, `__contains`, `__icontains`, `__gt`, `__lt`, `__in`, `__isnull`, `__year`, `__month`).
    *   `exclude(**kwargs)`: Get objects *not* matching criteria.
    *   `get(**kwargs)`: Get a *single* object matching criteria. Raises `DoesNotExist` or `MultipleObjectsReturned` if not exactly one match. Use `pk` for primary key lookup (`get(pk=1)`).
    *   `order_by(*fields)`: Order results (e.g., `order_by('-publish_date', 'title')`).
    *   Slicing: `[:5]`, `[10:20]`.
*   **Creating Objects:**
    *   `create(**kwargs)`: Creates, saves, and returns a new object.
    *   `obj = MyModel(...)`, `obj.save()`: Create instance, then save.
    *   `bulk_create([...])`: Efficiently create multiple objects in one query (doesn't call model `save()` methods).
*   **Updating Objects:**
    *   `obj.field = value`, `obj.save()`: Update instance, then save.
    *   `QuerySet.update(**kwargs)`: Update multiple objects directly in the database (efficient, but bypasses model `save()` methods and signals).
*   **Deleting Objects:**
    *   `obj.delete()`: Delete a single instance.
    *   `QuerySet.delete()`: Delete multiple objects.
*   **QuerySet Laziness:** QuerySets are lazy. The database query is only executed when the QuerySet is evaluated (e.g., iteration, slicing, `len()`, `list()`, `get()`).
*   **Optimization:**
    *   `select_related('foreign_key_field', 'one_to_one_field')`: Follows forward foreign-key/one-to-one relationships via JOINs.
    *   `prefetch_related('many_to_many_field', 'reverse_foreign_key_field')`: Performs separate lookups for related objects and joins them in Python.
    *   Use `count()` and `exists()` instead of `len()` or `if queryset:`.
    *   Use `values()` or `values_list()` if only specific fields are needed.
    *   Use `defer()` or `only()` to control field loading.

The Django ORM is powerful. Define models clearly, understand relationships and field options, manage schema changes with migrations, and use QuerySet methods effectively, including `select_related` and `prefetch_related` for performance.
# Django: Testing Strategies

Writing unit and integration tests for Django applications using the built-in framework.

## Core Concept: Automated Verification

Django's testing framework (based on `unittest`) helps ensure code correctness, prevent regressions, and facilitate refactoring.

*   **Test Runner:** `manage.py test` discovers and runs tests.
*   **`TestCase` (`django.test.TestCase`):** Subclass for tests. Each test method runs in a transaction that's rolled back, ensuring isolation. Includes a built-in test `Client`.
*   **Test Client (`self.client`):** Simulates HTTP requests (`GET`, `POST`, etc.) against views without a live server.
*   **Assertions:** Use `unittest` assertions (`assertEqual`, `assertTrue`, `assertRaises`) and Django's specific ones (`assertContains`, `assertRedirects`, `assertFormError`, `assertTemplateUsed`).
*   **Fixtures/Factories:** Use JSON/YAML fixtures (via `TestCase.fixtures` attribute) or factories (like `factory-boy`) to set up test data. `setUpTestData` (class method) is efficient for creating data shared by all tests in a class. `setUp` (instance method) runs before each test method.

## Writing Tests (`tests.py` or `tests/`)

```python
# myapp/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Article, Author, Category # Import models
from .forms import ArticleForm # Import forms

class ArticleModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.user = User.objects.create_user(username='testuser', password='password')
        cls.author = Author.objects.create(user=cls.user)
        cls.category = Category.objects.create(name='Testing', slug='testing')

    def test_was_published_recently_with_future_article(self):
        """was_published_recently() returns False for future articles."""
        future_date = timezone.now() + timezone.timedelta(days=30)
        future_article = Article(publish_date=future_date, author=self.author, title="Future")
        self.assertIs(future_article.was_published_recently(), False)

    # ... other model tests (string representation, custom methods) ...

class ArticleViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='password')
        cls.author = Author.objects.create(user=cls.user)
        cls.published_article = Article.objects.create(
            title="Published", slug="published", author=cls.author, status='published'
        )
        cls.draft_article = Article.objects.create(
            title="Draft", slug="draft", author=cls.author, status='draft'
        )

    # setUp method runs before each test (self.client is available)

    def test_article_list_view_status_code(self):
        response = self.client.get(reverse('myapp:article_list'))
        self.assertEqual(response.status_code, 200)

    def test_article_list_view_template(self):
        response = self.client.get(reverse('myapp:article_list'))
        self.assertTemplateUsed(response, 'myapp/article_list.html')

    def test_article_list_shows_published_article(self):
        response = self.client.get(reverse('myapp:article_list'))
        self.assertContains(response, self.published_article.title)
        self.assertNotContains(response, self.draft_article.title) # Assuming view filters drafts

    def test_article_detail_view_published(self):
        url = reverse('myapp:article_detail', kwargs={'pk': self.published_article.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.published_article.title)

    def test_article_detail_view_draft_404(self):
        # Assuming detail view only shows published articles
        url = reverse('myapp:article_detail', kwargs={'pk': self.draft_article.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_article_create_view_get_requires_login(self):
        response = self.client.get(reverse('myapp:article_create'))
        self.assertRedirects(response, f'/accounts/login/?next={reverse("myapp:article_create")}')

    def test_article_create_view_get_authenticated(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('myapp:article_create'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], ArticleForm)

    def test_article_create_view_post_valid(self):
        self.client.login(username='testuser', password='password')
        category = Category.objects.create(name='New Cat', slug='new-cat')
        data = {
            'title': 'Test Create Article',
            'slug': 'test-create-article',
            'author': self.author.pk, # Use PK for FK in POST
            'categories': [category.pk], # Use list of PKs for M2M
            'content': 'Test content.',
            'status': 'draft',
            'publish_date': timezone.now().strftime('%Y-%m-%dT%H:%M'),
        }
        response = self.client.post(reverse('myapp:article_create'), data)
        self.assertEqual(response.status_code, 302) # Should redirect on success
        self.assertTrue(Article.objects.filter(title='Test Create Article').exists())
        new_article = Article.objects.get(title='Test Create Article')
        self.assertEqual(new_article.author, self.author)
        self.assertIn(category, new_article.categories.all())

    def test_article_create_view_post_invalid(self):
        self.client.login(username='testuser', password='password')
        data = {'title': 'Bad'} # Missing required fields
        response = self.client.post(reverse('myapp:article_create'), data)
        self.assertEqual(response.status_code, 200) # Re-renders form
        self.assertFormError(response, 'form', 'content', 'This field is required.')
        self.assertFormError(response, 'form', 'author', 'This field is required.')
        self.assertFalse(Article.objects.filter(title='Bad').exists())

```

## Running Tests

```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test myapp

# Run tests for a specific test class
python manage.py test myapp.tests.ArticleViewTests

# Run a specific test method
python manage.py test myapp.tests.ArticleViewTests.test_article_detail_view_published

# Verbose output
python manage.py test -v 2
```

Write tests for models (custom methods) and views (status codes, templates, context, form handling, redirects, permissions). Use the test client to simulate user interactions. Aim for good coverage.
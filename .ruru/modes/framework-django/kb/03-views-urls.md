# Django: Views & URL Routing

Implementing request handling logic and mapping URLs to views.

## Part 1: Views (Request Handling)

In Django's MVT pattern, the **View** is responsible for receiving an `HttpRequest` object, performing necessary logic (interacting with models, processing forms), and returning an `HttpResponse` object (often by rendering a template).

Django offers two primary ways to write views:

1.  **Function-Based Views (FBVs):** Simple Python functions taking `request` as the first argument. Easy for simple cases. Use decorators like `@login_required`, `@permission_required`, `@require_http_methods`.
2.  **Class-Based Views (CBVs):** Python classes inheriting from `django.views.View` or generic views (`ListView`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView`). Use methods corresponding to HTTP verbs (`get()`, `post()`). Offer better code organization and reusability through inheritance and mixins (e.g., `LoginRequiredMixin`, `PermissionRequiredMixin`).

### Function-Based Views (FBVs) Example

```python
# myapp/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Article
from .forms import ArticleForm

# Example: List view
def article_list(request):
    articles = Article.objects.filter(status='published').order_by('-publish_date')
    context = {'articles': articles}
    return render(request, 'myapp/article_list.html', context)

# Example: Detail view
def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk, status='published')
    context = {'article': article}
    return render(request, 'myapp/article_detail.html', context)

# Example: Create view (handling GET and POST)
@login_required
@require_http_methods(["GET", "POST"])
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES or None)
        if form.is_valid():
            new_article = form.save(commit=False)
            # Assuming author is linked to user, set it here
            # new_article.author = request.user.author_profile
            new_article.save()
            form.save_m2m() # Important for ManyToMany
            return redirect('myapp:article_detail', pk=new_article.pk) # Redirect after POST
    else: # GET request
        form = ArticleForm()

    context = {'form': form}
    return render(request, 'myapp/article_form.html', context)
```

### Class-Based Views (CBVs) Example

```python
# myapp/views.py
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from .models import Article
from .forms import ArticleForm

# Example: List view using ListView
class ArticleListView(ListView):
    model = Article
    template_name = 'myapp/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        return Article.objects.filter(status='published').order_by('-publish_date')

# Example: Detail view using DetailView
class ArticleDetailView(DetailView):
    model = Article
    template_name = 'myapp/article_detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        return Article.objects.filter(status='published')

# Example: Create view using CreateView
class ArticleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'myapp/article_form.html'
    success_url = reverse_lazy('myapp:article_list') # Use reverse_lazy for URLs in class attributes
    permission_required = 'myapp.add_article'

    def form_valid(self, form):
        # form.instance.author = self.request.user.author_profile # Set author automatically
        return super().form_valid(form)

# Example: Update view using UpdateView
class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'myapp/article_form.html'
    # success_url defaults to model's get_absolute_url() if defined

    # def get_queryset(self):
    #     # Example: Ensure users can only edit their own articles
    #     return Article.objects.filter(author=self.request.user.author_profile)

# Example: Delete view using DeleteView
class ArticleDeleteView(LoginRequiredMixin, DeleteView):
    model = Article
    template_name = 'myapp/article_confirm_delete.html'
    success_url = reverse_lazy('myapp:article_list')

    # def get_queryset(self):
    #     # Example: Ensure users can only delete their own articles
    #     return Article.objects.filter(author=self.request.user.author_profile)
```

**FBVs vs. CBVs:** Use FBVs for simple views or highly custom logic. Use CBVs (especially generic ones) for standard CRUD and list/detail patterns to reduce boilerplate.

## Part 2: URL Routing (`urls.py`)

Django uses URL configurations (URLconfs) to map requested URLs to views.

*   **URLconf:** Python modules (`urls.py`) containing a list named `urlpatterns`.
*   **`urlpatterns`:** List mapping URL patterns to views.
*   **`path()`:** Defines a route: `path(route, view, kwargs=None, name=None)`.
    *   `route`: URL pattern string (e.g., `articles/<int:pk>/`).
    *   `view`: View function or `View.as_view()`.
    *   `name`: Unique name for reversing (`{% url 'name' %}`). **Highly recommended.**
*   **`include()`:** Used in project `urls.py` to include app `urls.py` files: `path('blog/', include('blog.urls', namespace='blog'))`.
*   **Namespaces:** Prevent URL name collisions between apps. Define `app_name = 'myapp'` in app `urls.py` and use the namespace in `include()` and reversing (`{% url 'myapp:detail' pk=1 %}`).
*   **Converters:** Capture parts of the URL: `<int:pk>`, `<slug:post_slug>`, `<str:username>`, `<uuid:id>`, `<path:full_path>`.

### Project `urls.py` Example

```python
# project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('articles/', include('myapp.urls', namespace='myapp')), # Include app URLs
    path('accounts/', include('django.contrib.auth.urls')), # Built-in auth
]
```

### App `urls.py` Example

```python
# myapp/urls.py
from django.urls import path
from . import views

app_name = 'myapp' # Define namespace

urlpatterns = [
    # /articles/
    path('', views.ArticleListView.as_view(), name='article_list'),
    # /articles/create/
    path('create/', views.ArticleCreateView.as_view(), name='article_create'),
    # /articles/123/
    path('<int:pk>/', views.ArticleDetailView.as_view(), name='article_detail'),
    # /articles/123/update/
    path('<int:pk>/update/', views.ArticleUpdateView.as_view(), name='article_update'),
    # /articles/123/delete/
    path('<int:pk>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),
    # /articles/category/tech/
    path('category/<slug:slug>/', views.category_detail, name='category_detail'), # Assuming FBV category_detail exists
]
```

### URL Reversing

Avoid hardcoding URLs.

*   **Templates:** `{% url 'namespace:url_name' arg1 arg2 ... %}`
    ```html
    <a href="{% url 'myapp:article_detail' pk=article.pk %}">View Article</a>
    ```
*   **Python:** `reverse('namespace:url_name', args=[...], kwargs={...})`
    ```python
    from django.urls import reverse
    from django.shortcuts import redirect

    return redirect(reverse('myapp:article_list'))
    # Or redirect using model's get_absolute_url() if defined
    # return redirect(article_object)
    ```

Define clear URL patterns using `path()`, organize them using `include()`, and always use named URLs with namespaces for maintainability.
# Django: Django REST Framework (DRF) Basics

Building REST APIs on top of Django applications using DRF.

## Core Concept: Toolkit for Building Web APIs

Django REST Framework (DRF) is a powerful toolkit for building Web APIs with Django, simplifying serialization, request/response handling, authentication, permissions, and routing.

**Key Features:**

*   **Serialization:** `Serializer` classes (`ModelSerializer`) convert complex data (models, querysets) to JSON/XML and handle deserialization/validation.
*   **Views & ViewSets:** `APIView`, generic views (`ListAPIView`, `RetrieveAPIView`), and ViewSets (`ModelViewSet`) for API endpoint logic. `ModelViewSet` provides default CRUD.
*   **Routers:** Automatically generate URL patterns for ViewSets.
*   **Authentication & Permissions:** Pluggable auth (Token, Session) and permissions (IsAuthenticated, custom) integrate with Django's auth.
*   **Request & Response:** Enhanced objects (`request.data`, flexible `Response`).
*   **Browsable API:** User-friendly HTML interface for development.

## Core Components & Workflow

**1. Serializers (`serializers.py`):**

Define how data is converted/validated. `ModelSerializer` is common.

```python
# myapp/serializers.py
from rest_framework import serializers
from .models import Article, Author, Category
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta: model = User; fields = ['id', 'username', 'first_name', 'last_name']

class AuthorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta: model = Author; fields = ['user', 'bio']

class CategorySerializer(serializers.ModelSerializer):
    class Meta: model = Category; fields = ['id', 'name', 'slug']

class ArticleSerializer(serializers.ModelSerializer):
    # Nested read-only serializer (optimize view queryset with select_related/prefetch_related)
    author = AuthorSerializer(read_only=True)
    # Use PrimaryKeyRelatedField for writable relationships
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, required=False
    )
    # Or SlugRelatedField for read-only slug representation
    # categories = serializers.SlugRelatedField(slug_field='slug', many=True, read_only=True)

    # Custom field validation
    def validate_title(self, value):
        if len(value) < 5: raise serializers.ValidationError("Title too short.")
        return value

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'author', 'categories',
            'content', 'publish_date', 'status', 'is_featured',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'publish_date']
        # Optionally: write_only_fields = [...]
```

**2. Views / ViewSets (`views.py`):**

Handle API request logic. `ModelViewSet` provides default CRUD actions (`list`, `retrieve`, `create`, `update`, `partial_update`, `destroy`).

```python
# myapp/views.py
from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Article, Category
from .serializers import ArticleSerializer, CategorySerializer
# from .permissions import IsAuthorOrReadOnly # Example custom permission

class CategoryViewSet(viewsets.ReadOnlyModelViewSet): # Read-only
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # , IsAuthorOrReadOnly]
    lookup_field = 'slug' # Use slug in URL instead of pk

    def get_queryset(self):
        queryset = Article.objects.all()
        # Optimize related fields needed by serializer
        queryset = queryset.select_related('author__user').prefetch_related('categories')
        # Filter based on status for list view if user is not staff
        if self.action == 'list' and not self.request.user.is_staff:
             queryset = queryset.filter(status='published')
        return queryset.order_by('-publish_date')

    # Automatically set author on creation
    def perform_create(self, serializer):
        # Assuming Author profile is linked via request.user.author_profile
        serializer.save(author=self.request.user.author_profile)

    # Example Custom Action (e.g., POST to /articles/{slug}/publish/)
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def publish(self, request, slug=None):
        article = self.get_object()
        if article.status != 'published':
            article.status = 'published'; article.publish_date = timezone.now(); article.save()
            return Response(self.get_serializer(article).data)
        return Response({'status': 'already published'}, status=status.HTTP_400_BAD_REQUEST)

# Example using generic view
class PublishedArticleListView(generics.ListAPIView):
    queryset = Article.objects.filter(status='published').select_related('author__user')
    serializer_class = ArticleSerializer
    permission_classes = [permissions.AllowAny]
```

**3. URLs (`urls.py`):**

Use Routers with ViewSets for automatic URL generation.

```python
# myapp/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'myapp_api' # API namespace

router = DefaultRouter()
router.register(r'articles', views.ArticleViewSet, basename='article')
router.register(r'categories', views.CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)), # Includes URLs like /articles/, /articles/{slug}/
    path('published/', views.PublishedArticleListView.as_view(), name='published-article-list'),
]

# --- In project/urls.py ---
# urlpatterns = [
#     ...
#     path('api/v1/', include('myapp.urls', namespace='myapp_api')),
#     # Add login/logout views to browsable API (optional)
#     path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
#     ...
# ]
```

**4. Authentication & Permissions:**

Configure defaults in `settings.py` (`REST_FRAMEWORK` dict) or per-view (`authentication_classes`, `permission_classes`). Common options: `SessionAuthentication`, `TokenAuthentication`, `permissions.AllowAny`, `permissions.IsAuthenticated`, `permissions.IsAdminUser`, `permissions.IsAuthenticatedOrReadOnly`.

**Request/Response:** Use `request.data` for parsed input and return data via `Response(data, status=...)`.

DRF speeds up API development. Create serializers, use ViewSets/generic views, and register with Routers. Configure auth/permissions.
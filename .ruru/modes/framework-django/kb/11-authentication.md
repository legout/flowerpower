# Django: Authentication & Authorization

Using Django's built-in system (`django.contrib.auth`) for managing users, permissions, and access control.

## Core Concept: Secure User Management

Django includes a robust system handling user accounts, groups, permissions, and cookie-based sessions.

**Key Components:**

*   **User Model:** Represents users. Default is `django.contrib.auth.models.User` (`username`, `password`, `email`, `first_name`, `last_name`, `is_staff`, `is_active`, `is_superuser`). Can be swapped for a custom user model.
*   **Authentication Backend:** Verifies credentials (e.g., `authenticate(request, username=..., password=...)`).
*   **Permissions:** Flags assigned to users/groups designating ability to perform actions (e.g., `myapp.add_article`). Auto-created for models. Checked via `user.has_perm('myapp.add_article')`.
*   **Groups:** Categorize users and assign permissions collectively.
*   **Password Management:** Securely hashes passwords (`set_password`, `check_password`).
*   **Session Framework:** Manages user sessions via signed cookies (`login(request, user)`, `logout(request)`).
*   **Views & Forms:** Built-in views (`LoginView`, `LogoutView`, `PasswordChangeView`) and forms (`AuthenticationForm`, `UserCreationForm`) for common tasks. Include via `path('accounts/', include('django.contrib.auth.urls'))`.

## Configuration (`settings.py`)

*   Ensure `django.contrib.auth`, `django.contrib.contenttypes`, `django.contrib.sessions` are in `INSTALLED_APPS`.
*   Ensure `SessionMiddleware` and `AuthenticationMiddleware` are in `MIDDLEWARE`.
*   `AUTH_USER_MODEL = 'yourapp.YourUserModel'`: If using a custom user model (define early!).
*   `LOGIN_URL = '/accounts/login/'`: Redirect target for `@login_required`.
*   `LOGIN_REDIRECT_URL = '/profile/'`: Redirect target after successful login.
*   `LOGOUT_REDIRECT_URL = '/'`: Redirect target after logout.

## Using the Auth System (`views.py`)

```python
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin # For CBVs
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm # Built-in forms

# --- Accessing User & Permissions ---
@login_required
def user_profile(request):
    # request.user is the logged-in User instance (or AnonymousUser)
    user = request.user
    is_editor = user.groups.filter(name='Editors').exists()
    can_add = user.has_perm('myapp.add_article')

    context = { 'user': user, 'is_editor': is_editor, 'can_add_article': can_add }
    return render(request, 'myapp/profile.html', context)

# --- Login / Logout (Custom View Example) ---
# Often use built-in views via include('django.contrib.auth.urls')
def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Welcome back, {username}!")
                # Redirect to settings.LOGIN_REDIRECT_URL or 'next' parameter
                next_url = request.POST.get('next', settings.LOGIN_REDIRECT_URL)
                return redirect(next_url)
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form, 'next': request.GET.get('next', '')})

def custom_logout(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect(settings.LOGOUT_REDIRECT_URL)

# --- User Registration (Custom View Example) ---
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST) # Use built-in or custom form
        if form.is_valid():
            user = form.save()
            login(request, user) # Optional: log user in immediately
            messages.success(request, "Registration successful!")
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# --- Protecting Views ---
# FBV Decorators
@login_required(login_url='/custom-login/') # Specify custom login URL if needed
def protected_view_fbv(request):
    # ...
    pass

@permission_required('myapp.change_article', raise_exception=True) # raise_exception shows 403
def change_article_fbv(request):
    # ...
    pass

# CBV Mixins
class ProtectedViewCBV(LoginRequiredMixin, View):
    login_url = '/custom-login/'
    # ...

class ChangeArticleCBV(PermissionRequiredMixin, UpdateView):
    permission_required = 'myapp.change_article'
    # ...

# Manual Check
def manual_perm_check_view(request):
    if not request.user.has_perm('myapp.view_special_report'):
        return HttpResponseForbidden("Access Denied")
    # ...
    pass

# --- Groups ---
# Assign user to a group (e.g., in admin or programmatically)
# editor_group = Group.objects.get(name='Editors')
# user.groups.add(editor_group)
```

## Custom User Models

*   If default `User` isn't sufficient (e.g., email as username).
*   **Best Practice:** Define at the *start* of a project. Changing later is complex.
*   Inherit from `AbstractBaseUser` (full control) or `AbstractUser` (keeps most defaults).
*   Define `USERNAME_FIELD`, `REQUIRED_FIELDS`. Create a custom `BaseUserManager`.
*   Set `AUTH_USER_MODEL = 'yourapp.YourUserModel'` in `settings.py`.

Leverage the built-in auth system, views, and forms where possible. Use decorators/mixins for access control. Customize the `User` model early if needed.
# Flask: User Sessions & Authentication (Flask-Login)

Handling user login, logout, and session management using the Flask-Login extension.

## Core Concept

Flask-Login provides user session management for Flask. It handles common tasks like logging users in, logging them out, and remembering them across browser sessions. It integrates well with Flask's session system and requires you to provide a user loader callback.

**Note:** Flask-Login handles session management (remembering who is logged in) but **not** password hashing/verification or user registration logic. You typically combine it with a password hashing library (like Werkzeug's security helpers or Passlib) and your own registration views/logic.

## Setup

1.  **Install:**
    ```bash
    pip install Flask-Login
    # Also likely need Flask-SQLAlchemy for user model and Flask-WTF for forms
    pip install Flask-SQLAlchemy Flask-WTF
    ```
2.  **Initialize Extension:**
    ```python
    # extensions.py
    from flask_login import LoginManager

    login_manager = LoginManager()
    # Configure login view: The endpoint name (view function name) for the login page.
    # Flask-Login redirects users here if they try to access a protected page without being logged in.
    login_manager.login_view = 'auth.login' # Assuming 'auth' is the blueprint name and 'login' is the view function
    # Optional: Customize the message flashed to the user when redirected
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info' # Bootstrap category

    # In your app factory (create_app function)
    from .extensions import login_manager
    def create_app(config_class=Config):
        app = Flask(__name__)
        app.config.from_object(config_class)
        # ... other extensions (like db) ...
        login_manager.init_app(app)
        # ... register blueprints ...
        return app
    ```
3.  **User Model:** Your User model (e.g., defined with Flask-SQLAlchemy) needs to inherit from `UserMixin` provided by Flask-Login. This adds default implementations for required properties and methods.
    ```python
    # models.py
    from flask_login import UserMixin
    from werkzeug.security import generate_password_hash, check_password_hash
    from app.extensions import db # Assuming db = SQLAlchemy() defined elsewhere

    class User(UserMixin, db.Model): # Inherit from UserMixin
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(64), index=True, unique=True)
        email = db.Column(db.String(120), index=True, unique=True)
        password_hash = db.Column(db.String(128))

        # Required methods (UserMixin provides defaults, but password handling is custom)
        def set_password(self, password):
            self.password_hash = generate_password_hash(password)

        def check_password(self, password):
            return check_password_hash(self.password_hash, password)

        # __repr__ is helpful for debugging
        def __repr__(self):
            return f'<User {self.username}>'

    ```
4.  **User Loader Callback:** You **must** provide a user loader function decorated with `@login_manager.user_loader`. This function takes a user ID (string) and returns the corresponding user object, or `None` if the ID is invalid. Flask-Login uses this to load the user object from the ID stored in the session.
    ```python
    # models.py or auth/routes.py or extensions.py
    from .extensions import login_manager
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # user_id is stored as a string in the session, convert to int for query
        return User.query.get(int(user_id))
    ```

## Logging Users In/Out

*   **`login_user(user, remember=False)`:** Logs a user in. Call this after verifying credentials. Stores the user's ID in the session. If `remember=True`, uses a "remember me" cookie for longer persistence.
*   **`logout_user()`:** Logs the current user out, clearing their ID from the session and removing the "remember me" cookie if present.
*   **`current_user`:** A proxy object provided by Flask-Login, available in views and templates. Represents the currently logged-in user object (loaded via the `user_loader`). If no user is logged in, it's an anonymous user object where `is_authenticated` is `False`.

```python
# auth/routes.py (example using a Blueprint named 'auth')
from flask import render_template, flash, redirect, url_for, request, Blueprint
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm # Assume LoginForm exists
from app.models import User
# from werkzeug.urls import url_parse # For safe redirect handling

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: # Check if already logged in
        return redirect(url_for('main.index')) # Assuming a 'main' blueprint for index
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        # Log the user in
        login_user(user, remember=form.remember_me.data)
        flash(f'Welcome back, {user.username}!')
        next_page = request.args.get('next')
        # Basic redirect safety check
        if not next_page: # or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user() # Log the user out
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

```

## Protecting Views (`@login_required`)

*   Decorate view functions with `@login_required` (imported from `flask_login`) to require users to be logged in to access them.
*   If an unauthenticated user tries to access a protected view, Flask-Login redirects them to the `login_manager.login_view` endpoint, storing the originally requested URL in the session (or query string) so they can be redirected back after logging in.

```python
# app/routes.py (example main blueprint)
from flask import render_template, Blueprint
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
def index():
    return render_template('index.html', title='Home')

@main_bp.route('/profile')
@login_required # Protect this view
def profile():
    # current_user is available here
    return render_template('profile.html', title='Profile', user=current_user)
```

## Using `current_user` in Templates

The `current_user` object is automatically available in templates rendered via `render_template`. You can check its properties:

```html
<!-- templates/base.html -->
<nav>
  <a href="{{ url_for('main.index') }}">Home</a>
  {% if current_user.is_authenticated %}
    <a href="{{ url_for('main.profile') }}">Profile</a>
    <a href="{{ url_for('auth.logout') }}">Logout ({{ current_user.username }})</a>
  {% else %}
    <a href="{{ url_for('auth.login') }}">Login</a>
    <a href="{{ url_for('auth.register') }}">Register</a>
  {% endif %}
</nav>
```

Flask-Login simplifies managing user sessions and protecting views in Flask applications.

*(Refer to the official Flask-Login documentation.)*
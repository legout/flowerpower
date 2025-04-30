# Flask: Forms with Flask-WTF

Handling web forms, validation, and CSRF protection using the Flask-WTF extension.

## Core Concept

Flask doesn't have built-in form handling like Django. The most common way to handle forms in Flask is using the **Flask-WTF** extension, which integrates the powerful **WTForms** library.

**Benefits:**
*   Defines forms as Python classes.
*   Handles form data parsing from `request.form`.
*   Provides built-in validators (required, length, email, etc.) and supports custom validators.
*   Generates HTML for form fields.
*   Integrates CSRF (Cross-Site Request Forgery) protection automatically.

## Setup

1.  **Install:**
    ```bash
    pip install Flask-WTF # Also installs WTForms
    ```
2.  **Configure `SECRET_KEY`:** Flask-WTF requires the Flask app's `SECRET_KEY` to be set for CSRF protection. Ensure this is configured (ideally loaded from an environment variable).
    ```python
    # config.py or main app file
    import os

    class Config:
        SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
        # ... other config

    app.config.from_object(Config)
    ```
3.  **Initialize Extension (Optional but recommended with App Factory):**
    ```python
    # extensions.py (example)
    from flask_wtf.csrf import CSRFProtect

    csrf = CSRFProtect()

    # In your app factory (create_app function)
    from .extensions import csrf
    def create_app(config_class=Config):
        app = Flask(__name__)
        app.config.from_object(config_class)
        csrf.init_app(app) # Initialize CSRF protection
        # ... register blueprints, other extensions ...
        return app
    ```
    If not using an app factory, initialize directly: `csrf = CSRFProtect(app)`.

## Defining Forms (`forms.py`)

*   Create a file (e.g., `app/forms.py`).
*   Import `FlaskForm` from `flask_wtf`.
*   Import desired field types from `wtforms` (e.g., `StringField`, `PasswordField`, `BooleanField`, `SubmitField`).
*   Import validators from `wtforms.validators` (e.g., `DataRequired`, `Length`, `Email`, `EqualTo`, `ValidationError`).
*   Define a class inheriting from `FlaskForm`.
*   Define form fields as class attributes, instantiating field types and passing validators in a list.

```python
# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
# from .models import User # If needed for custom validation

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Register')

    # Custom validator: Check if username already exists
    def validate_username(self, username):
        # user = User.query.filter_by(username=username.data).first()
        # if user is not None:
        #     raise ValidationError('Please use a different username.')
        # Placeholder check:
        if username.data == 'admin':
             raise ValidationError('Username "admin" is not allowed.')

    # Custom validator: Check if email already exists
    def validate_email(self, email):
        # user = User.query.filter_by(email=email.data).first()
        # if user is not None:
        #     raise ValidationError('Please use a different email address.')
        pass # Placeholder

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=120)])
    body = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Submit Post')
```

## Using Forms in Views (`routes.py`)

1.  **Import** the form class.
2.  **Instantiate** the form in your view function.
3.  **Check for Submission & Validation:** Use `form.validate_on_submit()`. This checks if the request method is `POST` (or `PUT`/`PATCH`) *and* if the submitted data passes all validators (including CSRF).
4.  **Access Data:** If valid, access cleaned data via `form.<field_name>.data`.
5.  **Render Form:** Pass the form instance to `render_template`.

```python
# app/routes.py
from flask import render_template, flash, redirect, url_for, request
from app import app # Assuming app instance is created elsewhere
from app.forms import LoginForm, RegistrationForm # Import forms
# from app.models import User # Import models if needed
# from flask_login import current_user, login_user, logout_user # Example Login

@app.route('/login', methods=['GET', 'POST'])
def login():
    # if current_user.is_authenticated:
    #     return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit(): # Checks method and validates data + CSRF
        # user = User.query.filter_by(username=form.username.data).first()
        # if user is None or not user.check_password(form.password.data):
        #     flash('Invalid username or password')
        #     return redirect(url_for('login'))
        # login_user(user, remember=form.remember_me.data)
        flash(f'Login requested for user {form.username.data}, remember_me={form.remember_me.data}')
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '': # Security check for redirects
            next_page = url_for('index')
        return redirect(next_page)
    # If GET request or validation failed
    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # user = User(username=form.username.data, email=form.email.data)
        # user.set_password(form.password.data)
        # db.session.add(user)
        # db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

```

## Rendering Forms in Templates (`template.html`)

*   **CSRF Token:** Include `{{ form.hidden_tag() }}` inside your `<form>` tag. This renders the hidden CSRF token field (and any other hidden fields like `SubmitField`). **This is essential for security.**
*   **Fields:** Render individual fields using `{{ form.<field_name>.label }}`, `{{ form.<field_name>(**kwargs) }}`, and display errors with `form.<field_name>.errors`.

```html
<!-- templates/login.html -->
{% extends "base.html" %}

{% block content %}
    <h1>Sign In</h1>
    <form action="" method="post" novalidate>
        {{ form.hidden_tag() }} {# Renders CSRF token and other hidden fields #}
        <p>
            {{ form.username.label }}<br>
            {{ form.username(size=32) }}<br>
            {% for error in form.username.errors %}
            <span style="color: red;">[{{ error }}]</span>
            {% endfor %}
        </p>
        <p>
            {{ form.password.label }}<br>
            {{ form.password(size=32) }}<br>
            {% for error in form.password.errors %}
            <span style="color: red;">[{{ error }}]</span>
            {% endfor %}
        </p>
        <p>{{ form.remember_me() }} {{ form.remember_me.label }}</p>
        <p>{{ form.submit() }}</p>
    </form>
{% endblock %}
```

Flask-WTF provides a robust and secure way to handle forms and validation in Flask applications.

*(Refer to the official Flask-WTF documentation.)*
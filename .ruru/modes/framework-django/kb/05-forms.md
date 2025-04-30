# Django: Forms

Handling user input, validation, and rendering HTML forms using Django's Forms framework.

## Core Concept: Processing User Input Securely

Django's Forms library provides a structured and secure way to handle HTML forms, separating field definition, validation logic, and rendering.

*   **Benefits:** Centralized validation, automatic HTML widget rendering, built-in CSRF protection, reusability, provides `cleaned_data`.
*   **Types:**
    *   `forms.Form`: Define fields manually. Use when not directly mapping to a single model.
    *   `forms.ModelForm`: Automatically generates fields based on a Django `Model`. Simplifies CRUD forms.

## Defining Forms (`forms.py`)

```python
# myapp/forms.py
from django import forms
from .models import Article # Assuming Article model exists

# Example using forms.Form
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, label="Your Name")
    email = forms.EmailField(required=True, help_text="A valid email address.")
    subject = forms.CharField(max_length=150)
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), required=True)
    subscribe = forms.BooleanField(required=False, initial=False, label="Subscribe to newsletter?")

    # Example: Custom validation for a specific field
    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        if subject and len(subject) < 5:
            raise forms.ValidationError("Subject must be at least 5 characters long.")
        return subject

    # Example: Custom validation involving multiple fields
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        subject = cleaned_data.get("subject")

        if name and subject and name.lower() in subject.lower():
            self.add_error('subject', "Subject cannot contain your name.")
            # Or raise forms.ValidationError("...") for non-field error

        return cleaned_data


# Example using forms.ModelForm
class ArticleForm(forms.ModelForm):
    confirm_publish = forms.BooleanField(required=False, label="I confirm this is ready to publish")

    class Meta:
        model = Article
        # Include specific fields
        fields = ['title', 'slug', 'author', 'categories', 'content', 'status', 'is_featured', 'publish_date']
        # Or exclude specific fields: exclude = ['created_at', 'updated_at']
        # Or use all fields: fields = '__all__'

        # Customize widgets
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
            'publish_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'categories': forms.CheckboxSelectMultiple, # Example for ManyToMany
        }
        # Customize labels and help texts
        labels = { 'is_featured': 'Feature this article?' }
        help_texts = { 'slug': 'URL-friendly version of the title.' }

    # Custom validation for ModelForm fields works the same way
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title and len(title) < 10:
            raise forms.ValidationError("Title must be at least 10 characters long.")
        return title

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        confirm_publish = cleaned_data.get('confirm_publish')

        if status == 'published' and not confirm_publish:
            self.add_error('confirm_publish', 'You must confirm before publishing.')

        return cleaned_data

```

*   **Common Fields:** `CharField`, `IntegerField`, `BooleanField`, `DateField`, `DateTimeField`, `EmailField`, `URLField`, `ChoiceField`, `ModelChoiceField` (FK), `ModelMultipleChoiceField` (M2M), `FileField`, `ImageField`.
*   **Common Widgets:** `TextInput`, `PasswordInput`, `Textarea`, `CheckboxInput`, `Select`, `RadioSelect`, `CheckboxSelectMultiple`, `DateInput`, `DateTimeInput`, `FileInput`.

## Using Forms in Views (`views.py`)

```python
# myapp/views.py
from django.shortcuts import render, redirect
from .forms import ArticleForm
# ... other imports

def article_create(request):
    if request.method == 'POST':
        # Populate form with submitted data (and files if applicable)
        form = ArticleForm(request.POST, request.FILES or None)
        if form.is_valid(): # Trigger validation
            # Access cleaned data: form.cleaned_data['field_name']
            new_article = form.save(commit=False)
            # Set fields not included in the form, like the author
            # new_article.author = request.user.author_profile
            new_article.save() # Save the main object
            form.save_m2m() # Save ManyToMany relationships (only needed for ModelForm with commit=False)
            return redirect(new_article.get_absolute_url()) # Redirect after successful POST
        # If form is invalid, it will be re-rendered with errors below
    else: # GET request
        form = ArticleForm() # Create an unbound (empty) form

    context = {'form': form}
    return render(request, 'myapp/article_form.html', context)
```

## Rendering Forms in Templates (`.html`)

```html
<!-- myapp/templates/myapp/article_form.html -->
{% extends "base.html" %}

{% block content %}
  <h2>{% if form.instance.pk %}Edit Article{% else %}Create Article{% endif %}</h2>

  <form method="post" enctype="multipart/form-data"> {# Use enctype for file uploads #}
    {% csrf_token %} {# REQUIRED for security against CSRF attacks #}

    {# Different ways to render the form: #}

    {# 1. Render all fields as paragraphs #}
    {{ form.as_p }}

    {# 2. Render all fields as table rows #}
    {# {{ form.as_table }} #}

    {# 3. Render all fields as list items #}
    {# {{ form.as_ul }} #}

    {# 4. Manual rendering (more control) #}
    {# {% for field in form %}
      <div class="fieldWrapper">
          {{ field.errors }} {# Display field-specific errors #}
          {{ field.label_tag }}
          {{ field }} {# Renders the widget #}
          {% if field.help_text %}
            <p class="help">{{ field.help_text|safe }}</p>
          {% endif %}
      </div>
    {% endfor %} #}

    {# Display non-field errors (from form.clean()) #}
    {% if form.non_field_errors %}
        <div class="non-field-errors">
            {% for error in form.non_field_errors %}
                <p class="error">{{ error }}</p>
            {% endfor %}
        </div>
    {% endif %}

    <button type="submit">Save Article</button>
  </form>
{% endblock %}
```

Use `ModelForm` for model-based forms and `Form` for custom scenarios. Always include `{% csrf_token %}`. Validate forms in views using `is_valid()` before accessing `cleaned_data` or saving.
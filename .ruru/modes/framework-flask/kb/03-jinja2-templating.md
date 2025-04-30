# Flask: Jinja2 Templating

Using the Jinja2 template engine integrated with Flask.

## Core Concept

Flask uses the powerful Jinja2 template engine by default. Templates allow you to separate the presentation logic (HTML structure) from your application logic (Python view functions). Jinja2 provides syntax for embedding variables, control structures, and expressions within your HTML files.

## Setup and Rendering

*   **Templates Folder:** By default, Flask looks for templates in a `templates` folder located in your application's root directory or within blueprint directories.
*   **`render_template()`:** Import and use the `render_template` function from Flask to render a template file. Pass the template filename and any context variables as keyword arguments.

```python
from flask import Flask, render_template

app = Flask(__name__)
# Assumes a 'templates' folder exists in the same directory as this script

@app.route('/')
def index():
    page_title = "Homepage"
    user_name = "Alice" # In real app, get from session or DB
    items = ["Apple", "Banana", "Cherry"]
    # Pass variables to the template context
    return render_template('index.html', title=page_title, name=user_name, item_list=items)

@app.route('/about')
def about():
    return render_template('about.html') # Can render without extra context
```

## Jinja2 Syntax Basics

*   **`{{ ... }}` for Variables:** Outputs the value of a variable or expression.
    *   `{{ my_variable }}`
    *   `{{ user.name }}` (Access attribute)
    *   `{{ my_dict['key'] }}` (Access dictionary key)
    *   `{{ my_list[0] }}` (Access list index)
    *   HTML escaping is **on by default**. Use `|safe` filter *only* for trusted HTML content.
*   **`{% ... %}` for Statements/Tags:** Control flow, loops, inheritance, etc.
    *   `{% if condition %}` ... `{% elif condition %}` ... `{% else %}` ... `{% endif %}`
    *   `{% for item in item_list %}` ... `{% else %}` ... `{% endfor %}`
    *   `{% block block_name %}` ... `{% endblock %}` (Template inheritance)
    *   `{% extends 'base.html' %}` (Template inheritance)
    *   `{% include 'partial.html' %}` (Include another template)
    *   `{% set my_var = 'value' %}` (Set a variable within the template)
    *   `{% macro my_macro(arg1) %}` ... `{% endmacro %}` (Define reusable template snippets)
*   **`{# ... #}` for Comments:** Template comments (not included in the final HTML output).

## Example Template (`templates/index.html`)

```html
{# This is a Jinja2 comment #}
{% extends 'base.html' %} {# Assumes base.html exists #}

{% block title %}{{ title }} - My Site{% endblock %}

{% block content %}
  <h1>Welcome, {{ name | default('Guest') }}!</h1> {# Use default filter #}

  {% if item_list %}
    <h2>Your Items:</h2>
    <ul>
      {% for item in item_list %}
        <li class="item-{{ loop.index0 }}">{{ loop.index }}. {{ item | upper }}</li> {# Use loop variable and upper filter #}
      {% endfor %}
    </ul>
  {% else %}
    <p>You have no items.</p>
  {% endif %}

  <p>
    Go to the <a href="{{ url_for('about') }}">About Page</a>. {# Use url_for helper #}
  </p>

  {# Example of setting a variable #}
  {% set current_year = 2024 %}
  <p>Current Year (set in template): {{ current_year }}</p>

{% endblock %}
```

## Template Inheritance

*   Define a base template (`base.html`) with common structure and `{% block %}` tags.
*   Child templates use `{% extends 'base.html' %}` and override specific blocks.
*   `{{ super() }}` inside a block renders the content of the parent block.

## Context Processors (`@app.context_processor`)

*   Functions decorated with `@app.context_processor` inject variables automatically into the context of *all* templates rendered by the application or blueprint.
*   Useful for common variables like the current user, site name, navigation items.

```python
@app.context_processor
def inject_user():
    # Assume get_current_user() returns the logged-in user object or None
    user = get_current_user()
    return dict(current_user=user) # Now 'current_user' is available in all templates

@app.context_processor
def utility_processor():
    def format_price(amount):
        return f"${amount:.2f}"
    return dict(format_price=format_price) # Make function available as filter/function
```
```html
{# In any template #}
{% if current_user %}
  <p>Logged in as {{ current_user.username }}</p>
{% endif %}
<p>Price: {{ item.price | format_price }}</p> {# Using injected function as filter #}
```

## Filters and Tests

*   **Filters (`|`):** Modify variables before output (e.g., `{{ name|upper }}`, `{{ date|dateformat }}`). Many built-in filters available.
*   **Tests (`is`):** Check conditions (e.g., `{% if user is defined %}`, `{% if count is odd %}`).

Jinja2 provides a flexible and powerful way to generate dynamic HTML within your Flask applications.

*(Refer to the official Flask Templating documentation and the Jinja2 Template Designer Documentation.)*
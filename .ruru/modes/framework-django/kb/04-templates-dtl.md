# Django: Templates (DTL - Django Template Language)

Creating dynamic HTML using Django's built-in template system for rendering presentation logic.

## Core Concept: Presentation Logic

Django Templates are text files (usually HTML) containing static content mixed with special syntax for inserting dynamic data and basic logic. The template engine processes these files, replacing variables and executing tags based on a **context** (a dictionary passed from the view), to generate the final HTML response.

*   **Syntax:** Uses `{{ variable }}`, `{% tag %}`, `{{ variable|filter }}`, `{# comment #}`.
*   **Context:** Dictionary passed from the view (`render(request, template_name, context)`). Variables are looked up here.
*   **Template Loading:** Django searches directories specified in `settings.py` (`TEMPLATES['DIRS']`) and within apps (`APP_DIRS=True`).
*   **Template Inheritance:** Define a base template (`base.html`) with `{% block %}` tags. Child templates use `{% extends 'base.html' %}` and override blocks.
*   **Auto-escaping:** `{{ variable }}` output is HTML-escaped by default for XSS protection. Use `|safe` filter only on trusted content.

## Basic Syntax Examples

```html
<!-- myapp/templates/myapp/article_detail.html -->
{% extends "base.html" %} <!-- Inherit from base template -->
{% load static %} <!-- Load static files tag library -->

{% block title %}{{ article.title }} - My Blog{% endblock %} <!-- Override title block -->

{% block content %} <!-- Override content block -->
  <article>
    <h1>{{ article.title }}</h1>

    {# Display author information if available #}
    {% if article.author %}
      <p>By {{ article.author.user.get_full_name|default:"Unknown Author" }} on {{ article.publish_date|date:"F j, Y" }}</p>
    {% else %}
      <p>Published on {{ article.publish_date|date:"F j, Y" }}</p>
    {% endif %}

    {# Display categories using a loop #}
    {% if article.categories.all %}
      <p>Categories:
        {% for category in article.categories.all %}
          <a href="{% url 'myapp:category_detail' category.slug %}">{{ category.name }}</a>{% if not forloop.last %}, {% endif %}
        {% empty %}
          No categories assigned.
        {% endfor %}
      </p>
    {% endif %}

    {# Display article content - use |safe only if content is trusted HTML #}
    <div class="content">
      {{ article.content|linebreaksbr }} {# Convert line breaks to <br> #}
    </div>

    {# Link to static file #}
    <img src="{% static 'images/default_article.png' %}" alt="Article image">

    {# Link back to list view using URL reversing #}
    <p><a href="{% url 'myapp:article_list' %}">Back to list</a></p>

  </article>
{% endblock %}
```

```html
<!-- templates/base.html (Example Base Template) -->
{% load static %}
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{% block title %}My Site{% endblock %}</title>
    <link rel="stylesheet" href="{% static 'css/base.css' %}">
    {% block extra_head %}{% endblock %}
</head>
<body>
    <header>
        <h1>My Awesome Blog</h1>
        <nav>
            <a href="{% url 'myapp:article_list' %}">Home</a>
            <!-- Add other navigation links -->
        </nav>
    </header>

    <main>
        {% block content %}
        <p>Default content goes here.</p>
        {% endblock %}
    </main>

    <footer>
        <p>&copy; {% now "Y" %} My Site</p> {# Example using 'now' tag #}
    </footer>
    {% block extra_body %}{% endblock %}
</body>
</html>
```

## Key Tags (`{% %}`)

*   **Control Flow:** `if`/`elif`/`else`/`endif`, `for`/`empty`/`endfor` (provides `forloop.counter`, `forloop.first`, `forloop.last`).
*   **Inheritance:** `extends 'base.html'`, `block <name>`/`endblock`.
*   **Loading:** `load <tag_library>` (e.g., `{% load static %}`, `{% load humanize %}`).
*   **URLs/Static:** `url 'namespace:name' arg1 ...`, `static 'path/file.css'`.
*   **Security:** `csrf_token` (Essential for POST forms).
*   **Inclusion:** `include 'template.html'`.
*   **Other:** `now "Y-m-d"`, `with var=value as name`, `comment`/`endcomment`.

## Key Filters (`{{ | }}`)

*   **Formatting:** `date:"D d M Y"`, `time:"H:i"`, `filesizeformat`, `linebreaks`, `linebreaksbr`, `lower`, `upper`, `title`, `capfirst`.
*   **Manipulation:** `length`, `truncatewords:N`, `truncatechars:N`, `pluralize`, `add`, `cut:" "`.
*   **Safety:** `safe` (disables auto-escaping - use with caution!), `escape`.
*   **Defaults:** `default:"fallback_value"`, `default_if_none:"fallback"`.
*   **Joining/Splitting:** `join:", "`, `split`.

Keep complex logic in views. Leverage template inheritance and built-in tags/filters. Be mindful of security (`|safe`, `{% csrf_token %}`).
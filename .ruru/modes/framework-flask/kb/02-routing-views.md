# Flask: Routing & Views

Mapping URLs to Python functions (views) that handle requests and generate responses.

## Core Concept: Routing (`@app.route` / `@blueprint.route`)

*   **Decorator:** The `@app.route()` or `@blueprint.route()` decorator is used to register a view function to handle requests for a specific URL path.
*   **Rule:** The first argument to the decorator is the URL rule (path).
*   **Methods:** By default, routes only accept `GET` requests. Specify other methods using the `methods` argument: `methods=['GET', 'POST']`.
*   **Endpoint:** Flask automatically assigns an endpoint name (usually the view function's name). You can specify a custom one with `endpoint='...'`. This name is used for URL generation (`url_for`).

## View Functions

*   **Definition:** A Python function that receives request data (implicitly via the `request` context local) and returns a response.
*   **Return Value:** The return value determines the response sent to the client. It can be:
    *   A string (Flask converts it to a response object with `text/html` mimetype).
    *   A tuple: `(response_body, status_code, headers_dict)` or `(response_body, status_code)` or `(response_body, headers_dict)`.
    *   A `Response` object instance (`from flask import Response`).
    *   A WSGI callable.
    *   Commonly, use helper functions:
        *   `render_template('template.html', **context)`: Renders a Jinja2 template.
        *   `jsonify(data_dict)`: Creates a JSON response.
        *   `redirect(url_for('endpoint_name'))`: Creates a redirect response.

## Variable Rules / URL Converters

*   Capture parts of the URL path and pass them as arguments to the view function.
*   **Syntax:** `<converter:variable_name>`
*   **Built-in Converters:**
    *   `string`: (Default) Accepts any text without a slash.
    *   `int`: Accepts positive integers.
    *   `float`: Accepts positive floating-point values.
    *   `path`: Like `string` but *does* accept slashes.
    *   `uuid`: Accepts UUID strings.
*   The variable name in the rule must match the argument name in the view function.

## Example: Basic Routing

```python
from flask import Flask, request, render_template, jsonify, redirect, url_for, abort

app = Flask(__name__)

# Route for the homepage
@app.route('/')
def index():
    return '<h1>Hello, World!</h1>'

# Route with a path variable (string)
@app.route('/user/<username>')
def show_user_profile(username):
    # You might fetch user data from a database here
    return f'User: {username}'

# Route with an integer path variable
@app.route('/post/<int:post_id>')
def show_post(post_id):
    # Fetch post by ID
    post = get_post_from_db(post_id) # Assume this function exists
    if not post:
        abort(404) # Raise a 404 Not Found error
    return render_template('post_detail.html', post=post)

# Route handling multiple methods (GET and POST)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Process login form data (e.g., from request.form)
        username = request.form.get('username')
        password = request.form.get('password')
        if check_login(username, password): # Assume this function exists
            # Log user in (e.g., set session variable)
            return redirect(url_for('index')) # Redirect to homepage after login
        else:
            error = 'Invalid credentials'
            return render_template('login.html', error=error) # Re-render form with error
    else: # GET request
        return render_template('login.html') # Show the login form

# Example returning JSON
@app.route('/api/data')
def api_data():
    data = {'key': 'value', 'items': [1, 2, 3]}
    return jsonify(data)

# Example using url_for
@app.route('/profile')
def profile():
    # Example redirect if user not logged in
    # if not current_user.is_authenticated:
    #     return redirect(url_for('login', next=request.url))
    return 'User Profile Page'

```

## Class-Based Views (`MethodView`)

*   Alternative way to structure views, especially useful for REST APIs or when different HTTP methods require distinct logic but operate on the same resource/URL.
*   Import `View` or `MethodView` from `flask.views`.
*   Define methods corresponding to HTTP methods (`get`, `post`, `put`, `delete`, etc.).
*   Register using `app.add_url_rule('/path', view_func=MyView.as_view('endpoint_name'))`.

```python
from flask import Flask, request, jsonify
from flask.views import MethodView

app = Flask(__name__)

class ItemAPI(MethodView):
    # In a real app, you'd likely interact with a database
    items = {1: {"name": "Item 1"}, 2: {"name": "Item 2"}}

    def get(self, item_id=None):
        """Handles GET requests."""
        if item_id is None:
            # Return list of items
            return jsonify(list(self.items.values()))
        else:
            # Return specific item
            item = self.items.get(item_id)
            if item:
                return jsonify(item)
            else:
                return jsonify({"error": "Item not found"}), 404

    def post(self):
        """Handles POST requests (create new item)."""
        if not request.json or not 'name' in request.json:
            return jsonify({"error": "Missing name"}), 400
        new_id = max(self.items.keys() or [0]) + 1
        self.items[new_id] = {"name": request.json['name']}
        return jsonify(self.items[new_id]), 201

    def delete(self, item_id):
        """Handles DELETE requests."""
        if item_id in self.items:
            del self.items[item_id]
            return '', 204 # No Content
        else:
            return jsonify({"error": "Item not found"}), 404

# Register the class-based view for different routes
item_view = ItemAPI.as_view('item_api')
app.add_url_rule('/items/', defaults={'item_id': None}, view_func=item_view, methods=['GET',])
app.add_url_rule('/items/', view_func=item_view, methods=['POST',])
app.add_url_rule('/items/<int:item_id>', view_func=item_view, methods=['GET', 'DELETE'])

```

Routing and views are the core components connecting incoming requests to your application logic in Flask.

*(Refer to the official Flask documentation on Routing and Views.)*
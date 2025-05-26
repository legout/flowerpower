# FlowerPower Web Application – Developer Guide

## Architecture Overview

- **Sanic**: Async web server for handling HTTP requests.
- **htpy**: Type-safe HTML templating for UI rendering.
- **Datastar**: Enables reactive, real-time frontend updates without JavaScript frameworks.

### Component Interaction
- Sanic serves API endpoints and static assets.
- htpy generates HTML views, integrated with Datastar for dynamic UI.
- Datastar manages frontend state and real-time updates via Server-Sent Events (SSE).

## Key Modules

- `web_ui/app.py`: Main Sanic app, route definitions, Datastar integration.
- `web_ui/config.py`: Configuration settings for the web UI.
- `web_ui/run.py`: Application entry point.
- `web_ui/projects_data.json`: Stores project metadata.
- `web_ui/test_app.py`: Test suite for the web UI.

## API Endpoints

> _Documented endpoints should be listed here. See `app.py` for route definitions._

Example:
```python
@app.route("/api/projects")
async def list_projects(request):
    ...
```

## Development Environment Setup

1. Clone the repository and install dependencies:
   ```sh
   git clone https://github.com/your-org/flowerpower.git
   cd flowerpower
   pip install -r web_ui/requirements.txt
   ```
2. Run the development server:
   ```sh
   python web_ui/run.py
   ```
3. Run tests:
   ```sh
   python -m unittest discover web_ui/
   ```

## Extending the Application

- Add new features by creating new routes in `app.py` and corresponding UI components with htpy.
- Use Datastar for real-time frontend updates.
- Follow existing patterns for error handling and state management.

## Best Practices

- Keep business logic separate from route handlers.
- Use async/await for all I/O operations.
- Document new API endpoints and UI components.
- Write tests for new features.

## References

- [Sanic Documentation](https://sanic.dev/)
- [htpy Documentation](https://github.com/htpy/htpy)
- [Datastar Python SDK](https://github.com/starfederation/datastar/tree/develop/sdk/python/src/datastar_py)

---
For user-facing instructions, see the User Guide.
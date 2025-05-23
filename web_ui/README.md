# FlowerPower Web UI

A modern web interface for FlowerPower built with Sanic, htpy, and Datastar.

## Features

- **Project Management**: List, create, and view FlowerPower projects
- **Reactive UI**: Built with Datastar for real-time updates
- **Modern Design**: Bootstrap-based responsive interface
- **Server-Sent Events**: Real-time communication between client and server

## Architecture

- **Backend**: Sanic (async Python web framework)
- **Templating**: htpy (declarative HTML generation)
- **Frontend Reactivity**: Datastar (lightweight reactive framework)
- **Styling**: Bootstrap 5

## Installation

1. **Install dependencies**:
   ```bash
   cd web_ui
   pip install -r requirements.txt
   ```

2. **Alternative: Use uv (recommended)**:
   ```bash
   cd web_ui
   uv pip install -r requirements.txt
   ```

## Running the Application

1. **Start the development server**:
   ```bash
   cd web_ui
   python app.py
   ```

2. **Access the application**:
   Open your browser and navigate to: http://localhost:8000

## Available Routes

- **Home**: `/` - Welcome page with overview
- **Projects List**: `/projects` - View all projects
- **New Project**: `/projects/new` - Create a new project
- **Project Detail**: `/projects/{id}` - View project details
- **API Projects**: `/api/projects` - JSON API for projects
- **Datastar Stream**: `/datastar/stream` - SSE endpoint for real-time updates

## Project Structure

```
web_ui/
├── app.py              # Main Sanic application
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Current Features

### Project Management
- **List Projects**: View all existing FlowerPower projects
- **Create Project**: Add new projects with name and description
- **View Project Details**: See individual project information
- **Mock Data**: Currently uses in-memory mock data for demonstration

### Reactive Components
- **Form Submission**: Uses Datastar for reactive form handling
- **Real-time Updates**: Server-sent events for live UI updates
- **Error Handling**: Displays success/error messages without page reload

## Technical Implementation

### Sanic Integration
- Async web server with proper request handling
- Blueprint organization ready for scaling
- CORS support for API access

### htpy Templates
- Declarative HTML generation using Python
- Component-based structure for reusability
- Bootstrap integration for styling

### Datastar Integration
- SSE stream endpoint at `/datastar/stream`
- Reactive form handling with `data-ds-*` attributes
- Real-time DOM updates without page refreshes

## Development Notes

### Mock Data
The application currently uses in-memory mock data stored in the `PROJECTS` list. This will be replaced with actual database integration in future tasks.

### Form Handling
- Forms use Datastar attributes for reactive submission
- Success/error messages are displayed via SSE updates
- Automatic redirects after successful operations

### Styling
- Bootstrap 5 for consistent UI components
- Responsive design for mobile compatibility
- Primary color scheme matching FlowerPower branding

## Future Enhancements

1. **Database Integration**: Replace mock data with actual FlowerPower project data
2. **Authentication**: Add user management and security
3. **Pipeline Visualization**: Integrate with FlowerPower's pipeline visualization
4. **Real-time Monitoring**: Live pipeline status updates
5. **File Upload**: Project configuration file management

## Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   # Kill process using port 8000
   lsof -ti:8000 | xargs kill -9
   ```

2. **Dependencies not found**:
   ```bash
   # Ensure you're in the right directory
   cd web_ui
   pip install -r requirements.txt
   ```

3. **Datastar not loading**:
   - Check internet connection (CDN dependency)
   - Verify JavaScript console for errors

### Development Mode
The application runs in debug mode by default, which provides:
- Auto-reload on code changes
- Detailed error messages
- Enhanced logging

## Contributing

When making changes to the web UI:

1. Follow the existing code structure
2. Use htpy for HTML generation
3. Implement Datastar attributes for reactive components
4. Test all routes and functionality
5. Update this README if adding new features

## API Documentation

### Projects API

**GET /api/projects**
- Returns: JSON list of all projects
- Format: `{"projects": [{"id": 1, "name": "...", "description": "...", "created_at": "..."}]}`

**POST /projects**
- Accepts: Form data with `name` and `description`
- Returns: JSON response with status
- Reactive: Updates UI via Datastar SSE
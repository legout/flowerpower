# FlowerPower Project Management API Documentation

## Overview
This document describes the REST API endpoints for FlowerPower project management features.

## Base URL
- Development: `http://localhost:8000`

## Endpoints

### 1. Dashboard
- **GET** `/dashboard`
- **Description**: Project overview dashboard with statistics and recent projects
- **Response**: HTML page with project statistics and quick actions

### 2. List Projects
- **GET** `/projects`
- **Description**: Display all projects in a card-based layout
- **Response**: HTML page with project cards

### 3. Create Project Form
- **GET** `/projects/new`
- **Description**: Display project creation form
- **Response**: HTML form for creating new projects

### 4. Create Project
- **POST** `/projects`
- **Description**: Create a new FlowerPower project
- **Request Body** (form-data):
  ```
  name: string (required) - Project name
  description: string (optional) - Project description
  ```
- **Response**: JSON with status and project_id
- **Example**:
  ```json
  {
    "status": "success",
    "project_id": 3
  }
  ```

### 5. Project Details
- **GET** `/projects/{project_id}`
- **Description**: Display detailed information about a specific project
- **Parameters**: `project_id` (integer) - Project ID
- **Response**: HTML page with project details and configuration

### 6. Edit Project Form
- **GET** `/projects/{project_id}/edit`
- **Description**: Display project editing form
- **Parameters**: `project_id` (integer) - Project ID
- **Response**: HTML form pre-filled with current project data

### 7. Update Project
- **POST** `/projects/{project_id}/edit`
- **Description**: Update an existing project
- **Parameters**: `project_id` (integer) - Project ID
- **Request Body** (form-data):
  ```
  name: string (required) - Project name
  description: string (optional) - Project description
  status: string (required) - Project status ("Active", "Inactive", "Error")
  ```
- **Response**: JSON with status and project_id

### 8. Project Configuration Form
- **GET** `/projects/{project_id}/config`
- **Description**: Display project configuration form
- **Parameters**: `project_id` (integer) - Project ID
- **Response**: HTML form with configuration options

### 9. Update Project Configuration
- **POST** `/projects/{project_id}/config`
- **Description**: Update project configuration settings
- **Parameters**: `project_id` (integer) - Project ID
- **Request Body** (form-data):
  ```
  environment: string - "development", "staging", or "production"
  auto_run: boolean - Enable automatic pipeline execution
  notifications: boolean - Enable notifications
  retry_attempts: integer - Number of retry attempts (0-10)
  ```
- **Response**: JSON with status and project_id

### 10. Delete Project
- **GET** `/projects/{project_id}/delete`
- **Description**: Delete a project (with confirmation)
- **Parameters**: `project_id` (integer) - Project ID
- **Response**: HTML page confirming deletion

### 11. API Projects (JSON)
- **GET** `/api/projects`
- **Description**: Get all projects as JSON (for AJAX calls)
- **Response**: JSON array of projects
- **Example**:
  ```json
  {
    "projects": [
      {
        "id": 1,
        "name": "Sample Data Pipeline",
        "description": "A sample pipeline for processing CSV data",
        "status": "Active",
        "created_at": "2025-01-20T10:00:00Z",
        "updated_at": "2025-01-20T10:00:00Z",
        "config": {
          "environment": "development",
          "auto_run": true,
          "notifications": true,
          "retry_attempts": 3
        }
      }
    ]
  }
  ```

### 12. Datastar Stream
- **GET** `/datastar/stream`
- **Description**: Server-Sent Events endpoint for real-time UI updates
- **Response**: SSE stream for Datastar integration

## Project Data Structure

Each project contains the following fields:

```json
{
  "id": 1,
  "name": "Project Name",
  "description": "Project description",
  "status": "Active|Inactive|Error",
  "created_at": "2025-01-20T10:00:00Z",
  "updated_at": "2025-01-20T10:00:00Z",
  "config": {
    "environment": "development|staging|production",
    "auto_run": true|false,
    "notifications": true|false,
    "retry_attempts": 0-10
  }
}
```

## Status Codes

- **200**: Success
- **404**: Project not found
- **500**: Server error

## Error Handling

All endpoints include proper error handling with user-friendly messages. Errors are displayed using Bootstrap alert components and Datastar for real-time updates.

## Real-time Updates

The application uses Datastar for reactive UI updates:
- Form submissions without page reload
- Real-time error and success messages
- Automatic redirects after successful operations
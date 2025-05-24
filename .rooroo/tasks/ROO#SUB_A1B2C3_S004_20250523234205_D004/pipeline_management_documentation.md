# Pipeline Management API Documentation

## Overview
This document describes the new pipeline management functionality added to the FlowerPower web application. The implementation includes both backend API endpoints and frontend UI components for managing pipelines associated with projects.

## Backend API Endpoints

### Pipeline CRUD Operations

#### GET /pipelines
- **Purpose**: List all pipelines across all projects
- **Response**: HTML page displaying pipeline cards with project information
- **Features**: 
  - Shows pipeline status, type, and project association
  - Provides quick action buttons (View, Edit, Run, Schedule)
  - Responsive grid layout with Bootstrap cards

#### GET /pipelines/new
- **Purpose**: Display form to create a new pipeline
- **Response**: HTML form with project selection and pipeline configuration options
- **Form Fields**:
  - Project selection (dropdown)
  - Pipeline name (required)
  - Description (optional)
  - Pipeline type (batch/streaming/scheduled)
  - Configuration options (auto-run, notifications, retry attempts, timeout)

#### POST /pipelines
- **Purpose**: Create a new pipeline
- **Request Body**: Form data with pipeline details
- **Response**: JSON with status and pipeline ID
- **Validation**:
  - Checks project existence
  - Prevents duplicate pipeline names within same project
  - Validates required fields
- **Features**: Real-time error feedback via Datastar

#### GET /pipelines/{pipeline_id}
- **Purpose**: Display detailed pipeline information
- **Response**: HTML page with comprehensive pipeline details
- **Sections**:
  - Basic information (name, description, project, type, status)
  - Configuration settings
  - Runtime statistics (run count, success/error counts, last run)
  - Quick action buttons

### Project-Pipeline Integration

#### GET /projects/{project_id}/pipelines
- **Purpose**: List pipelines for a specific project
- **Response**: HTML page showing project-specific pipelines
- **Features**:
  - Project context header
  - Filtered pipeline display
  - Direct access to create new pipeline for the project

#### GET /projects/{project_id}/pipelines/new
- **Purpose**: Create pipeline form pre-filled with project context
- **Response**: HTML form with project pre-selected
- **Benefits**: Streamlined workflow for adding pipelines to specific projects

## Data Model

### Pipeline Structure
```json
{
  "id": 1,
  "project_id": 1,
  "name": "pipeline_name",
  "description": "Pipeline description",
  "type": "batch|streaming|scheduled",
  "status": "Active|Inactive|Running|Scheduled|Error",
  "created_at": "2025-01-20T10:00:00Z",
  "config": {
    "auto_run": false,
    "notifications": true,
    "retry_attempts": 3,
    "timeout": 3600,
    "executor": "local|async|threadpool",
    "schedule": {
      "enabled": false,
      "cron": null,
      "interval": null
    }
  },
  "metadata": {
    "last_run": "2025-01-22T08:00:00Z",
    "next_run": null,
    "run_count": 5,
    "success_count": 4,
    "error_count": 1
  }
}
```

## Frontend Components

### Pipeline Card Component
- **Function**: `pipeline_card(pipeline, project_name=None)`
- **Features**:
  - Status and type badges
  - Action buttons (View, Edit, Run, Schedule)
  - Project name display (when not in project context)
  - Responsive design

### Updated Project Card Component
- **Function**: `project_card(project)`
- **New Features**:
  - Pipeline count display
  - Quick access to project pipelines
  - "Add Pipeline" button for direct pipeline creation

## FlowerPower Integration

### Pipeline Status Integration
- **Function**: `get_pipeline_status_from_flowerpower(pipeline_name)`
- **Purpose**: Integrates with FlowerPower's PipelineManager to check actual pipeline status
- **Implementation**: Basic integration checking if pipeline exists in FlowerPower registry
- **Future Enhancement**: Real-time status monitoring and execution integration

### Integration Points
1. **Pipeline Creation**: UI pipelines can be linked to actual FlowerPower pipeline definitions
2. **Status Monitoring**: Real-time status updates from FlowerPower execution engine
3. **Execution**: Direct pipeline execution through FlowerPower's PipelineManager
4. **Scheduling**: Integration with FlowerPower's job queue system

## Data Storage

### File Structure
- **Location**: `web_ui/projects_data.json`
- **Schema**: Extended to include `pipelines` array alongside existing `projects`
- **Persistence**: Automatic saving with timestamp tracking

### Data Management Functions
- `load_pipelines()`: Load all pipelines from storage
- `save_pipelines(pipelines)`: Save pipelines to storage
- `get_project_pipelines(project_id)`: Filter pipelines by project
- `load_data()`: Load complete data structure
- `save_data(data)`: Save complete data structure

## UI/UX Features

### Navigation
- Added "Pipelines" link to main navigation
- Project detail pages include pipeline access buttons
- Breadcrumb navigation for pipeline contexts

### Responsive Design
- Bootstrap-based responsive grid layout
- Mobile-friendly forms and buttons
- Consistent styling with existing project management UI

### Real-time Updates
- Datastar integration for form submissions
- Server-sent events for real-time UI updates
- Error handling with user-friendly messages

## Error Handling

### Validation
- Server-side validation for required fields
- Project existence validation
- Duplicate name prevention within projects

### User Feedback
- Real-time error messages via Datastar
- Success notifications with automatic redirects
- Graceful handling of missing pipelines/projects

## Future Enhancement Opportunities

1. **Pipeline Execution**: Direct execution interface with real-time logs
2. **Advanced Scheduling**: Full cron expression builder and interval configuration
3. **Pipeline Templates**: Pre-built pipeline templates for common use cases
4. **Monitoring Dashboard**: Real-time pipeline execution monitoring
5. **Pipeline Dependencies**: Visual dependency graphs and execution orchestration
6. **Version Control**: Pipeline configuration versioning and rollback capabilities

## Testing Recommendations

1. **Basic CRUD Operations**: Test pipeline creation, viewing, and listing
2. **Project Integration**: Verify pipeline-project associations
3. **Form Validation**: Test error handling for invalid inputs
4. **Data Persistence**: Verify proper saving and loading of pipeline data
5. **UI Responsiveness**: Test on different screen sizes and devices
6. **FlowerPower Integration**: Test actual pipeline existence checking
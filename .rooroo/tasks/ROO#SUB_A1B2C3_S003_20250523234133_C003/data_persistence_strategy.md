# FlowerPower Data Persistence Strategy

## Overview
This document describes the data storage and persistence strategy for FlowerPower project management.

## Current Implementation: JSON File Storage

### Storage Location
- **File Path**: `web_ui/projects_data.json`
- **Relative to Application**: Same directory as the Sanic application

### Data Structure
The JSON file contains a wrapper object with metadata:

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
  ],
  "last_updated": "2025-01-23T12:00:00.000000"
}
```

### Key Functions

#### `load_projects()`
- **Purpose**: Load projects from JSON file into memory
- **Error Handling**: Returns empty list if file doesn't exist or contains invalid JSON
- **Location**: Called during application startup

#### `save_projects(projects)`
- **Purpose**: Save projects list to JSON file
- **Parameters**: `projects` - list of project dictionaries
- **Returns**: `True` on success, `False` on failure
- **Error Handling**: Catches exceptions and returns boolean result

#### `get_next_project_id(projects)`
- **Purpose**: Generate unique ID for new projects
- **Logic**: Finds maximum existing ID and adds 1
- **Fallback**: Returns 1 if no projects exist

### Data Initialization
1. Application attempts to load existing projects from JSON file
2. If no file exists or file is empty, initializes with sample projects:
   - Sample Data Pipeline (ID: 1)
   - MQTT Analytics (ID: 2)
3. Sample projects include full data structure with config settings
4. Initial data is immediately saved to establish the JSON file

### Advantages of Current Approach
- **Simple**: No database dependencies
- **Portable**: File can be backed up/moved easily
- **Development-friendly**: Easy to inspect and modify data
- **No Setup Required**: Works out of the box

### Limitations of Current Approach
- **Concurrency**: No protection against concurrent access
- **Scalability**: Not suitable for large numbers of projects
- **Atomicity**: Risk of data corruption during writes
- **Performance**: Entire file read/written on each operation

## Future Migration Strategy

### Phase 1: SQLite Database
**Recommended for Production**

- **File**: `web_ui/flowerpower.db`
- **Schema**:
  ```sql
  CREATE TABLE projects (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      description TEXT,
      status TEXT DEFAULT 'Active',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      config_json TEXT  -- JSON string for configuration
  );
  ```

**Migration Benefits**:
- ACID compliance
- Better concurrent access
- Indexing for performance
- Still file-based (no server required)

### Phase 2: PostgreSQL/MySQL
**For Enterprise Deployment**

- **Connection**: Database server
- **Tables**: Normalized schema with separate config table
- **Benefits**: Multi-user, replication, advanced features

## Configuration Management

### Current Structure
Project configuration is stored as nested JSON within each project:

```json
"config": {
  "environment": "development|staging|production",
  "auto_run": true|false,
  "notifications": true|false,
  "retry_attempts": 0-10
}
```

### Configuration Options

#### Environment
- **Values**: "development", "staging", "production"
- **Purpose**: Determines runtime behavior and security settings
- **Default**: "development"

#### Auto Run
- **Type**: Boolean
- **Purpose**: Whether pipelines should execute automatically
- **Default**: `true` for development, `false` for production

#### Notifications
- **Type**: Boolean
- **Purpose**: Enable/disable system notifications
- **Default**: `true`

#### Retry Attempts
- **Type**: Integer (0-10)
- **Purpose**: Number of automatic retry attempts for failed operations
- **Default**: 3

## Data Validation

### Project Fields
- **Name**: Required, non-empty string
- **Description**: Optional string
- **Status**: Must be "Active", "Inactive", or "Error"
- **Timestamps**: ISO format strings

### Configuration Validation
- **Environment**: Must be valid environment string
- **Retry Attempts**: Must be integer between 0-10
- **Booleans**: Properly validated from form checkboxes

## Backup and Recovery

### Current Backup Strategy
- **Manual**: Copy `projects_data.json` file
- **Automatic**: Could implement periodic backups

### Recovery Process
1. Replace corrupted file with backup
2. Restart application (auto-loads data)
3. Verify data integrity through web interface

## Error Handling

### File Operations
- **Read Errors**: Application continues with empty project list
- **Write Errors**: Operations fail gracefully with user notification
- **Corruption**: Invalid JSON results in empty state (non-destructive)

### User Experience
- All errors displayed via Bootstrap alerts
- Datastar provides real-time error feedback
- No data loss during failed operations (rollback in memory)

## Performance Considerations

### Current Performance
- **Load Time**: O(1) - single file read at startup
- **Save Time**: O(n) - writes entire dataset
- **Memory Usage**: All projects kept in memory
- **Scalability**: Suitable for <1000 projects

### Optimization Opportunities
- Implement incremental saves
- Add data compression
- Cache frequently accessed data
- Background save operations

## Security Considerations

### File Permissions
- JSON file should be readable/writable by application only
- Consider encryption for sensitive project data

### Data Sanitization
- All user inputs properly escaped
- SQL injection protection (for future database migration)
- XSS prevention in templates

## Monitoring and Logging

### Current Logging
- Error messages printed to console
- Could implement structured logging for data operations

### Recommended Monitoring
- File size monitoring
- Save/load operation timing
- Error rate tracking
- Data validation failure alerts
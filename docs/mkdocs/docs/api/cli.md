# CLI Reference

This section provides a comprehensive reference for the FlowerPower Command Line Interface (CLI).

## Main Commands

## flowerpower init { #flowerpower-init }

Initialize a new FlowerPower project.

This command creates a new FlowerPower project with the necessary directory structure
and configuration files. If no project name is provided, the current directory name
will be used as the project name.

### Usage

```bash
flowerpower init [options]
```

### Arguments

| Name | Type | Description | Default |
|---|---|---|---|
| project_name | str | Name of the FlowerPower project to create. If not provided, | Required |
| base_dir | str | Base directory where the project will be created. If not provided, | Required |
| storage_options | str | Storage options for filesystem access, as a JSON or dict string | Required |


### Examples

```bash
$ flowerpower init

# Create a project with a specific name
```

```bash
$ flowerpower init --name my-awesome-project

# Create a project in a specific location
```

```bash
$ flowerpower init --name my-project --base-dir /path/to/projects
```

---

## flowerpower ui { #flowerpower-ui }

Start the Hamilton UI web application.

This command launches the Hamilton UI, which provides a web interface for
visualizing and interacting with your FlowerPower pipelines. The UI allows you
to explore pipeline execution graphs and view results.

### Usage

```bash
flowerpower ui [options]
```

### Arguments

| Name | Type | Description | Default |
|---|---|---|---|
| port | str | Port to run the UI server on | Required |
| base_dir | str | Base directory where the UI will store its data | Required |
| no_migration | str | Skip running database migrations on startup | Required |
| no_open | str | Prevent automatically opening the browser | Required |
| settings_file | str | Settings profile to use (mini, dev, prod) | Required |
| config_file | str | Optional custom configuration file path | Required |


### Examples

```bash
$ flowerpower ui

# Run the UI on a specific port
```

```bash
$ flowerpower ui --port 9000

# Use a custom data directory
```

```bash
$ flowerpower ui --base-dir ~/my-project/.hamilton-data

# Start without opening a browser
```

```bash
$ flowerpower ui --no-open

# Use production settings
```

```bash
$ flowerpower ui --settings prod
```

---


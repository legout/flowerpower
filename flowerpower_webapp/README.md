# FlowerPower Web Application

This is a Sanic web application for FlowerPower.

## Running the application

1. Install the necessary dependencies:
   ```bash
   pip install flowerpower[webserver]
   ```
2. **Project Discovery:**
   - The web application looks for FlowerPower projects in a directory named `fp_projects` located at the root of this repository.
   - Each subdirectory within `fp_projects` is considered a potential project if it contains a `conf/project.yml` file.
   - If the `fp_projects` directory does not exist at the repository root, the application will fall back to searching for projects in the current working directory (`.` when you run `python flowerpower_webapp/main.py`). This allows you to run the web app from within a single project's directory.
   - To get started, you can create the `fp_projects` directory in the repository root:
     ```bash
     mkdir fp_projects
     ```
   - Then, place your FlowerPower project folders inside `fp_projects`. For example:
     ```
     fp_projects/
     ├── my_project_alpha/
     │   ├── conf/
     │   │   └── project.yml
     │   └── ... (other project files)
     └── my_project_beta/
         ├── conf/
         │   └── project.yml
         └── ... (other project files)
     ```
   - If no projects are found in `fp_projects` (when it's the designated root), the application will automatically create a couple of sample projects (`sample_project_1`, `sample_project_2`) for demonstration purposes when you first run it.

3. Run the application:
   ```bash
   python flowerpower_webapp/main.py
   ```

The application will be available at `http://localhost:8000`. You can navigate to `/projects` to see the list of discovered projects.

### Creating a New Project

You can create a new FlowerPower project directly from the web interface:

1.  Navigate to the main page or the project listing page (`/projects`).
2.  Click on the "Create New Project" link/button. This will take you to the `/projects/new` page.
3.  Enter a unique name for your new project in the input field. The project name should consist of letters, numbers, underscores, hyphens, or dots.
4.  Click the "Create Project" button.
5.  If successful, the application will create:
    *   A new directory for your project under the `fp_projects` directory (e.g., `fp_projects/your_project_name/`).
    *   Inside the project directory:
        *   `conf/project.yml` (a default project configuration file).
        *   `conf/pipelines/` (a directory for your pipeline configuration files).
        *   `pipelines/` (a directory for your pipeline code modules).
6.  You will see a success message, and the newly created project will appear on the `/projects` listing page.
7.  If there's an error (e.g., project name already exists, invalid characters), an error message will be displayed.

### Viewing and Editing Project Configuration

Once a project is created or discovered, you can view and edit its `project.yml` configuration:

1.  Navigate to the project listing page (`/projects`).
2.  Click on the name of the project you wish to view or edit. This will take you to the project's detail page (e.g., `/projects/your_project_name`).
3.  The content of the project's `conf/project.yml` file will be displayed in a text area.
4.  **Editing:**
    *   You can directly modify the YAML content in the text area.
    *   After making your changes, click the "Save Configuration" button.
5.  **Validation:**
    *   The application will first check if the entered text is valid YAML.
    *   Then, it will validate if the YAML content conforms to the `ProjectConfig` schema (e.g., checking for required fields, correct data types).
6.  **Outcome:**
    *   If the configuration is valid and saved successfully, a success message will be displayed, and the `project.yml` file on the server will be updated.
    *   If there are errors (e.g., invalid YAML format, schema validation failure, file system issues), an error message will be displayed, and the file will not be saved.
7.  **File Not Found:**
    *   If a project directory exists but its `conf/project.yml` file is missing, the page will display an error message.
    *   A default `project.yml` template for that project (based on its name) will be loaded into the text area. You can then modify and save this template to create the `project.yml` file.

### Listing Project Pipelines

You can view a list of all available pipelines within a specific FlowerPower project:

1.  Navigate to the project's detail page (where you view/edit `project.yml`).
2.  Click on the "View Pipelines" link. This will take you to the pipeline listing page for that project (e.g., `/projects/your_project_name/pipelines`).
3.  The page will display a list of all pipelines discovered in the project.
    *   FlowerPower discovers pipelines by looking for Python files (e.g., `my_pipeline.py`) in the project's `pipelines/` directory that have a corresponding configuration file (e.g., `my_pipeline.yml`) in the `conf/pipelines/` directory.
4.  Each listed pipeline name will be a link to a (currently placeholder) page for that specific pipeline's details.
5.  If no pipelines are found in the project, a "No pipelines found for this project." message will be displayed.
6.  If there's an error (e.g., the project's `conf/project.yml` is missing or malformed, which might be needed by the `PipelineManager`), an error message will be shown.
7.  From this page, you can also navigate to:
    *   "Add New Pipeline".
    *   Back to the project's configuration page.
    *   Back to the list of all projects.
    *   Back to the home page.

### Adding a New Pipeline to a Project

You can create the basic file structure for a new pipeline within a project:

1.  Navigate to the pipeline listing page for the desired project (e.g., `/projects/your_project_name/pipelines`).
2.  Click on the "Add New Pipeline" button/link. This will take you to the form for adding a new pipeline (e.g., `/projects/your_project_name/pipelines/new`).
3.  **Enter Pipeline Name:**
    *   In the "Pipeline Name" input field, enter a name for your new pipeline.
    *   The name must be a valid Python identifier (e.g., `my_new_data_pipeline`). This generally means it should consist of letters, numbers, and underscores, and cannot start with a number.
4.  Click the "Create Pipeline" button.
5.  **Outcome:**
    *   **Success:** If the name is valid and the pipeline doesn't already exist, the application will:
        *   Create a new Python file: `fp_projects/your_project_name/pipelines/your_pipeline_name.py`.
        *   Create a new YAML configuration file: `fp_projects/your_project_name/conf/pipelines/your_pipeline_name.yml`.
        *   A success message will be displayed, and the input field for the pipeline name will be cleared.
        *   The newly created pipeline will then appear on the pipeline list page for that project.
    *   **Error:**
        *   If the pipeline name is invalid (e.g., contains spaces, starts with a number), an error message will be displayed.
        *   If a pipeline with that name already exists in the project, an error message will indicate this.
        *   If there are other issues (e.g., problems with the `PipelineManager` or file system permissions), a general error message will be shown.
6.  After creating a pipeline, you will need to manually edit its `.py` and `.yml` files to define its functionality and configuration. The web application currently only creates the boilerplate files.

### Viewing and Editing Pipeline Configuration

For each pipeline within a project, you can view and edit its specific YAML configuration file (e.g., `your_pipeline_name.yml`):

1.  Navigate to the pipeline listing page for the desired project (e.g., `/projects/your_project_name/pipelines`).
2.  Click on the name of the pipeline whose configuration you wish to view or edit. This will take you to that pipeline's detail page (e.g., `/projects/your_project_name/pipelines/your_pipeline_name`).
3.  The content of the pipeline's `.yml` file (located in `fp_projects/your_project_name/conf/pipelines/`) will be displayed in a text area.
4.  **Editing:**
    *   You can directly modify the YAML content in the text area.
    *   After making your changes, click the "Save Pipeline Configuration" button.
5.  **Validation:**
    *   The application will first check if the entered text is valid YAML.
    *   Then, it will validate if the YAML content conforms to the `PipelineConfig` schema (e.g., checking for expected sections like `params`, `run`, etc.).
6.  **Outcome:**
    *   If the configuration is valid and saved successfully, a success message will be displayed, and the pipeline's `.yml` file on the server will be updated.
    *   If there are errors (e.g., invalid YAML format, schema validation failure, file system issues), an error message will be displayed, and the file will not be saved.
7.  **File Not Found:**
    *   If a pipeline's `.yml` configuration file is missing (e.g., if only the `.py` file exists or after a new pipeline is created via the UI but before its config is saved for the first time):
        *   The page will display an error message indicating the file was not found.
        *   A default `PipelineConfig` template for that pipeline (based on its name) will be loaded into the text area.
        *   You can then modify and save this template to create the pipeline's `.yml` configuration file.

### Visualizing Pipeline DAG (Directed Acyclic Graph)

You can view a visual representation of a pipeline's structure (its DAG):

1.  Navigate to the pipeline's detail/configuration page (e.g., `/projects/your_project_name/pipelines/your_pipeline_name`).
2.  Click on the "View DAG" link. This will take you to the DAG visualization page for that pipeline (e.g., `/projects/your_project_name/pipelines/your_pipeline_name/dag`).
3.  **DAG Display:**
    *   If successful and `graphviz` is installed on the server, an SVG image of the DAG will be displayed.
    *   If `graphviz` is not installed, or if there are errors in the pipeline's Python code or configuration that prevent DAG generation, an error message will be displayed. The page might show a placeholder or a textual representation if SVG generation fails.
4.  **Dependencies:**
    *   DAG visualization as an SVG image requires **Graphviz** to be installed on the server where the FlowerPower web application is running. If Graphviz is not found, the application will attempt to gracefully handle this by showing an error message.
5.  **Troubleshooting:**
    *   If you see an error message instead of a DAG, check the following:
        *   Ensure Graphviz is installed and in the system's PATH.
        *   Verify that the pipeline's Python module (`.py` file) and its YAML configuration (`.yml` file) are correctly defined and free of syntax errors.
        *   Check the application logs for more detailed error messages.
6.  From the DAG page, you can navigate back to the pipeline's configuration, the pipeline list for the project, or the home page.

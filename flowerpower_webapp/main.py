import os
import pathlib
import re # For project name validation
import sys # For potential sys.path manipulation if needed, though aiming to avoid

# Attempt to set up path for flowerpower library if not installed in standard locations.
# This is a common pattern for local development.
# The ideal solution is for the app to be run in an environment where 'flowerpower' is installed or in PYTHONPATH.
try:
    import flowerpower
except ImportError:
    # Assuming flowerpower_webapp is sibling to a directory containing the flowerpower source (e.g., 'src/flowerpower')
    repo_root_for_fp_lib = pathlib.Path(__file__).resolve().parent.parent 
    # Check common locations like 'src' or the repo root itself if 'flowerpower' is a top-level package dir
    possible_fp_src_paths = [repo_root_for_fp_lib / "src", repo_root_for_fp_lib]
    fp_path_found = False
    for p_path in possible_fp_src_paths:
        if (p_path / "flowerpower").is_dir():
            if str(p_path) not in sys.path:
                sys.path.insert(0, str(p_path))
            fp_path_found = True
            break
    if not fp_path_found:
        print("Warning: 'flowerpower' module not found in sys.path. Project creation might fail if 'flowerpower.config' is unavailable.", file=sys.stderr)

import urllib.parse # For URL encoding/decoding project names
from sanic import Sanic, Request
from sanic.response import redirect
from sanic_ext import SanicExt
from htpy import Element, Html, div, h1, p, h3, ul, li, a as html_a, form, label, input as html_input, button as html_button, span, textarea, pre, RawHtml
from datastar.utils import datastar_html_response
from datastar.types import Message

# Assuming flowerpower.config, ProjectConfig, PipelineConfig, and PipelineManager are available
try:
    from flowerpower.config import ProjectConfig, PipelineConfig # Added PipelineConfig
    from flowerpower.pipeline import PipelineManager
    import msgspec.yaml
    import msgspec
except ImportError as e:
    print(f"Error importing FlowerPower modules or msgspec: {e}. Ensure 'flowerpower' and 'msgspec' are installed or correctly pathed.", file=sys.stderr)
    # Define dummy classes if the real ones can't be imported
    if 'ProjectConfig' not in globals():
        class ProjectConfig: # type: ignore
            def __init__(self, name: str = "Unknown"): self.name = name
            def to_yaml(self, path: str): raise NotImplementedError("Dummy ProjectConfig: Cannot save.")
            @classmethod
            def from_dict(cls, data: dict): raise NotImplementedError("Dummy ProjectConfig: Cannot load from dict.")
    
    if 'PipelineConfig' not in globals(): # Added dummy for PipelineConfig
        class PipelineConfig: # type: ignore
            def __init__(self, name: str = "Unknown"): self.name = name # Basic constructor
            def to_yaml_str(self) -> str: raise NotImplementedError("Dummy PipelineConfig: Cannot convert to YAML string.")
            @classmethod
            def from_dict(cls, data: dict): raise NotImplementedError("Dummy PipelineConfig: Cannot load from dict.")

    if 'PipelineManager' not in globals():
        class DummyPipelineVisualizer: # Nested dummy class
            def show_dag(self, name: str, format: str = 'svg', raw: bool = False, **kwargs) -> str | None:
                raise NotImplementedError("Dummy PipelineManager.visualizer.show_dag: Cannot generate DAG.")

        class PipelineManager: # type: ignore
            def __init__(self, base_dir: str): 
                self.base_dir = base_dir # Store base_dir for potential use by dummy methods
                self.visualizer = DummyPipelineVisualizer() # Instantiate the dummy visualizer
                # raise NotImplementedError("Dummy PipelineManager: Cannot initialize.") # Original init error
            def list_pipelines(self) -> list[str]: raise NotImplementedError("Dummy PipelineManager: Cannot list pipelines.")
            def new(self, name: str, overwrite: bool = False): raise NotImplementedError("Dummy PipelineManager: Cannot create new pipeline.")

    if 'msgspec' not in globals():
        class msgspec: # type: ignore
            class ValidationError(Exception): pass
            class yaml:
                @staticmethod
                def decode(text, type=None): raise NotImplementedError("Dummy msgspec.yaml.decode")
                @staticmethod
                def encode(obj): raise NotImplementedError("Dummy msgspec.yaml.encode")

app = Sanic("FlowerPowerApp")
SanicExt(app)
app.config.OAS = False # Disable OpenAPI spec generation for now

# Determine FLOWERPOWER_PROJECTS_ROOT
# Ensure repo_root is defined early if used by path adjustments above.
# If repo_root_for_fp_lib was defined, it's the same as repo_root here.
if "repo_root_for_fp_lib" in locals():
    repo_root = repo_root_for_fp_lib
else:
    repo_root = pathlib.Path(__file__).resolve().parent.parent

fp_projects_dir_candidate = repo_root / "fp_projects"

# Ensure FLOWERPOWER_PROJECTS_ROOT is always a Path object.
# Default to creating 'fp_projects' in the repo root if it doesn't exist,
# rather than CWD, to make behavior more predictable for project creation.
FLOWERPOWER_PROJECTS_ROOT = fp_projects_dir_candidate
USING_FP_PROJECTS_DIR = True # We will now always try to use or create fp_projects

def ensure_projects_root_exists():
    """Ensures the FLOWERPOWER_PROJECTS_ROOT directory exists."""
    if not FLOWERPOWER_PROJECTS_ROOT.exists():
        print(f"{FLOWERPOWER_PROJECTS_ROOT} does not exist. Creating it.")
        FLOWERPOWER_PROJECTS_ROOT.mkdir(parents=True, exist_ok=True)
    elif not FLOWERPOWER_PROJECTS_ROOT.is_dir():
        print(f"Error: {FLOWERPOWER_PROJECTS_ROOT} exists but is not a directory.", file=sys.stderr)
        # Handle error appropriately, maybe raise an exception or exit
        raise SystemExit(f"Error: {FLOWERPOWER_PROJECTS_ROOT} is not a directory.")


def create_dummy_projects_if_needed():
    """Creates dummy projects if fp_projects is used and is empty or contains no valid projects."""
    ensure_projects_root_exists() # Make sure the root directory is there first

    projects_found = False
    for item in FLOWERPOWER_PROJECTS_ROOT.iterdir():
        if item.is_dir() and (item / "conf" / "project.yml").exists():
            projects_found = True
            break
    
    if not projects_found:
        print(f"No projects found in {FLOWERPOWER_PROJECTS_ROOT}, creating dummy projects...")
        dummy_project_names = ["sample_project_1", "sample_project_2"]
        for name in dummy_project_names:
            project_path = FLOWERPOWER_PROJECTS_ROOT / name
            conf_dir = project_path / "conf"
            conf_dir.mkdir(parents=True, exist_ok=True)
            try:
                # Use ProjectConfig to create a minimal valid project.yml
                pc = ProjectConfig(name=name)
                pc.to_yaml(str(conf_dir / "project.yml"))
            except Exception as e:
                # If ProjectConfig failed (e.g. dummy or other issue), touch a file as fallback.
                print(f"Could not create project.yml for {name} using ProjectConfig ({e}), creating empty file.", file=sys.stderr)
                (conf_dir / "project.yml").touch(exist_ok=True)
        print(f"Created dummy projects in {FLOWERPOWER_PROJECTS_ROOT}")


class PageStore:
    my_text: str = "Initial Text"

class ProjectCreationStore:
    project_name: str = ""
    error_message: str = ""
    success_message: str = ""

    async def create_project(self, request: Request) -> Message | None:
        self.error_message = ""
        self.success_message = ""

        if not self.project_name or not re.match(r"^[a-zA-Z0-9_.-]+$", self.project_name):
            self.error_message = "Project name is required and can only contain letters, numbers, underscores, hyphens, and dots."
            return None

        ensure_projects_root_exists() 

        new_project_path = FLOWERPOWER_PROJECTS_ROOT / self.project_name
        if new_project_path.exists():
            self.error_message = f"Project '{self.project_name}' already exists at {new_project_path}."
            return None

        try:
            new_project_path.mkdir(parents=True, exist_ok=False)
            conf_dir = new_project_path / 'conf'
            pipelines_config_dir = conf_dir / 'pipelines'
            pipelines_code_dir = new_project_path / 'pipelines'

            conf_dir.mkdir()
            pipelines_config_dir.mkdir()
            pipelines_code_dir.mkdir()

            pc = ProjectConfig(name=self.project_name)
            pc.to_yaml(str(conf_dir / "project.yml"))

            self.success_message = f"Project '{self.project_name}' created successfully at {new_project_path}!"
            self.project_name = "" 
        except FileExistsError: 
            self.error_message = f"Project '{self.project_name}' already exists (race condition)."
        except NotImplementedError: 
             self.error_message = "Project creation is currently disabled due to a configuration problem (ProjectConfig not available)."
             if new_project_path.exists(): import shutil; shutil.rmtree(new_project_path)
        except Exception as e:
            self.error_message = f"An error occurred: {e}"
            if new_project_path.exists(): import shutil; shutil.rmtree(new_project_path)
        return None


class ProjectDetailStore:
    project_name: str = "Unknown Project"
    project_name_url_encoded: str = ""
    config_text: str = ""
    error_message: str = ""
    success_message: str = ""

    async def save_config(self, request: Request) -> Message | None:
        self.error_message = ""
        self.success_message = ""
        project_yml_path = FLOWERPOWER_PROJECTS_ROOT / self.project_name / 'conf' / 'project.yml'
        try:
            try: parsed_yaml_dict = msgspec.yaml.decode(self.config_text.encode('utf-8'), type=dict)
            except msgspec.ValidationError as e: self.error_message = f"Invalid YAML format: {e}"; return None
            try: ProjectConfig.from_dict(parsed_yaml_dict) 
            except (msgspec.ValidationError, NotImplementedError, Exception) as e: self.error_message = f"YAML content does not match ProjectConfig schema: {e}"; return None
            project_yml_path.parent.mkdir(parents=True, exist_ok=True)
            with open(project_yml_path, "w", encoding="utf-8") as f: f.write(self.config_text)
            self.success_message = "Configuration saved successfully."
        except NotImplementedError: self.error_message = "Configuration saving is currently disabled due to a configuration problem."
        except Exception as e: self.error_message = f"Failed to save configuration: {e}"
        return None

class PipelineListStore:
    project_name: str = ""
    project_name_url_encoded: str = ""
    pipelines: list[dict] = [] 
    error_message: str = ""

class NewPipelineStore:
    project_name: str = ""
    project_name_url_encoded: str = ""
    pipeline_name: str = ""
    error_message: str = ""
    success_message: str = ""

    async def create_pipeline(self, request: Request) -> Message | None:
        self.error_message = ""
        self.success_message = ""
        if not self.pipeline_name or not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", self.pipeline_name):
            self.error_message = "Pipeline name must be a valid Python identifier."
            return None
        project_path = FLOWERPOWER_PROJECTS_ROOT / self.project_name
        if not project_path.exists() or not project_path.is_dir():
            self.error_message = f"Project '{self.project_name}' not found."
            return None
        try:
            manager = PipelineManager(base_dir=str(project_path))
            manager.new(name=self.pipeline_name, overwrite=False) 
            self.success_message = f"Pipeline '{self.pipeline_name}' created successfully."
            self.pipeline_name = "" 
        except FileExistsError: self.error_message = f"Pipeline '{self.pipeline_name}' already exists."
        except ValueError as ve: self.error_message = f"Invalid pipeline name: {ve}"
        except NotImplementedError: self.error_message = "Pipeline creation is disabled (PipelineManager not available)."
        except Exception as e:
            self.error_message = f"An unexpected error occurred: {e}"
            print(f"Traceback: ({self.project_name}/{self.pipeline_name}):", file=sys.stderr)
            import traceback; traceback.print_exc(file=sys.stderr)
        return None

class PipelineDetailStore:
    project_name: str = ""
    project_name_url_encoded: str = ""
    pipeline_name: str = ""
    pipeline_name_url_encoded: str = ""
    config_text: str = ""
    error_message: str = ""
    success_message: str = ""

    async def save_pipeline_config(self, request: Request) -> Message | None:
        self.error_message = ""
        self.success_message = ""
        project_path = FLOWERPOWER_PROJECTS_ROOT / self.project_name
        pipeline_yml_path = project_path / 'conf' / 'pipelines' / (self.pipeline_name + '.yml')
        try:
            try: parsed_yaml_dict = msgspec.yaml.decode(self.config_text.encode('utf-8'), type=dict)
            except msgspec.ValidationError as e: self.error_message = f"Invalid YAML format: {e}"; return None
            try: PipelineConfig.from_dict(parsed_yaml_dict)
            except (msgspec.ValidationError, NotImplementedError, Exception) as e: 
                self.error_message = f"YAML content does not match PipelineConfig schema: {e}"; return None
            pipeline_yml_path.parent.mkdir(parents=True, exist_ok=True)
            with open(pipeline_yml_path, "w", encoding="utf-8") as f: f.write(self.config_text)
            self.success_message = "Pipeline configuration saved successfully."
        except NotImplementedError: self.error_message = "Saving disabled (PipelineConfig or msgspec not available)."
        except Exception as e: self.error_message = f"Failed to save pipeline configuration: {e}"
        return None

class PipelineDagStore:
    project_name: str = ""
    project_name_url_encoded: str = ""
    pipeline_name: str = ""
    pipeline_name_url_encoded: str = ""
    dag_representation: str = "" # Will hold SVG string or textual DAG / error message
    error_message: str = ""


def main_page_content(stores: dict[str, PageStore]) -> Element:
    return div(
        h1("FlowerPower Web"),
        p("Welcome to the FlowerPower web interface. ", html_a("Browse Projects", href="/projects"), " or ", html_a("Create a New Project", href="/projects/new"), "."),
        h3(stores["page"].my_text), 
        html_input(type="text", data_model="stores.page.my_text"),
        html_button("Click Me", data_on_click="stores.page.my_text = 'Button Clicked!'"),
    )

def project_list_page_content(projects: list[dict], projects_root_path: pathlib.Path) -> Element:
    project_items = [
        li(
            html_a(project['name'], href=f"/projects/{urllib.parse.quote(project['name'])}")
        ) for project in projects
    ]
    return div(
        h1("FlowerPower Projects"),
        p(f"Projects found in: {projects_root_path}"),
        html_a("Create New Project", href="/projects/new", role="button"),
        ul(project_items) if projects else p(f"No projects found in {projects_root_path}. You can create one!"),
        p(html_a("Back to Home", href="/"))
    )

def new_project_page_content(stores: dict[str, ProjectCreationStore]) -> Element: 
    store = stores["page"] 
    return div(
        h1("Create New FlowerPower Project"),
        form(data_on_submit_prevent="await stores.page.create_project()")( 
            div(
                label("Project Name:", for_="project_name_input"),
                html_input(id="project_name_input", type="text", data_model="stores.page.project_name", placeholder="Enter project name", required=True),
            ),
            html_button(type="submit")("Create Project"),
            div(
                (span(store.success_message, style="color: green;") if store.success_message else ""),
                (span(store.error_message, style="color: red;") if store.error_message else ""),
            )
        ),
        p(html_a("Back to Projects List", href="/projects")),
        p(html_a("Back to Home", href="/"))
    )

def project_detail_page_content(stores: dict[str, ProjectDetailStore]) -> Element:
    store = stores["page"]
    return div(
        h1(f"Project Configuration: {store.project_name}"),
        (span(store.success_message, style="color: green;") if store.success_message else ""),
        (span(store.error_message, style="color: red;") if store.error_message else ""),
        form(data_on_submit_prevent="await stores.page.save_config()")(
            div(
                label(f"Editing project.yml for {store.project_name}:", for_="config_text_area"),
                textarea(id="config_text_area", data_model="stores.page.config_text", rows="20", cols="100", style="font-family: monospace; width: 90%;")
            ),
            html_button(type="submit")("Save Configuration")
        ),
        p(html_a("View Pipelines", href=f"/projects/{store.project_name_url_encoded}/pipelines")), # Link to pipeline list
        p(html_a("Back to Projects List", href="/projects")),
        p(html_a("Back to Home", href="/"))
    )

def pipeline_list_page_content(stores: dict[str, PipelineListStore]) -> Element:
    store = stores["page"]
    pipeline_items = [
        li(
            html_a(p['name'], href=f"/projects/{store.project_name_url_encoded}/pipelines/{p['url_encoded_name']}")
        ) for p in store.pipelines
    ]
    return div(
        h1(f"Pipelines for Project: {store.project_name}"),
        (span(store.error_message, style="color: red;") if store.error_message else ""),
        (html_a("Add New Pipeline", href=f"/projects/{store.project_name_url_encoded}/pipelines/new", role="button") 
         if not store.error_message else ""), # Only show if no major error
        (ul(pipeline_items) if store.pipelines else 
            (p("No pipelines found for this project.") if not store.error_message else "")),
        p(html_a("Back to Project Configuration", href=f"/projects/{store.project_name_url_encoded}")),
        p(html_a("Back to All Projects", href="/projects")),
        p(html_a("Back to Home", href="/"))
    )

def new_pipeline_page_content(stores: dict[str, NewPipelineStore]) -> Element:
    store = stores["page"]
    return div(
        h1(f"Add New Pipeline to Project: {store.project_name}"),
        (span(store.success_message, style="color: green;") if store.success_message else ""),
        (span(store.error_message, style="color: red;") if store.error_message else ""),
        form(data_on_submit_prevent="await stores.page.create_pipeline()")(
            div(
                label("Pipeline Name:", for_="pipeline_name_input"),
                html_input(id="pipeline_name_input", type="text", data_model="stores.page.pipeline_name", 
                           placeholder="Enter new pipeline name (e.g., my_processing_pipeline)", required=True,
                           pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$", 
                           title="Must be a valid Python identifier."),
            ),
            html_button(type="submit")("Create Pipeline")
        ),
        p(html_a("Back to Pipeline List", href=f"/projects/{store.project_name_url_encoded}/pipelines")),
        p(html_a("Back to Project Configuration", href=f"/projects/{store.project_name_url_encoded}")),
        p(html_a("Back to Home", href="/"))
    )

def pipeline_detail_page_content(stores: dict[str, PipelineDetailStore]) -> Element:
    store = stores["page"]
    return div(
        h1(f"Pipeline: {store.pipeline_name} (Project: {store.project_name})"),
        (span(store.success_message, style="color: green;") if store.success_message else ""),
        (span(store.error_message, style="color: red;") if store.error_message else ""),
        form(data_on_submit_prevent="await stores.page.save_pipeline_config()")(
            div(
                label(f"Editing {store.pipeline_name}.yml:", for_="pipeline_config_text_area"),
                textarea(id="pipeline_config_text_area", data_model="stores.page.config_text", 
                           rows="20", cols="80", style="font-family: monospace; width: 90%;")
            ),
            html_button(type="submit")("Save Pipeline Configuration")
        ),
        p(html_a("View DAG", href=f"/projects/{store.project_name_url_encoded}/pipelines/{store.pipeline_name_url_encoded}/dag")), # Link to DAG page
        p(html_a("Back to Pipeline List", href=f"/projects/{store.project_name_url_encoded}/pipelines")),
        p(html_a("Back to Project Configuration", href=f"/projects/{store.project_name_url_encoded}")),
        p(html_a("Back to Home", href="/"))
    )

def pipeline_dag_page_content(stores: dict[str, PipelineDagStore]) -> Element:
    store = stores["page"]
    dag_content: Element | list[Element]
    if store.dag_representation and store.dag_representation.strip().lower().startswith("<svg"):
        dag_content = RawHtml(store.dag_representation)
    else:
        dag_content = pre(store.dag_representation)
    
    return div(
        h1(f"DAG for Pipeline: {store.pipeline_name} (Project: {store.project_name})"),
        (span(store.error_message, style="color: red;") if store.error_message else div(dag_content)),
        p(html_a("Back to Pipeline Configuration", href=f"/projects/{store.project_name_url_encoded}/pipelines/{store.pipeline_name_url_encoded}")),
        p(html_a("Back to Pipeline List", href=f"/projects/{store.project_name_url_encoded}/pipelines")),
        p(html_a("Back to Home", href="/"))
    )

@app.route("/")
async def main_view(request: Request):
    return datastar_html_response(Html(main_page_content(stores={"page": PageStore()})))

@app.route("/projects")
async def list_projects_view(request: Request):
    ensure_projects_root_exists() 
    projects = []
    for item in FLOWERPOWER_PROJECTS_ROOT.iterdir():
        if item.is_dir():
            project_conf_path = item / "conf" / "project.yml"
            if project_conf_path.exists() and project_conf_path.is_file():
                projects.append({"name": item.name, "path": str(item)})
    return datastar_html_response(Html(project_list_page_content(projects, FLOWERPOWER_PROJECTS_ROOT)))

@app.route("/projects/new", methods=["GET"])
async def new_project_form_view(request: Request):
    return datastar_html_response(Html(new_project_page_content(stores={"page": ProjectCreationStore()})))

@app.route("/projects/<project_name_url:str>", methods=["GET"])
async def project_detail_view(request: Request, project_name_url: str):
    project_name = urllib.parse.unquote(project_name_url)
    store = ProjectDetailStore()
    store.project_name = project_name
    store.project_name_url_encoded = project_name_url
    project_yml_path = FLOWERPOWER_PROJECTS_ROOT / project_name / 'conf' / 'project.yml'
    ensure_projects_root_exists()
    project_dir = FLOWERPOWER_PROJECTS_ROOT / project_name
    if not project_dir.exists() or not project_dir.is_dir():
        store.error_message = f"Project directory for '{project_name}' not found."
        store.config_text = f"# Project '{project_name}' directory does not exist at {project_dir}"
    elif not project_yml_path.exists() or not project_yml_path.is_file():
        store.error_message = f"project.yml not found for project '{project_name}'."
        default_config = ProjectConfig(name=project_name)
        try:
            store.config_text = msgspec.yaml.encode(default_config).decode('utf-8')
            store.error_message += " A default template has been provided."
        except (NotImplementedError, AttributeError):
            store.config_text = f"# project.yml not found for '{project_name}'.\n# Saving is disabled."
            store.error_message = "project.yml not found. Saving is disabled."
    else:
        try:
            with open(project_yml_path, "r", encoding="utf-8") as f: store.config_text = f.read()
        except Exception as e:
            store.error_message = f"Error reading project.yml: {e}"; store.config_text = f"# Error loading config: {e}"
    return datastar_html_response(Html(project_detail_page_content(stores={"page": store})))

@app.route("/projects/<project_name_url:str>/pipelines", methods=["GET"])
async def list_pipelines_view(request: Request, project_name_url: str):
    project_name = urllib.parse.unquote(project_name_url)
    store = PipelineListStore()
    store.project_name = project_name
    store.project_name_url_encoded = project_name_url
    project_path = FLOWERPOWER_PROJECTS_ROOT / project_name
    if not project_path.exists() or not project_path.is_dir():
        store.error_message = f"Project '{project_name}' not found at {project_path}."
    else:
        try:
            if not (project_path / "conf" / "project.yml").exists():
                 store.error_message = f"Project '{project_name}' is missing conf/project.yml."
            else:
                manager = PipelineManager(base_dir=str(project_path))
                pipeline_names = manager.list_pipelines()
                store.pipelines = [{'name': name, 'url_encoded_name': urllib.parse.quote(name)} for name in pipeline_names]
        except NotImplementedError: 
            store.error_message = "Pipeline listing is disabled (PipelineManager not available)."
        except Exception as e:
            store.error_message = f"Error listing pipelines for '{project_name}': {e}"
            print(f"Traceback ({project_name}):", file=sys.stderr); import traceback; traceback.print_exc(file=sys.stderr)
    return datastar_html_response(Html(pipeline_list_page_content(stores={"page": store})))

@app.route("/projects/<project_name_url:str>/pipelines/new", methods=["GET"])
async def new_pipeline_form_view(request: Request, project_name_url: str):
    project_name = urllib.parse.unquote(project_name_url)
    store = NewPipelineStore()
    store.project_name = project_name
    store.project_name_url_encoded = project_name_url
    project_path = FLOWERPOWER_PROJECTS_ROOT / project_name
    if not project_path.exists() or not project_path.is_dir():
        store.error_message = f"Project '{project_name}' not found. Cannot add pipeline."
    return datastar_html_response(Html(new_pipeline_page_content(stores={"page": store})))

@app.route("/projects/<project_name_url:str>/pipelines/<pipeline_name_url:str>", methods=["GET"])
async def pipeline_detail_view(request: Request, project_name_url: str, pipeline_name_url: str):
    project_name = urllib.parse.unquote(project_name_url)
    pipeline_name = urllib.parse.unquote(pipeline_name_url)
    store = PipelineDetailStore()
    store.project_name = project_name
    store.project_name_url_encoded = project_name_url
    store.pipeline_name = pipeline_name
    store.pipeline_name_url_encoded = pipeline_name_url
    project_path = FLOWERPOWER_PROJECTS_ROOT / project_name
    pipeline_yml_path = project_path / 'conf' / 'pipelines' / (pipeline_name + '.yml')
    if not project_path.exists() or not project_path.is_dir():
        store.error_message = f"Project '{project_name}' not found."
        store.config_text = f"# Project '{project_name}' not found."
    elif not (project_path / "conf" / "project.yml").exists(): 
        store.error_message = f"Project '{project_name}' is missing its main conf/project.yml file."
        store.config_text = f"# Project '{project_name}' main configuration is missing."
    elif not pipeline_yml_path.exists() or not pipeline_yml_path.is_file():
        store.error_message = f"Pipeline configuration '{pipeline_name}.yml' not found in project '{project_name}'."
        try:
            default_pipeline_cfg = PipelineConfig(name=pipeline_name) 
            store.config_text = msgspec.yaml.encode(default_pipeline_cfg).decode('utf-8')
            store.error_message += " A default template has been provided. You can modify and save it to create the file."
        except (NotImplementedError, AttributeError):
            store.config_text = f"# Pipeline config for '{pipeline_name}' not found.\n# Default template generation failed (PipelineConfig/msgspec missing)."
            store.error_message = "Pipeline config not found. Default template generation failed."
    else:
        try:
            with open(pipeline_yml_path, "r", encoding="utf-8") as f: store.config_text = f.read()
        except Exception as e:
            store.error_message = f"Error reading pipeline configuration '{pipeline_name}.yml': {e}"
            store.config_text = f"# Error loading config: {e}"
    return datastar_html_response(Html(pipeline_detail_page_content(stores={"page": store})))

@app.route("/projects/<project_name_url:str>/pipelines/<pipeline_name_url:str>/dag", methods=["GET"])
async def pipeline_dag_view(request: Request, project_name_url: str, pipeline_name_url: str):
    project_name = urllib.parse.unquote(project_name_url)
    pipeline_name = urllib.parse.unquote(pipeline_name_url)
    
    store = PipelineDagStore()
    store.project_name = project_name
    store.project_name_url_encoded = project_name_url
    store.pipeline_name = pipeline_name
    store.pipeline_name_url_encoded = pipeline_name_url

    project_path = FLOWERPOWER_PROJECTS_ROOT / project_name

    if not project_path.exists() or not project_path.is_dir():
        store.error_message = f"Project '{project_name}' not found."
        store.dag_representation = "Project not found."
    elif not (project_path / "conf" / "project.yml").exists():
        store.error_message = f"Project '{project_name}' is missing its main conf/project.yml file. Cannot generate DAG."
        store.dag_representation = "Project configuration missing."
    elif not (project_path / "conf" / "pipelines" / (pipeline_name + ".yml")).exists():
        store.error_message = f"Pipeline configuration '{pipeline_name}.yml' not found. Cannot generate DAG."
        store.dag_representation = "Pipeline configuration missing."
    else:
        try:
            manager = PipelineManager(base_dir=str(project_path))
            # Assuming show_dag might raise ImportError if graphviz is missing,
            # or return None/str for other issues.
            dag_svg_or_text = manager.visualizer.show_dag(name=pipeline_name, format='svg', raw=True)

            if dag_svg_or_text and isinstance(dag_svg_or_text, str):
                store.dag_representation = dag_svg_or_text
            else: # Covers None or unexpected types
                store.error_message = "Could not generate DAG. Graphviz might not be installed or the pipeline module may have errors."
                store.dag_representation = "SVG DAG generation failed. Textual representation not yet available as a fallback."
        
        except ImportError as ie: # Specifically for graphviz potentially
            store.error_message = f"Graphviz might not be installed or found in PATH, which is required for SVG DAG visualization: {ie}"
            store.dag_representation = "SVG DAG generation failed due to missing Graphviz. Textual representation not yet available."
            print(f"ImportError during DAG generation for {project_name}/{pipeline_name}: {ie}", file=sys.stderr)
        except NotImplementedError:
             store.error_message = "DAG visualization is currently disabled (PipelineManager or its visualizer not available)."
             store.dag_representation = "DAG visualization disabled."
        except FileNotFoundError as fnfe: # e.g. if pipeline .py file is missing
            store.error_message = f"Error generating DAG for '{pipeline_name}': A required file was not found: {fnfe}"
            store.dag_representation = "DAG generation failed due to missing file."
            print(f"FileNotFoundError during DAG generation for {project_name}/{pipeline_name}: {fnfe}", file=sys.stderr)
        except Exception as e:
            store.error_message = f"An unexpected error occurred while generating DAG for pipeline '{pipeline_name}': {e}"
            store.dag_representation = "DAG generation failed due to an unexpected error."
            print(f"Traceback for DAG generation error ({project_name}/{pipeline_name}):", file=sys.stderr)
            import traceback; traceback.print_exc(file=sys.stderr)
            
    return datastar_html_response(Html(pipeline_dag_page_content(stores={"page": store})))

if __name__ == "__main__":
    ensure_projects_root_exists() 
    create_dummy_projects_if_needed() 
    app.run(host="0.0.0.0", port=8000, auto_reload=True, debug=True)

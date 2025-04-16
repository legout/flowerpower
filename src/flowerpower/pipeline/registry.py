# -*- coding: utf-8 -*-
"""Pipeline Registry for discovery, listing, creation, and deletion."""

import logging
import posixpath

from typing import TYPE_CHECKING, Any

import jinja2
import rich  # <-- Add this import
from fsspec.spec import AbstractFileSystem
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table


# Import necessary config types and utility functions
from ..cfg.base import Config
 # Assuming view_img might be used indirectly or needed later
from ..utils.templates import PIPELINE_PY_TEMPLATE

if TYPE_CHECKING:
    # Keep this for type hinting if needed elsewhere, though Config is imported directly now
    pass


logger = logging.getLogger(__name__)


class PipelineRegistry:
    """Manages discovery, listing, creation, and deletion of pipelines."""

    def __init__(
        self,
        fs: AbstractFileSystem,
        base_dir: str,
        cfg_dir: str,
        pipelines_dir: str,
        load_config_func: callable,
    ):
        """
        Initializes the PipelineRegistry.

        Args:
            fs: Filesystem object.
            base_dir: Base directory for the project.
            cfg_dir: Configuration directory path.
            pipelines_dir: Pipelines directory path.
            load_config_func: Function to load configuration.
        """
        self._fs = fs
        self._base_dir = base_dir
        self._cfg_dir = cfg_dir
        self._pipelines_dir = pipelines_dir
        self._load_config_func = load_config_func
        self._console = Console()

    # --- Methods moved from PipelineManager ---

    def new(
        self,
        name: str,
        cfg: "Config",  # Accept Config object directly
        template: str | None = None,
        template_kwargs: dict | None = None,
        overwrite: bool = False,
    ) -> None:
        """
        Create a new pipeline.

        Args:
            name (str): The name of the pipeline.
            cfg (Config): The loaded configuration object.
            template (str | None, optional): The template to use. Defaults to None.
            template_kwargs (dict | None, optional): The template keyword arguments. Defaults to None.
            overwrite (bool, optional): Whether to overwrite existing files. Defaults to False.

        Returns:
            None

        Raises:
            FileExistsError: If the pipeline already exists and overwrite is False.

        Examples:
            >>> pm = PipelineManager()
            >>> pm.new("my_pipeline")
        """
        pipeline_cfg_path = posixpath.join(self._cfg_dir, "pipelines", f"{name}.yml")
        pipeline_py_path = posixpath.join(self._pipelines_dir, f"{name}.py")

        if self._fs.exists(pipeline_cfg_path) and not overwrite:
            raise FileExistsError(
                f"Pipeline config {pipeline_cfg_path} already exists."
            )
        if self._fs.exists(pipeline_py_path) and not overwrite:
            raise FileExistsError(f"Pipeline module {pipeline_py_path} already exists.")

        # Create pipeline config file (minimal structure)
        default_pipeline_cfg = {
            "name": name,
            "description": f"Pipeline {name}",
            # Add other minimal default config sections if necessary
            "run": {"final_vars": []},
            "schedule": {"enabled": False},
            "tracker": {},
        }
        # Use cfg.save_pipeline to ensure consistency if available, otherwise dump manually
        # Assuming Config object has a way to save a specific pipeline config
        # This part might need refinement based on Config class capabilities
        try:
            # Ideal scenario: Config object handles saving pipeline specifics
            cfg.save_pipeline(name, default_pipeline_cfg, fs=self._fs)
            logger.info(f"Created pipeline config: {pipeline_cfg_path}")
        except AttributeError:
            # Fallback: Manually dump YAML (less ideal)
            import yaml  # Import locally if not standard

            with self._fs.open(pipeline_cfg_path, "w") as f:
                yaml.dump(default_pipeline_cfg, f, default_flow_style=False)
            logger.warning(
                f"Created pipeline config using basic YAML dump: {pipeline_cfg_path}"
            )

        # Create pipeline python module from template
        if template is None:
            template_content = PIPELINE_PY_TEMPLATE
        else:
            # Load custom template (assuming it's accessible via fs)
            try:
                with self._fs.open(template, "r") as f:
                    template_content = f.read()
            except FileNotFoundError:
                logger.error(f"Custom template not found: {template}")
                # Decide how to handle: raise error or fallback to default?
                # For now, fallback to default
                logger.warning("Falling back to default pipeline template.")
                template_content = PIPELINE_PY_TEMPLATE
            except Exception as e:
                logger.error(f"Error loading custom template {template}: {e}")
                logger.warning("Falling back to default pipeline template.")
                template_content = PIPELINE_PY_TEMPLATE

        template_kwargs = template_kwargs or {}
        template_kwargs.setdefault("pipeline_name", name)  # Ensure name is available

        try:
            jinja_template = jinja2.Template(template_content)
            rendered_code = jinja_template.render(**template_kwargs)
        except Exception as e:
            logger.error(f"Error rendering Jinja template for {name}: {e}")
            # Handle error, maybe raise or use a very basic fallback
            rendered_code = (
                f"# Pipeline: {name}\n\n# Add your Hamilton functions here\n"
            )
            logger.warning("Using basic fallback code due to template rendering error.")

        with self._fs.open(pipeline_py_path, "w") as f:
            f.write(rendered_code)
        logger.info(f"Created pipeline module: {pipeline_py_path}")

        # Sync filesystem if needed
        if hasattr(self._fs, "sync") and callable(getattr(self._fs, "sync")):
            self._fs.sync()

    def delete(self, name: str, cfg: bool = True, module: bool = False):
        """
        Delete a pipeline.

        Args:
            name (str): The name of the pipeline.
            cfg (bool, optional): Whether to delete the config file. Defaults to True.
            module (bool, optional): Whether to delete the module file. Defaults to False.

        Returns:
            None

        Raises:
            FileNotFoundError: If the specified files do not exist.

        Examples:
            >>> pm = PipelineManager()
            >>> pm.delete("my_pipeline")
        """
        deleted_files = []
        if cfg:
            pipeline_cfg_path = posixpath.join(
                self._cfg_dir, "pipelines", f"{name}.yml"
            )
            if self._fs.exists(pipeline_cfg_path):
                self._fs.rm(pipeline_cfg_path)
                deleted_files.append(pipeline_cfg_path)
                logger.info(f"Deleted pipeline config: {pipeline_cfg_path}")
            else:
                logger.warning(
                    f"Config file not found, skipping deletion: {pipeline_cfg_path}"
                )

        if module:
            pipeline_py_path = posixpath.join(self._pipelines_dir, f"{name}.py")
            if self._fs.exists(pipeline_py_path):
                self._fs.rm(pipeline_py_path)
                deleted_files.append(pipeline_py_path)
                logger.info(f"Deleted pipeline module: {pipeline_py_path}")
            else:
                logger.warning(
                    f"Module file not found, skipping deletion: {pipeline_py_path}"
                )

        if not deleted_files:
            logger.warning(
                f"No files found or specified for deletion for pipeline '{name}'."
            )

        # Sync filesystem if needed
        if hasattr(self._fs, "sync") and callable(getattr(self._fs, "sync")):
            self._fs.sync()

    def _get_files(self) -> list[str]:
        """
        Get the list of pipeline files.

        Returns:
            list[str]: The list of pipeline files.
        """
        try:
            return self._fs.glob(posixpath.join(self._pipelines_dir, "*.py"))
        except Exception as e:
            logger.error(
                f"Error accessing pipeline directory {self._pipelines_dir}: {e}"
            )
            return []

    def _get_names(self) -> list[str]:
        """
        Get the list of pipeline names.

        Returns:
            list[str]: The list of pipeline names.
        """
        files = self._get_files()
        return [posixpath.basename(f).replace(".py", "") for f in files]

    def get_summary(
        self, name: str, reload: bool = False, rich_render: bool = False
    ) -> dict[str, Any] | Table:
        """
        Get the summary of a pipeline.

        Args:
            name (str): The name of the pipeline.
            reload (bool, optional): Whether to reload the configuration. Defaults to False.
            rich_render (bool, optional): Whether to return a rich Table object. Defaults to False.


        Returns:
            dict[str, Any] | Table: The summary of the pipeline as a dictionary or rich Table.
        """
        # Use the passed load_config_func
        cfg = self._load_config_func(name=name, reload=reload)

        summary_data = {
            "Name": cfg.pipeline.name,
            "Description": cfg.pipeline.description,
            "Config Path": cfg.pipeline_cfg_path,
            "Module Path": posixpath.join(self._pipelines_dir, f"{name}.py"),
            "Run Config": cfg.pipeline.run.to_dict(),
            "Schedule Config": cfg.pipeline.schedule.to_dict(),
            "Tracker Config": cfg.pipeline.tracker.to_dict(),
            "Project Config": cfg.project.to_dict(),  # Include relevant project config
        }

        if rich_render:
            table = Table(
                title=f"Pipeline Summary: {name}",
                show_header=False,
                box=rich.box.ROUNDED,
            )
            table.add_column("Parameter", style="cyan")
            table.add_column("Value", style="magenta")

            for key, value in summary_data.items():
                if isinstance(value, dict):
                    # Simple representation for dicts in the table
                    value_str = "\n".join([f"  {k}: {v}" for k, v in value.items()])
                    table.add_row(key, value_str)
                else:
                    table.add_row(key, str(value))
            return table
        else:
            return summary_data

    def show_summary(
        self,
        name: str,
        reload: bool = False,
        show_code: bool = False,
        max_lines: int | None = None,
    ) -> None:
        """
        Show the summary of a pipeline.

        Args:
            name (str): The name of the pipeline.
            reload (bool, optional): Whether to reload the configuration. Defaults to False.
            show_code (bool, optional): Whether to show the pipeline code. Defaults to False.
            max_lines (int | None, optional): Maximum lines of code to show. Defaults to None.

        Returns:
            None
        """
        summary_table = self.get_summary(name=name, reload=reload, rich_render=True)
        self._console.print(summary_table)

        if show_code:
            pipeline_py_path = posixpath.join(self._pipelines_dir, f"{name}.py")
            try:
                with self._fs.open(pipeline_py_path, "r") as f:
                    code = f.read()

                if max_lines:
                    code_lines = code.splitlines()
                    code = "\n".join(code_lines[:max_lines])
                    if len(code_lines) > max_lines:
                        code += f"\n... (truncated - {len(code_lines) - max_lines} more lines)"

                code_view = Syntax(
                    code,
                    "python",
                    theme="default",  # Or choose another theme
                    line_numbers=True,
                    word_wrap=True,
                )
                self._console.print(
                    Panel(
                        code_view,
                        title=f"Code: {pipeline_py_path}",
                        border_style="green",
                    )
                )
            except FileNotFoundError:
                self._console.print(
                    f"[bold red]Error:[/bold red] Code file not found: {pipeline_py_path}"
                )
            except Exception as e:
                self._console.print(
                    f"[bold red]Error reading code file {pipeline_py_path}:[/bold red] {e}"
                )

        # Optionally show DAG if needed/possible from registry context
        # show_dag functionality might remain in PipelineManager if it needs driver/execution context

        # Display schedule info if available (might need worker interaction)
        # This part might be better handled by a dedicated scheduling component or remain in PipelineManager
        # For now, let's keep it simple and focus on config/code summary.
        # Example placeholder:
        # try:
        #     # Assuming a way to get schedule info related to this pipeline
        #     schedule_info = self._get_schedule_info(name) # Hypothetical method
        #     if schedule_info:
        #         schedule_tree = Tree("📅 Schedule Info", style="bold yellow")
        #         # Populate tree...
        #         self._console.print(schedule_tree)
        # except Exception as e:
        #     logger.warning(f"Could not retrieve schedule info for {name}: {e}")

    @property
    def summary(self) -> dict[str, dict | str]:
        """
        Get the summary of all pipelines.

        Returns:
            dict[str, dict | str]: The summary of all pipelines.
        """
        all_summaries = {}
        for name in self._get_names():
            try:
                all_summaries[name] = self.get_summary(name=name, rich_render=False)
            except Exception as e:
                logger.error(f"Failed to get summary for pipeline '{name}': {e}")
                all_summaries[name] = {"error": str(e)}  # Indicate error in summary
        return all_summaries

    def _all_pipelines(
        self,
        filter_str: str | None = None,
        include_cfg: bool = True,
        include_module: bool = True,
        rich_render: bool = False,
    ) -> dict[str, dict[str, Any]] | Table:
        """
        Get information about all pipelines, optionally filtered.

        Args:
            filter_str (str | None, optional): A string to filter pipeline names. Defaults to None.
            include_cfg (bool, optional): Whether to include config file path. Defaults to True.
            include_module (bool, optional): Whether to include module file path. Defaults to True.
            rich_render (bool, optional): Whether to return a rich Table object. Defaults to False.


        Returns:
             dict[str, dict[str, Any]] | Table: Dictionary or rich Table with pipeline info.
        """
        pipeline_names = self._get_names()
        if filter_str:
            pipeline_names = [name for name in pipeline_names if filter_str in name]

        pipelines_info = {}
        for name in pipeline_names:
            info = {"name": name}
            if include_cfg:
                cfg_path = posixpath.join(self._cfg_dir, "pipelines", f"{name}.yml")
                info["config_path"] = cfg_path
                info["config_exists"] = self._fs.exists(cfg_path)
            if include_module:
                module_path = posixpath.join(self._pipelines_dir, f"{name}.py")
                info["module_path"] = module_path
                info["module_exists"] = self._fs.exists(module_path)
            pipelines_info[name] = info

        if rich_render:
            table = Table(title="Pipelines", box=rich.box.ROUNDED)
            table.add_column("Name", style="cyan", no_wrap=True)
            if include_cfg:
                table.add_column("Config Path", style="magenta")
                table.add_column("Config Exists", style="yellow")
            if include_module:
                table.add_column("Module Path", style="green")
                table.add_column("Module Exists", style="blue")

            for name, info in pipelines_info.items():
                row_data = [name]
                if include_cfg:
                    row_data.extend(
                        [
                            info.get("config_path", "N/A"),
                            str(info.get("config_exists", "N/A")),
                        ]
                    )
                if include_module:
                    row_data.extend(
                        [
                            info.get("module_path", "N/A"),
                            str(info.get("module_exists", "N/A")),
                        ]
                    )
                table.add_row(*row_data)
            return table
        else:
            return pipelines_info

    def show_pipelines(self) -> None:
        """
        Show all pipelines in a table.
        """
        pipelines_table = self._all_pipelines(rich_render=True)
        self._console.print(pipelines_table)

    def list_pipelines(self) -> list[str]:
        """
        List all pipeline names.

        Returns:
            list[str]: A list of pipeline names.
        """
        return self._get_names()

    @property
    def pipelines(self) -> list[str]:
        """
        Get the list of pipeline names.

        Returns:
            list[str]: The list of pipeline names.
        """
        return self.list_pipelines()

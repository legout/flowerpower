import importlib
import posixpath
from types import ModuleType

from fsspeckit import AbstractFileSystem
from hamilton import driver
from rich import print

# Import necessary config types and utility functions
from ..cfg import ProjectConfig
from ..settings import CONFIG_DIR, PIPELINES_DIR
from ..utils.filesystem import add_modules_path, format_pipeline_package_root
from ..utils.security import validate_directory_fragment, validate_pipeline_name
from ..utils.visualization import view_img
from ..utils.misc import load_module
from .config_manager import PipelineConfigManager


class PipelineVisualizer:
    """Handles the visualization of pipeline DAGs."""

    def __init__(
        self,
        project_cfg: ProjectConfig,
        fs: AbstractFileSystem,
        base_dir: str = ".",
        cfg_dir: str = CONFIG_DIR,
        pipelines_dir: str = PIPELINES_DIR,
    ):
        """
        Initializes the PipelineVisualizer.

        Args:
            project_cfg: The project configuration object.
            fs: The filesystem instance.
            base_dir: Project root used for config loading and import path setup.
            cfg_dir: Configuration directory containing project/pipeline YAML files.
            pipelines_dir: Python package / directory containing pipeline modules.
        """
        self.project_cfg = project_cfg
        self._fs = fs
        self._base_dir = base_dir
        self._cfg_dir = validate_directory_fragment(cfg_dir)
        self._pipelines_dir = validate_directory_fragment(pipelines_dir)
        self._config_manager = PipelineConfigManager(
            base_dir=base_dir,
            fs=fs,
            storage_options={},
            cfg_dir=self._cfg_dir,
            pipelines_dir=self._pipelines_dir,
        )
        add_modules_path(self._fs, self._pipelines_dir, self._base_dir)

    def _get_dag_object(
        self,
        name: str,
        reload: bool = False,
        additional_modules: list[str | ModuleType] | None = None,
    ):
        """Get the Hamilton DAG object for a pipeline.

        Args:
            name (str): The name of the pipeline.
            reload (bool): Whether to reload the module.
            additional_modules (list[str | ModuleType] | None): Optional modules to
                load alongside the primary pipeline for visualization.

        Returns:
            Hamilton DAG object.

        Raises:
            ImportError: If the module cannot be loaded.

        Notes:
            - Unqualified string entries in ``additional_modules`` are resolved
              using the configured pipeline package first, then via raw imports,
              with hyphen-to-underscore and ``pipelines.<name>`` fallbacks.
            - ``reload=True`` reloads every module (primary + additional) before the
              driver is constructed, which mirrors runtime execution behaviour.

        """
        name = validate_pipeline_name(name)
        pipeline_cfg = self._config_manager.load_pipeline_config(name, reload=reload)

        # Load modules (primary + optional additional)
        modules = self._resolve_modules(name, additional_modules, reload)

        # Create a basic driver builder for visualization purposes
        # Use the run config from the loaded pipeline_cfg
        builder = (
            driver.Builder()
            .enable_dynamic_execution(allow_experimental_mode=True)
            .with_modules(*modules)
            .with_config(pipeline_cfg.run.config or {})
            # No adapters or complex executors needed for display_all_functions
        )

        # Build the driver
        dr = builder.build()

        # Return the visualization object
        return dr.display_all_functions()

    def save_dag(
        self,
        name: str,
        base_dir: str = ".",
        format: str = "png",
        reload: bool = False,
        output_path: str | None = None,
        additional_modules: list[str | ModuleType] | None = None,
    ) -> str:
        """
        Save an image of the graph of functions for a given pipeline name.

        Args:
            name (str): The name of the pipeline graph.
            format (str, optional): The format of the graph file. Defaults to "png".
            reload (bool, optional): Whether to reload the pipeline data. Defaults to False.

        Raises:
            ImportError: If any module cannot be loaded.

        Notes:
            - ``additional_modules`` uses the same resolution strategy as pipeline execution.
            - Pass ``reload=True`` to reload the primary and additional modules before rendering.

        Example:
            >>> from flowerpower.pipeline.visualizer import PipelineVisualizer
            >>> visualizer = PipelineVisualizer(project_cfg, fs)
            >>> visualizer.save_dag(name="example_pipeline", format="png")
            >>> visualizer.save_dag(
            ...     name="example_pipeline",
            ...     format="png",
            ...     additional_modules=["setup"],
            ... )
            >>> # Compose hello_world + setup from examples/hello-world/pipelines/
        """
        name = validate_pipeline_name(name)
        dag = self._get_dag_object(
            name=name, reload=reload, additional_modules=additional_modules
        )

        # Determine final output path
        if output_path is None:
            graph_dir = posixpath.join(base_dir, "graphs")
            self._fs.makedirs(graph_dir, exist_ok=True)
            base = posixpath.join(graph_dir, name)
            final_path = f"{base}.{format}"
            render_path = base
        else:
            # If output_path already has an extension, use as-is; otherwise append format
            if "." in posixpath.basename(output_path):
                final_path = output_path
                # Remove extension for graphviz render base path
                render_path = final_path.rsplit(".", 1)[0]
                fmt = final_path.rsplit(".", 1)[1]
                if fmt != format:
                    # Honor explicit extension if it differs from format argument
                    format = fmt
            else:
                final_path = f"{output_path}.{format}"
                render_path = output_path

        # Render the DAG using the graphviz object returned by display_all_functions
        dag.render(
            render_path,  # graphviz appends the format automatically
            format=format,
            cleanup=True,
            view=False,
        )
        project_label = name
        if self.project_cfg.name:
            project_label = f"{self.project_cfg.name}.{name}"
        print(
            f"📊 Saved graph for [bold blue]{project_label}[/bold blue] to [green]{final_path}[/green]"
        )
        return final_path

    def show_dag(
        self,
        name: str,
        format: str = "png",
        reload: bool = False,
        raw: bool = False,
        additional_modules: list[str | ModuleType] | None = None,
    ):
        """
        Display the graph of functions for a given pipeline name.

        Args:
            name (str): The name of the pipeline graph.
            format (str, optional): The format of the graph file. Defaults to "png".
            reload (bool, optional): Whether to reload the pipeline data. Defaults to False.
            raw (bool, optional): Whether to return the raw graph object instead of displaying. Defaults to False.

        Returns:
            Optional[graphviz.Digraph]: The generated graph object if raw=True, else None.

        Raises:
            ImportError: If any module cannot be loaded.

        Notes:
            - ``additional_modules`` follows the same resolution strategy as pipeline execution.
            - Use ``reload=True`` to pull in code changes from every module before rendering.

        Example:
            >>> from flowerpower.pipeline.visualizer import PipelineVisualizer
            >>> visualizer = PipelineVisualizer(project_cfg, fs)
            >>> visualizer.show_dag(name="example_pipeline", format="png")
            >>> visualizer.show_dag(
            ...     name="example_pipeline",
            ...     format="png",
            ...     additional_modules=["setup"],
            ... )
            >>> # Compose hello_world + setup modules during development
        """
        name = validate_pipeline_name(name)
        dag = self._get_dag_object(
            name=name, reload=reload, additional_modules=additional_modules
        )
        if raw:
            return dag
        # Use view_img utility to display the rendered graph
        view_img(dag.pipe(format=format), format=format)
        return None  # Explicitly return None when not raw

    def _resolve_modules(
        self,
        name: str,
        additional_modules: list[str | ModuleType] | None,
        reload: bool,
    ) -> list[ModuleType]:
        modules: list[ModuleType] = []

        def _append_unique(module_obj: ModuleType) -> None:
            if any(existing is module_obj for existing in modules):
                return
            modules.append(module_obj)

        if additional_modules:
            for entry in additional_modules:
                module_obj = self._coerce_to_module(entry, reload=reload)
                _append_unique(module_obj)

        primary_module = self._coerce_to_module(name, reload=reload)
        _append_unique(primary_module)

        return modules

    def _coerce_to_module(
        self, entry: str | ModuleType, reload: bool = False
    ) -> ModuleType:
        if isinstance(entry, ModuleType):
            if reload:
                importlib.reload(entry)
            return entry

        formatted = entry.replace("-", "_")
        package_root = format_pipeline_package_root(self._pipelines_dir)
        candidates: list[str] = []
        if package_root and "." not in formatted:
            candidates.append(f"{package_root}.{formatted}")
        for candidate in (entry, formatted):
            if candidate not in candidates:
                candidates.append(candidate)
        if package_root and not formatted.startswith(f"{package_root}."):
            qualified_candidate = f"{package_root}.{formatted}"
            if qualified_candidate not in candidates:
                candidates.append(qualified_candidate)
        if package_root != PIPELINES_DIR and not formatted.startswith(
            f"{PIPELINES_DIR}."
        ):
            candidates.append(f"{PIPELINES_DIR}.{formatted}")

        errors: list[ImportError] = []
        for candidate in candidates:
            try:
                return load_module(name=candidate, reload=reload)
            except ImportError as error:
                errors.append(error)

        raise ImportError(
            f"Could not import module '{entry}'. Tried: {candidates}"
        ) from errors[-1] if errors else None

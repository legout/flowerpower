import importlib
import posixpath
from types import ModuleType

from fsspeckit import AbstractFileSystem
from hamilton import driver
from rich import print

# Import necessary config types and utility functions
from ..cfg import PipelineConfig, ProjectConfig
from ..utils.misc import view_img
from .base import load_module  # Import module loading utility


class PipelineVisualizer:
    """Handles the visualization of pipeline DAGs."""

    def __init__(self, project_cfg: ProjectConfig, fs: AbstractFileSystem):
        """
        Initializes the PipelineVisualizer.

        Args:
            project_cfg: The project configuration object.
            fs: The filesystem instance.
        """
        self.project_cfg = project_cfg
        self._fs = fs
        # Attributes like fs and base_dir are accessed via self.project_cfg

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
            - String entries in ``additional_modules`` are resolved using the same
              strategy as pipeline execution: the raw name, a hyphen-to-underscore
              variant, and ``pipelines.<name>`` are attempted in order.
            - ``reload=True`` reloads every module (primary + additional) before the
              driver is constructed, which mirrors runtime execution behaviour.

        """
        # Load pipeline-specific config
        pipeline_cfg = PipelineConfig.load(name=name, fs=self._fs)

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
        base_dir: str,
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
        print(
            f"📊 Saved graph for [bold blue]{self.project_cfg.name}.{name}[/bold blue] to [green]{final_path}[/green]"
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

        try:
            module_obj = load_module(name=entry, reload=reload)
        except ImportError as original_error:
            formatted = entry.replace("-", "_")
            candidates = [formatted]
            if not formatted.startswith("pipelines."):
                candidates.append(f"pipelines.{formatted}")

            for candidate in candidates:
                try:
                    module_obj = load_module(name=candidate, reload=reload)
                    break
                except ImportError:
                    continue
            else:
                raise ImportError(
                    f"Could not import module '{entry}'. Tried: {candidates}"
                ) from original_error

        return module_obj

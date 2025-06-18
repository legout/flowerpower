import posixpath
from types import TracebackType

from hamilton import driver
from rich import print

# Import necessary config types and utility functions
from ..cfg import PipelineConfig
from ..fs import AbstractFileSystem
from ..utils.misc import view_img
from .base import load_module  # Import module loading utility


class PipelineVisualizer:
    """Handles the visualization of pipeline DAGs."""

    def __init__(self, project_name: str, base_dir: str, fs: AbstractFileSystem):
        """
        Initializes the PipelineVisualizer.

        Args:
            project_cfg: The project configuration object.
            fs: The filesystem instance.
        """
        self._project_name = project_name
        self._base_dir = base_dir
        self._fs = fs
        # Attributes like fs and base_dir are accessed via self.project_cfg

    def __enter__(self) -> "PipelineVisualizer":
        """Enter the context manager.

        Enables use of the manager in a with statement for automatic resource cleanup.

        Returns:
            PipelineVisualizer: Self for use in context manager.

        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the context manager.

        Handles cleanup of resources when exiting a with statement.

        Args:
            exc_type: Type of exception that occurred, if any
            exc_val: Exception instance that occurred, if any
            exc_tb: Traceback of exception that occurred, if any


        """
        # Add cleanup code if needed
        pass

    def _display_all_function(self, name: str, reload: bool = False):
        """Internal helper to load module/config and get the Hamilton DAG object.

        Args:
            name (str): The name of the pipeline.
            reload (bool): Whether to reload the module.

        Returns:
            Hamilton DAG object.

        Raises:
            ImportError: If the module cannot be loaded.

        """
        # Load pipeline-specific config
        pipeline_cfg = PipelineConfig.load(name=name, fs=self._fs)

        # Load the pipeline module
        # Ensure the pipelines directory is in sys.path (handled by PipelineManager usually)
        module = load_module(name=name, reload=reload)

        # Create a basic driver builder for visualization purposes
        # Use the run config from the loaded pipeline_cfg
        builder = (
            driver.Builder()
            .enable_dynamic_execution(allow_experimental_mode=True)
            .with_modules(module)
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
        format: str = "png",
        reload: bool = False,
    ):
        """
        Save an image of the graph of functions for a given pipeline name.

        Args:
            name (str): The name of the pipeline graph.
            format (str, optional): The format of the graph file. Defaults to "png".
            reload (bool, optional): Whether to reload the pipeline data. Defaults to False.

        Raises:
            ImportError: If the module cannot be loaded.

        Example:
            >>> from flowerpower.pipeline.visualizer import PipelineVisualizer
            >>> visualizer = PipelineVisualizer(name, base_dir, fs)
            >>> visualizer.save_dag(name="example_pipeline", format="png")
        """
        dag = self._display_all_function(name=name, reload=reload)

        # Use project_cfg attributes for path and filesystem access
        graph_dir = posixpath.join(self._base_dir, "graphs")
        self._fs.makedirs(graph_dir, exist_ok=True)

        output_path = posixpath.join(
            graph_dir, name
        )  # Output filename is just the pipeline name
        output_path_with_ext = f"{output_path}.{format}"

        # Render the DAG using the graphviz object returned by display_all_functions
        dag.render(
            output_path,  # graphviz appends the format automatically
            format=format,
            cleanup=True,
            view=False,
        )
        print(
            f"📊 Saved graph for [bold blue]{self._project_name}.{name}[/bold blue] to [green]{output_path_with_ext}[/green]"
        )

    def show_dag(
        self,
        name: str,
        format: str = "png",
        reload: bool = False,
        raw: bool = False,
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
            ImportError: If the module cannot be loaded.

        Example:
            >>> from flowerpower.pipeline.visualizer import PipelineVisualizer
            >>> visualizer = PipelineVisualizer(name, base_dir, fs)
            >>> visualizer.show_dag(name="example_pipeline", format="png")
        """
        dag = self._display_all_function(name=name, reload=reload)
        if raw:
            return dag
        # Use view_img utility to display the rendered graph
        view_img(dag.pipe(format=format), format=format)
        return None  # Explicitly return None when not raw

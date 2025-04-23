import posixpath
from typing import Any

from hamilton import driver
from rich import print

# Import necessary config types and utility functions
from ..cfg import PipelineConfig, ProjectConfig
from ..utils.misc import view_img
from .base import load_module  # Import module loading utility


class PipelineVisualizer:
    """Handles the visualization of pipeline DAGs."""

    def __init__(self, project_cfg: ProjectConfig):
        """
        Initializes the PipelineVisualizer.

        Args:
            project_cfg: The project configuration object.
        """
        self.project_cfg = project_cfg
        # Attributes like fs and base_dir are accessed via self.project_cfg

    def _display_all_function(self, name: str, reload: bool = False):
        """Internal helper to load module/config and get the Hamilton DAG object."""
        # Load pipeline-specific config
        pipeline_cfg = PipelineConfig.load(
            base_dir=self.project_cfg.base_dir, name=name, fs=self.project_cfg.fs
        )

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
        """
        dag = self._display_all_function(name=name, reload=reload)

        # Use project_cfg attributes for path and filesystem access
        graph_dir = posixpath.join(self.project_cfg.base_dir, "graphs")
        self.project_cfg.fs.makedirs(graph_dir, exist_ok=True)

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
            f"📊 Saved graph for [bold blue]{self.project_cfg.name}.{name}[/bold blue] to [green]{output_path_with_ext}[/green]"
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
        """
        dag = self._display_all_function(name=name, reload=reload)
        if raw:
            return dag
        # Use view_img utility to display the rendered graph
        view_img(dag.pipe(format=format), format=format)
        return None  # Explicitly return None when not raw

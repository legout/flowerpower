import posixpath

from fsspec_utils import AbstractFileSystem
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

    def _get_dag_object(self, name: str, reload: bool = False):
        """Get the Hamilton DAG object for a pipeline.

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
        base_dir: str,
        format: str = "png",
        reload: bool = False,
        output_path: str | None = None,
    ) -> str:
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
            >>> visualizer = PipelineVisualizer(project_cfg, fs)
            >>> visualizer.save_dag(name="example_pipeline", format="png")
        """
        dag = self._get_dag_object(name=name, reload=reload)

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
            >>> visualizer = PipelineVisualizer(project_cfg, fs)
            >>> visualizer.show_dag(name="example_pipeline", format="png")
        """
        dag = self._get_dag_object(name=name, reload=reload)
        if raw:
            return dag
        # Use view_img utility to display the rendered graph
        view_img(dag.pipe(format=format), format=format)
        return None  # Explicitly return None when not raw

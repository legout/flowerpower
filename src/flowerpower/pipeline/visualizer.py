import posixpath
from typing import Any, Callable, Dict, Optional

from fsspec.spec import AbstractFileSystem
from hamilton import driver
from rich import print

# Ensure view_img is imported from the correct location
from ..utils.misc import view_img


class PipelineVisualizer:
    """Handles the visualization of pipeline DAGs."""

    def __init__(
        self,
        fs: AbstractFileSystem,
        base_dir: str,
        # Assuming the passed functions can handle the 'reload' parameter
        load_config_func: Callable[[str, bool], Dict[str, Any]],
        load_module_func: Callable[[str, bool], Any],
        get_driver_builder_func: Callable[[Any, Dict[str, Any]], driver.Builder],
    ):
        """
        Initializes the PipelineVisualizer.

        Args:
            fs: Filesystem object.
            base_dir: Base directory for pipelines.
            load_config_func: Function to load pipeline configuration.
            load_module_func: Function to load pipeline module.
            get_driver_builder_func: Function to get a basic Hamilton Driver Builder.
        """
        self._fs = fs
        self._base_dir = base_dir
        self._load_config_func = load_config_func
        self._load_module_func = load_module_func
        self._get_driver_builder_func = get_driver_builder_func

    def _display_all_function(self, name: str, reload: bool = True):
        """Internal helper to get the Hamilton DAG object."""
        # Load config and module using the provided functions
        # Pass reload flag, assuming the functions handle it
        config = self._load_config_func(name, reload=reload)
        module = self._load_module_func(name, reload=reload)

        # Get the basic driver builder
        builder = self._get_driver_builder_func(module, config)

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

        graph_dir = posixpath.join(self._base_dir, "graphs")
        self._fs.makedirs(graph_dir, exist_ok=True)

        output_path = posixpath.join(graph_dir, name)
        dag.render(
            output_path,
            format=format,
            cleanup=True,
            view=False, # Ensure it doesn't try to open the file
        )
        print(
            f"📊 Saved graph for [bold blue]{name}[/bold blue] to [green]{output_path}.{format}[/green]"
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
        return None # Explicitly return None when not raw
"""Pipeline lifecycle management."""

from typing import TYPE_CHECKING, Optional

import rich

if TYPE_CHECKING:
    from .registry import HookType, PipelineRegistry


class PipelineLifecycleManager:
    """Handles pipeline creation, deletion, and metadata management.
    
    This class is responsible for:
    - Creating new pipelines
    - Deleting existing pipelines
    - Managing pipeline metadata and summaries
    - Displaying pipeline information
    - Managing hooks
    """
    
    def __init__(self, registry: "PipelineRegistry"):
        """Initialize the lifecycle manager.
        
        Args:
            registry: Pipeline registry for pipeline operations
        """
        self._registry = registry
    
    def create_pipeline(
        self,
        name: str,
        overwrite: bool = False,
        template: Optional[str] = None,
        tags: Optional[list[str]] = None,
        description: Optional[str] = None
    ) -> None:
        """Create a new pipeline.
        
        Args:
            name: Name of the pipeline to create
            overwrite: Whether to overwrite existing pipeline
            template: Template to use for pipeline creation
            tags: Tags to associate with the pipeline
            description: Description of the pipeline
        """
        self._registry.create_pipeline(
            name=name,
            overwrite=overwrite,
            template=template,
            tags=tags or [],
            description=description or ""
        )
    
    def delete_pipeline(
        self,
        name: str,
        cfg: bool = True,
        module: bool = False
    ) -> None:
        """Delete a pipeline.
        
        Args:
            name: Name of the pipeline to delete
            cfg: Whether to delete configuration file
            module: Whether to delete module file
        """
        self._registry.delete_pipeline(name=name, cfg=cfg, module=module)
    
    def get_summary(
        self,
        name: Optional[str] = None,
        cfg: bool = True,
        code: bool = True,
        project: bool = True
    ) -> dict:
        """Get pipeline summary information.
        
        Args:
            name: Name of pipeline to summarize, or None for all pipelines
            cfg: Whether to include configuration information
            code: Whether to include code information
            project: Whether to include project information
            
        Returns:
            dict: Summary information
        """
        if name is None:
            # Get summary for all pipelines
            return self._registry.get_summaries(cfg=cfg, code=code, project=project)
        else:
            # Get summary for specific pipeline
            pipeline = self._registry.get_pipeline_object(name=name)
            return pipeline.get_summary(cfg=cfg, code=code, project=project)
    
    def show_summary(
        self,
        name: Optional[str] = None,
        cfg: bool = True,
        code: bool = True,
        project: bool = True,
        to_html: bool = False,
        to_svg: bool = False
    ) -> None:
        """Display pipeline summary.
        
        Args:
            name: Name of pipeline to summarize, or None for all pipelines
            cfg: Whether to include configuration information
            code: Whether to include code information
            project: Whether to include project information
            to_html: Whether to output HTML
            to_svg: Whether to output SVG
        """
        summary = self.get_summary(name=name, cfg=cfg, code=code, project=project)
        
        if name is None:
            # Display all pipelines in a table
            from rich.table import Table
            table = Table(title="Pipeline Summaries")
            table.add_column("Pipeline", style="cyan")
            table.add_column("Tags", style="magenta")
            table.add_column("Description", style="green")
            table.add_column("Modified", style="yellow")
            
            for pipeline_name, info in summary.items():
                tags = ", ".join(info.get("tags", []))
                desc = info.get("description", "")[:50] + "..." if len(info.get("description", "")) > 50 else info.get("description", "")
                modified = info.get("modified", "N/A")
                table.add_row(pipeline_name, tags, desc, modified)
            
            rich.print(table)
        else:
            # Display single pipeline details
            rich.print(f"Pipeline: {name}")
            rich.print("=" * 50)
            
            for key, value in summary.items():
                if isinstance(value, dict):
                    rich.print(f"{key}:")
                    for sub_key, sub_value in value.items():
                        rich.print(f"  {sub_key}: {sub_value}")
                else:
                    rich.print(f"{key}: {value}")
    
    def show_pipelines(self) -> None:
        """Display available pipelines in a formatted table."""
        pipelines = self.list_pipelines()
        
        if not pipelines:
            rich.print("No pipelines found.")
            return
        
        # Get pipeline info for display
        pipeline_info = []
        for name in pipelines:
            try:
                summary = self.get_summary(name=name, cfg=False, code=False, project=False)
                pipeline_info.append({
                    "name": name,
                    "tags": ", ".join(summary.get("tags", [])),
                    "description": summary.get("description", "")[:50] + "..." 
                                if len(summary.get("description", "")) > 50 
                                else summary.get("description", "")
                })
            except Exception:
                pipeline_info.append({
                    "name": name,
                    "tags": "",
                    "description": "Error loading info"
                })
        
        # Display as table
        from rich.table import Table
        table = Table(title="Available Pipelines")
        table.add_column("Pipeline", style="cyan")
        table.add_column("Tags", style="magenta")
        table.add_column("Description", style="green")
        
        for info in pipeline_info:
            table.add_row(info["name"], info["tags"], info["description"])
        
        rich.print(table)
    
    def list_pipelines(self) -> list[str]:
        """List all available pipeline names.
        
        Returns:
            list[str]: List of pipeline names
        """
        return self._registry.list_pipelines()
    
    @property
    def pipelines(self) -> list[str]:
        """Get list of available pipeline names.
        
        Returns:
            list[str]: List of pipeline names
        """
        return self.list_pipelines()
    
    @property
    def summary(self) -> dict[str, dict | str]:
        """Get complete summary of all pipelines.
        
        Returns:
            dict[str, dict | str]: Complete summary information
        """
        return self.get_summary()
    
    def add_hook(
        self,
        name: str,
        type: "HookType",
        to: Optional[str] = None,
        function_name: Optional[str] = None
    ) -> None:
        """Add a hook to a pipeline.
        
        Args:
            name: Name of the pipeline
            type: Type of hook to add
            to: Target for the hook
            function_name: Name of the function to hook
        """
        self._registry.add_hook(
            name=name,
            type=type,
            to=to,
            function_name=function_name
        )
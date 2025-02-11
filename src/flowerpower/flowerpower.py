import datetime as dt
import os
import posixpath
from pathlib import Path

import rich
from fsspec.spec import AbstractFileSystem

from .cfg import Config
from .fs import get_filesystem


def init(
    name: str | None = None,
    base_dir: str | None = None,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
):
    if name is None:
        name = str(Path.cwd().name)
        base_dir = str(Path.cwd().parent)

    if base_dir is None:
        base_dir = str(Path.cwd())

    fs = get_filesystem(posixpath.join(base_dir, name), **storage_options)

    fs.makedirs("conf/pipelines", exist_ok=True)
    fs.makedirs("pipelines", exist_ok=True)

    cfg = Config.load(base_dir=posixpath.join(base_dir, name), name=name)

    with open(posixpath.join(base_dir, name, "README.md"), "w") as f:
        f.write(
            f"# {name.replace('_', ' ').upper()}\n\n"
            f"**created with FlowerPower**\n\n*{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        )
    cfg.save()
    os.chdir(posixpath.join(base_dir, name))

    rich.print(
        f"\n✨ Initialized FlowerPower project [bold blue]{name}[/bold blue] "
        f"at [italic green]{base_dir}[/italic green]\n"
    )

    rich.print(
        """[yellow]Getting Started:[/yellow]

    📦  It is recommended to use the project manager [bold cyan]`uv`[/bold cyan] to manage the
        dependenvies of your project.

    🔧  Install uv:
            [dim]Run:[/dim] [bold white]pip install uv[/bold white]
            [dim]More options:[/dim]
                [blue underline]https://docs.astral.sh/uv/getting-started/installation/[/blue underline]

    🚀  Initialize your project:
            [dim]Run the following in your project directory:[/dim]
            [bold white]uv init --app --no-readme --vcs git[/bold white]
    """
    )


# def find_pipelines(cls):
#     """Find all pipeline modules in the project's pipelines directory."""
#     pipeline_path = Path("pipelines")
#     if not pipeline_path.exists():
#         return []

#     pipelines = []
#     for file in pipeline_path.glob("*.py"):
#         if file.name.startswith("_"):
#             continue

#         module_name = file.stem
#         try:
#             pipeline = Pipeline(module_name)
#             pipelines.append(pipeline)
#         except Exception as e:
#             rich.print(f"[red]Error loading pipeline {module_name}: {str(e)}[/red]")

#     return pipelines


# def list_pipelines():
#     pipelines = Pipeline.find_pipelines()
#     if not pipelines:
#         rich.print("\n📭 [yellow]No pipelines found in this project[/yellow]\n")
#         return

#     rich.print("\n🌸 [bold magenta]Available Pipelines:[/bold magenta]\n")
#     table = rich.table.Table(show_header=True, header_style="bold cyan")
#     table.add_column("Name")
#     table.add_column("Description")
#     table.add_column("Status")

#     for pipeline in pipelines:
#         status = (
#             "[green]Active[/green]" if pipeline.is_active() else "[red]Inactive[/red]"
#         )
#         table.add_row(
#             pipeline.name, pipeline.description or "[dim]No description[/dim]", status
#         )

#     rich.print(table)
#     rich.print()

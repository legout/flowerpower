import datetime as dt
import os
from pathlib import Path


from .cfg import Config
from .pipeline import Pipeline, PipelineManager
from .scheduler import SchedulerManager
import rich

def init(name: str|None=None, base_dir:str|None=None, conf_path: str = "conf", pipelines_path: str = "pipelines"):
    if name is None:
        name = Path.cwd().name
        base_dir = Path.cwd().parent

    if base_dir is None:
        base_dir = Path.cwd()

    os.makedirs(os.path.join(base_dir, name, "conf"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, name, "pipelines"), exist_ok=True)

    cfg = Config.load(base_dir=os.path.join(base_dir,name))

    with open(os.path.join(base_dir, name, "README.md"), "w") as f:
        f.write(
            f"# {name.replace('_', ' ').upper()}\n\n"
            f"**created with FlowerPower**\n\n*{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        )
    cfg.save()
    os.chdir(os.path.join(base_dir, name))

    rich.print(f"\n✨ Initialized FlowerPower project [bold blue]{name}[/bold blue] at [italic green]{base_dir}[/italic green]\n")

    rich.print("""[yellow]Getting Started:[/yellow]

    📦 It is recommended to use the project manager [bold cyan]`uv`[/bold cyan] to manage your project.

    🔧 Install uv:
        [dim]Run:[/dim] [bold white]pip install uv[/bold white]
        [dim]More options:[/dim] [blue underline]https://docs.astral.sh/uv/getting-started/installation/[/blue underline]

    🚀 Initialize your project:
        [dim]Run the following in your project directory:[/dim]
        [bold white]uv init --app --no-readme --vcs git[/bold white]
    """)

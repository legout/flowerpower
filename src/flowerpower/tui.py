from textual.app import App
from textual.layouts.grid import GridLayout
from textual.reactive import Reactive
from textual.scroll_view import ScrollView
from textual.widgets import Footer, Header, Static

from flowerpower.pipeline import PipelineManager


class PipelineList(Static):
    def __init__(self, pipelines):
        super().__init__()
        self.pipelines = pipelines

    def render(self):
        return "\n".join(f"- {pipeline.name}" for pipeline in self.pipelines)


class FlowerPowerTUI(App):
    pipelines = Reactive([])

    async def on_load(self):
        await self.bind("q", "quit")  # , "Beenden")
        await self.bind("a", "add_pipeline")  # , "Pipeline hinzufügen")
        await self.bind("d", "delete_pipeline")  # , "Pipeline löschen")

    async def on_mount(self):
        self.pipeline_manager = PipelineManager()
        self.refresh_pipelines()

        grid = await self.view.dock_grid(edge="top")

        grid.add_column(fraction=1, name="left", min_size=30)
        grid.add_column(fraction=3, name="right")

        grid.add_row(fraction=1, name="row")

        grid.add_areas(
            area_left="left,row",
            area_right="right,row",
        )

        header = Header()
        footer = Footer()

        self.pipeline_list = PipelineList(self.pipelines)
        self.details_view = ScrollView()

        await self.view.dock(header, edge="top")
        await self.view.dock(footer, edge="bottom")
        grid.place(area_left=self.pipeline_list, area_right=self.details_view)

        await self.view.dock(grid)

    def refresh_pipelines(self):
        self.pipelines = self.pipeline_manager.find_pipelines()

    async def action_add_pipeline(self):
        # Logik zum Hinzufügen einer neuen Pipeline
        pass

    async def action_delete_pipeline(self):
        # Logik zum Löschen einer Pipeline
        pass

    async def on_key(self, event):
        if event.key == "up":
            # Navigiere nach oben in der Pipeline-Liste
            pass
        elif event.key == "down":
            # Navigiere nach unten in der Pipeline-Liste
            pass
        elif event.key == "enter":
            # Zeige Details zur ausgewählten Pipeline an
            pass


if __name__ == "__main__":
    FlowerPowerTUI().run()

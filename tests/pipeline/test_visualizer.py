from unittest.mock import MagicMock, patch

from flowerpower.pipeline.visualizer import PipelineVisualizer


def test_save_dag_defaults_to_project_graphs_directory() -> None:
    project_cfg = MagicMock()
    project_cfg.name = "demo"
    fs = MagicMock()
    dag = MagicMock()

    visualizer = PipelineVisualizer(project_cfg=project_cfg, fs=fs)
    visualizer._get_dag_object = MagicMock(return_value=dag)

    result = visualizer.save_dag(name="example", format="svg")

    fs.makedirs.assert_called_once_with("./graphs", exist_ok=True)
    dag.render.assert_called_once_with(
        "./graphs/example",
        format="svg",
        cleanup=True,
        view=False,
    )
    assert result == "./graphs/example.svg"


def test_save_dag_status_message_omits_none_project_name() -> None:
    project_cfg = MagicMock()
    project_cfg.name = None
    fs = MagicMock()
    dag = MagicMock()

    visualizer = PipelineVisualizer(project_cfg=project_cfg, fs=fs)
    visualizer._get_dag_object = MagicMock(return_value=dag)

    with patch("flowerpower.pipeline.visualizer.print") as mock_print:
        visualizer.save_dag(name="example", format="svg")

    printed_message = mock_print.call_args[0][0]
    assert "None.example" not in printed_message
    assert "example" in printed_message

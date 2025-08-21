from typer.testing import CliRunner

from flowerpower.cli import app  # Corrected import based on file inspection

runner = CliRunner()


def test_hello_world_pipeline_run():
    """
    Tests the `flowerpower pipeline run` command with the hello-world example.
    """
    project_dir = "examples/hello-world"  # Relative to the repository root
    pipeline_name = "hello_world"

    # Ensure the project directory and pipeline file exist to help with debugging if it fails.
    # This is not a test assertion, but a pre-condition check for the test environment.
    import os

    assert os.path.isdir(project_dir), (
        f"Project directory '{project_dir}' not found. Test run from: {os.getcwd()}"
    )
    assert os.path.isfile(
        os.path.join(project_dir, "pipelines", f"{pipeline_name}.py")
    ), (
        f"Pipeline file '{pipeline_name}.py' not found in '{project_dir}/pipelines'. Test run from: {os.getcwd()}"
    )
    assert os.path.isfile(os.path.join(project_dir, "conf", "project.yml")), (
        f"Project config 'project.yml' not found in '{project_dir}/conf'. Test run from: {os.getcwd()}"
    )

    result = runner.invoke(
        app,
        [
            "pipeline",
            "run",
            "--project-dir",
            project_dir,
            pipeline_name,
            # "--outputs", # Optional: Request specific outputs to make stdout more predictable
            # "spend_mean,spend_std_dev"
        ],
        catch_exceptions=False,  # Set to True to debug exceptions from the CLI app itself
    )

    print(f"STDOUT: {result.stdout}")
    print(f"STDERR: {result.stderr}")
    print(f"Exit Code: {result.exit_code}")

    assert result.exit_code == 0, (
        f"CLI command failed with exit code {result.exit_code}. STDERR: {result.stderr}"
    )

    # Hamilton/FlowerPower execution logs can be quite verbose.
    # Instead of "Hello, World!", we should check for:
    # 1. Indication of successful execution or nodes being computed.
    # 2. Absence of obvious error messages in stdout/stderr (stderr check is good via exit_code).

    # A general check for some activity related to the pipeline nodes.
    # The hello_world pipeline has nodes like 'spend_mean', 'avg_x_wk_spend'.
    # The logger output might mention these.
    # Let's check for a positive indication of execution.
    # A common pattern in Hamilton's default tracker is to list requested/computed outputs.
    # If no specific outputs are requested, it might just log general execution flow.
    # A simple check that it's not empty and doesn't contain common error keywords might be a start.
    assert (
        "Executing" in result.stdout
        or "pipeline" in result.stdout.lower()
        or "hamilton" in result.stdout.lower()
    )

    # More specific checks could be added if the output format is consistent:
    # Example: Check if it mentions computing some of the final nodes from hello_world.py
    assert (
        "spend_mean" in result.stdout
        or "avg_x_wk_spend" in result.stdout
        or "spend_per_signup" in result.stdout
    )

    # Ensure no critical error messages are in stdout if exit code was 0 (stderr is already checked by assert on exit_code)
    error_keywords = ["Error", "Exception", "Failed", "Traceback"]
    for keyword in error_keywords:
        assert keyword.lower() not in result.stdout.lower(), (
            f"Found error keyword '{keyword}' in STDOUT despite exit_code 0."
        )

    # No specific files are expected to be created by this particular pipeline for this test.
    # If it were to create files, we'd add checks like:
    # assert os.path.exists(os.path.join(project_dir, "output_file.csv"))
    # with open(os.path.join(project_dir, "output_file.csv"), "r") as f:
    #     content = f.read()
    #     assert "expected content" in content

    # Cleanup (if any files were created)
    # Example: if os.path.exists("output_file.csv"): os.remove("output_file.csv")


def test_hello_world_pipeline_run_with_specific_outputs():
    """
    Tests the `flowerpower pipeline run` command with specific outputs requested.
    """
    project_dir = "examples/hello-world"
    pipeline_name = "hello_world"
    requested_outputs = "spend_mean,spend_std_dev"

    result = runner.invoke(
        app,
        [
            "pipeline",
            "run",
            "--project-dir",
            project_dir,
            pipeline_name,
            "--outputs",
            requested_outputs,
        ],
        catch_exceptions=False,
    )

    print(f"STDOUT (specific outputs): {result.stdout}")
    print(f"STDERR (specific outputs): {result.stderr}")
    print(f"Exit Code (specific outputs): {result.exit_code}")

    assert result.exit_code == 0, f"CLI command failed. STDERR: {result.stderr}"

    # When specific outputs are requested, Hamilton typically logs these.
    assert "spend_mean" in result.stdout
    assert "spend_std_dev" in result.stdout
    assert "avg_x_wk_spend" not in result.stdout  # This was not requested

    error_keywords = ["Error", "Exception", "Failed", "Traceback"]
    for keyword in error_keywords:
        assert keyword.lower() not in result.stdout.lower(), (
            f"Found error keyword '{keyword}' in STDOUT despite exit_code 0."
        )


# Add more tests for other CLI commands or pipelines as needed.

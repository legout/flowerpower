import importlib
import sys

import typer

from ..plugins.mqtt import run_pipeline_on_message as run_pipeline_on_message_
from ..plugins.mqtt import start_listener as start_listener_
from .utils import load_hook, parse_dict_or_list_param

app = typer.Typer(help="MQTT management commands")


@app.command()
def start_listener(
    on_message: str,
    topic: str,
    base_dir: str,
    host: str = "localhost",
    port: int = 1883,
    username: str | None = None,
    password: str | None = None,
):
    """Start an MQTT client to listen to messages on a topic

    The connection to the MQTT broker is established using the provided configuration o a
    MQTT event broker defined in the project configuration file `conf/project.yml`.
    If not configuration is found, you have to provide the connection parameters,
    such as `host`, `port`, `username`, and `password`.

    The `on_message` module should contain a function `on_message` that will be called
    with the message payload as argument.

    Args:
        on_message: Name of the module containing the on_message function
        topic: MQTT topic to listen to
        base_dir: Base directory for the module
        host: MQTT broker host
        port: MQTT broker port
        username: MQTT broker username
        password: MQTT broker password

    Examples:
        $ flowerpower mqtt start_listener --on-message my_module --topic my_topic --base-dir /path/to/module
    """
    sys.path.append(base_dir)
    on_message_module = importlib.import_module(on_message)
    start_listener_(
        on_message=on_message_module.on_message,
        topic=topic,
        base_dir=base_dir,
        host=host,
        port=port,
        username=username,
        password=password,
        background=False,
    )


@app.command()
def run_pipeline_on_message(
    name: str,
    topic: str | None = None,
    executor: str | None = None,
    base_dir: str | None = None,
    inputs: str | None = None,
    final_vars: str | None = None,
    config: str | None = None,
    with_tracker: bool = False,
    with_opentelemetry: bool = False,
    with_progressbar: bool = False,
    storage_options: str | None = None,
    as_job: bool = False,
    host: str | None = None,
    port: int | None = None,
    username: str | None = None,
    password: str | None = None,
    clean_session: bool = True,
    qos: int = 0,
    client_id: str | None = None,
    client_id_suffix: str | None = None,
    config_hook: str | None = None,
    max_retries: int = typer.Option(
        3, help="Maximum number of retry attempts if pipeline execution fails"
    ),
    retry_delay: float = typer.Option(
        1.0, help="Base delay between retries in seconds"
    ),
    jitter_factor: float = typer.Option(
        0.1, help="Random factor (0-1) applied to delay for jitter"
    ),
):
    """Run a pipeline on a message

    This command sets up an MQTT listener that executes a pipeline whenever a message is
    received on the specified topic. The pipeline can be configured to retry on failure
    using exponential backoff with jitter for better resilience.

    Args:
        name: Name of the pipeline
        topic: MQTT topic to listen to
        executor: Name of the executor
        base_dir: Base directory for the pipeline
        inputs: Inputs as JSON or key=value pairs or dict string
        final_vars: Final variables as JSON or list
        config: Config for the hamilton pipeline executor
        with_tracker: Enable tracking with hamilton ui
        with_opentelemetry: Enable OpenTelemetry tracing
        with_progressbar: Enable progress bar
        storage_options: Storage options as JSON, dict string or key=value pairs
        as_job: Run as a job in the scheduler
        host: MQTT broker host
        port: MQTT broker port
        username: MQTT broker username
        password: MQTT broker password
        clean_session: Whether to start a clean session with the broker
        qos: MQTT Quality of Service level (0, 1, or 2)
        client_id: Custom MQTT client identifier
        client_id_suffix: Optional suffix to append to client_id
        config_hook: Function to process incoming messages into pipeline config
        max_retries: Maximum number of retry attempts if pipeline execution fails
        retry_delay: Base delay between retries in seconds
        jitter_factor: Random factor (0-1) applied to delay for jitter

    Examples:
        # Basic usage with a specific topic
        $ flowerpower mqtt run-pipeline-on-message my_pipeline --topic sensors/data

        # Configure retries for resilience
        $ flowerpower mqtt run-pipeline-on-message my_pipeline --topic sensors/data --max-retries 5 --retry-delay 2.0

        # Run as a job with custom MQTT settings
        $ flowerpower mqtt run-pipeline-on-message my_pipeline --topic events/process --as-job --qos 2 --host mqtt.example.com

        # Use a config hook to process messages
        $ flowerpower mqtt run-pipeline-on-message my_pipeline --topic data/incoming --config-hook process_message


    """

    parsed_inputs = parse_dict_or_list_param(inputs, "dict")
    parsed_config = parse_dict_or_list_param(config, "dict")
    parsed_final_vars = parse_dict_or_list_param(final_vars, "list")
    parsed_storage_options = parse_dict_or_list_param(storage_options, "dict")

    config_hook_function = None
    if config_hook:
        config_hook_function = load_hook(name, config_hook, base_dir, storage_options)

    run_pipeline_on_message_(
        name=name,
        topic=topic,
        executor=executor,
        base_dir=base_dir,
        inputs=parsed_inputs,
        final_vars=parsed_final_vars,
        config=parsed_config,
        with_tracker=with_tracker,
        with_opentelemetry=with_opentelemetry,
        with_progressbar=with_progressbar,
        storage_options=parsed_storage_options,
        as_job=as_job,
        host=host,
        port=port,
        username=username,
        password=password,
        clean_session=clean_session,
        qos=qos,
        client_id=client_id,
        client_id_suffix=client_id_suffix,
        config_hook=config_hook_function,
        max_retries=max_retries,
        retry_delay=retry_delay,
        jitter_factor=jitter_factor,
    )

import datetime as dt
import random
import socket
import time
from pathlib import Path
from types import TracebackType
from typing import Any, Callable

import mmh3
from loguru import logger
from munch import Munch
from paho.mqtt.client import CallbackAPIVersion, Client

from ...cfg import ProjectConfig
from ...cfg.pipeline.run import ExecutorConfig, WithAdapterConfig
from ...cfg.project.adapter import AdapterConfig
from ...fs import AbstractFileSystem, BaseStorageOptions, get_filesystem
from ...pipeline.manager import PipelineManager
from ...utils.logging import setup_logging
from .cfg import MqttConfig

setup_logging()


class MqttManager:
    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        host: str | None = "localhost",
        port: int | None = 1883,
        topic: str | None = None,
        first_reconnect_delay: int = 1,
        max_reconnect_count: int = 5,
        reconnect_rate: int = 2,
        max_reconnect_delay: int = 60,
        transport: str = "tcp",
        clean_session: bool = True,
        client_id: str | None = None,
        client_id_suffix: str | None = None,
        **kwargs,
    ):
        if "user" in kwargs:
            username = kwargs["user"]
        if "pw" in kwargs:
            password = kwargs["pw"]

        self.topic = topic

        self._username = username
        self._password = password
        self._host = host
        self._port = port
        self._first_reconnect_delay = first_reconnect_delay
        self._max_reconnect_count = max_reconnect_count
        self._reconnect_rate = reconnect_rate
        self._max_reconnect_delay = max_reconnect_delay
        self._transport = transport

        self._clean_session = clean_session
        self._client_id = client_id
        self._client_id_suffix = client_id_suffix

        self._client = None

    @classmethod
    def from_event_broker(cls, base_dir: str | None = None):
        base_dir = base_dir or str(Path.cwd())

        jq_backend = ProjectConfig.load(base_dir=base_dir).job_queue.backend
        if jq_backend is None:
            raise ValueError(
                "No MQTT event broker configuration found. Recheck the provided `base_dir`.\n"
                "If you are not using a MQTT event broker, initialize the MQTT client using the MQTTManager class.\n"
                "or use the provide a configuration dict to the MQTTManager.from_dict() method."
            )
        if hasattr(jq_backend, "event_broker") is False:
            raise ValueError(
                "No MQTT event broker configuration found. Recheck the provided `base_dir`.\n"
                "If you are not using a MQTT event broker, initialize the MQTT client using the MQTTManager class.\n"
                "or use the provide a configuration dict to the MQTTManager.from_dict() method."
            )
        if jq_backend.event_broker.type != "mqtt":
            raise ValueError(
                "No MQTT event broker configuration found. Recheck the provided `base_dir`.\n"
                "If you are not using a MQTT event broker, initialize the MQTT client using the MQTTManager class.\n"
                "or use the provide a configuration dict to the MQTTManager.from_dict() method."
            )
        else:
            event_broker_cfg = jq_backend.event_broker
            return cls(
                **event_broker_cfg.dict(),
            )

    @classmethod
    def from_config(
        cls,
        cfg: MqttConfig | None = None,
        path: str | None = None,
        fs: AbstractFileSystem | None = None,
        storage_options: dict | BaseStorageOptions = {},
    ):
        if cfg is None:
            if path is None:
                raise ValueError(
                    "No configuration provided. Please provide `config` or `path` to the configuration file."
                )

        if cfg is None:
            import os

            if fs is None:
                fs = get_filesystem(
                    path=os.path.dirname(path), storage_options=storage_options
                )

            cfg = MqttConfig.from_yaml(path=os.path.basename(path), fs=fs)

        return cls(
            **cfg.dict(),
        )

    @classmethod
    def from_dict(cls, cfg: dict):
        return cls(
            **cfg,
        )

    def __enter__(self) -> "MqttManager":
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        # Add any cleanup code here if needed
        self.disconnect()

    @staticmethod
    def _on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            logger.info(f"Connected to MQTT Broker {userdata.host}!")
            logger.info(
                f"Connected as {userdata.client_id} with clean session {userdata.clean_session}"
            )
        else:
            logger.error(f"Failed to connect, return code {rc}")

    @staticmethod
    def _on_disconnect(client, userdata, disconnect_flags, rc, properties=None):
        reconnect_count, reconnect_delay = 0, userdata.first_reconnect_delay

        if userdata.max_reconnect_count == 0:
            logger.info("Disconnected successfully!")
            return

        while reconnect_count < userdata.max_reconnect_count:
            logger.info(f"Reconnecting in {reconnect_delay} seconds...")
            time.sleep(reconnect_delay)

            try:
                client.reconnect()
                logger.info("Reconnected successfully!")
                return
            except Exception as err:
                logger.error(f"{err}. Reconnect failed. Retrying...")

            reconnect_delay *= userdata.reconnect_rate
            reconnect_delay = min(reconnect_delay, userdata.max_reconnect_delay)
            reconnect_count += 1
        logger.info(f"Reconnect failed after {reconnect_count} attempts. Exiting...")

    @staticmethod
    def _on_publish(client, userdata, mid, rc, properties):
        logger.info(f"Published message id: {mid}")

    @staticmethod
    def _on_subscribe(client, userdata, mid, qos, properties):
        if isinstance(qos, list):
            qos_msg = str(qos[0])
        else:
            qos_msg = f"and granted QoS {qos[0]}"
        logger.info(f"Subscribed {qos_msg}")

    def connect(self) -> Client:
        if self._client_id is None and self._clean_session:
            # Random Client ID when clean session is True
            self._client_id = f"flowerpower-client-{random.randint(0, 10000)}"
        elif self._client_id is None and not self._clean_session:
            # Deterministic Client ID when clean session is False
            self._client_id = f"flowerpower-client-{
                mmh3.hash_bytes(
                    str(self._host)
                    + str(self._port)
                    + str(self.topic)
                    + str(socket.gethostname())
                ).hex()
            }"

        if self._client_id_suffix:
            self._client_id = f"{self._client_id}-{self._client_id_suffix}"

        logger.debug(
            f"Client ID: {self._client_id} - Clean session: {self._clean_session}"
        )
        client = Client(
            CallbackAPIVersion.VERSION2,
            client_id=self._client_id,
            transport=self._transport,
            clean_session=self._clean_session,
            userdata=Munch(
                user=self._username,
                pw=self._password,
                host=self._host,
                port=self._port,
                topic=self.topic,
                first_reconnect_delay=self._first_reconnect_delay,
                max_reconnect_count=self._max_reconnect_count,
                reconnect_rate=self._reconnect_rate,
                max_reconnect_delay=self._max_reconnect_delay,
                transport=self._transport,
                client_id=self._client_id,
                clean_session=self._clean_session,
            ),
        )
        if self._password != "" and self._username != "":
            client.username_pw_set(self._username, self._password)

        client.on_connect = self._on_connect  # self._on_connect
        client.on_disconnect = self._on_disconnect  # self._on_disconnect
        client.on_publish = self._on_publish
        client.on_subscribe = self._on_subscribe

        client.connect(self._host, self._port)
        self._client = client
        # topic = topic or topic
        if self.topic:
            self.subscribe()

    def disconnect(self):
        self._max_reconnect_count = 0
        self._client._userdata.max_reconnect_count = 0
        self._client.disconnect()

    def reconnect(self):
        self._client.reconnect()

    def publish(self, topic, payload):
        if self._client is None:
            self.connect()
        # elif self._client.is_connected() is False:
        #    self.reconnect()
        self._client.publish(topic, payload)

    def subscribe(self, topic: str | None = None, qos: int = 2):
        if topic is not None:
            self.topic = topic
        self._client.subscribe(self.topic, qos=qos)

    def unsubscribe(self, topic: str | None = None):
        if topic is not None:
            self.topic = topic
        self._client.unsubscribe(self.topic)

    def register_on_message(self, on_message: Callable):
        self._client.on_message = on_message

    def run_in_background(
        self,
        on_message: Callable,
        topic: str | None = None,
        qos: int = 2,
    ) -> None:
        """
        Run the MQTT client in the background.

        Args:
            on_message: Callback function to run when a message is received
            topic: MQTT topic to listen to

        Returns:
            None
        """
        if self._client is None or not self._client.is_connected():
            self.connect()

        if topic:
            self.subscribe(topic, qos=qos)

        self._client.on_message = on_message
        self._client.loop_start()

    def run_until_break(
        self,
        on_message: Callable,
        topic: str | None = None,
        qos: int = 2,
    ):
        """
        Run the MQTT client until a break signal is received.

        Args:
            on_message: Callback function to run when a message is received
            topic: MQTT topic to listen to

        Returns:
            None
        """
        if self._client is None or not self._client.is_connected():
            self.connect()

        if topic:
            self.subscribe(topic, qos=qos)

        self._client.on_message = on_message
        self._client.loop_forever()

    def start_listener(
        self,
        on_message: Callable,
        topic: str | None = None,
        background: bool = False,
        qos: int = 2,
    ) -> None:
        """
        Start the MQTT listener.

        Args:
            on_message: Callback function to run when a message is received
            topic: MQTT topic to listen to
            background: Run the listener in the background

        Returns:
            None
        """
        if background:
            self.run_in_background(on_message, topic, qos)
        else:
            self.run_until_break(on_message, topic, qos)

    def stop_listener(
        self,
    ) -> None:
        """
        Stop the MQTT listener.

        Returns:
            None
        """
        self._client.loop_stop()
        logger.info("Client stopped.")

    def run_pipeline_on_message(
        self,
        name: str,
        topic: str | None = None,
        inputs: dict | None = None,
        final_vars: list | None = None,
        config: dict | None = None,
        cache: bool | dict = False,
        executor_cfg: str | dict | ExecutorConfig | None = None,
        with_adapter_cfg: dict | WithAdapterConfig | None = None,
        pipeline_adapter_cfg: dict | AdapterConfig | None = None,
        project_adapter_cfg: dict | AdapterConfig | None = None,
        adapter: dict[str, Any] | None = None,
        reload: bool = False,
        log_level: str | None = None,
        result_ttl: float | dt.timedelta = 0,
        run_in: int | str | dt.timedelta | None = None,
        max_retries: int | None = None,
        retry_delay: float | None = None,
        jitter_factor: float | None = None,
        retry_exceptions: tuple | list | None = None,
        as_job: bool = False,
        base_dir: str | None = None,
        storage_options: dict = {},
        fs: AbstractFileSystem | None = None,
        background: bool = False,
        qos: int = 2,
        config_hook: Callable[[bytes, int], dict] | None = None,
        **kwargs,
    ):
        """
        Start a pipeline listener that listens to a topic and processes the message using a pipeline.

        Args:
            name (str): Name of the pipeline
            topic (str | None): MQTT topic to listen to
            inputs (dict | None): Inputs for the pipeline
            final_vars (list | None): Final variables for the pipeline
            config (dict | None): Configuration for the pipeline driver
            cache (bool | dict): Cache for the pipeline
            executor_cfg (str | dict | ExecutorConfig | None): Executor configuration
            with_adapter_cfg (dict | WithAdapterConfig | None): With adapter configuration
            pipeline_adapter_cfg (dict | AdapterConfig | None): Pipeline adapter configuration
            project_adapter_cfg (dict | AdapterConfig | None): Project adapter configuration
            adapter (dict[str, Any] | None): Adapter configuration
            reload (bool): Reload the pipeline
            log_level (str | None): Log level for the pipeline
            result_ttl (float | dt.timedelta): Result expiration time for the pipeline
            run_in (int | str | dt.timedelta | None): Run in time for the pipeline
            max_retries (int | None): Maximum number of retries for the pipeline
            retry_delay (float | None): Delay between retries for the pipeline
            jitter_factor (float | None): Jitter factor for the pipeline
            retry_exceptions (tuple | list | None): Exceptions to retry for the pipeline
            as_job (bool): Run the pipeline as a job
            base_dir (str | None): Base directory for the pipeline
            storage_options (dict): Storage options for the pipeline
            fs (AbstractFileSystem | None): File system for the pipeline
            background (bool): Run the listener in the background
            qos (int): Quality of Service for the MQTT client
            config_hook (Callable[[bytes, int], dict] | None): Hook function to modify the configuration of the pipeline
            **kwargs: Additional keyword arguments

        Returns:
            None

        Raises:
            ValueError: If the config_hook is not callable

        Example:
            ```python
            from flowerpower.plugins.mqtt import MqttManager
            mqtt = MqttManager()
            mqtt.run_pipeline_on_message(
                name="my_pipeline",
                topic="my_topic",
                inputs={"key": "value"},
                config={"param": "value"},
                as_job=True,
            )
            ```
        """

        if inputs is None:
            inputs = {}

        if config is None:
            config = {}

        if config_hook is not None and not callable(config_hook):
            raise ValueError("config_hook must be a callable function")

        def on_message(client, userdata, msg):
            logger.info(f"Received message on topic {topic}")

            inputs["payload"] = msg.payload
            inputs["topic"] = msg.topic

            if config_hook is not None:
                config_ = config_hook(inputs["payload"], inputs["topic"])
                logger.debug(f"Config from hook: {config_}")

                if any([k in config_ for k in config.keys()]):
                    logger.warning("Config from hook overwrites config from pipeline")

                config.update(config_)
                logger.debug(f"Config after update: {config}")

            with PipelineManager(
                storage_options=storage_options, fs=fs, base_dir=base_dir
            ) as pipeline:
                try:
                    if as_job:
                        pipeline.add_job(
                            name=name,
                            inputs=inputs,
                            final_vars=final_vars,
                            config=config,
                            cache=cache,
                            executor_cfg=executor_cfg,
                            with_adapter_cfg=with_adapter_cfg,
                            pipeline_adapter_cfg=pipeline_adapter_cfg,
                            project_adapter_cfg=project_adapter_cfg,
                            adapter=adapter,
                            run_in=run_in,
                            reload=reload,
                            log_level=log_level,
                            result_ttl=result_ttl,
                            max_retries=max_retries,
                            retry_delay=retry_delay,
                            jitter_factor=jitter_factor,
                            retry_exceptions=retry_exceptions,
                            **kwargs,
                        )
                    else:
                        pipeline.run(
                            name=name,
                            inputs=inputs,
                            final_vars=final_vars,
                            config=config,
                            cache=cache,
                            executor_cfg=executor_cfg,
                            with_adapter_cfg=with_adapter_cfg,
                            pipeline_adapter_cfg=pipeline_adapter_cfg,
                            project_adapter_cfg=project_adapter_cfg,
                            adapter=adapter,
                            reload=reload,
                            log_level=log_level,
                            result_ttl=result_ttl,
                            run_in=run_in,
                            max_retries=max_retries,
                            retry_delay=retry_delay,
                            jitter_factor=jitter_factor,
                            retry_exceptions=retry_exceptions,
                            **kwargs,
                        )
                    logger.success("Message processed successfully")
                    return
                except Exception as e:
                    _ = e
                    logger.exception(e)

                logger.warning("Message processing failed")

        self.start_listener(
            on_message=on_message, topic=topic, background=background, qos=qos
        )


def start_listener(
    on_message: Callable,
    topic: str | None = None,
    background: bool = False,
    mqtt_cfg: dict | MqttConfig = {},
    base_dir: str | None = None,
    username: str | None = None,
    password: str | None = None,
    host: str | None = None,
    port: int | None = None,
    clean_session: bool = True,
    qos: int = 2,
    client_id: str | None = None,
    client_id_suffix: str | None = None,
    config_hook: Callable[[bytes, int], dict] | None = None,
    **kwargs,
) -> None:
    """
    Start the MQTT listener.

    The connection to the MQTT broker is established using the provided configuration of a
    MQTT event broker defined in the project configuration file `conf/project.toml`.
    If no configuration is found, you have to provide either the argument `mqtt_cfg`, dict with the
    connection parameters or the arguments `username`, `password`, `host`, and `port`.

    Args:
        on_message (Callable): Callback function to run when a message is received
        topic (str | None): MQTT topic to listen to
        background (bool): Run the listener in the background
        mqtt_cfg (dict | MqttConfig): MQTT client configuration. Use either this or arguments
            username, password, host, and port.
        base_dir (str | None): Base directory for the module
        username (str | None): Username for the MQTT client
        password (str | None): Password for the MQTT client
        host (str | None): Host for the MQTT client
        port (int | None): Port for the MQTT client
        clean_session (bool): Clean session flag for the MQTT client
        qos (int): Quality of Service for the MQTT client
        client_id (str | None): Client ID for the MQTT client
        client_id_suffix (str | None): Client ID suffix for the MQTT client
        config_hook (Callable[[bytes, int], dict] | None): Hook function to modify the configuration of the pipeline
        **kwargs: Additional keyword arguments

    Returns:
        None

    Raises:
        ValueError: If the config_hook is not callable
        ValueError: If no client configuration is found

    Example:
        ```python
        from flowerpower.plugins.mqtt import start_listener

        start_listener(
            on_message=my_on_message_function,
            topic="my_topic",
            background=True,
            mqtt_cfg={"host": "localhost", "port": 1883},
        )
        ```
    """
    try:
        client = MqttManager.from_event_broker(base_dir)
    except ValueError:
        if mqtt_cfg:
            if isinstance(mqtt_cfg, MqttConfig):
                client = MqttManager.from_config(mqtt_cfg)
            elif isinstance(mqtt_cfg, dict):
                client = MqttManager.from_dict(mqtt_cfg)
        elif host and port:
            client = MqttManager(
                username=username,
                password=password,
                host=host,
                port=port,
                clean_session=clean_session,
                client_id=client_id,
                client_id_suffix=client_id_suffix,
                config_hook=config_hook,
                **kwargs,
            )
        else:
            raise ValueError(
                "No client configuration found. Please provide a client configuration "
                "or a FlowerPower project base directory, in which a event broker is "
                "configured in the `config/project.yml` file."
            )

    client.start_listener(
        on_message=on_message, topic=topic, background=background, qos=qos
    )


def run_pipeline_on_message(
    name: str,
    topic: str | None = None,
    inputs: dict | None = None,
    final_vars: list | None = None,
    config: dict | None = None,
    cache: bool | dict = False,
    executor_cfg: str | dict | ExecutorConfig | None = None,
    with_adapter_cfg: dict | WithAdapterConfig | None = None,
    pipeline_adapter_cfg: dict | AdapterConfig | None = None,
    project_adapter_cfg: dict | AdapterConfig | None = None,
    adapter: dict[str, Any] | None = None,
    reload: bool = False,
    log_level: str | None = None,
    result_ttl: float | dt.timedelta = 0,
    run_in: int | str | dt.timedelta | None = None,
    max_retries: int | None = None,
    retry_delay: float | None = None,
    jitter_factor: float | None = None,
    retry_exceptions: tuple | list | None = None,
    as_job: bool = False,
    base_dir: str | None = None,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
    background: bool = False,
    mqtt_cfg: dict | MqttConfig = {},
    host: str | None = None,
    port: int | None = None,
    username: str | None = None,
    password: str | None = None,
    clean_session: bool = True,
    qos: int = 2,
    client_id: str | None = None,
    client_id_suffix: str | None = None,
    config_hook: Callable[[bytes, int], dict] | None = None,
    **kwargs,
):
    """
    Start a pipeline listener that listens to a topic and processes the message using a pipeline.

    Args:
        name (str): Name of the pipeline
        topic (str | None): MQTT topic to listen to
        inputs (dict | None): Inputs for the pipeline
        final_vars (list | None): Final variables for the pipeline
        config (dict | None): Configuration for the pipeline driver
        cache (bool | dict): Cache for the pipeline
        executor_cfg (str | dict | ExecutorConfig | None): Executor configuration
        with_adapter_cfg (dict | WithAdapterConfig | None): With adapter configuration
        pipeline_adapter_cfg (dict | AdapterConfig | None): Pipeline adapter configuration
        project_adapter_cfg (dict | AdapterConfig | None): Project adapter configuration
        adapter (dict[str, Any] | None): Adapter configuration
        reload (bool): Reload the pipeline
        log_level (str | None): Log level for the pipeline
        result_ttl (float | dt.timedelta): Result expiration time for the pipeline
        run_in (int | str | dt.timedelta | None): Run in time for the pipeline
        max_retries (int | None): Maximum number of retries for the pipeline
        retry_delay (float | None): Delay between retries for the pipeline
        jitter_factor (float | None): Jitter factor for the pipeline
        retry_exceptions (tuple | list | None): Exceptions to retry for the pipeline
        as_job (bool): Run the pipeline as a job
        base_dir (str | None): Base directory for the pipeline
        storage_options (dict): Storage options for the pipeline
        fs (AbstractFileSystem | None): File system for the pipeline
        background (bool): Run the listener in the background
        mqtt_cfg (dict | MqttConfig): MQTT client configuration. Use either this or arguments
            username, password, host, and port.
        host (str | None): Host for the MQTT client
        port (int | None): Port for the MQTT client
        username (str | None): Username for the MQTT client
        password (str | None): Password for the MQTT client
        clean_session (bool): Clean session flag for the MQTT client
        qos (int): Quality of Service for the MQTT client
        client_id (str | None): Client ID for the MQTT client
        client_id_suffix (str | None): Client ID suffix for the MQTT client
        config_hook (Callable[[bytes, int], dict] | None): Hook function to modify the configuration of the pipeline
        **kwargs: Additional keyword arguments

    Returns:
        None

    Raises:
        ValueError: If the config_hook is not callable
        ValueError: If no client configuration is found

    Example:
        ```python
        from flowerpower.plugins.mqtt import run_pipeline_on_message

        run_pipeline_on_message(
            name="my_pipeline",
            topic="my_topic",
            inputs={"key": "value"},
            config={"param": "value"},
            as_job=True,
        )
        ```
    """
    try:
        client = MqttManager.from_event_broker(base_dir)
    except ValueError:
        if mqtt_cfg:
            if isinstance(mqtt_cfg, MqttConfig):
                client = MqttManager.from_config(mqtt_cfg)
            elif isinstance(mqtt_cfg, dict):
                client = MqttManager.from_dict(mqtt_cfg)
        elif host and port:
            client = MqttManager(
                username=username,
                password=password,
                host=host,
                port=port,
                clean_session=clean_session,
                client_id=client_id,
                client_id_suffix=client_id_suffix,
                config_hook=config_hook,
                **kwargs,
            )
        else:
            raise ValueError(
                "No client configuration found. Please provide a client configuration "
                "or a FlowerPower project base directory, in which a event broker is "
                "configured in the `config/project.yml` file."
            )

    if client._client_id is None and client_id is not None:
        client._client_id = client_id

    if client._client_id_suffix is None and client_id_suffix is not None:
        client._client_id_suffix = client_id_suffix

    """
    cli_clean_session | config_clean_session | result
    TRUE		        TRUE		           TRUE
    FALSE		        FALSE                  FALSE
    FALSE               TRUE                   FALSE
    TRUE                FALSE                  FALSE

    Clean session should only use default value if neither cli nor config source says otherwise
    """
    client._clean_session = client._clean_session and clean_session

    if client.topic is None and topic is not None:
        client.topic = topic

    client.run_pipeline_on_message(
        name=name,
        topic=topic,
        inputs=inputs,
        final_vars=final_vars,
        config=config,
        cache=cache,
        executor_cfg=executor_cfg,
        with_adapter_cfg=with_adapter_cfg,
        pipeline_adapter_cfg=pipeline_adapter_cfg,
        project_adapter_cfg=project_adapter_cfg,
        adapter=adapter,
        reload=reload,
        log_level=log_level,
        result_ttl=result_ttl,
        run_in=run_in,
        max_retries=max_retries,
        retry_delay=retry_delay,
        jitter_factor=jitter_factor,
        retry_exceptions=retry_exceptions,
        as_job=as_job,
        base_dir=base_dir,
        storage_options=storage_options,
        fs=fs,
        background=background,
        qos=qos,
        client_id=client_id,
        client_id_suffix=client_id_suffix,
        config_hook=config_hook,
        **kwargs,
    )

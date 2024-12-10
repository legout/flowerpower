import datetime as dt
import random
import time
from types import TracebackType
from typing import Callable

from fsspec import AbstractFileSystem
from loguru import logger
from munch import Munch
from paho.mqtt.client import CallbackAPIVersion, Client

from .cfg import Config
from .pipeline import Pipeline


class MQTTClient:
    def __init__(
        self,
        user: str | None = None,
        pw: str | None = None,
        host: str | None = "localhost",
        port: int | None = 1883,
        topic: str | None = None,
        first_reconnect_delay: int = 1,
        max_reconnect_count: int = 5,
        reconnect_rate: int = 2,
        max_reconnect_delay: int = 60,
        transport: str = "tcp",
    ):
        self.topic = topic

        self._user = user
        self._pw = pw
        self._host = host
        self._port = port
        self._first_reconnect_delay = first_reconnect_delay
        self._max_reconnect_count = max_reconnect_count
        self._reconnect_rate = reconnect_rate
        self._max_reconnect_delay = max_reconnect_delay
        self._transport = transport

        self._client = None

    def __enter__(self) -> "MQTTClient":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        # Add any cleanup code here if needed
        pass

    def connect(self) -> Client:
        def on_connect(client, userdata, flags, rc, properties):
            if rc == 0:
                logger.info(f"Connected to MQTT Broker {userdata.host}!")
            else:
                logger.error(f"Failed to connect, return code {rc}")

        def on_disconnect(client, userdata, disconnect_flags, rc, properties=None):
            logger.info(f"Disconnected with result code: {rc}")
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
            logger.info(
                f"Reconnect failed after {reconnect_count} attempts. Exiting..."
            )

        client = Client(
            CallbackAPIVersion.VERSION2,
            client_id=f"flowerpower-{random.randint(0, 10000)}",
            transport=self._transport,
            userdata=Munch(
                user=self._user,
                pw=self._pw,
                host=self._host,
                port=self._port,
                topic=self.topic,
                first_reconnect_delay=self._first_reconnect_delay,
                max_reconnect_count=self._max_reconnect_count,
                reconnect_rate=self._reconnect_rate,
                max_reconnect_delay=self._max_reconnect_delay,
                transport=self._transport,
            ),
        )
        if self._pw != "" and self._user != "":
            client.username_pw_set(self._user, self._pw)

        client.on_connect = on_connect
        client.on_disconnect = on_disconnect

        client.connect(self._host, self._port)

        # topic = topic or topic
        if self.topic:
            self.subscribe()

        self._client = client

    def disconnect(self):
        self._max_reconnect_count = 0
        self._client._userdata.max_reconnect_count = 0
        self._client.disconnect()

    def reconnect(self):
        self._client.reconnect()

    def publish(self, topic, payload):
        if self._client is None:
            self.connect()
        elif self._client.is_connected() is False:
            self.reconnect()
        self._client.publish(topic, payload)

    def subscribe(self, topic: str | None = None):
        if topic is not None:
            self.topic = topic
        self._client.subscribe(self.topic)

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
            self.subscribe(topic)

        self._client.on_message = on_message
        self._client.loop_start()

    def run_until_break(
        self,
        on_message: Callable,
        topic: str | None = None,
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
            self.subscribe(topic)

        self._client.on_message = on_message
        self._client.loop_forever()

    def start_listener(
        self, on_message: Callable, topic: str | None = None, background: bool = False
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
            self.run_in_background(on_message, topic)
        else:
            self.run_until_break(on_message, topic)

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

    @classmethod
    def from_event_broker(cls, base_dir: str):
        event_broker_cfg = Config.load(base_dir=base_dir).project.worker.event_broker
        if event_broker_cfg is not None:
            if event_broker_cfg.get("type", None) == "mqtt":
                return cls(
                    user=event_broker_cfg.get("user", None),
                    pw=event_broker_cfg.get("pw", None),
                    host=event_broker_cfg.get("host", "localhost"),
                    port=event_broker_cfg.get("port", 1883),
                    transport=event_broker_cfg.get("transport", "tcp"),
                )
            raise ValueError("No event broker configuration found in config file.")
        else:
            raise ValueError("No event broker configuration found in config file.")

    @classmethod
    def from_config(cls, cfg: dict):
        return cls(
            user=cfg.get("user", None),
            pw=cfg.get("pw", None),
            host=cfg.get("host", "localhost"),
            port=cfg.get("port", 1883),
            transport=cfg.get("transport", "tcp"),
        )

    def start_pipeline_listener(
        self,
        name: str,
        topic: str | None = None,
        inputs: dict | None = None,
        final_vars: list | None = None,
        config: dict | None = None,
        executor: str | None = None,
        with_tracker: bool | None = None,
        with_opentelemetry: bool | None = None,
        reload: bool = False,
        result_expiration_time: float | dt.timedelta = 0,
        as_job: bool = False,
        base_dir: str | None = None,
        storage_options: dict = {},
        fs: AbstractFileSystem | None = None,
        background: bool = False,
        **kwargs,
    ):
        """
        Start a pipeline listener that listens to a topic and processes the message using a pipeline.

        Args:
            name: Name of the pipeline
            topic: MQTT topic to listen to
            inputs: Inputs for the pipeline
            final_vars: Final variables for the pipeline
            config: Configuration for the pipeline driver
            executor: Executor to use for the pipeline
            with_tracker: Use tracker for the pipeline
            with_opentelemetry: Use OpenTelemetry for the pipeline
            reload: Reload the pipeline
            result_expiration_time: Result expiration time for the pipeline
            as_job: Run the pipeline as a job
            base_dir: Base directory for the pipeline
            storage_options: Storage options for the pipeline
            fs: File system for the pipeline
            background: Run the listener in the background
            **kwargs: Additional keyword arguments

        Returns:
            MQTTClient: MQTT client
        """

        def on_message(client, userdata, msg):
            logger.info("Message arrived")

            inputs["payload"] = msg.payload

            with Pipeline(
                name=name, storage_options=storage_options, fs=fs
            ) as pipeline:
                try:
                    if as_job:
                        pipeline.add_job(
                            inputs=inputs,
                            final_vars=final_vars,
                            executor=executor,
                            config=config,
                            with_tracker=with_tracker,
                            with_opentelemetry=with_opentelemetry,
                            reload=reload,
                            result_expiration_time=result_expiration_time,
                            **kwargs,
                        )
                    else:
                        pipeline.run(
                            inputs=inputs,
                            final_vars=final_vars,
                            executor=executor,
                            config=config,
                            with_tracker=with_tracker,
                            with_opentelemetry=with_opentelemetry,
                            reload=reload,
                            result_expiration_time=result_expiration_time,
                            **kwargs,
                        )
                    logger.success("Message processed successfully")
                    return
                except Exception as e:
                    _ = e
                    logger.exception(e)

                logger.warning("processing failed")

        self.start_listener(on_message=on_message, topic=topic, background=background)


def start_listener(
    on_message: Callable,
    topic: str | None = None,
    background: bool = False,
    client_config: dict = {},
    base_dir: str | None = None,
) -> None:
    """
    Start the MQTT listener.

    Args:
        client: MQTT client
        on_message: Callback function to run when a message is received
        topic: MQTT topic to listen to
        background: Run the listener in the background

    Returns:
        None
    """
    if client_config:
        client = MQTTClient.from_config(client_config)
    elif base_dir:
        client = MQTTClient.from_event_broker(base_dir)
    else:
        raise ValueError(
            "No client configuration found. Please provide a client configuration "
            "or a FlowerPower project base directory, in which a event broker is "
            "configured in the `config/project.yml` file."
        )

    client.start_listener(on_message=on_message, topic=topic, background=background)


def start_pipeline_listener(
    name: str,
    topic: str | None = None,
    inputs: dict | None = None,
    final_vars: list | None = None,
    config: dict | None = None,
    executor: str | None = None,
    with_tracker: bool | None = None,
    with_opentelemetry: bool | None = None,
    reload: bool = False,
    result_expiration_time: float | dt.timedelta = 0,
    as_job: bool = False,
    base_dir: str | None = None,
    storage_options: dict = {},
    fs: AbstractFileSystem | None = None,
    background: bool = False,
    **kwargs,
):
    """
    Start a pipeline listener that listens to a topic and processes the message using a pipeline.

    Args:
        name: Name of the pipeline
        topic: MQTT topic to listen to
        inputs: Inputs for the pipeline
        final_vars: Final variables for the pipeline
        config: Configuration for the pipeline driver
        executor: Executor to use for the pipeline
        with_tracker: Use tracker for the pipeline
        with_opentelemetry: Use OpenTelemetry for the pipeline
        reload: Reload the pipeline
        result_expiration_time: Result expiration time for the pipeline
        as_job: Run the pipeline as a job
        base_dir: Base directory for the pipeline
        storage_options: Storage options for the pipeline
        fs: File system for the pipeline
        background: Run the listener in the background
        **kwargs: Additional keyword arguments
    """
    client = MQTTClient.from_event_broker(base_dir=base_dir)
    client.start_pipeline_listener(
        name=name,
        topic=topic,
        inputs=inputs,
        final_vars=final_vars,
        config=config,
        executor=executor,
        with_tracker=with_tracker,
        with_opentelemetry=with_opentelemetry,
        reload=reload,
        result_expiration_time=result_expiration_time,
        as_job=as_job,
        base_dir=base_dir,
        storage_options=storage_options,
        fs=fs,
        background=background,
        **kwargs,
    )

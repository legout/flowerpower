from ...cfg.base import BaseConfig


class MqttConfig(BaseConfig):
    username: str | None = None
    password: str | None = None
    host: str | None = "localhost"
    port: int | None = 1883
    topic: str | None = None
    first_reconnect_delay: int = 1
    max_reconnect_count: int = 5
    reconnect_rate: int = 2
    max_reconnect_delay: int = 60
    transport: str = "tcp"
    clean_session: bool = True
    client_id: str | None = None
    client_id_suffix: str | None = None

import typer

from ..cli.utils import parse_dict_or_list_param
from ..mqtt import MQTTClient

app = typer.Typer(help="MQTT management commands")


@app.command()
def start_broker(
    host: str = "localhost",
    port: int = 1883,
    username: str = None,
    password: str = None,
    log_level: str = "INFO",
):
    """Start an MQTT broker."""
    MQTTClient.start_broker(host, port, username, password, log_level)

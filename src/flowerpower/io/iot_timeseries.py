from mindsphere_tools.iot_timeseries import Client
from ..helpers import get_app_credentials


def iot_client() -> Client:
    app_cred = get_app_credentials()
    return Client(appCredentials=app_cred)

import os

from dotenv import load_dotenv
from mindsphere_tools.loginmanager import (
    App,
    AppCredentials,
    AwsCredentialsManager,
    TechnicalUserCredentials,
)

load_dotenv()


def get_app_credentials() -> AppCredentials:
    if os.getenv("INHUB_USER") is None:
        raise ValueError(
            "Please set the environment variables for the InHub app credentials."
        )
    return AppCredentials(
        user=os.getenv("INHUB_USER"),
        pw=os.getenv("INHUB_PW"),
        hostTenant=os.getenv("INHUB_HOST_TENANT"),
        userTenant=os.getenv("INHUB_USER_TENANT"),
        app=App(
            appName=os.getenv("INHUB_APP_NAME"),
            appVersion=os.getenv("INHUB_APP_VERSION"),
        ),
    )


def get_technical_user_credentials() -> TechnicalUserCredentials:
    if os.getenv("IDL_CLIENT_ID") is None:
        raise ValueError(
            "Please set the environment variables for the InHub technical user credentials."
        )
    return TechnicalUserCredentials(
        client_id=os.getenv("IDL_CLIENT_ID"),
        client_secret=os.getenv("IDL_CLIENT_SECRET"),
    )


def set_idl_credentials() -> None:
    tu = get_technical_user_credentials()
    aws = AwsCredentialsManager(technicalUserCredentials=tu)
    aws.set_credentials(write=True, overwrite=True)

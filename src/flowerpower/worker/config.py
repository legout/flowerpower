import msgspec
from typing import Optional, Dict
import yaml
import urllib.parse
from .utils import build_url
from ..io.fs.base import AbstractFileSystem

class BaseConfig(msgspec.Struct, kw_only=False):
    @classmethod
    def from_yaml(cls, path: str, fs:AbstractFileSystem) -> "BaseConfig":
        """
        Load configuration from a YAML file and create an instance of the class.

        Args:
            path (str): Path to the YAML file.

        Returns:
            BaseConfig: An instance of the class with the loaded configuration. 
        """
        with fs.open(path, "r") as f:
            return msgspec.yaml.decode(f, type=cls, strict=False)
    
    @classmethod
    def from_dict(cls, config_dict: Dict) -> "BaseConfig":
        """
        Create an instance of the class from a dictionary.

        Args:
            config_dict (Dict): Dictionary containing configuration values.

        Returns:
            BaseConfig: An instance of the class with the provided configuration.
        """
        return cls(**config_dict)
    



class BackendConfig(BaseConfig):
    type: str
    url: str | None = None
    host: str | None = None
    port: int | None = None
    username: str | None = None
    password: str | None = None
    database: str | None = None
    ssl: bool = False
    ca_file: str | None = None
    cert_file: str | None = None
    key_file: str | None = None
    verify_ssl: bool = True

    def __post__init__(self):
        # Perform any necessary post-initialization here
        if not self.url:
            self.url = build_url(
                type=self.type,
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                database=self.database,
                ssl=self.ssl,
                ca_file=self.ca_file,
                cert_file=self.cert_file,
                key_file=self.key_file,
                verify_ssl=self.verify_ssl
            )
        else:
            # If URL is provided, parse it to extract components
            parsed_url = urllib.parse.urlparse(self.url)
            self.type = parsed_url.scheme
            self.host = parsed_url.hostname
            self.port = parsed_url.port
            self.username = parsed_url.username
            self.password = parsed_url.password
            self.database = parsed_url.path.lstrip('/')

class TaskQueueConfig(BaseConfig):
    type: str
    backend: BackendConfig | dict[str, BackendConfig] | None = None


class RQConfig(TaskQueueConfig):
    type: str = "rq"
    default_queue: str = "default"
    default_timeout: int = 180


class HueyConfig(TaskQueueConfig):
    huey_name: str
    type: str = "huey"
    immediate: bool = False

class APSchedulerConfig(TaskQueueConfig):
    type: str = "apscheduler"
    timezone: str = "UTC"
    jobstores: Optional[Dict] = None
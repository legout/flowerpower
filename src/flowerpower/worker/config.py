import msgspec
from typing import Optional, Dict
import yaml
import urllib.parse
from .utils import build_url

class TaskQueueConfig(msgspec.Struct, kw_only=True):
    type: str
    url: str | None = None
    host: str |None = None
    port: int | None = None
    username: str | None = None
    password: str | None = None
    database: str | None = None
    ssl: bool = False
    ca_file: str | None = None
    cert_file: str | None = None
    key_file: str | None = None
    verify_ssl: bool = True

    @classmethod
    def from_yaml(cls, path: str) -> "TaskQueueConfig":
        with open(path, "r") as f:
            config_dict = yaml.safe_load(f)
        return cls.from_dict(config_dict)

    @classmethod
    def from_dict(cls, config_dict: Dict) -> "TaskQueueConfig":
        return cls(**config_dict)
    
    def post_init(self):
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
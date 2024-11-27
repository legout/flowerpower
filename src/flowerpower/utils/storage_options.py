import configparser
import os

import yaml
from fsspec import AbstractFileSystem, filesystem
from pydantic import BaseModel


class BaseStorageOptions(BaseModel):
    protocol: str

    def to_dict(self) -> dict:
        return {k: v for k, v in self.model_dump().items() if v is not None}

    @classmethod
    def from_yaml(
        cls, path: str, fs: AbstractFileSystem = None
    ) -> "BaseStorageOptions":
        with fs.open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def to_yaml(self, path: str, fs: AbstractFileSystem = None):
        if fs is None:
            fs = filesystem("file")
        data = self.to_dict()
        with fs.open(path, "w") as f:
            yaml.safe_dump(data, f)

    def to_filesystem(self) -> AbstractFileSystem:
        return filesystem(**self.to_dict())

    def update(self, **kwargs):
        self = self.model_copy(update=kwargs)


class AzureStorageOptions(BaseStorageOptions):
    pass


class GcsStorageOptions(BaseStorageOptions):
    pass


class AwsStorageOptions(BaseStorageOptions):
    protocol: str = "s3"
    access_key_id: str | None = None
    secret_access_key: str | None = None
    session_token: str | None = None
    endpoint_url: str | None = None
    region: str | None = None
    allow_invalid_certificates: bool | None = None
    allow_http: bool | None = None

    @classmethod
    def from_aws_credentials(
        cls,
        profile: str,
        allow_invalid_certificates: bool = False,
        allow_http: bool = False,
    ) -> "AwsStorageOptions":
        cp = configparser.ConfigParser()
        cp.read(os.path.expanduser("~/.aws/credentials"))
        cp.read(os.path.expanduser("~/.aws/config"))
        if profile not in cp:
            raise ValueError(f"Profile '{profile}' not found in AWS credentials file")

        return cls(
            protocol="s3",
            access_key_id=cp[profile].get("aws_access_key_id", None),
            secret_access_key=cp[profile].get("aws_secret_access_key", None),
            session_token=cp[profile].get("aws_session_token", None),
            endpoint_url=cp[profile].get("aws_endpoint_url", None)
            or cp[profile].get("endpoint_url", None)
            or cp[profile].get("aws_endpoint", None)
            or cp[profile].get("endpoint", None),
            region=(
                cp[profile].get("region", None)
                or cp[f"profile {profile}"].get("region", None)
                if f"profile {profile}" in cp
                else None
            ),
            allow_invalid_certificates=allow_invalid_certificates,
            allow_http=allow_http,
        )

    @classmethod
    def from_env(cls) -> "AwsStorageOptions":
        return cls(
            access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            session_token=os.getenv("AWS_SESSION_TOKEN"),
            endpoint_url=os.getenv("AWS_ENDPOINT_URL"),
            region=os.getenv("AWS_DEFAULT_REGION"),
            allow_invalid_certificates="true"
            == (os.getenv("ALLOW_INVALID_CERTIFICATES", "False").lower()),
            allow_http="true" == (os.getenv("AWS_ALLOW_HTTP", "False").lower()),
        )

    def to_fsspec_kwargs(self) -> dict:
        fsspec_kwargs = {
            "key": self.access_key_id,
            "secret": self.secret_access_key,
            "token": self.session_token,
            "endpoint_url": self.endpoint_url,
            "client_kwargs": {
                "region_name": self.region,
                "verify": (
                    not self.allow_invalid_certificates
                    if self.allow_invalid_certificates is not None
                    else None
                ),
                "use_ssl": not self.allow_http if self.allow_http is not None else None,
            },
        }
        return {k: v for k, v in fsspec_kwargs.items() if v is not None}

    def to_object_store_kwargs(self, conditional_put="") -> dict:
        object_store_kwargs = {
            k: str(v)
            for k, v in self.to_dict().items()
            if v is not None and k != "protocol"
        }
        if len(conditional_put):
            object_store_kwargs["conditional_put"] = conditional_put
        return object_store_kwargs

    def to_env(self) -> None:
        env = {
            "AWS_ACCESS_KEY_ID": self.access_key_id,
            "AWS_SECRET_ACCESS_KEY": self.secret_access_key,
            "AWS_SESSION_TOKEN": self.session_token,
            "AWS_ENDPOINT_URL": self.endpoint_url,
            "AWS_DEFAULT_REGION": self.region,
            "ALLOW_INVALID_CERTIFICATES": str(self.allow_invalid_certificates),
            "AWS_ALLOW_HTTP": str(self.allow_http),
        }
        env = {k: v for k, v in env.items() if v is not None}
        os.environ.update(env)

    def to_filesystem(self):
        return filesystem(self.protocol, **self.to_fsspec_kwargs())


class GitHubStorageOptions(BaseStorageOptions):
    protocol: str = "github"
    org: str | None = None
    repo: str | None = None
    sha: str | None = None

    @classmethod
    def from_env(cls) -> "GitHubStorageOptions":
        return cls(
            protocol="github",
            org=os.getenv("GITHUB_ORG"),
            repo=os.getenv("GITHUB_REPO"),
            sha=os.getenv("GITHUB_SHA"),
        )

    def to_env(self) -> None:
        os.environ.update(
            {"GITHUB_ORG": self.org, "GITHUB_REPO": self.repo, "GITHUB_SHA": self.sha}
        )


class GitLabStorageOptions(BaseStorageOptions):
    protocol: str = "gitlab"
    base_url: str = "https://gitlab.com"
    access_token: str | None = None
    project_id: str | int | None = None
    project_name: str | None = None

    @classmethod
    def from_env(cls) -> "GitLabStorageOptions":
        return cls(
            protocol="gitlab",
            base_url=os.getenv("GITLAB_BASE_URL"),
            access_token=os.getenv("GITLAB_ACCESS_TOKEN"),
            project_id=os.getenv("GITLAB_PROJECT_ID"),
            project_name=os.getenv("GITLAB_PROJECT_NAME"),
        )

    def model_post_init(self, __context):
        if self.project_id is None and self.project_name is None:
            raise ValueError("Either 'project_id' or 'project_name' must be provided")


# class StorageOptions(BaseModel):
#     aws: AwsStorageOptions | None = None
#     azure: AzureStorageOptions | None = None
#     gcs: GcsStorageOptions | None = None
#     github: GitHubStorageOptions | None = None
#     gitlab: GitLabStorageOptions | None = None

#     @classmethod
#     def from_yaml(cls, path: str, fs: AbstractFileSystem = None) -> "StorageOptions":
#         with fs.open(path, "r") as f:
#             data = yaml.safe_load(f)
#         return cls(**data)

#     @classmethod
#     def from_env(cls) -> "StorageOptions":
#         return cls(
#             aws=AwsStorageOptions.from_env(),
#             github=GitHubStorageOptions.from_env(),
#             gitlab=GitLabStorageOptions.from_env(),
#         )


def get_storage_options(
    protocol: str, **storage_options
) -> (
    AwsStorageOptions
    | AzureStorageOptions
    | GcsStorageOptions
    | GitHubStorageOptions
    | GitLabStorageOptions
):
    if protocol == "s3":
        return AwsStorageOptions(**storage_options)
    elif protocol == "az" or protocol == "abfs" or protocol == "adl":
        return AzureStorageOptions(**storage_options)
    elif protocol == "gs" or protocol == "gcs":
        return GcsStorageOptions(**storage_options)
    elif protocol == "github":
        return GitHubStorageOptions(**storage_options)
    elif protocol == "gitlab":
        return GitLabStorageOptions(**storage_options)
    else:
        raise ValueError(f"Unsupported protocol: {protocol}")

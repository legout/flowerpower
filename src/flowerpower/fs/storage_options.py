import configparser
import os
from typing import Any, TypeVar, Union

import msgspec
import yaml
from fsspec import AbstractFileSystem, filesystem
from fsspec.utils import infer_storage_options


class BaseStorageOptions(msgspec.Struct):
    """Base class for filesystem storage configuration options.

    Provides common functionality for all storage option classes including:
    - YAML serialization/deserialization
    - Dictionary conversion
    - Filesystem instance creation
    - Configuration updates

    Attributes:
        protocol (str): Storage protocol identifier (e.g., "s3", "gs", "file")

    Example:
        >>> # Create and save options
        >>> options = BaseStorageOptions(protocol="s3")
        >>> options.to_yaml("config.yml")
        >>>
        >>> # Load from YAML
        >>> loaded = BaseStorageOptions.from_yaml("config.yml")
        >>> print(loaded.protocol)
        's3'
    """

    protocol: str

    def to_dict(self, with_protocol: bool = False) -> dict:
        """Convert storage options to dictionary.

        Args:
            with_protocol: Whether to include protocol in output dictionary

        Returns:
            dict: Dictionary of storage options with non-None values

        Example:
            >>> options = BaseStorageOptions(protocol="s3")
            >>> print(options.to_dict())
            {}
            >>> print(options.to_dict(with_protocol=True))
            {'protocol': 's3'}
        """
        data = msgspec.structs.asdict(self)
        result = {}
        for key, value in data.items():
            if value is None:
                continue

            if key == "protocol":
                if with_protocol:
                    result[key] = value
            else:
                result[key] = value
        return result

    @classmethod
    def from_yaml(
        cls, path: str, fs: AbstractFileSystem = None
    ) -> "BaseStorageOptions":
        """Load storage options from YAML file.

        Args:
            path: Path to YAML configuration file
            fs: Filesystem to use for reading file

        Returns:
            BaseStorageOptions: Loaded storage options instance

        Example:
            >>> # Load from local file
            >>> options = BaseStorageOptions.from_yaml("config.yml")
            >>> print(options.protocol)
            's3'
        """
        if fs is None:
            fs = filesystem("file")
        with fs.open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def to_yaml(self, path: str, fs: AbstractFileSystem = None) -> None:
        """Save storage options to YAML file.

        Args:
            path: Path where to save configuration
            fs: Filesystem to use for writing

        Example:
            >>> options = BaseStorageOptions(protocol="s3")
            >>> options.to_yaml("config.yml")
        """
        if fs is None:
            fs = filesystem("file")
        data = self.to_dict()
        with fs.open(path, "w") as f:
            yaml.safe_dump(data, f)

    def to_filesystem(self) -> AbstractFileSystem:
        """Create fsspec filesystem instance from options.

        Returns:
            AbstractFileSystem: Configured filesystem instance

        Example:
            >>> options = BaseStorageOptions(protocol="file")
            >>> fs = options.to_filesystem()
            >>> files = fs.ls("/path/to/data")
        """
        return filesystem(**self.to_dict(with_protocol=True))

    def update(self, **kwargs: Any) -> "BaseStorageOptions":
        """Update storage options with new values.

        Args:
            **kwargs: New option values to set

        Returns:
            BaseStorageOptions: Updated instance

        Example:
            >>> options = BaseStorageOptions(protocol="s3")
            >>> options = options.update(region="us-east-1")
            >>> print(options.region)
            'us-east-1'
        """
        return self.replace(**kwargs)


class AzureStorageOptions(BaseStorageOptions):
    """Azure Storage configuration options.

    Provides configuration for Azure storage services:
    - Azure Blob Storage (az://)
    - Azure Data Lake Storage Gen2 (abfs://)
    - Azure Data Lake Storage Gen1 (adl://)

    Supports multiple authentication methods:
    - Connection string
    - Account key
    - Service principal
    - Managed identity
    - SAS token

    Attributes:
        protocol (str): Storage protocol ("az", "abfs", or "adl")
        account_name (str): Storage account name
        account_key (str): Storage account access key
        connection_string (str): Full connection string
        tenant_id (str): Azure AD tenant ID
        client_id (str): Service principal client ID
        client_secret (str): Service principal client secret
        sas_token (str): SAS token for limited access

    Example:
        >>> # Blob Storage with account key
        >>> options = AzureStorageOptions(
        ...     protocol="az",
        ...     account_name="mystorageacct",
        ...     account_key="key123..."
        ... )
        >>>
        >>> # Data Lake with service principal
        >>> options = AzureStorageOptions(
        ...     protocol="abfs",
        ...     account_name="mydatalake",
        ...     tenant_id="tenant123",
        ...     client_id="client123",
        ...     client_secret="secret123"
        ... )
        >>>
        >>> # Simple connection string auth
        >>> options = AzureStorageOptions(
        ...     protocol="az",
        ...     connection_string="DefaultEndpoints..."
        ... )
    """

    protocol: str
    account_name: str | None = None
    account_key: str | None = None
    connection_string: str | None = None
    tenant_id: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    sas_token: str | None = None

    @classmethod
    def from_env(cls) -> "AzureStorageOptions":
        """Create storage options from environment variables.

        Reads standard Azure environment variables:
        - AZURE_STORAGE_ACCOUNT_NAME
        - AZURE_STORAGE_ACCOUNT_KEY
        - AZURE_STORAGE_CONNECTION_STRING
        - AZURE_TENANT_ID
        - AZURE_CLIENT_ID
        - AZURE_CLIENT_SECRET
        - AZURE_STORAGE_SAS_TOKEN

        Returns:
            AzureStorageOptions: Configured storage options

        Example:
            >>> # With environment variables set:
            >>> options = AzureStorageOptions.from_env()
            >>> print(options.account_name)  # From AZURE_STORAGE_ACCOUNT_NAME
            'mystorageacct'
        """
        return cls(
            protocol=os.getenv("AZURE_STORAGE_PROTOCOL", "az"),
            account_name=os.getenv("AZURE_STORAGE_ACCOUNT_NAME"),
            account_key=os.getenv("AZURE_STORAGE_ACCOUNT_KEY"),
            connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
            tenant_id=os.getenv("AZURE_TENANT_ID"),
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
            sas_token=os.getenv("AZURE_STORAGE_SAS_TOKEN"),
        )

    def to_env(self) -> None:
        """Export options to environment variables.

        Sets standard Azure environment variables.

        Example:
            >>> options = AzureStorageOptions(
            ...     protocol="az",
            ...     account_name="mystorageacct",
            ...     account_key="key123"
            ... )
            >>> options.to_env()
            >>> print(os.getenv("AZURE_STORAGE_ACCOUNT_NAME"))
            'mystorageacct'
        """
        env = {
            "AZURE_STORAGE_PROTOCOL": self.protocol,
            "AZURE_STORAGE_ACCOUNT_NAME": self.account_name,
            "AZURE_STORAGE_ACCOUNT_KEY": self.account_key,
            "AZURE_STORAGE_CONNECTION_STRING": self.connection_string,
            "AZURE_TENANT_ID": self.tenant_id,
            "AZURE_CLIENT_ID": self.client_id,
            "AZURE_CLIENT_SECRET": self.client_secret,
            "AZURE_STORAGE_SAS_TOKEN": self.sas_token,
        }
        env = {k: v for k, v in env.items() if v is not None}
        os.environ.update(env)


class GcsStorageOptions(BaseStorageOptions):
    """Google Cloud Storage configuration options.

    Provides configuration for GCS access with support for:
    - Service account authentication
    - Default application credentials
    - Token-based authentication
    - Project configuration
    - Custom endpoints

    Attributes:
        protocol (str): Storage protocol ("gs" or "gcs")
        token (str): Path to service account JSON file
        project (str): Google Cloud project ID
        access_token (str): OAuth2 access token
        endpoint_url (str): Custom storage endpoint
        timeout (int): Request timeout in seconds

    Example:
        >>> # Service account auth
        >>> options = GcsStorageOptions(
        ...     protocol="gs",
        ...     token="path/to/service-account.json",
        ...     project="my-project-123"
        ... )
        >>>
        >>> # Application default credentials
        >>> options = GcsStorageOptions(
        ...     protocol="gcs",
        ...     project="my-project-123"
        ... )
        >>>
        >>> # Custom endpoint (e.g., test server)
        >>> options = GcsStorageOptions(
        ...     protocol="gs",
        ...     endpoint_url="http://localhost:4443",
        ...     token="test-token.json"
        ... )
    """

    protocol: str
    token: str | None = None
    project: str | None = None
    access_token: str | None = None
    endpoint_url: str | None = None
    timeout: int | None = None

    @classmethod
    def from_env(cls) -> "GcsStorageOptions":
        """Create storage options from environment variables.

        Reads standard GCP environment variables:
        - GOOGLE_CLOUD_PROJECT: Project ID
        - GOOGLE_APPLICATION_CREDENTIALS: Service account file path
        - STORAGE_EMULATOR_HOST: Custom endpoint (for testing)
        - GCS_OAUTH_TOKEN: OAuth2 access token

        Returns:
            GcsStorageOptions: Configured storage options

        Example:
            >>> # With environment variables set:
            >>> options = GcsStorageOptions.from_env()
            >>> print(options.project)  # From GOOGLE_CLOUD_PROJECT
            'my-project-123'
        """
        return cls(
            protocol="gs",
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            token=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            endpoint_url=os.getenv("STORAGE_EMULATOR_HOST"),
            access_token=os.getenv("GCS_OAUTH_TOKEN"),
        )

    def to_env(self) -> None:
        """Export options to environment variables.

        Sets standard GCP environment variables.

        Example:
            >>> options = GcsStorageOptions(
            ...     protocol="gs",
            ...     project="my-project",
            ...     token="service-account.json"
            ... )
            >>> options.to_env()
            >>> print(os.getenv("GOOGLE_CLOUD_PROJECT"))
            'my-project'
        """
        env = {
            "GOOGLE_CLOUD_PROJECT": self.project,
            "GOOGLE_APPLICATION_CREDENTIALS": self.token,
            "STORAGE_EMULATOR_HOST": self.endpoint_url,
            "GCS_OAUTH_TOKEN": self.access_token,
        }
        env = {k: v for k, v in env.items() if v is not None}
        os.environ.update(env)

    def to_fsspec_kwargs(self) -> dict:
        """Convert options to fsspec filesystem arguments.

        Returns:
            dict: Arguments suitable for GCSFileSystem

        Example:
            >>> options = GcsStorageOptions(
            ...     protocol="gs",
            ...     token="service-account.json",
            ...     project="my-project"
            ... )
            >>> kwargs = options.to_fsspec_kwargs()
            >>> fs = filesystem("gcs", **kwargs)
        """
        kwargs = {
            "token": self.token,
            "project": self.project,
            "access_token": self.access_token,
            "endpoint_url": self.endpoint_url,
            "timeout": self.timeout,
        }
        return {k: v for k, v in kwargs.items() if v is not None}


class AwsStorageOptions(BaseStorageOptions):
    """AWS S3 storage configuration options.

    Provides comprehensive configuration for S3 access with support for:
    - Multiple authentication methods (keys, profiles, environment)
    - Custom endpoints for S3-compatible services
    - Region configuration
    - SSL/TLS settings

    Attributes:
        protocol (str): Always "s3" for S3 storage
        access_key_id (str): AWS access key ID
        secret_access_key (str): AWS secret access key
        session_token (str): AWS session token
        endpoint_url (str): Custom S3 endpoint URL
        region (str): AWS region name
        allow_invalid_certificates (bool): Skip SSL certificate validation
        allow_http (bool): Allow unencrypted HTTP connections
        profile (str): AWS credentials profile name

    Example:
        >>> # Basic credentials
        >>> options = AwsStorageOptions(
        ...     access_key_id="AKIAXXXXXXXX",
        ...     secret_access_key="SECRETKEY",
        ...     region="us-east-1"
        ... )
        >>>
        >>> # Profile-based auth
        >>> options = AwsStorageOptions.create(profile="dev")
        >>>
        >>> # S3-compatible service (MinIO)
        >>> options = AwsStorageOptions(
        ...     endpoint_url="http://localhost:9000",
        ...     access_key_id="minioadmin",
        ...     secret_access_key="minioadmin",
        ...     allow_http=True
        ... )
    """

    protocol: str = "s3"
    access_key_id: str | None = None
    secret_access_key: str | None = None
    session_token: str | None = None
    endpoint_url: str | None = None
    region: str | None = None
    allow_invalid_certificates: bool | None = None
    allow_http: bool | None = None

    @classmethod
    def create(
        cls,
        protocol: str = "s3",
        access_key_id: str | None = None,
        secret_access_key: str | None = None,
        session_token: str | None = None,
        endpoint_url: str | None = None,
        region: str | None = None,
        allow_invalid_certificates: bool | None = None,
        allow_http: bool | None = None,
        # Alias and loading params
        key: str | None = None,
        secret: str | None = None,
        token: str | None = None,  # maps to session_token
        profile: str | None = None,
    ) -> "AwsStorageOptions":
        """Creates an AwsStorageOptions instance, handling aliases and profile loading.

        Args:
            protocol: Storage protocol, defaults to "s3".
            access_key_id: AWS access key ID.
            secret_access_key: AWS secret access key.
            session_token: AWS session token.
            endpoint_url: Custom S3 endpoint URL.
            region: AWS region name.
            allow_invalid_certificates: Skip SSL certificate validation.
            allow_http: Allow unencrypted HTTP connections.
            key: Alias for access_key_id.
            secret: Alias for secret_access_key.
            token: Alias for session_token.
            profile: AWS credentials profile name to load credentials from.

        Returns:
            An initialized AwsStorageOptions instance.
        """

        # Initial values from explicit args or their aliases
        args = {
            "protocol": protocol,
            "access_key_id": access_key_id if access_key_id is not None else key,
            "secret_access_key": secret_access_key
            if secret_access_key is not None
            else secret,
            "session_token": session_token if session_token is not None else token,
            "endpoint_url": endpoint_url,
            "region": region,
            "allow_invalid_certificates": allow_invalid_certificates,
            "allow_http": allow_http,
        }

        if profile is not None:
            # Note: allow_invalid_certificates and allow_http are passed to from_aws_credentials.
            # If they are None here, from_aws_credentials will use its own defaults for those flags when reading.
            profile_instance = cls.from_aws_credentials(
                profile=profile,
                allow_invalid_certificates=args["allow_invalid_certificates"],
                allow_http=args["allow_http"],
            )
            # Fill in missing values from profile if not already set by direct/aliased args
            if args["access_key_id"] is None:
                args["access_key_id"] = profile_instance.access_key_id
            if args["secret_access_key"] is None:
                args["secret_access_key"] = profile_instance.secret_access_key
            if args["session_token"] is None:
                args["session_token"] = profile_instance.session_token
            if args["endpoint_url"] is None:
                args["endpoint_url"] = profile_instance.endpoint_url
            if args["region"] is None:
                args["region"] = profile_instance.region
            # If allow_invalid_certificates/allow_http were None in args, and from_aws_credentials
            # used its defaults to set them on profile_instance, we update args.
            if (
                args["allow_invalid_certificates"] is None
                and profile_instance.allow_invalid_certificates is not None
            ):
                args["allow_invalid_certificates"] = (
                    profile_instance.allow_invalid_certificates
                )
            if args["allow_http"] is None and profile_instance.allow_http is not None:
                args["allow_http"] = profile_instance.allow_http

        # Ensure protocol is 's3' if it somehow became None
        if args["protocol"] is None:
            args["protocol"] = "s3"

        return cls(**args)

    @classmethod
    def from_aws_credentials(
        cls,
        profile: str,
        allow_invalid_certificates: bool = False,
        allow_http: bool = False,
    ) -> "AwsStorageOptions":
        """Create storage options from AWS credentials file.

        Loads credentials from ~/.aws/credentials and ~/.aws/config files.

        Args:
            profile: AWS credentials profile name
            allow_invalid_certificates: Skip SSL certificate validation
            allow_http: Allow unencrypted HTTP connections

        Returns:
            AwsStorageOptions: Configured storage options

        Raises:
            ValueError: If profile not found
            FileNotFoundError: If credentials files missing

        Example:
            >>> # Load developer profile
            >>> options = AwsStorageOptions.from_aws_credentials(
            ...     profile="dev",
            ...     allow_http=True  # For local testing
            ... )
        """
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
        """Create storage options from environment variables.

        Reads standard AWS environment variables:
        - AWS_ACCESS_KEY_ID
        - AWS_SECRET_ACCESS_KEY
        - AWS_SESSION_TOKEN
        - AWS_ENDPOINT_URL
        - AWS_DEFAULT_REGION
        - ALLOW_INVALID_CERTIFICATES
        - AWS_ALLOW_HTTP

        Returns:
            AwsStorageOptions: Configured storage options

        Example:
            >>> # Load from environment
            >>> options = AwsStorageOptions.from_env()
            >>> print(options.region)
            'us-east-1'  # From AWS_DEFAULT_REGION
        """
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
        """Convert options to fsspec filesystem arguments.

        Returns:
            dict: Arguments suitable for fsspec S3FileSystem

        Example:
            >>> options = AwsStorageOptions(
            ...     access_key_id="KEY",
            ...     secret_access_key="SECRET",
            ...     region="us-west-2"
            ... )
            >>> kwargs = options.to_fsspec_kwargs()
            >>> fs = filesystem("s3", **kwargs)
        """
        fsspec_kwargs = {
            "key": self.access_key_id,
            "secret": self.secret_access_key,
            "token": self.session_token,
            "endpoint_url": self.endpoint_url,
            "client_kwargs": {
                "region_name": self.region,
                "verify": not self.allow_invalid_certificates
                if self.allow_invalid_certificates is not None
                else True,
                "use_ssl": not self.allow_http if self.allow_http is not None else True,
            },
        }
        return {k: v for k, v in fsspec_kwargs.items() if v is not None}

    def to_object_store_kwargs(self, with_conditional_put: bool = False) -> dict:
        """Convert options to object store arguments.

        Args:
            with_conditional_put: Add etag-based conditional put support

        Returns:
            dict: Arguments suitable for object store clients

        Example:
            >>> options = AwsStorageOptions(
            ...     access_key_id="KEY",
            ...     secret_access_key="SECRET"
            ... )
            >>> kwargs = options.to_object_store_kwargs()
            >>> client = ObjectStore(**kwargs)
        """
        kwargs = {
            k: str(v)
            for k, v in self.to_dict().items()
            if v is not None and k != "protocol"
        }
        if with_conditional_put:
            kwargs["conditional_put"] = "etag"
        return kwargs

    def to_env(self) -> None:
        """Export options to environment variables.

        Sets standard AWS environment variables.

        Example:
            >>> options = AwsStorageOptions(
            ...     access_key_id="KEY",
            ...     secret_access_key="SECRET",
            ...     region="us-east-1"
            ... )
            >>> options.to_env()
            >>> print(os.getenv("AWS_ACCESS_KEY_ID"))
            'KEY'
        """
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
    """GitHub repository storage configuration options.

    Provides access to files in GitHub repositories with support for:
    - Public and private repositories
    - Branch/tag/commit selection
    - Token-based authentication
    - Custom GitHub Enterprise instances

    Attributes:
        protocol (str): Always "github" for GitHub storage
        org (str): Organization or user name
        repo (str): Repository name
        ref (str): Git reference (branch, tag, or commit SHA)
        token (str): GitHub personal access token
        api_url (str): Custom GitHub API URL for enterprise instances

    Example:
        >>> # Public repository
        >>> options = GitHubStorageOptions(
        ...     org="microsoft",
        ...     repo="vscode",
        ...     ref="main"
        ... )
        >>>
        >>> # Private repository
        >>> options = GitHubStorageOptions(
        ...     org="myorg",
        ...     repo="private-repo",
        ...     token="ghp_xxxx",
        ...     ref="develop"
        ... )
        >>>
        >>> # Enterprise instance
        >>> options = GitHubStorageOptions(
        ...     org="company",
        ...     repo="internal",
        ...     api_url="https://github.company.com/api/v3",
        ...     token="ghp_xxxx"
        ... )
    """

    protocol: str = "github"
    org: str | None = None
    repo: str | None = None
    ref: str | None = None
    token: str | None = None
    api_url: str | None = None

    @classmethod
    def from_env(cls) -> "GitHubStorageOptions":
        """Create storage options from environment variables.

        Reads standard GitHub environment variables:
        - GITHUB_ORG: Organization or user name
        - GITHUB_REPO: Repository name
        - GITHUB_REF: Git reference
        - GITHUB_TOKEN: Personal access token
        - GITHUB_API_URL: Custom API URL

        Returns:
            GitHubStorageOptions: Configured storage options

        Example:
            >>> # With environment variables set:
            >>> options = GitHubStorageOptions.from_env()
            >>> print(options.org)  # From GITHUB_ORG
            'microsoft'
        """
        return cls(
            protocol="github",
            org=os.getenv("GITHUB_ORG"),
            repo=os.getenv("GITHUB_REPO"),
            ref=os.getenv("GITHUB_REF"),
            token=os.getenv("GITHUB_TOKEN"),
            api_url=os.getenv("GITHUB_API_URL"),
        )

    def to_env(self) -> None:
        """Export options to environment variables.

        Sets standard GitHub environment variables.

        Example:
            >>> options = GitHubStorageOptions(
            ...     org="microsoft",
            ...     repo="vscode",
            ...     token="ghp_xxxx"
            ... )
            >>> options.to_env()
            >>> print(os.getenv("GITHUB_ORG"))
            'microsoft'
        """
        env = {
            "GITHUB_ORG": self.org,
            "GITHUB_REPO": self.repo,
            "GITHUB_REF": self.ref,
            "GITHUB_TOKEN": self.token,
            "GITHUB_API_URL": self.api_url,
        }
        env = {k: v for k, v in env.items() if v is not None}
        os.environ.update(env)

    def to_fsspec_kwargs(self) -> dict:
        """Convert options to fsspec filesystem arguments.

        Returns:
            dict: Arguments suitable for GitHubFileSystem

        Example:
            >>> options = GitHubStorageOptions(
            ...     org="microsoft",
            ...     repo="vscode",
            ...     token="ghp_xxxx"
            ... )
            >>> kwargs = options.to_fsspec_kwargs()
            >>> fs = filesystem("github", **kwargs)
        """
        kwargs = {
            "org": self.org,
            "repo": self.repo,
            "ref": self.ref,
            "token": self.token,
            "api_url": self.api_url,
        }
        return {k: v for k, v in kwargs.items() if v is not None}


class GitLabStorageOptions(BaseStorageOptions):
    """GitLab repository storage configuration options.

    Provides access to files in GitLab repositories with support for:
    - Public and private repositories
    - Self-hosted GitLab instances
    - Project ID or name-based access
    - Branch/tag/commit selection
    - Token-based authentication

    Attributes:
        protocol (str): Always "gitlab" for GitLab storage
        base_url (str): GitLab instance URL, defaults to gitlab.com
        project_id (str | int): Project ID number
        project_name (str): Project name/path
        ref (str): Git reference (branch, tag, or commit SHA)
        token (str): GitLab personal access token
        api_version (str): API version to use

    Example:
        >>> # Public project on gitlab.com
        >>> options = GitLabStorageOptions(
        ...     project_name="group/project",
        ...     ref="main"
        ... )
        >>>
        >>> # Private project with token
        >>> options = GitLabStorageOptions(
        ...     project_id=12345,
        ...     token="glpat_xxxx",
        ...     ref="develop"
        ... )
        >>>
        >>> # Self-hosted instance
        >>> options = GitLabStorageOptions(
        ...     base_url="https://gitlab.company.com",
        ...     project_name="internal/project",
        ...     token="glpat_xxxx"
        ... )
    """

    protocol: str = "gitlab"
    base_url: str = "https://gitlab.com"
    project_id: str | int | None = None
    project_name: str | None = None
    ref: str | None = None
    token: str | None = None
    api_version: str = "v4"

    def __post_init__(self) -> None:
        """Validate GitLab configuration after initialization.

        Ensures either project_id or project_name is provided.

        Args:
            __context: Pydantic validation context (unused)

        Raises:
            ValueError: If neither project_id nor project_name is provided

        Example:
            >>> # Valid initialization
            >>> options = GitLabStorageOptions(project_id=12345)
            >>>
            >>> # Invalid initialization
            >>> try:
            ...     options = GitLabStorageOptions()
            ... except ValueError as e:
            ...     print(str(e))
            'Either project_id or project_name must be provided'
        """
        if self.project_id is None and self.project_name is None:
            raise ValueError("Either project_id or project_name must be provided")

    @classmethod
    def from_env(cls) -> "GitLabStorageOptions":
        """Create storage options from environment variables.

        Reads standard GitLab environment variables:
        - GITLAB_URL: Instance URL
        - GITLAB_PROJECT_ID: Project ID
        - GITLAB_PROJECT_NAME: Project name/path
        - GITLAB_REF: Git reference
        - GITLAB_TOKEN: Personal access token
        - GITLAB_API_VERSION: API version

        Returns:
            GitLabStorageOptions: Configured storage options

        Example:
            >>> # With environment variables set:
            >>> options = GitLabStorageOptions.from_env()
            >>> print(options.project_id)  # From GITLAB_PROJECT_ID
            '12345'
        """
        return cls(
            protocol="gitlab",
            base_url=os.getenv("GITLAB_URL", "https://gitlab.com"),
            project_id=os.getenv("GITLAB_PROJECT_ID"),
            project_name=os.getenv("GITLAB_PROJECT_NAME"),
            ref=os.getenv("GITLAB_REF"),
            token=os.getenv("GITLAB_TOKEN"),
            api_version=os.getenv("GITLAB_API_VERSION", "v4"),
        )

    def to_env(self) -> None:
        """Export options to environment variables.

        Sets standard GitLab environment variables.

        Example:
            >>> options = GitLabStorageOptions(
            ...     project_id=12345,
            ...     token="glpat_xxxx"
            ... )
            >>> options.to_env()
            >>> print(os.getenv("GITLAB_PROJECT_ID"))
            '12345'
        """
        env = {
            "GITLAB_URL": self.base_url,
            "GITLAB_PROJECT_ID": str(self.project_id) if self.project_id else None,
            "GITLAB_PROJECT_NAME": self.project_name,
            "GITLAB_REF": self.ref,
            "GITLAB_TOKEN": self.token,
            "GITLAB_API_VERSION": self.api_version,
        }
        env = {k: v for k, v in env.items() if v is not None}
        os.environ.update(env)

    def to_fsspec_kwargs(self) -> dict:
        """Convert options to fsspec filesystem arguments.

        Returns:
            dict: Arguments suitable for GitLabFileSystem

        Example:
            >>> options = GitLabStorageOptions(
            ...     project_id=12345,
            ...     token="glpat_xxxx"
            ... )
            >>> kwargs = options.to_fsspec_kwargs()
            >>> fs = filesystem("gitlab", **kwargs)
        """
        kwargs = {
            "base_url": self.base_url,
            "project_id": self.project_id,
            "project_name": self.project_name,
            "ref": self.ref,
            "token": self.token,
            "api_version": self.api_version,
        }
        return {k: v for k, v in kwargs.items() if v is not None}


class LocalStorageOptions(BaseStorageOptions):
    """Local filesystem configuration options.

    Provides basic configuration for local file access. While this class
    is simple, it maintains consistency with other storage options and
    enables transparent switching between local and remote storage.

    Attributes:
        protocol (str): Always "file" for local filesystem
        auto_mkdir (bool): Create directories automatically
        mode (int): Default file creation mode (unix-style)

    Example:
        >>> # Basic local access
        >>> options = LocalStorageOptions()
        >>> fs = options.to_filesystem()
        >>> files = fs.ls("/path/to/data")
        >>>
        >>> # With auto directory creation
        >>> options = LocalStorageOptions(auto_mkdir=True)
        >>> fs = options.to_filesystem()
        >>> with fs.open("/new/path/file.txt", "w") as f:
        ...     f.write("test")  # Creates /new/path/ automatically
    """

    protocol: str = "file"
    auto_mkdir: bool = False
    mode: int | None = None

    def to_fsspec_kwargs(self) -> dict:
        """Convert options to fsspec filesystem arguments.

        Returns:
            dict: Arguments suitable for LocalFileSystem

        Example:
            >>> options = LocalStorageOptions(auto_mkdir=True)
            >>> kwargs = options.to_fsspec_kwargs()
            >>> fs = filesystem("file", **kwargs)
        """
        kwargs = {
            "auto_mkdir": self.auto_mkdir,
            "mode": self.mode,
        }
        return {k: v for k, v in kwargs.items() if v is not None}


def from_dict(protocol: str, storage_options: dict) -> BaseStorageOptions:
    """Create appropriate storage options instance from dictionary.

    Factory function that creates the correct storage options class based on protocol.

    Args:
        protocol: Storage protocol identifier (e.g., "s3", "gs", "file")
        storage_options: Dictionary of configuration options

    Returns:
        BaseStorageOptions: Appropriate storage options instance

    Raises:
        ValueError: If protocol is not supported

    Example:
        >>> # Create S3 options
        >>> options = from_dict("s3", {
        ...     "access_key_id": "KEY",
        ...     "secret_access_key": "SECRET"
        ... })
        >>> print(type(options).__name__)
        'AwsStorageOptions'
    """
    if protocol == "s3":
        if (
            "profile" in storage_options
            or "key" in storage_options
            or "secret" in storage_options
        ):
            return AwsStorageOptions.create(**storage_options)
        return AwsStorageOptions(**storage_options)
    elif protocol in ["az", "abfs", "adl"]:
        return AzureStorageOptions(**storage_options)
    elif protocol in ["gs", "gcs"]:
        return GcsStorageOptions(**storage_options)
    elif protocol == "github":
        return GitHubStorageOptions(**storage_options)
    elif protocol == "gitlab":
        return GitLabStorageOptions(**storage_options)
    elif protocol == "file":
        return LocalStorageOptions()
    else:
        raise ValueError(f"Unsupported protocol: {protocol}")


def from_env(protocol: str) -> BaseStorageOptions:
    """Create storage options from environment variables.

    Factory function that creates and configures storage options from
    protocol-specific environment variables.

    Args:
        protocol: Storage protocol identifier (e.g., "s3", "github")

    Returns:
        BaseStorageOptions: Configured storage options instance

    Raises:
        ValueError: If protocol is not supported

    Example:
        >>> # With AWS credentials in environment
        >>> options = from_env("s3")
        >>> print(options.access_key_id)  # From AWS_ACCESS_KEY_ID
        'AKIAXXXXXX'
    """
    if protocol == "s3":
        return AwsStorageOptions.from_env()
    elif protocol == "github":
        return GitHubStorageOptions.from_env()
    elif protocol == "gitlab":
        return GitLabStorageOptions.from_env()
    elif protocol == "file":
        return LocalStorageOptions()
    else:
        raise ValueError(f"Unsupported protocol: {protocol}")


class StorageOptions(msgspec.Struct):
    """High-level storage options container and factory.

    Provides a unified interface for creating and managing storage options
    for different protocols.

    Attributes:
        storage_options (BaseStorageOptions): Underlying storage options instance

    Example:
        >>> # Create from protocol
        >>> options = StorageOptions.create(
        ...     protocol="s3",
        ...     access_key_id="KEY",
        ...     secret_access_key="SECRET"
        ... )
        >>>
        >>> # Create from existing options
        >>> s3_opts = AwsStorageOptions(access_key_id="KEY")
        >>> options = StorageOptions(storage_options=s3_opts)
    """

    storage_options: BaseStorageOptions

    @classmethod
    def create(cls, **data: Any) -> "StorageOptions":
        """Create storage options from arguments.

        Args:
            **data: Either:
                - protocol and configuration options
                - storage_options=pre-configured instance

        Returns:
            StorageOptions: Configured storage options instance

        Raises:
            ValueError: If protocol missing or invalid

        Example:
            >>> # Direct protocol config
            >>> options = StorageOptions.create(
            ...     protocol="s3",
            ...     region="us-east-1"
            ... )
        """
        protocol = data.get("protocol")
        if protocol is None and "storage_options" not in data:
            raise ValueError("protocol must be specified")

        if "storage_options" not in data:
            if protocol == "s3":
                if "profile" in data or "key" in data or "secret" in data:
                    storage_options = AwsStorageOptions.create(**data)
                else:
                    storage_options = AwsStorageOptions(**data)
            elif protocol == "github":
                storage_options = GitHubStorageOptions(**data)
            elif protocol == "gitlab":
                storage_options = GitLabStorageOptions(**data)
            elif protocol in ["az", "abfs", "adl"]:
                storage_options = AzureStorageOptions(**data)
            elif protocol in ["gs", "gcs"]:
                storage_options = GcsStorageOptions(**data)
            elif protocol == "file":
                storage_options = LocalStorageOptions(**data)
            else:
                raise ValueError(f"Unsupported protocol: {protocol}")

            return cls(storage_options=storage_options)
        else:
            return cls(**data)

    @classmethod
    def from_yaml(cls, path: str, fs: AbstractFileSystem = None) -> "StorageOptions":
        """Create storage options from YAML configuration.

        Args:
            path: Path to YAML configuration file
            fs: Filesystem for reading configuration

        Returns:
            StorageOptions: Configured storage options

        Example:
            >>> # Load from config file
            >>> options = StorageOptions.from_yaml("storage.yml")
            >>> print(options.storage_options.protocol)
            's3'
        """
        with fs.open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)

    @classmethod
    def from_env(cls, protocol: str) -> "StorageOptions":
        """Create storage options from environment variables.

        Args:
            protocol: Storage protocol to configure

        Returns:
            StorageOptions: Environment-configured options

        Example:
            >>> # Load AWS config from environment
            >>> options = StorageOptions.from_env("s3")
        """
        if protocol == "s3":
            return cls(storage_options=AwsStorageOptions.from_env())
        elif protocol == "github":
            return cls(storage_options=GitHubStorageOptions.from_env())
        elif protocol == "gitlab":
            return cls(storage_options=GitLabStorageOptions.from_env())
        elif protocol == "file":
            return cls(storage_options=LocalStorageOptions())
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")

    def to_filesystem(self) -> AbstractFileSystem:
        """Create fsspec filesystem instance.

        Returns:
            AbstractFileSystem: Configured filesystem instance

        Example:
            >>> options = StorageOptions(protocol="file")
            >>> fs = options.to_filesystem()
            >>> files = fs.ls("/data")
        """
        return self.storage_options.to_filesystem()

    def to_dict(self, protocol: bool = False) -> dict:
        """Convert storage options to dictionary.

        Args:
            protocol: Whether to include protocol in output

        Returns:
            dict: Storage options as dictionary

        Example:
            >>> options = StorageOptions(
            ...     protocol="s3",
            ...     region="us-east-1"
            ... )
            >>> print(options.to_dict())
            {'region': 'us-east-1'}
        """
        return self.storage_options.to_dict(protocol=protocol)

    def to_object_store_kwargs(self, with_conditional_put: bool = False) -> dict:
        """Get options formatted for object store clients.

        Args:
            with_conditional_put: Add etag-based conditional put support

        Returns:
            dict: Object store configuration dictionary

        Example:
            >>> options = StorageOptions(protocol="s3")
            >>> kwargs = options.to_object_store_kwargs()
            >>> store = ObjectStore(**kwargs)
        """
        return self.storage_options.to_object_store_kwargs(
            with_conditional_put=with_conditional_put
        )


def infer_protocol_from_uri(uri: str) -> str:
    """Infer the storage protocol from a URI string.

    Analyzes the URI to determine the appropriate storage protocol based on
    the scheme or path format.

    Args:
        uri: URI or path string to analyze. Examples:
            - "s3://bucket/path"
            - "gs://bucket/path"
            - "github://org/repo"
            - "/local/path"

    Returns:
        str: Inferred protocol identifier

    Example:
        >>> # S3 protocol
        >>> infer_protocol_from_uri("s3://my-bucket/data")
        's3'
        >>>
        >>> # Local file
        >>> infer_protocol_from_uri("/home/user/data")
        'file'
        >>>
        >>> # GitHub repository
        >>> infer_protocol_from_uri("github://microsoft/vscode")
        'github'
    """
    if uri.startswith("s3://"):
        return "s3"
    elif uri.startswith("gs://") or uri.startswith("gcs://"):
        return "gs"
    elif uri.startswith("github://"):
        return "github"
    elif uri.startswith("gitlab://"):
        return "gitlab"
    elif uri.startswith(("az://", "abfs://", "adl://")):
        return uri.split("://")[0]
    else:
        return "file"


def storage_options_from_uri(uri: str) -> BaseStorageOptions:
    """Create storage options instance from a URI string.

    Infers the protocol and extracts relevant configuration from the URI
    to create appropriate storage options.

    Args:
        uri: URI string containing protocol and optional configuration.
            Examples:
            - "s3://bucket/path"
            - "gs://project/bucket/path"
            - "github://org/repo"

    Returns:
        BaseStorageOptions: Configured storage options instance

    Example:
        >>> # S3 options
        >>> opts = storage_options_from_uri("s3://my-bucket/data")
        >>> print(opts.protocol)
        's3'
        >>>
        >>> # GitHub options
        >>> opts = storage_options_from_uri("github://microsoft/vscode")
        >>> print(opts.org)
        'microsoft'
        >>> print(opts.repo)
        'vscode'
    """
    protocol = infer_protocol_from_uri(uri)
    options = infer_storage_options(uri)

    if protocol == "s3":
        return AwsStorageOptions(protocol=protocol, **options)
    elif protocol in ["gs", "gcs"]:
        return GcsStorageOptions(protocol=protocol, **options)
    elif protocol == "github":
        parts = uri.replace("github://", "").split("/")
        return GitHubStorageOptions(
            protocol=protocol, org=parts[0], repo=parts[1] if len(parts) > 1 else None
        )
    elif protocol == "gitlab":
        parts = uri.replace("gitlab://", "").split("/")
        return GitLabStorageOptions(
            protocol=protocol, project_name=parts[-1] if parts else None
        )
    elif protocol in ["az", "abfs", "adl"]:
        return AzureStorageOptions(protocol=protocol, **options)
    else:
        return LocalStorageOptions()


def merge_storage_options(
    *options: BaseStorageOptions | dict | None, overwrite: bool = True
) -> BaseStorageOptions:
    """Merge multiple storage options into a single configuration.

    Combines options from multiple sources with control over precedence.

    Args:
        *options: Storage options to merge. Can be:
            - BaseStorageOptions instances
            - Dictionaries of options
            - None values (ignored)
        overwrite: Whether later options override earlier ones

    Returns:
        BaseStorageOptions: Combined storage options

    Example:
        >>> # Merge with overwrite
        >>> base = AwsStorageOptions(
        ...     region="us-east-1",
        ...     access_key_id="OLD_KEY"
        ... )
        >>> override = {"access_key_id": "NEW_KEY"}
        >>> merged = merge_storage_options(base, override)
        >>> print(merged.access_key_id)
        'NEW_KEY'
        >>>
        >>> # Preserve existing values
        >>> merged = merge_storage_options(
        ...     base,
        ...     override,
        ...     overwrite=False
        ... )
        >>> print(merged.access_key_id)
        'OLD_KEY'
    """
    result = {}
    protocol = None

    for opts in options:
        if opts is None:
            continue
        if isinstance(opts, BaseStorageOptions):
            opts = opts.to_dict(with_protocol=True)
        if not protocol and "protocol" in opts:
            protocol = opts["protocol"]
        for k, v in opts.items():
            if overwrite or k not in result:
                result[k] = v

    if not protocol:
        protocol = "file"
    return from_dict(protocol, result)

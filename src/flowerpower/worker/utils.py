import urllib.parse

def build_url(
    type: str,
    host: str | None = None,
    port: int | None = None,
    username: str| None  = None,
    password: str| None  = None,
    database: str| None  = None,
    ssl: bool = False,
    ca_file: str| None  = None,
    cert_file: str| None  = None,
    key_file: str| None  = None,
    verify_ssl: bool = True,  # Controls certificate validation
) -> str:
    """
    Generate a connection URL for various database types.
    
    Args:
        type: Database type (postgresql, mysql, sqlite, mongodb, redis, nats, mqtt, memory)
        host: Database host
        port: Database port
        username: Authentication username
        password: Authentication password
        database: Database name
        ssl: Whether to use SSL
        ca_file: CA certificate file path
        cert_file: Client certificate file path
        key_file: Client key file path
        verify_ssl: Whether to verify SSL certificates (default: True)
        
    Returns:
        Connection URL string
    """
    # Set default values based on database type
    default_ports = {
        "postgresql": 5432,
        "mysql": 3306,
        "mongodb": 27017,
        "redis": 6379,
        "nats": 4222,
        "mqtt": 1883 if not ssl else 8883,
    }

    if host is None and type.lower() not in ["memory", "sqlite"]:
        host = "localhost"
    if port is None and type.lower() in default_ports:
        port = default_ports[type.lower()]


    type = type.lower()
    
    # Handle memory database type (SQLite in-memory)
    if type == "memory":
        return "sqlite+aiosqlite:///:memory:"
    
    # Build authentication part of URL if credentials are provided
    auth = ""
    if username:
        auth = urllib.parse.quote(username)
        if password:
            auth += f":{urllib.parse.quote(password)}"
        auth += "@"
    
    # Build the base URL with host and port
    base_url = ""
    if host:
        base_url = host
        if port:
            base_url += f":{port}"
    
    # Build query parameters for SSL options
    query_params = []
    
    # Protocol prefix for NATS with SSL
    nats_prefix = "nats+tls" if ssl and type == "nats" else "nats"
    
    if ssl:
        if type == "postgresql":
            # For PostgreSQL, use the appropriate SSL mode
            if verify_ssl:
                if ca_file:
                    query_params.append("ssl=verify-ca")
                else:
                    query_params.append("ssl=verify-full")
            else:
                query_params.append("ssl=allow")
            
            if ca_file:
                query_params.append(f"sslrootcert={ca_file}")
            if cert_file:
                query_params.append(f"sslcert={cert_file}")
            if key_file:
                query_params.append(f"sslkey={key_file}")
                
        elif type == "mysql":
            query_params.append("ssl=true")
            
            if ca_file:
                query_params.append(f"ssl_ca={ca_file}")
            if cert_file:
                query_params.append(f"ssl_cert={cert_file}")
            if key_file:
                query_params.append(f"ssl_key={key_file}")
            if not verify_ssl:
                query_params.append("ssl_verify_cert=false")
                
        elif type == "mongodb":
            query_params.append("tls=true")
            
            if ca_file:
                query_params.append(f"tlsCAFile={ca_file}")
            if cert_file and key_file:
                query_params.append(f"tlsCertificateKeyFile={cert_file}")
            if not verify_ssl:
                query_params.append("tlsAllowInvalidCertificates=true")
                
        elif type == "redis":
            # For Redis, we use rediss:// instead of redis:// for SSL
            type = "rediss"
            
            if not verify_ssl:
                query_params.append("ssl_cert_reqs=none")
            if ca_file:
                query_params.append(f"ssl_ca_certs={ca_file}")
            if cert_file:
                query_params.append(f"ssl_certfile={cert_file}")
            if key_file:
                query_params.append(f"ssl_keyfile={key_file}")
                
        elif type == "nats":
            # NATS with SSL uses nats+tls:// protocol (handled in prefix)
            if not verify_ssl:
                query_params.append("tls_verify=false")
            if ca_file:
                query_params.append(f"tls_ca_file={ca_file}")
            if cert_file:
                query_params.append(f"tls_cert_file={cert_file}")
            if key_file:
                query_params.append(f"tls_key_file={key_file}")
                
        elif type == "mqtt":
            query_params.append("tls=true")
            
            if not verify_ssl:
                query_params.append("tls_insecure=true")
            if ca_file:
                query_params.append(f"tls_ca_file={ca_file}")
            if cert_file:
                query_params.append(f"tls_cert_file={cert_file}")
            if key_file:
                query_params.append(f"tls_key_file={key_file}")
    
    # Construct query string
    query_string = ""
    if query_params:
        query_string = "?" + "&".join(query_params)
    
    # Generate URL based on database type
    if type == "postgresql":
        db_path = f"{database}" if database else ""
        return f"postgresql+asyncpg://{auth}{base_url}/{db_path}{query_string}"
    
    elif type == "mysql":
        db_path = f"{database}" if database else ""
        return f"mysql+aiomysql://{auth}{base_url}/{db_path}{query_string}"
    
    elif type == "sqlite":
        db_path = f"{database}" if database else ""
        return f"sqlite+aiosqlite:///{db_path}{query_string}"
    
    elif type == "mongodb":
        db_path = f"{database}" if database else ""
        return f"mongodb://{auth}{base_url}/{db_path}{query_string}"
    
    elif type in ["redis", "rediss"]:
        db_number = f"/{database}" if database and database.isdigit() else ""
        return f"{type}://{auth}{base_url}{db_number}{query_string}"
    
    elif type == "nats":
        return f"{nats_prefix}://{auth}{base_url}{query_string}"
    
    elif type == "mqtt":
        return f"mqtt://{auth}{base_url}{query_string}"
    
    else:
        raise ValueError(f"Unsupported database type: {type}")
## Golang Libraries Deep Dive

This document provides an overview of commonly used Go standard libraries and popular third-party libraries, focusing on their purpose, use cases, key features, and best practices, primarily referencing official documentation from `pkg.go.dev` and respective project sources.

### Standard Libraries (pkg.go.dev)

#### `net/http`
*   **Purpose**: Provides HTTP client and server implementations.
*   **Common Use Cases**: Building web servers, APIs, and making HTTP requests to external services.
*   **Key Features/Best Practices**:
    *   `http.Server`: For creating robust HTTP servers. Configure timeouts (ReadTimeout, WriteTimeout, IdleTimeout) for resilience.
    *   `http.Client`: For making HTTP requests. The default client is suitable for many cases, but creating custom clients allows configuring timeouts, transport settings (like connection pooling), and redirects. Reuse clients for efficiency.
    *   `http.HandleFunc`/`http.Handle`: Registering request handlers.
    *   `http.Request`: Represents an incoming server request or outgoing client request. Access headers, body, URL parameters, etc.
    *   `http.ResponseWriter`: Interface used by handlers to construct the HTTP response.
    *   Use `context.Context` for request cancellation and deadlines.
*   **Source**: `https://pkg.go.dev/net/http`

#### `context`
*   **Purpose**: Carries deadlines, cancellation signals, and request-scoped values across API boundaries and between goroutines.
*   **Common Use Cases**: Managing request lifecycles in servers, controlling timeouts and cancellations for operations (like database queries, HTTP requests), passing request-specific data (like user IDs or trace IDs).
*   **Key Features/Best Practices**:
    *   `context.Background()`: Root context, typically used in `main` or initialization.
    *   `context.TODO()`: Use when unsure which context to use or if the function hasn't been updated for context propagation yet. Avoid using in production code long-term.
    *   `WithCancel`, `WithDeadline`, `WithTimeout`: Create derived contexts with cancellation or time limits. **Always call the returned `cancel` function**, even if the operation completes successfully, to release resources associated with the context. `go vet` helps check this.
    *   `WithValue`: Attaches request-scoped data. Use sparingly and only for data that transits processes/APIs, not for optional function parameters. Use custom types for keys to avoid collisions.
    *   Pass `Context` as the first argument to functions, typically named `ctx`.
    *   Do not store `Context` inside a struct; pass it explicitly.
*   **Source**: `https://pkg.go.dev/context` [11, 13, 14]

#### `encoding/json`
*   **Purpose**: Implements encoding and decoding of JSON data as defined in RFC 7159.
*   **Common Use Cases**: Marshaling Go structs into JSON for API responses, unmarshaling JSON from API requests into Go structs, working with JSON configuration files.
*   **Key Features/Best Practices**:
    *   `json.Marshal`: Encodes a Go value (structs, maps, slices, basic types) into a JSON byte slice.
    *   `json.Unmarshal`: Decodes a JSON byte slice into a Go value (typically a pointer to a struct or map).
    *   Struct field tags (`json:"fieldName,omitempty,string"`): Control JSON field names, omit empty fields, or encode/decode numbers as strings.
    *   `json.Encoder`/`json.Decoder`: Stream-based encoding/decoding, useful for working with `io.Reader`/`io.Writer` (e.g., HTTP request/response bodies, files). More efficient for large JSON data or network streams.
    *   Handle potential errors during marshaling and unmarshaling.
    *   Use `map[string]interface{}` or specific structs depending on whether the JSON structure is known beforehand.
*   **Source**: `https://pkg.go.dev/encoding/json`

#### `database/sql`
*   **Purpose**: Provides a generic interface around SQL (or SQL-like) databases. It must be used with a specific database driver.
*   **Common Use Cases**: Interacting with relational databases (PostgreSQL, MySQL, SQLite, SQL Server, etc.).
*   **Key Features/Best Practices**:
    *   Requires a driver package (e.g., `github.com/lib/pq` for PostgreSQL) imported for its side effects (`_ "github.com/lib/pq"`).
    *   `sql.Open`: Returns a `*sql.DB`, representing a pool of database connections. Create it once and share it.
    *   `db.PingContext`: Verify the database connection.
    *   `db.QueryContext`/`db.QueryRowContext`: Execute queries that return rows. Always use the `Context` variants for cancellation/timeout support.
    *   `db.ExecContext`: Execute statements that don't return rows (INSERT, UPDATE, DELETE).
    *   `sql.Rows`: Result of `QueryContext`. Iterate using `rows.Next()` and scan data using `rows.Scan()`. **Always check `rows.Err()` after the loop and `defer rows.Close()`**.
    *   `sql.Tx`: Represents a database transaction. Use `db.BeginTx` to start, and `tx.Commit()` or `tx.Rollback()` (usually deferred with error checking) to end.
    *   Prepared Statements (`db.PrepareContext`): Use for security (prevent SQL injection) and performance when executing the same statement multiple times.
*   **Source**: `https://pkg.go.dev/database/sql`

#### `io`
*   **Purpose**: Provides basic interfaces to I/O primitives. Its primary role is to wrap existing implementations of I/O operations and compose them.
*   **Common Use Cases**: Abstracting reading and writing operations, working with data streams (files, network connections, buffers).
*   **Key Features/Best Practices**:
    *   `io.Reader`: Interface for reading data (e.g., `os.File`, `bytes.Buffer`, `http.Request.Body`). Key method: `Read(p []byte) (n int, err error)`.
    *   `io.Writer`: Interface for writing data (e.g., `os.File`, `bytes.Buffer`, `http.ResponseWriter`). Key method: `Write(p []byte) (n int, err error)`.
    *   `io.Closer`: Interface for closing resources. Key method: `Close() error`. Often used with `defer`.
    *   `io.Seeker`: Interface for seeking within a stream.
    *   `io.Copy`: Efficiently copies data from a `Reader` to a `Writer`.
    *   `io.ReadAll`: Reads all data from a `Reader` until EOF. Use with caution for potentially large streams.
    *   `ioutil` (now largely moved into `io` and `os`): Contains utility functions like `ReadFile`, `WriteFile`.
*   **Source**: `https://pkg.go.dev/io` [20]

#### `os`
*   **Purpose**: Provides a platform-independent interface to operating system functionality.
*   **Common Use Cases**: File system operations (create, open, read, write, stat, remove files/directories), accessing environment variables, working with command-line arguments, managing processes.
*   **Key Features/Best Practices**:
    *   `os.Args`: Access command-line arguments.
    *   `os.Getenv`/`os.LookupEnv`/`os.Setenv`: Manage environment variables.
    *   `os.Open`/`os.Create`/`os.OpenFile`: Open or create files. Returns `*os.File`. Remember to `defer file.Close()`.
    *   `os.File`: Represents an open file descriptor. Implements `io.Reader`, `io.Writer`, `io.Closer`, `io.Seeker`. Methods include `Read`, `Write`, `Stat`, `Sync`, `Truncate`.
    *   `os.Stat`/`os.Lstat`: Get file metadata (`os.FileInfo`).
    *   `os.Mkdir`/`os.MkdirAll`/`os.Remove`/`os.RemoveAll`: Directory and file manipulation.
    *   `os.Exit`: Exit the program immediately (use sparingly, often better to return errors up the call stack).
    *   `os.Stdin`, `os.Stdout`, `os.Stderr`: Standard input, output, and error file descriptors.
*   **Source**: `https://pkg.go.dev/os` [28, 47]

#### `flag`
*   **Purpose**: Implements command-line flag parsing.
*   **Common Use Cases**: Defining and parsing command-line options for applications.
*   **Key Features/Best Practices**:
    *   Define flags using `flag.String`, `flag.Int`, `flag.Bool`, etc., or `flag.StringVar`, `flag.IntVar`, `flag.BoolVar` to bind to existing variables.
    *   Each flag definition includes name, default value, and usage description.
    *   Call `flag.Parse()` early in `main` to parse the arguments from `os.Args[1:]`.
    *   Access flag values via the pointers returned by `flag.String` etc., or directly via bound variables after `flag.Parse()` has run.
    *   `flag.Args()`: Returns non-flag arguments.
    *   Supports `-flag`, `-flag=x`, `-flag x` syntax (last form not for booleans).
    *   Automatically provides `-h`/`-help` usage messages.
*   **Source**: `https://pkg.go.dev/flag` [15, 21, 29, 32, 33]

### Popular Third-Party Libraries/Frameworks

#### Web Frameworks

*   **Gin (`github.com/gin-gonic/gin`)**
    *   **Purpose**: High-performance HTTP web framework with a Martini-like API. [7, 17, 30]
    *   **Common Use Cases**: Building REST APIs, web applications.
    *   **Key Features**: Fast routing (radix tree based), middleware support, JSON validation, route grouping, error management, rendering (JSON, XML, HTML), crash recovery. [7, 17, 30]
    *   **Best Practices**: Use middleware for common tasks (logging, auth), group related routes, leverage built-in data binding and validation. [22, 24]
    *   **Source**: `https://pkg.go.dev/github.com/gin-gonic/gin` [17], `https://gin-gonic.com/docs/` [7, 30]
*   **Echo (`github.com/labstack/echo/v4`)**
    *   **Purpose**: High-performance, extensible, minimalist Go web framework. [3, 6, 44]
    *   **Common Use Cases**: Building REST APIs, microservices, web applications. [27]
    *   **Key Features**: Optimized router, extensive middleware support, data binding (JSON, XML, form), template rendering, centralized error handling, automatic TLS, HTTP/2 support. [3, 6, 27]
    *   **Best Practices**: Utilize `echo.Context` for request/response handling, leverage middleware effectively, use data binding and validation features. [3, 19]
    *   **Source**: `https://pkg.go.dev/github.com/labstack/echo/v4` [44], `https://echo.labstack.com/docs` [3]

#### CLI Libraries

*   **Cobra (`github.com/spf13/cobra`)**
    *   **Purpose**: Library for creating powerful modern CLI applications (like `git` or `kubectl`). [9, 12, 35]
    *   **Common Use Cases**: Building complex CLIs with subcommands, flags, and arguments. Used by Kubernetes, Hugo, GitHub CLI. [9, 12]
    *   **Key Features**: Subcommand-based CLIs, POSIX-compliant flags (using `pflag`), nested subcommands, global/local/persistent flags, automatic help generation, command suggestions, shell autocompletion (Bash, Zsh, Fish, PowerShell), man page generation, optional Viper integration. [9, 18, 35]
    *   **Best Practices**: Structure applications with a root command and subcommands, use persistent flags for global options, leverage generator (`cobra-cli`) for bootstrapping. [9, 18, 25]
    *   **Source**: `https://pkg.go.dev/github.com/spf13/cobra` [12], `https://cobra.dev/` [35], `https://github.com/spf13/cobra` [9]
*   **urfave/cli (`github.com/urfave/cli/v2`)**
    *   **Purpose**: Simple, fast package for building command-line applications. [8, 10, 23, 36]
    *   **Common Use Cases**: Creating CLIs with commands, subcommands, and flags.
    *   **Key Features**: Declarative API, commands/subcommands, flexible help system, dynamic shell completion (Bash, Zsh, Fish, PowerShell), flag parsing (including environment variables, files via altsrc), no external dependencies (core library), documentation generation. [8, 10, 38]
    *   **Best Practices**: Define app structure declaratively, use `Action` functions for command logic, leverage context for accessing flags and arguments. [8, 38]
    *   **Source**: `https://pkg.go.dev/github.com/urfave/cli/v2` [36], `https://cli.urfave.org/` [10, 38]

#### Configuration Management

*   **Viper (`github.com/spf13/viper`)**
    *   **Purpose**: Complete configuration solution for Go applications, designed to work within an application and handle all types of configuration needs and formats.
    *   **Common Use Cases**: Managing configuration from files (JSON, TOML, YAML, HCL, envfile), environment variables, remote K/V stores (etcd, Consul), command-line flags.
    *   **Key Features**: Setting defaults, reading from multiple sources with precedence, live watching of config files, unmarshaling into structs, explicit Get functions (GetString, GetInt, etc.). Integrates well with Cobra flags.
    *   **Best Practices**: Set defaults, bind flags (e.g., from Cobra), read from files and environment variables, use `viper.Unmarshal` for typed configuration.
    *   **Source**: `https://pkg.go.dev/github.com/spf13/viper`, `https://github.com/spf13/viper`

#### ORMs / DB Tools

*   **GORM (`gorm.io/gorm`)**
    *   **Purpose**: ORM (Object-Relational Mapper) library for Go, aims to be developer friendly.
    *   **Common Use Cases**: Database interactions using Go structs as models, simplifying CRUD operations, migrations, associations (Has One, Has Many, Belongs To, Many To Many).
    *   **Key Features**: Full-featured ORM, associations, hooks (Before/After Create/Save/Update/Delete), preloading/eager loading, transactions, migrations, SQL builder, extensibility.
    *   **Best Practices**: Define models with GORM struct tags, handle errors carefully, use transactions for multi-statement operations, understand lazy vs. eager loading implications.
    *   **Source**: `https://pkg.go.dev/gorm.io/gorm`, `https://gorm.io/docs/`
*   **sqlx (`github.com/jmoiron/sqlx`)**
    *   **Purpose**: Set of extensions on Go's standard `database/sql` package, aiming to make common patterns more convenient without being a full ORM. [16, 41]
    *   **Common Use Cases**: Simplifying scanning query results into structs and maps, using named query parameters. [16, 34, 41]
    *   **Key Features**: Marshaling rows into structs (including embedded structs), maps, slices; named parameter support (including prepared statements); `Get` and `Select` helpers for common query patterns. Maintains compatibility with `database/sql` interfaces. [16, 34, 40, 41]
    *   **Best Practices**: Use `db.GetContext`/`db.SelectContext` for querying into structs/slices, use named queries (`db.NamedExecContext`, `db.NamedQueryContext`) with structs or maps for clearer parameter binding, leverage `sqlx.In` for `IN` queries. [16, 40]
    *   **Source**: `https://pkg.go.dev/github.com/jmoiron/sqlx` [41], `https://github.com/jmoiron/sqlx` [16]

#### Logging Libraries

*   **zap (`go.uber.org/zap`)**
    *   **Purpose**: Blazing fast, structured, leveled logging library from Uber. [5, 37, 43]
    *   **Common Use Cases**: High-performance structured logging, often in JSON format for easy parsing by log aggregation systems. [4, 5]
    *   **Key Features**: Very high performance with low allocation overhead (reflection-free JSON encoding). [4, 43] Provides two loggers: `zap.Logger` (fastest, strongly-typed fields) and `zap.SugaredLogger` (slightly slower, more convenient, loosely-typed fields, `printf`-style methods). [43] Supports logging levels, custom output destinations, stack traces for errors. [5, 37]
    *   **Best Practices**: Choose `Logger` for performance-critical paths, `SugaredLogger` for convenience. Use structured fields (`zap.String`, `zap.Int`, etc.) for context. Configure production vs. development loggers appropriately. Ensure `logger.Sync()` is called before application exit (e.g., using `defer`). [4, 5, 37]
    *   **Source**: `https://pkg.go.dev/go.uber.org/zap` [4], `https://github.com/uber-go/zap` [43]
*   **logrus (`github.com/sirupsen/logrus`)**
    *   **Purpose**: Structured logger for Go, completely API compatible with the standard library logger.
    *   **Common Use Cases**: Structured logging, adding context (fields) to log entries, customizable formatting (Text, JSON), log hooks for sending logs to external systems.
    *   **Key Features**: Pluggable hooks (e.g., for sending logs to Sentry, Logstash, etc.), built-in formatters (Text, JSON), standard library compatibility, field-based logging, logging levels.
    *   **Best Practices**: Use `logrus.WithField` or `logrus.WithFields` to add context, configure formatters and hooks during initialization, treat the standard logger instance as a global singleton or create separate instances.
    *   **Source**: `https://pkg.go.dev/github.com/sirupsen/logrus`, `https://github.com/sirupsen/logrus`
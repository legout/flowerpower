# Golang Developer (`dev-golang`) Knowledge Base

This knowledge base provides essential information for the Golang Developer mode (`dev-golang`). It covers core language features, standard library usage, common third-party libraries, best practices, concurrency patterns, performance optimization, testing strategies, tooling, and common pitfalls.

## File Structure & Summaries

*   `./general-summary.md`: (Line Count: 4) Brief overview of Golang's core features: simplicity, efficiency, concurrency (goroutines/channels), standard library, tooling, and suitability for backend/systems programming.
*   `./setup-summary.md`: (Line Count: 10) Essential steps for setting up a basic Go project: `go mod init`, write code, `go build`, `go run`, `go mod tidy`, `go install`.
*   `best-practices/`:
    *   `best_practices.md`: (Line Count: 141) Explanation of general Golang best practices (naming, errors, packages, formatting, simplicity, interfaces, avoiding globals).
*   `concurrency/`:
    *   `advanced_concurrency.md`: (Line Count: 201) Deep dive into advanced Go concurrency patterns (pipelines, fan-out/in, worker pools, rate limiting, context), `sync` primitives, best practices, and pitfalls (races, leaks, deadlocks).
*   `libraries/`:
    *   `common_libraries.md`: (Line Count: 198) Overview of common Go standard libraries (`net/http`, `context`, `encoding/json`, `database/sql`, `io`, `os`, `flag`) and popular third-party libraries (Gin, Echo, Cobra, urfave/cli, Viper, GORM, sqlx, zap, logrus).
*   `performance/`:
    *   `optimization.md`: (Line Count: 208) Covers Golang performance optimization techniques including profiling (`pprof`), garbage collection (GC) understanding/tuning, reducing allocations, CPU optimization, memory layout, and common pitfalls.
*   `pitfalls/`:
    *   `pitfalls_antipatterns.md`: (Line Count: 191) Deep dive into common Golang pitfalls and anti-patterns, including concurrency mistakes (data races, leaks, channel misuse), error handling issues, interface pollution, package management complexities, and performance anti-patterns.
*   `testing/`:
    *   `strategies.md`: (Line Count: 178) Deep dive into Golang testing strategies using the standard `testing` package, table-driven tests, integration testing, benchmarking, fixtures, mocking/stubbing techniques, code coverage, and best practices.
*   `tooling/`:
    *   `tooling.md`: (Line Count: 238) Overview of the Go tooling ecosystem, including standard commands (`go build`, `go test`, `go mod`, `go fmt`, `go vet`, `go run`, `go install`, `go generate`), profiling (`pprof`), dependency management (Go Modules), testing patterns, linting (`golangci-lint`), and debugging (`dlv`).
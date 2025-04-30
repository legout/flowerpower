Based on the provided tooling information, setting up a basic Go project involves these essential steps:

1.  **Initialize Module:** Navigate to your project directory and run `go mod init [module-path]` (e.g., `go mod init github.com/youruser/yourproject`) to create a `go.mod` file, enabling Go Modules for dependency management.
2.  **Write Code:** Create your Go source files (e.g., `main.go` for an executable).
3.  **Build:** Compile your code using `go build`. For a main package, this creates an executable in the current directory.
4.  **Run:** Execute your compiled program directly (`./yourprogram`) or use `go run main.go` to compile and run in one step for development.
5.  **Manage Dependencies:** As you add imports, run `go mod tidy` to automatically download required dependencies and update `go.mod` and `go.sum`.
6.  **Install (Optional):** Use `go install` to compile and place the executable in your `$GOPATH/bin` or `$GOBIN` directory for system-wide access.
# Dev Solver Mode - Knowledge Base

This directory contains the knowledge base (KB) files for the `dev-solver` mode, designed to assist in complex problem-solving and debugging tasks.

## KB Structure

The KB is organized into libraries, each focusing on a specific area relevant to problem-solving. The master index for all libraries is located at `index.toml`.

## Available Libraries

The following libraries are currently available:

*   **`debugging_techniques`**: Synthesized KB for Debugging Techniques from Vertex AI MCP. (See details below)
    *   *Index:* `debugging_techniques/index.toml`

*(Note: The placeholder files `01-analysis-framework.md` and `02-solution-evaluation.md` mentioned previously are not part of the structured library system and may be integrated or removed later.)*

---

## Library Details

### `debugging_techniques`

*   **Source:** Vertex AI MCP
*   **Description:** This library provides synthesized knowledge about various debugging techniques, generated via the Vertex AI MCP server. The content is structured into foundational and advanced topics.
*   **Index File:** `debugging_techniques/index.toml`
*   **Synthesized Documents:** The core content is located within the `synthesized/` sub-directory, organized further into `foundations/` and `advanced/`.

    *   `synthesized/foundations/core_techniques.md`: Summary of foundational debugging techniques including debuggers, print/logging, rubber ducking, bug reproduction, VCS analysis, static analysis, and testing.
    *   `synthesized/foundations/setup-summary.md`: Brief overview of setting up debugging tools, emphasizing IDE integration and language-specific requirements.
    *   `synthesized/foundations/general-summary.md`: High-level overview of debugging, covering its purpose and the spectrum of techniques from foundational to advanced.
    *   `synthesized/advanced/concurrency_debugging.md`: Addresses challenges and techniques for debugging issues in multi-threaded or concurrent programs, such as race conditions and deadlocks.
    *   `synthesized/advanced/distributed_systems_debugging.md`: Covers the complexities and strategies for debugging applications composed of multiple interacting services across a network.
    *   `synthesized/advanced/dynamic_analysis.md`: Explanation of dynamic analysis techniques used for debugging software during runtime execution.
    *   `synthesized/advanced/memory_debugging.md`: Focuses on techniques and tools for finding memory-related bugs like leaks, buffer overflows, and use-after-free errors.
    *   `synthesized/advanced/performance_profiling.md`: Using profiling tools to analyze application performance, identify bottlenecks, and optimize resource usage (CPU, memory, I/O).
    *   `synthesized/advanced/post_mortem.md`: Debugging using information collected after a program has crashed or terminated abnormally, typically via core dumps or crash logs.
    *   `synthesized/advanced/reverse_debugging.md`: Explanation of reverse debugging, allowing developers to step backward in execution time to find the origin of bugs.

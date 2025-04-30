+++
title = "Advanced Debugging: Reverse Debugging"
summary = "Explanation of reverse debugging, allowing developers to step backward in execution time to find the origin of bugs."
tags = ["debugging", "advanced", "reverse-debugging", "time-travel-debugging", "record-replay"]
+++

# Advanced Debugging: Reverse Debugging

Reverse debugging (also known as time-travel debugging) allows developers to navigate program execution history both forwards and backward. Instead of only stepping forward, you can step back, run backward to a previous breakpoint, or examine past variable states.

**How it Works (Common Approaches):**

1.  **Record and Replay:** The debugger records the entire execution trace (or non-deterministic events like system calls, thread switches) during an initial run. Subsequent debugging sessions replay this recording, allowing backward movement by restoring previous states from the trace.
2.  **Snapshotting:** The debugger takes periodic snapshots of the program's state, allowing it to revert to a previous snapshot and re-execute forward if needed to reach an intermediate point.

**Key Capabilities:**

*   **Step Backward:** Execute the program in reverse, line by line.
*   **Run Backward:** Continue execution backward until a condition (like a previous breakpoint) is met.
*   **Inspect Past State:** Examine the values variables held at previous points in time.
*   **Identify Origins:** Quickly trace back from an observed error (e.g., corrupted data) to the point where the corruption actually occurred.

**Tools:**

*   **GDB (GNU Debugger):** Offers reverse debugging capabilities (often requires recording first).
*   **rr (Record and Replay):** A popular tool for recording Linux application executions for reversible debugging.
*   **WinDbg (Windows Debugger):** Supports Time Travel Debugging (TTD) by recording execution.
*   **UndoDB:** Commercial reverse debugger.

**Use Cases:**

*   Finding the root cause of bugs that manifest long after the initial error occurred (e.g., memory corruption, complex state issues).
*   Understanding intricate sequences of events that lead to failure.
*   Debugging non-deterministic bugs by recording a failing run and replaying it deterministically.
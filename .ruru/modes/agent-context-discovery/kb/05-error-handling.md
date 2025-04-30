# Error Handling

**Error Handling Note:** If file analysis (`list_files`, `read_file`, `search_files`), saving (`write_to_file`), or logging (`insert_content`) fail, analyze the error. Log the issue to the task log (using `insert_content`) if possible, and report the failure clearly in your `attempt_completion` message.
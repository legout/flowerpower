# Standard: Tool Usage XML Syntax

**Applies To:** All modes using tools.

**1. General Principle:**

All tool usage requests MUST adhere strictly to the specified XML format. Parameters MUST be direct children of the main tool tag.

**2. Correct Format:**

The correct structure places parameter tags directly inside the tool name tag:

```xml
<tool_name>
  <parameter1_name>value1</parameter1_name>
  <parameter2_name>value2</parameter2_name>
  <!-- ... other parameters ... -->
</tool_name>
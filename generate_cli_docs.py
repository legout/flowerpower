import os
import re
import json
from typing import Dict, Any, List

def parse_typer_command(file_content: str, command_name: str) -> Dict[str, Any]:
    """
    Parses a Typer command function from the file content.
    Extracts description, arguments, options, and examples.
    """
    command_data = {
        "name": command_name,
        "description": "",
        "usage": "",
        "arguments": [],
        "options": [],
        "examples": [],
    }

    # Find the command definition block
    # This regex looks for:
    # 1. @app.command() decorator
    # 2. def function_name(...):
    # 3. The triple-quoted docstring
    # 4. The function body
    # It attempts to capture the entire block for the specific command name.
    command_block_match = re.search(
        rf"@app\.command\(\)\s+def {re.escape(command_name)}\s*\(.*?\):\s*\"\"\"(?P<docstring>.*?)\"\"\"",
        file_content,
        re.DOTALL,
    )

    if not command_block_match:
        return None

    docstring = command_block_match.group("docstring")

    # Extract description (first paragraph before Args: or Examples:)
    description_match = re.match(r"^\s*(.*?)(?:\n\s*Args:|\n\s*Examples:|$)", docstring, re.DOTALL)
    if description_match:
        command_data["description"] = description_match.group(1).strip()

    # Extract arguments and options
    args_section = re.search(r"Args:\s*(.*?)(?:\n\s*Examples:|$)", docstring, re.DOTALL)
    if args_section:
        arg_lines = args_section.group(1).strip().split('\n')
        for line in arg_lines:
            line = line.strip()
            if not line:
                continue

            # Argument: `name: Description`
            arg_match = re.match(r"^(?P<name>\w+):\s*(?P<description>.*)", line)
            if arg_match:
                # Check if it's an option by looking for typer.Option in the function signature
                # This is a heuristic, a more robust solution would parse the AST
                param_name = arg_match.group("name")
                if f"typer.Option({param_name}" in file_content or f"typer.Option(..., '{param_name}'" in file_content:
                    # This is likely an option, need to extract short name and default
                    # This requires parsing the function signature, which is complex with regex
                    # For simplicity, we'll assume short name and default are not easily extractable from docstring
                    # A more advanced parser would use AST.
                    option_match = re.search(
                        rf"{re.escape(param_name)}:\s*.*?=[\w\s]*typer\.Option\((?P<default_val>.*?)(?:,\s*\"--{re.escape(param_name)}\")?(?:,\s*\"-(?P<short_name>\w)\")?",
                        file_content,
                    )

                    option_data = {
                        "name": f"--{param_name.replace('_', '-')}",
                        "short": "",
                        "type": "str", # Default type, can be improved with AST
                        "description": arg_match.group("description").strip(),
                        "default": "None",
                    }
                    if option_match:
                        if option_match.group("short_name"):
                            option_data["short"] = f"-{option_match.group('short_name')}"
                        if option_match.group("default_val") and option_match.group("default_val") != "...":
                            option_data["default"] = option_match.group("default_val").strip().replace('"', '')
                    command_data["options"].append(option_data)
                elif f"typer.Argument({param_name}" in file_content:
                    # It's an argument defined with typer.Argument
                    command_data["arguments"].append({
                        "name": param_name,
                        "type": "str", # Default type
                        "description": arg_match.group("description").strip(),
                        "default": "Required",
                    })
                else:
                    # It's a regular argument in the function signature
                    command_data["arguments"].append({
                        "name": param_name,
                        "type": "str", # Default type
                        "description": arg_match.group("description").strip(),
                        "default": "Required", # Typer arguments are often required by default unless specified
                    })


    # Extract examples
    examples_section = re.search(r"Examples:\s*(.*)", docstring, re.DOTALL)
    if examples_section:
        example_lines = examples_section.group(1).strip().split('\n')
        current_example = []
        for line in example_lines:
            line = line.strip()
            if line.startswith("$"):
                if current_example:
                    command_data["examples"].append("\n".join(current_example).strip())
                current_example = [line]
            elif current_example:
                current_example.append(line)
        if current_example:
            command_data["examples"].append("\n".join(current_example).strip())

    # Generate usage example (simple heuristic)
    command_data["usage"] = f"flowerpower {' '.join(command_data['name'].split('-'))} [options]"


    return command_data

def generate_markdown_table(headers: List[str], data: List[Dict[str, str]]) -> str:
    if not data:
        return "N/A"
    table = "| " + " | ".join(headers) + " |\n"
    table += "|---" * len(headers) + "|\n"
    for row in data:
        row_values = [str(row.get(h.lower().replace(' ', '_'), '')) for h in headers]
        table += "| " + " | ".join(row_values) + " |\n"
    return table

def format_for_quarto(command_data: Dict[str, Any], parent_command: str = "") -> str:
    md = f"## `flowerpower {parent_command}{' ' if parent_command else ''}{command_data['name']}`\n\n"
    md += f"{command_data['description']}\n\n"
    md += f"### Usage\n\n```bash\n{command_data['usage']}\n```\n\n"

    if command_data["arguments"]:
        md += "### Arguments\n\n"
        md += generate_markdown_table(["Name", "Type", "Description", "Default"], command_data["arguments"])
        md += "\n\n"

    if command_data["options"]:
        md += "### Options\n\n"
        md += generate_markdown_table(["Name", "Short", "Type", "Description", "Default"], command_data["options"])
        md += "\n\n"

    if command_data["examples"]:
        md += "### Examples\n\n"
        for example in command_data["examples"]:
            md += f"```bash\n{example}\n```\n\n"
    return md

def format_for_mkdocs(command_data: Dict[str, Any], parent_command: str = "") -> str:
    md = f"## `flowerpower {parent_command}{' ' if parent_command else ''}{command_data['name']}` {{ #flowerpower-{command_data['name']} }}\n\n"
    md += f"{command_data['description']}\n\n"
    md += f"### Usage\n\n```bash\n{command_data['usage']}\n```\n\n"

    if command_data["arguments"]:
        md += "### Arguments\n\n"
        md += generate_markdown_table(["Name", "Type", "Description", "Default"], command_data["arguments"])
        md += "\n\n"

    if command_data["options"]:
        md += "### Options\n\n"
        md += generate_markdown_table(["Name", "Short", "Type", "Description", "Default"], command_data["options"])
        md += "\n\n"

    if command_data["examples"]:
        md += "### Examples\n\n"
        for example in command_data["examples"]:
            md += f"```bash\n{example}\n```\n\n"
    return md

def main():
    cli_dir = "src/flowerpower/cli"
    output_data = {}

    # Main CLI commands
    with open(os.path.join(cli_dir, "__init__.py"), "r") as f:
        init_content = f.read()
    
    # Extract main commands from __init__.py
    main_commands = ["init", "ui"]
    output_data["main"] = []
    for cmd in main_commands:
        data = parse_typer_command(init_content, cmd)
        if data:
            output_data["main"].append(data)

    # Subcommands
    subcommand_files = {
        "pipeline": "pipeline.py",
        "job-queue": "job_queue.py",
        "mqtt": "mqtt.py",
    }

    output_data["subcommands"] = {}
    for parent_cmd, filename in subcommand_files.items():
        with open(os.path.join(cli_dir, filename), "r") as f:
            sub_content = f.read()
        
        # Find all @app.command() definitions in the subcommand file
        # This regex is a bit more general to find all command functions
        sub_command_matches = re.findall(r"@app\.command\(\)\s+def (\w+)\s*\(", sub_content)
        
        output_data["subcommands"][parent_cmd] = []
        for sub_cmd_name in sub_command_matches:
            data = parse_typer_command(sub_content, sub_cmd_name)
            if data:
                # Adjust usage for subcommands
                data["usage"] = data["usage"].replace("flowerpower", f"flowerpower {parent_cmd}")
                output_data["subcommands"][parent_cmd].append(data)

    # Generate documentation files
    docs_base_quarto = "docs/quarto/api"
    docs_base_mkdocs = "docs/mkdocs/docs/api"
    
    os.makedirs(docs_base_quarto, exist_ok=True)
    os.makedirs(docs_base_mkdocs, exist_ok=True)

    # CLI overview files
    with open(os.path.join(docs_base_quarto, "cli.qmd"), "w") as f:
        f.write("# CLI Reference\n\n")
        f.write("This section provides a comprehensive reference for the FlowerPower Command Line Interface (CLI).\n\n")
        f.write("## Main Commands\n\n")
        for cmd_data in output_data["main"]:
            f.write(format_for_quarto(cmd_data))
            f.write("---\n\n") # Separator

    with open(os.path.join(docs_base_mkdocs, "cli.md"), "w") as f:
        f.write("# CLI Reference\n\n")
        f.write("This section provides a comprehensive reference for the FlowerPower Command Line Interface (CLI).\n\n")
        f.write("## Main Commands\n\n")
        for cmd_data in output_data["main"]:
            f.write(format_for_mkdocs(cmd_data))
            f.write("---\n\n") # Separator

    # Subcommand files
    for parent_cmd, commands in output_data["subcommands"].items():
        quarto_filename = f"cli_{parent_cmd.replace('-', '_')}.qmd"
        mkdocs_filename = f"cli_{parent_cmd.replace('-', '_')}.md"
        
        with open(os.path.join(docs_base_quarto, quarto_filename), "w") as f:
            f.write(f"# `flowerpower {parent_cmd}` Commands\n\n")
            f.write(f"This section details the commands available under `flowerpower {parent_cmd}`.\n\n")
            for cmd_data in commands:
                f.write(format_for_quarto(cmd_data, parent_command=parent_cmd))
                f.write("---\n\n") # Separator

        with open(os.path.join(docs_base_mkdocs, mkdocs_filename), "w") as f:
            f.write(f"# `flowerpower {parent_cmd}` Commands {{ #flowerpower-{parent_cmd} }}\n\n")
            f.write(f"This section details the commands available under `flowerpower {parent_cmd}`.\n\n")
            for cmd_data in commands:
                f.write(format_for_mkdocs(cmd_data, parent_command=parent_cmd))
                f.write("---\n\n") # Separator

    print("CLI documentation generated successfully!")

if __name__ == "__main__":
    main()
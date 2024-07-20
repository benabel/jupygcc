import subprocess
from shlex import split
import os
import re


def handle_metadata(cell_code: str):
    # Define regular expression pattern for metadata
    metadata_pattern = r"^//\| (\w+): (.*)$"

    # Split string into metadata and code
    metadata_lines, code = re.split(r"(?m)^(?!\/\/\|)", cell_code, maxsplit=1)

    # Extract metadata dictionary from metadata lines
    metadata_dict = {}
    for line in metadata_lines.split("\n"):
        match = re.match(metadata_pattern, line)
        if match:
            metadata_dict[match.group(1)] = match.group(2)
    return metadata_dict, code


def has_main_function(c_code):
    """
    Check if there is a main function in the given C code.
    """
    # Check if there is at least one line starting with #include
    if not re.search(r"^\s*#include", c_code, re.MULTILINE):
        return False

    # Search for main function definition
    main_func_pattern = r"^\s*(int|void)\s+main\s*\(([^)]*)\)\s*{(?s:.*?)}"
    main_func_match = re.search(main_func_pattern, c_code, re.MULTILINE)

    return bool(main_func_match)


def compile_run_c(c_code: str, metadata_dict: dict):
    if not has_main_function(c_code):
        c_code = f"""#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

int main() {{
{c_code}
return 0;
}}"""

    try:
        # Step 1: Compile the C code from the string
        compile_command = split("gcc -std=c99 -x c -o test_code -")
        compile_process = subprocess.run(
            compile_command,
            input=c_code,
            encoding="utf-8",
            check=True,
            capture_output=True,
        )
        # print("Compilation output:", compile_process.stdout)
        # print("Compilation errors:", compile_process.stderr)

        # Step 2: Run the compiled executable
        run_command = ["./test_code"]
        run_process = subprocess.run(
            run_command,
            check=True,
            capture_output=True,
            text=True,
            input=metadata_dict.get("stdin"),
        )
        # print program ouput
        print(run_process.stdout)

        # Clean up: Remove the compiled executable

        os.remove("test_code")
        return run_process.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e}\n{e.stderr}"

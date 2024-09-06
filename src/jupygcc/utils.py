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

def modify_code_for_interactive_input(c_code: str) -> str:
    # Regex to find scanf statements
    scanf_pattern = re.compile(r'scanf\s*\(\s*"%(\w+)"\s*,\s*&([^;]+)\s*\)\s*;')

    # Function to replace scanf with scanf and printf
    def replace_scanf(match):
        type_specifier = match.group(1)
        variable = match.group(2)
        return f'scanf("%{type_specifier}", &{variable}); printf("%{type_specifier}\\n", {variable});'

    # Replace all scanf statements
    modified_code = scanf_pattern.sub(replace_scanf, c_code)
    return modified_code

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

    # Modify the code to add printf after scanf
    c_code = modify_code_for_interactive_input(c_code)

    try:
        # Step 1: Compile the C code from the string
        compile_command = split("gcc -std=c99 -x c -o jupygcc_code -")
        compile_process = subprocess.run(
            compile_command,
            input=c_code,
            encoding="utf-8",
            check=True,
            capture_output=True,
        )
        
        if compile_process.stdout:
            print("Compilation output:", compile_process.stdout)
        if compile_process.stderr:
            print("Compilation errors:", compile_process.stderr)

        # Step 2: Run the compiled executable
        stdin = metadata_dict.get("stdin")
        run_command = ["./jupygcc_code"]
        run_process = subprocess.run(
            run_command,
            check=True,
            capture_output=True,
            text=True,
            input=stdin,
        )
        
        print(run_process.stdout)

        # Clean up: Remove the compiled executable
        os.remove("jupygcc_code")
        return run_process.stdout
    except subprocess.CalledProcessError as e:
        print(f"Execution Error: {e}\n{e.stderr}")

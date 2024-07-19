import tempfile
import os
import subprocess
from IPython.core.magic import register_cell_magic

@register_cell_magic("gcc")
def gcc_magic(line, cell):
    """Compile and run C code using gcc."""
    # Create a temporary C file
    with tempfile.NamedTemporaryFile(suffix=".c", delete=False) as f:
        f.write(cell.encode("utf-8"))

    # Compile the C file
    try:
        subprocess.run(["gcc", f.name, "-o", f.name[:-2]], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Compilation failed with error: {e.stdout.decode()}")
        os.unlink(f.name)
        return

    # Run the compiled program
    try:
        result = subprocess.run([f.name[:-2]], capture_output=True, text=True)
    except Exception as e:
        print(f"Running the program failed with error: {e}")
    finally:
        os.unlink(f.name)
        os.unlink(f.name[:-2])

    print(result.stdout)

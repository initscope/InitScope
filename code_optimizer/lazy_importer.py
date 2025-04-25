import os
import ast
import re

def find_python_files(directory):
    """Recursively find all Python files in the given directory."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files

def read_file_lines(file_path):
    """Read the lines of a file."""
    with open(file_path, "r") as f:
        lines = f.readlines()
    return lines

def write_file_if_modified(file_path, original_lines, modified, lines, message):
    """Write modified lines back to the file if there are changes."""
    if modified and lines != original_lines:
        with open(file_path, "w") as f:
            f.writelines(lines)
        print(f"{message} in {file_path}")
        return True
    return False

def detect_import_alias_with_ast(file_path, module_name):
    """Parse a Python file and detect if the module is imported, with or without an alias."""
    with open(file_path, "r") as file:
        tree = ast.parse(file.read())
    
    alias = None
    global_import_line_numbers = []
    from_imports = {}  # New dictionary to store 'from module import ...' items

    # Traverse the AST to locate global import statements
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias_node in node.names:
                if alias_node.name == module_name and node.col_offset == 0:  # Ensure it's a global import
                    alias = alias_node.asname or module_name  # Set alias or default to module name
                    global_import_line_numbers.append(node.lineno - 1)  # Capture line number (0-indexed)
        elif isinstance(node, ast.ImportFrom):
            if node.module == module_name and node.col_offset == 0:  # Ensure it's a global import
                for alias_node in node.names:
                    import_name = alias_node.name
                    as_name = alias_node.asname or import_name  # Set alias or default to import name
                    from_imports[as_name] = import_name  # Track the imported name and its alias
                global_import_line_numbers.append(node.lineno - 1)  # Capture line number for each import

    return alias, global_import_line_numbers, from_imports

def replace_global_imports_with_lazy(file_path, module_name):
    """Replace global imports of the module with lazy imports, handling potential aliases using AST."""
    alias, global_import_line_numbers, from_imports = detect_import_alias_with_ast(file_path, module_name)
    if not global_import_line_numbers and not from_imports:
        return False  # No global import of the specified module found
    
    lines = read_file_lines(file_path)
    original_lines = lines[:]

    # Comment out only the global imports
    for line_num in global_import_line_numbers:
        lines[line_num] = f"# {lines[line_num].strip()}  # Commented out for lazy import\n"

    # Check for module usage and insert lazy imports with proper indentation
    modified = False
    
    # Handle usage of regular import module pattern
    usage_pattern = f"{alias}." if alias else None
    
    import re

    for i, line in enumerate(lines):
        # Handle `from module import ...` usage patterns
        for as_name, import_name in from_imports.items():
            # Use a regex to check for the exact usage of `as_name` (e.g., `array`)
            if re.search(rf'\b{as_name}\b(?=\s*[\.\(])', line):  # Check if `as_name` is used in the correct context
                indentation = len(line) - len(line.lstrip())
                lazy_import_statement = f"{' ' * indentation}from {module_name} import {import_name}  # Lazy import\n"

                # Insert the lazy import before the first usage if not already there, avoiding duplicate imports
                if not any(f"from {module_name} import {import_name}" in lines[j] for j in range(max(0, i - 2), i + 1)):
                    lines.insert(i, lazy_import_statement)
                    modified = True
                    break

        # Handle import module as alias usage pattern if it exists
        if usage_pattern and (usage_pattern in line or f"{alias} " in line):  # Handle cases with or without dot notation
            indentation = len(line) - len(line.lstrip())  # Calculate current line's indentation
            lazy_import_statement = f"{' ' * indentation}import {module_name} as {alias}  # Lazy import\n"

            # Insert the lazy import before the first usage if not already there, avoiding duplicate imports
            if not any(f"import {module_name}" in lines[j] for j in range(max(0, i - 2), i + 1)):
                lines.insert(i, lazy_import_statement)
                modified = True

    return write_file_if_modified(
        file_path, original_lines, modified, lines,
        "Updated lazy imports for from module import"
    )

def update_codebase(directory, module_name):
    """Update all Python files in the directory to lazy load the specified module."""
    python_files = find_python_files(directory)
    changes_made = 0

    for file_path in python_files:
        if replace_global_imports_with_lazy(file_path, module_name):
            changes_made += 1

    print(f"Total files updated: {changes_made}")

if __name__ == "__main__":
    # Input directory path and module name
    directory = input("Enter the directory of the codebase: ")
    module_name = input("Enter the module name to lazy import: ")
    update_codebase(directory, module_name)
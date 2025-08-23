import ast
import inspect
import subprocess
import sys
from pathlib import Path

from sandbox import utils

UTILS_PATH = Path(inspect.getfile(utils))

FUNCTIONS_MAP = {
    "format_args": utils.format_args,
    "ts_plot": utils.ts_plot,
}


def get_utils_imports_and_functions():
    """Parse utils.py to extract imports and function definitions."""
    utils_code = UTILS_PATH.read_text()
    utils_tree = ast.parse(utils_code)

    imports = []
    functions = {}

    for node in utils_tree.body:
        if isinstance(node, ast.Import | ast.ImportFrom):
            imports.append(ast.unparse(node))
        elif isinstance(node, ast.FunctionDef):
            functions[node.name] = node

    return imports, functions


def find_called_functions(func_node):
    """Return names of functions called inside a given function node."""
    called = set()
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            called.add(node.func.id)
    return called


def resolve_dependencies(func_name, functions, added):
    """Recursively resolve dependencies for a function."""
    if func_name in added:
        return []

    if func_name not in functions:
        return []

    node = functions[func_name]
    added.add(func_name)

    deps = []
    for called in find_called_functions(node):
        if called in functions and called not in added:
            deps += resolve_dependencies(called, functions, added)

    deps.append(node)
    return deps


def inline_functions(file_path: str) -> Path:
    code = Path(file_path).read_text()
    tree = ast.parse(code)

    utils_imports, utils_functions = get_utils_imports_and_functions()

    new_body = []
    inserted_imports = False
    added_funcs = set()

    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "sandbox.utils":
            if not inserted_imports:
                for imp in utils_imports:
                    new_body.append(ast.parse(imp).body[0])
                inserted_imports = True

            for alias in node.names:
                if alias.name in FUNCTIONS_MAP:
                    deps = resolve_dependencies(
                        alias.name,
                        utils_functions,
                        added_funcs,
                    )
                    new_body.extend(deps)
        else:
            new_body.append(node)

    tree.body = new_body
    new_code = ast.unparse(tree)

    out_dir = Path("share")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"{Path(file_path).stem}_ext.py"
    out_path.write_text(new_code)
    return out_path


def run_ruff(file_path: Path):
    """Run ruff check --fix and ruff format on the given file."""
    subprocess.run(["ruff", "check", "--fix", str(file_path)], check=False)
    subprocess.run(["ruff", "format", str(file_path)], check=False)


def main():
    file_path = sys.argv[1]
    out_path = inline_functions(file_path)
    run_ruff(out_path)


if __name__ == "__main__":
    main()

import re
import shutil
import sys
from pathlib import Path
import inspect
import importlib.util
import subprocess

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SHARE_PATH = PROJECT_ROOT / "share"
UTILS_PATH = PROJECT_ROOT / "src/tm/utils.py"
UTILS_ALIAS = "tu"
UTILS_IMPORT = r"import tm\.utils as tu"
UTILS_FUNCTIONS = [
    "ts_plot",
    "format_args",
]


def should_process(src_path):
    """
    Check if relevant tm functions are present in source
    """
    text = src_path.read_text()
    return any(re.search(rf"{UTILS_ALIAS}\.{fn}", text) for fn in UTILS_FUNCTIONS)


def copy_source(src_path):
    """
    Create a copy with _ext suffix inside share/
    """
    dest_name = f"{src_path.stem}_ext.py"
    dest_path = SHARE_PATH / dest_name
    dest_path.parent.mkdir(exist_ok=True)
    shutil.copy(src_path, dest_path)
    return dest_path


def extract_imports(utils_path):
    lines = utils_path.read_text().splitlines()
    imports = []
    for line in lines:
        if (
            line.strip().startswith("import")
            or line.strip().startswith("from")
            or not line.strip()
        ):
            imports.append(line)
        else:
            break
    return "\n".join(imports)


def replace_imports(dest_path):
    """
    Replace `import tm.utils as tu` with explicit imports
    """
    contents = dest_path.read_text()
    new_imports = extract_imports(UTILS_PATH)
    contents = re.sub(rf"^{UTILS_IMPORT}", new_imports, contents, flags=re.MULTILINE)
    dest_path.write_text(contents)


def get_insert_line(dest_path):
    """
    Find line number of second '# %%'
    """
    lines = dest_path.read_text().splitlines()
    matches = [i for i, line in enumerate(lines, 1) if line.strip() == "# %%"]
    return matches[1] if len(matches) > 1 else None


def extract_function_code(func_name):
    """
    Use inspect to get source code of a function from utils.py
    """
    spec = importlib.util.spec_from_file_location("utils", UTILS_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    func = getattr(mod, func_name)
    source = inspect.getsource(func)
    return source


def insert_function(dest_path, func_name, insert_line):
    """
    Insert renamed function into target file and update usage
    """
    text = dest_path.read_text()
    if not re.search(rf"{UTILS_ALIAS}\.{func_name}", text):
        return

    func_code = extract_function_code(func_name)
    lines = text.splitlines()
    new_lines = lines[: insert_line - 1] + [func_code, ""] + lines[insert_line - 1 :]
    text = "\n".join(new_lines)
    text = text.replace(f"{UTILS_ALIAS}.{func_name}", f"{func_name}")
    dest_path.write_text(text)


def run_ruff(dest_path):
    subprocess.run(
        ["ruff", "check", "--select", "F,I", "--fix", str(dest_path)], check=False
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: python translate_utils.py <source.py>")
        sys.exit(1)

    src_path = Path(sys.argv[1])
    if not should_process(src_path):
        print("No relevant tu functions found. Exiting.")
        sys.exit(1)

    dest_path = copy_source(src_path)
    replace_imports(dest_path)

    insert_line = get_insert_line(dest_path)
    if insert_line is None:
        print("Second '# %%' not found.")
        sys.exit(1)

    for fn in UTILS_FUNCTIONS:
        insert_function(dest_path, fn, insert_line)

    run_ruff(dest_path)
    print(f"Processed file written to: {dest_path}")


if __name__ == "__main__":
    main()

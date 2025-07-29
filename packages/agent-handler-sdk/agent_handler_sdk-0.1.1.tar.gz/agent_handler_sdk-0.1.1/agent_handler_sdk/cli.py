import sys
from pathlib import Path
from typing import Dict, Any
import importlib.resources as pkg_resources

try:
    # Python 3.11+
    import tomllib as toml  # type: ignore
except ImportError:
    # For older versions
    import tomli as toml

# Use str() to convert Traversable to string path
TEMPLATE_DIR = Path(str(pkg_resources.files("agent_handler_sdk"))) / "templates" / "connector"
SDK_ROOT = Path(__file__).parent.parent  # adjust if your structure is different


def get_sdk_version() -> str:
    pyproject = SDK_ROOT / "pyproject.toml"
    data = toml.loads(pyproject.read_text(encoding="utf-8"))
    # if you use Poetry format:
    return str(data["tool"]["poetry"]["version"])


def render_template(filename: str, **context: Any) -> str:
    """
    Load a template file from the SDK's templates/connector directory
    and format it with the given context.
    """
    template_path = TEMPLATE_DIR.joinpath(filename)
    text = template_path.read_text()
    return text.format(**context)


def scaffold_connector() -> int:
    """
    Usage: ahs-scaffold <connector-name> [--target-dir <dir>]

    Creates:
      <target-dir>/connectors/<name>/
        pyproject.toml
        metadata.yaml
        <name>_connector/
          __init__.py
          tools/
            handlers.py
        tests/
          test_handlers.py
    """
    args = sys.argv[1:]
    if not args:
        print(scaffold_connector.__doc__)
        sys.exit(1)

    name = args[0]
    target = Path(".")
    if "--target-dir" in args:
        idx = args.index("--target-dir")
        target = Path(args[idx + 1])

    version = get_sdk_version()

    base = target / "connectors" / name
    pkg_dir = base / f"{name}_connector"
    tools_dir = pkg_dir / "tools"
    tests_dir = base / "tests"

    # Create directories
    for d in (base, pkg_dir, tools_dir, tests_dir):
        d.mkdir(parents=True, exist_ok=True)

    # Map template → output path
    files_to_render = {
        "pyproject.toml.tpl": base / "pyproject.toml",
        "metadata.yaml.tpl": base / "metadata.yaml",
        "init.py.tpl": pkg_dir / "__init__.py",
        "handlers.py.tpl": tools_dir / "handlers.py",
        "test_handlers.py.tpl": tests_dir / "test_handlers.py",
        "README.md.tpl": base / "README.md",
    }

    # Render each template with both name & version
    for tpl_name, out_path in files_to_render.items():
        content = render_template(tpl_name, name=name, version=version)
        out_path.write_text(content, encoding="utf-8")

    print(f"Scaffolded connector '{name}' (SDK v{version}) at {base}")
    return 0

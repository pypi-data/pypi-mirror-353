import shutil
from pathlib import Path

def copy_template(src: Path, dst: Path):
    shutil.copytree(src, dst, dirs_exist_ok=True)
def ensure_directory_exists(path: Path):
    """Ensure that a directory exists, creating it if necessary."""
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        print(f"Directory created: {path}")
    else:
        print(f"Directory already exists: {path}")
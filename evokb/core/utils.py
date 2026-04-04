from pathlib import Path


def read_file(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8", errors="ignore")
    return ""


def list_files(directory: Path, pattern="*.md"):
    if "**" in pattern:
        return list(directory.rglob(pattern.replace("**/", "").replace("**", "*")))
    return list(directory.glob(pattern))


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)
    return path

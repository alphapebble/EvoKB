#!/usr/bin/env python3
"""
EvoKB Ingest Agent

Fetches raw data from external sources:
- GitHub repos
- URLs
- APIs
"""

from pathlib import Path
import subprocess
import sys

RAW_DIR = Path("raw")


def run(cmd: list) -> str:
    """Run shell command."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Warning: {' '.join(cmd)} failed")
        return ""
    return result.stdout


def ingest_from_github(org: str, repo: str, path: str = "", pattern: str = "*.md"):
    """Clone repo and extract markdown files."""
    import tempfile
    import shutil

    url = f"https://github.com/{org}/{repo}.git"

    with tempfile.TemporaryDirectory() as tmp:
        print(f"Cloning {org}/{repo}...")
        run(["git", "clone", "--depth", "1", "--filter=blob:none", url, tmp])

        repo_dir = Path(tmp) / repo
        if not repo_dir.exists():
            repo_dir = Path(tmp)

        target = repo_dir / path if path else repo_dir
        if not target.exists():
            print(f"Path {path} not found in {repo}")
            return

        RAW_DIR.mkdir(exist_ok=True)

        files = list(target.glob(f"**/{pattern}"))
        print(f"Found {len(files)} {pattern} files")

        for f in files:
            if f.name in ["README.md", "index.md"]:
                continue
            out_name = f"{repo}__{f.stem}{f.suffix}"
            out_path = RAW_DIR / out_name

            content = f.read_text()
            content = f"---\nsource: {org}/{repo}\n---\n\n" + content
            out_path.write_text(content)
            print(f"  ✓ {out_name}")


def main():
    """Main ingest loop."""
    # Example: fetch from AlphaPebble playbooks
    # Uncomment to enable:
    # ingest_from_github("alphapebble", "playbooks")

    print("No external sources configured.")
    print("Add raw/*.md files manually or configure sources in scripts/ingest.py")
    print(f"\nRaw files go in: {RAW_DIR}")
    print(f"Run: python scripts/compile.py to build wiki")


if __name__ == "__main__":
    main()

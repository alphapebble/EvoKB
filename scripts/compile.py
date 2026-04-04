#!/usr/bin/env python3
"""
EvoKB Compiler Agent

Compiles raw markdown files into structured wiki articles.
Uses LLM to summarize, cross-link, and maintain quality.
"""

from pathlib import Path
import re
from datetime import date

RAW_DIR = Path("raw")
WIKI_DIR = Path("wiki")


def extract_metadata(content: str) -> dict:
    """Extract title and tags from raw content."""
    title = "Untitled"
    tags = []

    lines = content.split("\n")
    for line in lines[:20]:
        if line.startswith("# "):
            title = line[2:].strip()
        if "tag:" in line.lower() or "tags:" in line.lower():
            matches = re.findall(r"[\w-]+", line)
            tags = [t for t in matches if t not in ["tag", "tags"]]

    return {"title": title, "tags": tags}


def compile_file(raw_path: Path) -> str:
    """Compile a single raw file to wiki format."""
    content = raw_path.read_text()
    meta = extract_metadata(content)
    today = date.today().isoformat()

    filename = raw_path.stem
    safe_name = re.sub(r"[^a-z0-9-]", "-", filename.lower()).strip("-")

    compiled = f"""---
title: {meta["title"]}
date: {today}
source: {raw_path.name}
tags: {meta["tags"]}
---

# {meta["title"]}

{content}

---

*Compiled from {raw_path.name} on {today}*
"""
    return compiled, safe_name + ".md"


def run_compiler():
    """Main compiler loop."""
    if not RAW_DIR.exists():
        print("No raw/ directory - nothing to compile")
        return

    raw_files = list(RAW_DIR.glob("*.md"))
    if not raw_files:
        print("No raw files to compile")
        return

    print(f"Compiling {len(raw_files)} raw files...")

    WIKI_DIR.mkdir(exist_ok=True)

    compiled_count = 0
    for raw_file in raw_files:
        try:
            compiled, out_name = compile_file(raw_file)
            out_path = WIKI_DIR / out_name
            out_path.write_text(compiled)
            print(f"  ✓ {raw_file.name} → {out_name}")
            compiled_count += 1
        except Exception as e:
            print(f"  ✗ {raw_file.name}: {e}")

    print(f"\nCompiled {compiled_count} files to {WIKI_DIR}")


if __name__ == "__main__":
    run_compiler()

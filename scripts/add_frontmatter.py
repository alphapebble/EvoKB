#!/usr/bin/env python3
import os
import re
from pathlib import Path


def extract_title(content):
    lines = content.strip().split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
        if line.startswith("**") and line.endswith("**"):
            return line[2:-2].strip()
    return "Untitled"


def add_frontmatter(file_path):
    content = file_path.read_text()

    if content.startswith("---"):
        return

    title = extract_title(content)
    import datetime

    date = datetime.date.today().isoformat()

    frontmatter = f"""---
title: {title}
date: {date}
---

"""
    file_path.write_text(frontmatter + content)
    print(f"Added frontmatter to {file_path.name}")


def main():
    wiki_dir = Path("wiki")
    for md_file in wiki_dir.glob("*.md"):
        if md_file.name == "index.md":
            continue
        add_frontmatter(md_file)


if __name__ == "__main__":
    main()

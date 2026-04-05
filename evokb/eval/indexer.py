"""Auto-generate index.md and log.md for wiki navigation."""

import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List

from evokb.core.utils import read_file, list_files
from evokb.core.config import WIKI_DIR


def extract_frontmatter(content: str) -> Dict:
    """Extract YAML frontmatter from markdown."""
    if not content.startswith("---"):
        return {}

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}

    fm = {}
    fm_lines = parts[1].strip().split("\n")
    for line in fm_lines:
        if ":" in line:
            key, val = line.split(":", 1)
            fm[key.strip()] = val.strip().strip('"').strip("'")

    return fm


def extract_summary(content: str) -> str:
    """Extract summary from content."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            content = parts[2]

    lines = content.split("\n")
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):
            return line[:150]
    return ""


def generate_index(wiki_dir: Path = None) -> str:
    """Generate index.md with all wiki pages and summaries."""
    wiki_dir = wiki_dir or WIKI_DIR

    pages = []

    for md_file in list_files(wiki_dir, "*.md"):
        content = read_file(md_file)
        if not content:
            continue

        fm = extract_frontmatter(content)

        title = fm.get("title", md_file.stem.replace("-", " ").title())
        summary = fm.get("summary", extract_summary(content))
        tags = fm.get("tags", "")
        source = fm.get("source", "")

        pages.append(
            {
                "title": title,
                "name": md_file.stem,
                "summary": summary,
                "tags": tags,
                "source": source,
            }
        )

    pages.sort(key=lambda p: p["title"].lower())

    index_content = """# Wiki Index

Auto-generated index of all knowledge base pages.

## Contents

"""

    by_tag = {}
    for p in pages:
        if p["tags"]:
            for tag in p["tags"].split(","):
                tag = tag.strip()
                if tag:
                    if tag not in by_tag:
                        by_tag[tag] = []
                    by_tag[tag].append(p)

    if by_tag:
        index_content += "### By Tag\n\n"
        for tag in sorted(by_tag.keys()):
            index_content += f"- **{tag}**\n"
            for p in by_tag[tag]:
                index_content += f"  - [[{p['name']}]]\n"
        index_content += "\n"

    index_content += "### All Pages\n\n"
    for p in pages:
        index_content += f"- [[{p['name']}]]"
        if p["summary"]:
            index_content += f" — {p['summary']}"
        index_content += "\n"

    index_content += f"\n---\n*Generated: {datetime.now().isoformat()}*"

    return index_content


def generate_log(wiki_dir: Path = None, log_file: Path = None) -> str:
    """Generate log.md with chronological activity."""
    wiki_dir = wiki_dir or WIKI_DIR

    events = []

    for md_file in list_files(wiki_dir, "*.md"):
        content = read_file(md_file)
        if not content:
            continue

        fm = extract_frontmatter(content)

        created = fm.get("created", fm.get("date", ""))
        updated = fm.get("updated", fm.get("last_updated", ""))
        source = fm.get("source", "")

        events.append(
            {
                "file": md_file.name,
                "created": created,
                "updated": updated,
                "source": source,
                "title": fm.get("title", md_file.stem),
            }
        )

    events.sort(key=lambda e: e["updated"] or e["created"], reverse=True)

    log_content = """# Wiki Log

Chronological record of wiki activity.

## Recent Activity

"""

    for e in events[:50]:
        date = e["updated"] or e["created"] or "unknown"
        log_content += f"## [{date[:10]}] {e['file']}\n"
        log_content += f"- Title: {e['title']}\n"
        if e["source"]:
            log_content += f"- Source: {e['source']}\n"
        log_content += "\n"

    log_content += f"\n---\n*Generated: {datetime.now().isoformat()}*"

    return log_content


def update_index_and_log(wiki_dir: Path = None, log_dir: Path = None):
    """Update both index.md and log.md."""
    wiki_dir = wiki_dir or WIKI_DIR
    log_dir = log_dir or WIKI_DIR

    index_content = generate_index(wiki_dir)
    index_file = Path(log_dir) / "index.md"
    index_file.write_text(index_content)
    print(f"Updated: {index_file}")

    log_content = generate_log(wiki_dir)
    log_file = Path(log_dir) / "log.md"
    log_file.write_text(log_content)
    print(f"Updated: {log_file}")


if __name__ == "__main__":
    update_index_and_log()

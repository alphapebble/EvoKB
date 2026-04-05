"""Provenance tracking for wiki content."""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from evokb.core.config import WIKI_DIR
from evokb.core.utils import ensure_dir, read_file


PROVENANCE_FILE = WIKI_DIR / "provenance.json"


def load_provenance() -> Dict:
    """Load provenance records."""
    if not PROVENANCE_FILE.exists():
        return {"records": [], "by_file": {}}
    try:
        return json.loads(PROVENANCE_FILE.read_text())
    except:
        return {"records": [], "by_file": {}}


def save_provenance(data: Dict):
    """Save provenance records."""
    ensure_dir(WIKI_DIR)
    PROVENANCE_FILE.write_text(json.dumps(data, indent=2))


def track_source(
    file_name: str,
    source: str,
    source_type: str = "file",
    content_hash: str = None,
    query: str = None,
):
    """Track source of wiki content."""
    data = load_provenance()

    record = {
        "file": file_name,
        "source": source,
        "source_type": source_type,
        "content_hash": content_hash,
        "query": query,
        "tracked_at": datetime.now().isoformat(),
    }

    data["records"].append(record)
    data["by_file"][file_name] = record

    save_provenance(data)
    return record


def get_provenance(file_name: str) -> Optional[Dict]:
    """Get provenance for a specific file."""
    data = load_provenance()
    return data["by_file"].get(file_name)


def get_all_provenance() -> List[Dict]:
    """Get all provenance records."""
    data = load_provenance()
    return data.get("records", [])


def link_query_to_file(file_name: str, query: str):
    """Link a query that led to content creation."""
    data = load_provenance()

    if file_name in data["by_file"]:
        data["by_file"][file_name]["query"] = query
        data["by_file"][file_name]["derived_from_query_at"] = datetime.now().isoformat()

    save_provenance(data)


def print_provenance_report():
    """Print provenance report."""
    records = get_all_provenance()

    print("\n" + "=" * 60)
    print("PROVENANCE REPORT")
    print("=" * 60)
    print(f"Total tracked: {len(records)} files\n")

    by_type = {}
    for r in records:
        t = r.get("source_type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1

    print("By source type:")
    for t, count in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  - {t}: {count}")

    print("\nRecent records:")
    for r in records[-10:]:
        print(f"  - {r['file']} <- {r['source']} ({r.get('source_type', '?')})")

    print()


if __name__ == "__main__":
    print_provenance_report()

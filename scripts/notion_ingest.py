"""
EvoKB Notion Integration

Imports from Notion (already labeled/classified).
Better than Gmail since Notion already organizes content.

Usage:
    python scripts/notion_ingest.py --database <database_id>
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

try:
    from notion_client import Client

    NOTION_AVAILABLE = True
except ImportError:
    NOTION_AVAILABLE = False

RAW_DIR = Path("raw")


def get_notion_client():
    """Get Notion client with API key."""
    if not NOTION_AVAILABLE:
        raise ImportError("notion-client not installed. Run: pip install notion")

    api_key = os.environ.get("NOTION_API_KEY")
    if not api_key:
        raise Exception("NOTION_API_KEY not set")

    return Client(auth=api_key)


def extract_page_content(page: Dict) -> Dict:
    """Extract content from Notion page."""
    result = {
        "title": "Untitled",
        "content": "",
        "url": page.get("url", ""),
        "created_time": page.get("created_time", ""),
        "last_edited": page.get("last_edited_time", ""),
    }

    # Get title from properties
    props = page.get("properties", {})
    for prop_name, prop in props.items():
        if prop.get("type") == "title":
            title_text = prop.get("title", [])
            if title_text:
                result["title"] = title_text[0].get("plain_text", "Untitled")
            break

    # If no title property, try first rich_text
    if result["title"] == "Untitled":
        for prop_name, prop in props.items():
            if prop.get("type") == "rich_text":
                rt = prop.get("rich_text", [])
                if rt:
                    result["title"] = rt[0].get("plain_text", "Untitled")
                    break

    return result


def fetch_database(
    client, database_id: str, filter_tags: List[str] = None
) -> List[Dict]:
    """Fetch pages from Notion database."""
    query = {"page_size": 100}

    # Could add filtering by tags
    if filter_tags:
        query["filter"] = {
            "and": [
                {"property": "Tags", "multi_select": {"contains": tag}}
                for tag in filter_tags
            ]
        }

    results = client.databases.query(database_id=database_id, **query)

    pages = []
    for page in results.get("results", []):
        page_data = extract_page_content(page)

        # Get page blocks (content)
        try:
            blocks = client.blocks.children.list(block_id=page["id"])
            content_parts = []

            for block in blocks.get("results", []):
                block_type = block.get("type")
                block_data = block.get(block_type, {})

                if block_type == "paragraph":
                    text = block_data.get("rich_text", [])
                    if text:
                        content_parts.append(text[0].get("plain_text", ""))
                elif block_type == "heading_1":
                    text = block_data.get("rich_text", [])
                    if text:
                        content_parts.append(f"# {text[0].get('plain_text', '')}")
                elif block_type == "heading_2":
                    text = block_data.get("rich_text", [])
                    if text:
                        content_parts.append(f"## {text[0].get('plain_text', '')}")
                elif block_type == "heading_3":
                    text = block_data.get("rich_text", [])
                    if text:
                        content_parts.append(f"### {text[0].get('plain_text', '')}")
                elif block_type == "bulleted_list_item":
                    text = block_data.get("rich_text", [])
                    if text:
                        content_parts.append(f"- {text[0].get('plain_text', '')}")
                elif block_type == "code":
                    text = block_data.get("rich_text", [])
                    lang = block_data.get("language", "")
                    if text:
                        content_parts.append(
                            f"```{lang}\n{text[0].get('plain_text', '')}\n```"
                        )

            page_data["content"] = "\n\n".join(content_parts)
        except Exception as e:
            page_data["content"] = f"Could not fetch content: {e}"

        pages.append(page_data)

    return pages


def save_as_raw(pages: List[Dict], source: str = "notion"):
    """Save Notion pages as raw markdown."""
    RAW_DIR.mkdir(exist_ok=True)

    saved = 0
    for page in pages:
        # Create filename from title
        safe_title = page["title"].lower()
        safe_title = "".join(c if c.isalnum() or c in "- " else "" for c in safe_title)
        safe_title = safe_title.strip().replace(" ", "-")[:50]

        if not safe_title:
            safe_title = "untitled"

        filename = f"notion__{safe_title}.md"

        content = f"""---
source: notion
url: {page["url"]}
created: {page["created_time"]}
updated: {page["last_edited"]}
---

# {page["title"]}

{page["content"]}

---
Imported from Notion on {datetime.now().isoformat()}
"""

        out_path = RAW_DIR / filename
        out_path.write_text(content)
        saved += 1
        print(f"  ✓ {filename}")

    return saved


def run_notion_ingest(database_id: str = None, filter_tags: List[str] = None):
    """Main Notion ingest function."""
    print("📝 EvoKB Notion Ingest")
    print("=" * 40)

    if not NOTION_AVAILABLE:
        print("ERROR: Notion client not installed")
        print("Run: pip install notion")
        return

    # Get database ID
    if not database_id:
        database_id = os.environ.get("NOTION_DATABASE_ID")

    if not database_id:
        print("ERROR: No database ID")
        print("Set NOTION_DATABASE_ID env var or pass --database")
        print("\nSetup:")
        print("1. Get Notion API key: https://www.notion.so/my-integrations")
        print("2. Share a database with your integration")
        print("3. Copy database ID from URL")
        return

    print(f"Database: {database_id}")
    if filter_tags:
        print(f"Filter tags: {filter_tags}")

    try:
        client = get_notion_client()
        pages = fetch_database(client, database_id, filter_tags)
        print(f"Found {len(pages)} pages")

        if pages:
            saved = save_as_raw(pages)
            print(f"\n✓ Saved {saved} pages to raw/")
        else:
            print("No pages found")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Notion Ingest")
    parser.add_argument("--database", help="Notion database ID")
    parser.add_argument("--tags", help="Comma-separated tags to filter")

    args = parser.parse_args()

    tags = args.tags.split(",") if args.tags else None
    run_notion_ingest(args.database, tags)

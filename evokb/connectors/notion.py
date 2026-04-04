#!/usr/bin/env python3
"""Notion connector for EvoKB."""

from scripts.notion_ingest import run_notion_ingest

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Notion Ingest")
    parser.add_argument("--database", help="Notion database ID")
    parser.add_argument("--tags", help="Comma-separated tags to filter")

    args = parser.parse_args()

    tags = args.tags.split(",") if args.tags else None
    run_notion_ingest(args.database, tags)

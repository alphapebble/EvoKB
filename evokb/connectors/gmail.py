#!/usr/bin/env python3
"""Gmail connector for EvoKB."""

from scripts.gmail_ingest import run_gmail_ingest

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Gmail Ingest")
    parser.add_argument(
        "--labels", default="newsletter,tech", help="Comma-separated labels"
    )
    parser.add_argument("--search", help="Gmail search query")
    parser.add_argument("--max", type=int, default=50, help="Max emails")

    args = parser.parse_args()

    labels = args.labels.split(",") if args.labels else None
    run_gmail_ingest(labels, args.search, args.max)

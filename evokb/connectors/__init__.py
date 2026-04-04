"""
EvoKB Connectors - Data ingestion from external sources

Connectors:
- gmail: Extract newsletters and tech articles
- notion: Import from Notion databases
- web: Scrape URLs
"""

from .gmail import fetch_emails, run_gmail_ingest
from .notion import fetch_database, run_notion_ingest

__all__ = [
    "fetch_emails",
    "run_gmail_ingest",
    "fetch_database",
    "run_notion_ingest",
]

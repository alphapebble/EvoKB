"""
EvoKB Connectors - Data ingestion from external sources

Available Connectors:
- gmail: Extract newsletters and tech articles from Gmail
- notion: Import from Notion databases
- slack: Import from Slack channels
- discord: Import from Discord channels
- web: Scrape URLs (see evokb.ingest.scraper)
"""

from .gmail import run_gmail_ingest, fetch_emails, get_gmail_service
from .notion import run_notion_ingest
from .slack import run_slack_ingest
from .discord import run_discord_ingest

__all__ = [
    "run_gmail_ingest",
    "fetch_emails",
    "get_gmail_service",
    "run_notion_ingest",
    "run_slack_ingest",
    "run_discord_ingest",
]

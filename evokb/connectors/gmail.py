"""Gmail connector for EvoKB - Newsletter & Tech Article Extraction.

This module provides Gmail integration for extracting newsletters and tech articles.

Setup:
1. Go to https://console.cloud.google.com
2. Enable Gmail API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download credentials as credentials.json
5. Run the OAuth flow once

Usage:
    from evokb.connectors.gmail import run_gmail_ingest
    run_gmail_ingest(labels=["newsletter", "tech"])
"""

import base64
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from evokb.core.config import GMAIL_CONFIG, RAW_DIR
from evokb.core.utils import ensure_dir

try:
    from google.auth import credentials
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    build = None

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_FILE = Path("gmail_token.json")
CREDENTIALS_FILE = Path("credentials.json")


def get_gmail_service() -> Optional[Any]:
    """Authenticate with Gmail API using OAuth2."""
    if not GMAIL_AVAILABLE:
        print("[ERROR] google-api-python-client not installed")
        print("[INFO] Run: pip install google-api-python-client google-auth-oauthlib")
        return None

    creds = None

    # Load existing token
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_info(
            json.loads(TOKEN_FILE.read_text()), SCOPES
        )

    # Check if credentials are valid
    if creds and creds.valid:
        return build("gmail", "v1", credentials=creds)

    # Need to run OAuth flow
    if not CREDENTIALS_FILE.exists():
        print("[ERROR] credentials.json not found")
        print("[INFO] Download OAuth credentials from Google Cloud Console")
        print("[INFO] https://console.cloud.google.com/apis/credentials")
        return None

    # Run OAuth flow
    try:
        flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
        creds = flow.run_local_server(port=8080)

        # Save token for future use
        TOKEN_FILE.write_text(json.dumps(json.loads(creds.to_json())))

        return build("gmail", "v1", credentials=creds)
    except Exception as e:
        print(f"[ERROR] OAuth failed: {e}")
        return None


def extract_email_content(message: Dict) -> Optional[Dict]:
    """Extract content from email payload."""
    payload = message.get("payload", {})
    headers = payload.get("headers", {})

    subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "")
    sender = next((h["value"] for h in headers if h["name"].lower() == "from"), "")

    body = ""
    if "parts" in payload:
        for part in payload["parts"]:
            if part.get("mimeType") == "text/plain":
                body_data = part.get("body", {}).get("data", "")
                if body_data:
                    try:
                        body = base64.urlsafe_b64decode(body_data).decode("utf-8")
                    except Exception:
                        pass
                    break

    if not body:
        body_data = payload.get("body", {}).get("data", "")
        if body_data:
            try:
                body = base64.urlsafe_b64decode(body_data).decode("utf-8")
            except Exception:
                pass

    if not body:
        return None

    body = re.sub(r"\s+", " ", body)
    body = body[:15000]

    if len(body.strip()) < 100:
        return None

    return {
        "subject": subject,
        "sender": sender,
        "body": body,
        "date": message.get("internalDate"),
    }


def is_newsletter_tech(email: Dict) -> bool:
    """Check if email is newsletter or tech content."""
    subject = email.get("subject", "").lower()
    sender = email.get("sender", "").lower()

    patterns = [
        "newsletter",
        "digest",
        "weekly",
        "monthly",
        "tech",
        "engineering",
        "dev",
    ]
    domains = [
        "techcrunch",
        "wired",
        "theverge",
        "ars technica",
        "hackernews",
        "producthunt",
        "dev.to",
        "substack",
        "latesthacking",
        "krebsonsecurity",
    ]

    return any(p in subject for p in patterns) or any(d in sender for d in domains)


def fetch_emails(
    service, query: str = "label:INBOX", max_results: int = 50
) -> List[Dict]:
    """Fetch emails matching query."""
    results = (
        service.users()
        .messages()
        .list(userId="me", q=query, maxResults=max_results)
        .execute()
    )

    messages = results.get("messages", [])
    emails = []

    for msg in messages:
        try:
            msg_data = (
                service.users()
                .messages()
                .get(userId="me", id=msg["id"], format="full")
                .execute()
            )

            email = extract_email_content(msg_data)
            if email and is_newsletter_tech(email):
                emails.append(email)
        except Exception:
            continue

    return emails


def save_as_markdown(emails: List[Dict], raw_dir: Path = None) -> int:
    """Save extracted emails as markdown files."""
    raw_dir = raw_dir or RAW_DIR
    ensure_dir(raw_dir)

    saved = 0
    for email in emails:
        safe_subject = re.sub(r"[^a-z0-9]", "-", email["subject"].lower())[:50]
        safe_subject = re.sub(r"-+", "-", safe_subject).strip("-")
        filename = f"gmail__{safe_subject}.md"

        content = f"""---
source: gmail
sender: "{email["sender"]}"
date: "{email.get("date", "")}"
type: newsletter
extracted: "{datetime.now().isoformat()}"
---

# {email["subject"]}

{email["body"]}

---
Extracted by EvoKB Gmail Connector
"""

        out_path = raw_dir / filename
        out_path.write_text(content)
        saved += 1
        print(f"[INFO] Saved: {filename}")

    return saved


def run_gmail_ingest(
    labels: List[str] = None,
    search: str = None,
    max_results: int = 50,
    raw_dir: Path = None,
    config: Dict = None,
) -> int:
    """Run Gmail ingestion.

    Args:
        labels: Gmail labels to filter (e.g., ["newsletter", "tech"])
        search: Custom Gmail search query
        max_results: Maximum emails to fetch
        raw_dir: Output directory (default: RAW_DIR)
        config: Configuration dict (default: GMAIL_CONFIG)

    Returns:
        Number of emails saved
    """
    config = config or GMAIL_CONFIG

    if not config.get("enabled", False):
        print(
            "[INFO] Gmail connector not enabled. Set connectors.gmail.enabled: true in config.yaml"
        )
        return 0

    if not GMAIL_AVAILABLE:
        print("[ERROR] Google libraries not installed")
        print("[INFO] pip install google-api-python-client google-auth-oauthlib")
        return 0

    if search:
        query = search
    elif labels:
        query = f"label:{labels[0]}"
    else:
        label_list = config.get("labels", ["newsletter", "tech"])
        query = f"label:{label_list[0]}"

    print(f"[GMAIL] Query: {query}")
    print("[GMAIL] Fetching emails...")

    service = get_gmail_service()
    if not service:
        return 0

    try:
        emails = fetch_emails(service, query, max_results)
        print(f"[GMAIL] Found {len(emails)} matching emails")

        if emails:
            saved = save_as_markdown(emails, raw_dir)
            print(f"[GMAIL] Saved {saved} emails to raw/")
            return saved
        else:
            print("[GMAIL] No matching emails found")
            return 0

    except Exception as e:
        print(f"[ERROR] Gmail fetch failed: {e}")
        return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Gmail Ingest for EvoKB")
    parser.add_argument("--labels", default="newsletter", help="Comma-separated labels")
    parser.add_argument("--search", help="Gmail search query")
    parser.add_argument("--max", type=int, default=50, help="Max results")
    parser.add_argument("--setup", action="store_true", help="Run OAuth setup")

    args = parser.parse_args()

    if args.setup:
        get_gmail_service()
    else:
        labels = args.labels.split(",") if args.labels else None
        run_gmail_ingest(labels, args.search, args.max)

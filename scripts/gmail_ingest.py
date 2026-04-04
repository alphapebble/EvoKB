"""
EvoKB Gmail Integration - Newsletter & Tech Article Extraction

Extracts content from Gmail emails (newsletters, tech articles only).
Privacy-conscious: only extracts text content, not metadata.

Usage:
    python scripts/gmail_ingest.py --labels newsletter,tech
    python scripts/gmail_ingest.py --search "subject:newsletter"
"""

import os
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

try:
    import google.auth
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials

    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

RAW_DIR = Path("raw")
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_gmail_service():
    """Authenticate with Gmail API."""
    if not GOOGLE_AVAILABLE:
        raise ImportError(
            "google-api-python-client not installed. Run: pip install google-api-python-client"
        )

    creds = None

    # Check for token.json (from OAuth)
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_info(
            json.load(open("token.json")), SCOPES
        )

    # Check for GITHUB_TOKEN as alternative (service account or PAT)
    if not creds and os.environ.get("GITHUB_TOKEN"):
        # Can't use GITHUB_TOKEN for Gmail - just for GitHub
        pass

    if not creds:
        raise Exception("No credentials. Run OAuth flow or set up service account.")

    return build("gmail", "v1", credentials=creds)


def extract_newsletter_content(message: Dict) -> Optional[Dict]:
    """Extract content from newsletter/tech article email."""
    payload = message.get("payload", {})
    headers = payload.get("headers", {})

    # Get subject
    subject = ""
    for h in headers:
        if h["name"].lower() == "subject":
            subject = h["value"]
            break

    # Get from
    sender = ""
    for h in headers:
        if h["name"].lower() == "from":
            sender = h["value"]
            break

    # Extract body
    body = ""
    if "parts" in payload:
        for part in payload["parts"]:
            if part.get("mimeType") == "text/plain":
                body = part.get("body", {}).get("data", "")
                break

    if not body:
        body = payload.get("body", {}).get("data", "")

    # Decode base64
    if body:
        import base64

        try:
            body = base64.urlsafe_b64decode(body).decode("utf-8")
        except:
            pass

    # Clean content
    body = re.sub(r"\s+", " ", body)  # Normalize whitespace
    body = body[:10000]  # Limit length

    if len(body) < 100:  # Too short
        return None

    return {
        "subject": subject,
        "sender": sender,
        "body": body,
        "date": message.get("internalDate"),
    }


def is_newsletter_tech(email: Dict) -> bool:
    """Check if email is a newsletter or tech article."""
    subject = email.get("subject", "").lower()
    sender = email.get("sender", "").lower()

    # Newsletter patterns
    newsletter_patterns = [
        "newsletter",
        "digest",
        "weekly",
        "monthly",
        "tech",
        "engineering",
        "dev",
        "ai",
    ]

    # Tech sender domains
    tech_domains = [
        "techcrunch",
        "wired",
        "theverge",
        "ars technica",
        "hackernews",
        "producthunt",
        "dev.to",
        "substack.com",
    ]

    subject_match = any(p in subject for p in newsletter_patterns)
    sender_match = any(d in sender for d in tech_domains)

    return subject_match or sender_match


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
        msg_data = (
            service.users()
            .messages()
            .get(userId="me", id=msg["id"], format="full")
            .execute()
        )

        email = extract_newsletter_content(msg_data)
        if email and is_newsletter_tech(email):
            emails.append(email)

    return emails


def save_as_raw(emails: List[Dict], source: str = "gmail"):
    """Save extracted emails as raw markdown."""
    RAW_DIR.mkdir(exist_ok=True)

    saved = 0
    for email in emails:
        # Create filename from subject
        safe_subject = re.sub(r"[^a-z0-9]", "-", email["subject"].lower())[:50]
        filename = f"gmail__{safe_subject}.md"

        content = f"""---
source: gmail
sender: {email["sender"]}
date: {email["date"]}
type: newsletter
---

# {email["subject"]}

{email["body"]}

---
Extracted from Gmail on {datetime.now().isoformat()}
"""

        out_path = RAW_DIR / filename
        out_path.write_text(content)
        saved += 1
        print(f"  ✓ {filename}")

    return saved


def run_gmail_ingest(
    labels: List[str] = None, search: str = None, max_results: int = 50
):
    """Main Gmail ingest function."""
    print("📧 EvoKB Gmail Ingest")
    print("=" * 40)

    if not GOOGLE_AVAILABLE:
        print("ERROR: Google API not installed")
        print("Run: pip install google-api-python-client")
        return

    # Build query
    if search:
        query = search
    elif labels:
        query = f"label:{labels[0]}"
    else:
        query = "label:INBOX"

    print(f"Query: {query}")

    try:
        service = get_gmail_service()
        emails = fetch_emails(service, query, max_results)
        print(f"Found {len(emails)} newsletter/tech emails")

        if emails:
            saved = save_as_raw(emails)
            print(f"\n✓ Saved {saved} emails to raw/")
        else:
            print("No matching emails found")

    except Exception as e:
        print(f"Error: {e}")
        print("\nSetup:")
        print("1. Go to https://console.cloud.google.com")
        print("2. Enable Gmail API")
        print("3. Create OAuth credentials")
        print(
            "4. Run: python -c 'from scripts.gmail_ingest import get_gmail_service; get_gmail_service()'"
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Gmail Ingest")
    parser.add_argument("--labels", help="Comma-separated labels", default="newsletter")
    parser.add_argument("--search", help="Gmail search query")
    parser.add_argument("--max", type=int, default=50, help="Max results")

    args = parser.parse_args()

    labels = args.labels.split(",") if args.labels else None
    run_gmail_ingest(labels, args.search, args.max)

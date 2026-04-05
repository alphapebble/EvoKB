"""Tests for Gmail connector."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from evokb.connectors.gmail import (
    is_newsletter_tech,
    extract_email_content,
    save_as_markdown,
    run_gmail_ingest,
    GMAIL_AVAILABLE,
)


def test_is_newsletter_tech_newsletter_subject():
    """Test newsletter detection by subject."""
    email = {"subject": "Weekly Tech Newsletter", "sender": "someone@example.com"}
    assert is_newsletter_tech(email) is True


def test_is_newsletter_tech_tech_sender():
    """Test newsletter detection by sender domain."""
    email = {"subject": "Important Update", "sender": "newsletter@techcrunch.com"}
    assert is_newsletter_tech(email) is True


def test_is_newsletter_tech_not_matching():
    """Test non-matching email."""
    email = {"subject": "Re: Meeting", "sender": "bob@gmail.com"}
    assert is_newsletter_tech(email) is False


def test_is_newsletter_tech_substack():
    """Test substack newsletter detection."""
    email = {"subject": "Your weekly digest", "sender": "author@substack.com"}
    assert is_newsletter_tech(email) is True


@patch("evokb.connectors.gmail.GMAIL_AVAILABLE", False)
def test_gmail_not_available():
    """Test Gmail connector when libraries not installed."""
    result = run_gmail_ingest()
    assert result == 0


@patch("evokb.connectors.gmail.GMAIL_CONFIG", {"enabled": False})
def test_gmail_not_enabled():
    """Test Gmail connector when not enabled in config."""
    result = run_gmail_ingest()
    assert result == 0


def test_save_as_markdown(tmp_path):
    """Test saving emails as markdown."""
    emails = [
        {
            "subject": "Test Newsletter",
            "sender": "test@example.com",
            "body": "This is a test email body with some content.",
            "date": "1234567890",
        }
    ]

    saved = save_as_markdown(emails, tmp_path)

    assert saved == 1
    assert len(list(tmp_path.glob("*.md"))) == 1


def test_extract_email_content_no_body():
    """Test extraction with empty body."""
    message = {
        "payload": {
            "headers": [
                {"name": "Subject", "value": "Test"},
                {"name": "From", "value": "test@example.com"},
            ],
            "body": {},
        }
    }

    result = extract_email_content(message)
    assert result is None


def test_save_as_markdown_empty_list(tmp_path):
    """Test saving empty email list."""
    saved = save_as_markdown([], tmp_path)
    assert saved == 0

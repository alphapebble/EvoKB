"""Slack connector for EvoKB."""

from typing import List, Dict, Any
from pathlib import Path

from evokb.core.config import SLACK_CONFIG
from evokb.core.utils import ensure_dir, read_file


def get_slack_messages(channel: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Fetch messages from a Slack channel."""
    if not SLACK_CONFIG.get("enabled"):
        print("Slack connector not enabled in config.yaml")
        return []

    # TODO: Implement actual Slack API client
    print(f"Fetching messages from #{channel}...")
    return []


def run_slack_ingest(channels: List[str] = None) -> List[Dict[str, Any]]:
    """Ingest messages from Slack channels."""
    if not SLACK_CONFIG.get("enabled"):
        print(
            "Slack connector not enabled. Set connectors.slack.enabled: true in config.yaml"
        )
        return []

    channels = channels or SLACK_CONFIG.get("channels", ["general"])
    all_messages = []

    for channel in channels:
        messages = get_slack_messages(channel)
        all_messages.extend(messages)

        for msg in messages:
            file_path = Path("raw") / f"slack_{channel}_{msg.get('ts')}.md"
            content = f"""# Slack: #{channel}

**User:** {msg.get("user")}
**Time:** {msg.get("ts")}

{msg.get("text")}
"""
            file_path.write_text(content)

    print(f"Imported {len(all_messages)} Slack messages")
    return all_messages


if __name__ == "__main__":
    run_slack_ingest()

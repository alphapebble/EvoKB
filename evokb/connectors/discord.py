"""Discord connector for EvoKB."""

from typing import List, Dict, Any
from pathlib import Path

from evokb.core.config import DISCORD_CONFIG
from evokb.core.utils import ensure_dir


def get_discord_messages(channel_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Fetch messages from a Discord channel."""
    if not DISCORD_CONFIG.get("enabled"):
        print("Discord connector not enabled in config.yaml")
        return []

    # TODO: Implement actual Discord API client
    print(f"Fetching messages from channel {channel_id}...")
    return []


def run_discord_ingest(channel_ids: List[str] = None) -> List[Dict[str, Any]]:
    """Ingest messages from Discord channels."""
    if not DISCORD_CONFIG.get("enabled"):
        print(
            "Discord connector not enabled. Set connectors.discord.enabled: true in config.yaml"
        )
        return []

    channel_ids = channel_ids or DISCORD_CONFIG.get("channels", [])
    all_messages = []

    for channel_id in channel_ids:
        messages = get_discord_messages(channel_id)
        all_messages.extend(messages)

        for msg in messages:
            file_path = Path("raw") / f"discord_{channel_id}_{msg.get('id')}.md"
            content = f"""# Discord

**Author:** {msg.get("author")}
**Time:** {msg.get("timestamp")}

{msg.get("content")}
"""
            file_path.write_text(content)

    print(f"Imported {len(all_messages)} Discord messages")
    return all_messages


if __name__ == "__main__":
    run_discord_ingest()

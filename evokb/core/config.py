from pathlib import Path
import os
import yaml
from typing import Any, Dict

CONFIG_FILE = Path("config.yaml")


def load_config() -> Dict[str, Any]:
    """Load config from YAML file with env var overrides."""
    if not CONFIG_FILE.exists():
        return {}

    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f) or {}


_config = load_config()

MODEL = os.environ.get("MODEL", _config.get("model", "ollama/llama3.2"))
OLLAMA_BASE_URL = os.environ.get(
    "OLLAMA_BASE_URL", _config.get("ollama_base_url", "http://localhost:11434")
)
CHECK_INTERVAL = _config.get("check_interval", 8)
RAW_DIR = Path(_config.get("raw_dir", "raw"))
WIKI_DIR = Path(_config.get("wiki_dir", "wiki"))
CLUSTERS_DIR = Path(_config.get("clusters_dir", "clusters"))
PROGRAM_MD = Path(_config.get("schema_file", "EVOKB_SCHEMA.md"))

# Connector configs
GMAIL_CONFIG = _config.get("connectors", {}).get("gmail", {})
NOTION_CONFIG = _config.get("connectors", {}).get("notion", {})
SLACK_CONFIG = _config.get("connectors", {}).get("slack", {})
DISCORD_CONFIG = _config.get("connectors", {}).get("discord", {})

# Ingest settings
INGEST_CONFIG = _config.get("ingest", {})
FILE_TYPES = INGEST_CONFIG.get("file_types", [".md", ".txt", ".pdf"])
URL_PATTERNS = INGEST_CONFIG.get("url_patterns", [])

# Search settings
SEARCH_CONFIG = _config.get("search", {})
USE_TANTIVY = SEARCH_CONFIG.get("use_tantivy", False)

# Eval settings
EVAL_CONFIG = _config.get("eval", {})
LINT_ON_INGEST = EVAL_CONFIG.get("lint_on_ingest", True)
MIN_QUALITY_SCORE = EVAL_CONFIG.get("min_quality_score", 0.7)

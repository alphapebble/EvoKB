from pathlib import Path
import os

MODEL = os.environ.get("MODEL", "ollama/llama3.2")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
CHECK_INTERVAL = 8
RAW_DIR = Path("raw")
WIKI_DIR = Path("wiki")
CLUSTERS_DIR = Path("clusters")
PROGRAM_MD = Path("program.md")

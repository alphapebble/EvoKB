# EvoKB — Evolving Knowledge Base

**Self-evolving Markdown-first knowledge base** powered by an **autoresearch-style LLM librarian**.

Drop raw documents (notes, papers, web clips) into the `raw/` folder. The librarian reads `program.md` and proposes improvements to the `wiki/` folder — summaries, backlinks, structure, and connections.

Inspired by Andrej Karpathy's LLM Knowledge Base vision and his autoresearch loop.

## Features
- Plain Markdown as the single source of truth (fully editable in Obsidian or VS Code)
- Autoresearch-style agent loop (propose → evaluate → apply)
- Monte Carlo evidence sampling for smart retrieval
- Local-first (Ollama by default)
- Lightweight — no heavy vector DB required
- File watcher for automatic processing
- Knowledge clusters for smart retrieval

## Architecture

```
evokb/
├── raw/              # Drop papers, web clips, notes here
├── wiki/             # LLM-compiled clean Markdown wiki (source of truth)
├── clusters/         # Evolving Knowledge Clusters (DuckDB)
├── program.md        # Librarian instructions (human + agent editable)
├── src/
│   ├── __init__.py
│   ├── config.py     # Configuration
│   ├── librarian.py # Main file watcher + entry point
│   ├── retriever.py # Autoresearch loop + Monte Carlo sampling
│   ├── cluster.py   # Knowledge Cluster class + DuckDB store
│   └── utils.py     # File utilities
└── pyproject.toml
```

## Quick Start

```bash
git clone https://github.com/alphapebble/EvoKB.git
cd EvoKB

uv venv
source .venv/bin/activate

uv pip install -e .

mkdir -p raw wiki clusters

evokb
```

## Usage

### Start the Librarian

```bash
evokb
```

The librarian runs an autoresearch-style loop:
1. Reads `program.md` for instructions
2. Scans `raw/` for new documents
3. Proposes improvements to `wiki/`
4. Uses Monte Carlo sampling for retrieval

### Query the Knowledge Base

```python
from src.retriever import query_evo_kb

answer, cluster = query_evo_kb("your question here")
print(answer)
```

## Configuration

Edit `src/config.py` to change settings:

```python
MODEL = "ollama/llama3.2"
CHECK_INTERVAL = 8
```

Edit `program.md` to customize the librarian's behavior.

## Contributing

Contributions welcome!

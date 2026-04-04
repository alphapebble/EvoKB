# EvoKB — Evolving Knowledge Base

A lightweight, self-maintaining **Context Engine** powered by an **autoresearch-style LLM librarian**.

> **Philosophy**: From "retrieve documents → answer" → to "construct context → reason"

## Architecture

```
┌──────────────┐
│ Raw Data     │  (files, emails, APIs)
└──────┬───────┘
       │
┌──────▼───────┐
│ Indexless    │  (keyword + Monte Carlo search)
│ Retrieval   │
└──────┬───────┘
       │
┌──────▼───────┐
│ Context      │  (summarize, deduplicate, filter)
│ Builder      │
└──────┬───────┘
       │
┌──────▼───────┐
│ LLM Agent    │  (reason, tool-use, memory)
└──────────────┘
```

## Features
- Plain Markdown as the single source of truth (human-editable in Obsidian/VS Code)
- Autoresearch-style agent loop: propose → evaluate → apply → improve
- **Indexless retrieval** — No vector DB, no embeddings
- **Monte Carlo evidence sampling** for smart retrieval
- Local-first (runs with Ollama by default)
- Knowledge clusters for fast, reusable answers

## Inspired By
- **Karpathy**: LLM = CPU, Context = RAM
- **NotebookLM**: AI-powered research and note-taking

## Quick Start

```bash
git clone https://github.com/alphapebble/evokb.git
cd evokb
uv venv
source .venv/bin/activate
uv pip install -e .
mkdir -p raw wiki clusters
evokb
```

## Project Structure

```
evokb/
├── raw/              # Incoming raw documents
├── wiki/             # Clean, evolving knowledge base
├── clusters/         # Knowledge clusters for fast retrieval
├── program.md        # Librarian instructions
├── evokb/
│   ├── __init__.py
│   ├── config.py
│   ├── librarian.py  # Main agent loop
│   ├── retriever.py  # Indexless search + Monte Carlo
│   ├── evaluator.py  # Score changes
│   ├── cluster.py    # Knowledge clusters
│   └── utils.py
├── tests/            # Test suite
├── BUILD_GUIDE.md   # Production-grade build guide
└── pyproject.toml
```

## Usage

### Start the Librarian

```bash
evokb
```

### Query the Knowledge Base

```python
from evokb import query_evo_kb, search_kb, index_wiki

# Search using Tantivy
results = search_kb("your question here")
print(results)

# Or use the full retriever with LLM
answer, cluster = query_evo_kb("your question here")
print(answer)
```

## Documentation

- [BUILD_GUIDE.md](BUILD_GUIDE.md) — Step-by-step production-grade guide

## Roadmap

- [x] Tantivy search integration
- [x] Context builder layer
- [x] Agent classifier
- [x] FastAPI backend
- [x] Docker support

## Contributing

Contributions welcome!

## License

MIT License

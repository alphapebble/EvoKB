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

## Quick Start

```bash
git clone https://github.com/alphapebble/evokb.git
cd evokb
uv venv
source .venv/bin/activate
uv pip install -e .
mkdir -p raw wiki clusters
python -m evokb.agents.librarian
```

## Project Structure

```
evokb/
├── raw/              # Incoming raw documents
├── wiki/             # Clean, evolving knowledge base
├── clusters/         # Knowledge clusters for fast retrieval
├── EVOKB_SCHEMA.md   # Agent schema
├── evokb/
│   ├── __init__.py
│   ├── api.py        # FastAPI server
│   ├── core/         # Core utilities (config, utils, retriever, router, search, context)
│   ├── agents/       # Agent implementations (agent, librarian, hermes)
│   ├── memory/       # Memory/cluster store
│   ├── eval/         # Evaluation metrics
│   ├── reporting/    # Reporting dashboard
│   ├── connectors/   # External integrations (gmail, notion)
│   └── ingest/       # Data ingestion (scraper, schema_evolution)
├── tests/            # Test suite (99 tests)
├── scripts/          # Pipeline scripts
└── pyproject.toml
```

## Usage

### Start the Librarian

```bash
python -m evokb.agents.librarian
```

### Query the Knowledge Base

```python
from evokb.core.retriever import query_evo_kb
from evokb.core.search import search_kb, index_wiki

# Search using keyword-based search
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
- [ ] Audio Overviews (AI-generated podcasts from wiki)
- [ ] TTS (Text-to-Speech for wiki content)

## Contributing

Contributions welcome!

## License

MIT License

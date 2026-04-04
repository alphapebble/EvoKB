# EvoKB — Evolving Knowledge Base

A lightweight, self-maintaining Markdown-first knowledge base powered by an **autoresearch-style LLM librarian**.

Drop raw documents (notes, papers, web clips) into `raw/`. The librarian automatically compiles them into clean, interlinked wiki pages in `wiki/`, creates backlinks, summaries, and evolves the knowledge over time.

**Inspired by** Andrej Karpathy's LLM Knowledge Base vision and his autoresearch loop.

## Features
- Plain Markdown as the single source of truth (human-editable in Obsidian/VS Code)
- Autoresearch-style agent loop: propose → apply → evaluate → improve
- Local-first (runs with Ollama by default)
- No heavy vector DB or complex RAG at the core
- Easy to extend with your own data

## Quick Start

```bash
# 1. Clone & setup
git clone https://github.com/alphapebble/evokb.git
cd evokb
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Install dependencies
uv pip install -e .

# 3. Put your documents in raw/
mkdir -p raw wiki clusters

# 4. Run the librarian
evokb
# or: python -m src.librarian
```

Drop Markdown/PDF/TXT files into `raw/` and watch the librarian work.

## Project Structure

```
evokb/
├── raw/              # Incoming raw documents
├── wiki/             # Clean, evolving knowledge base (edit manually too)
├── clusters/         # Knowledge clusters for fast retrieval
├── program.md        # Instructions that guide the librarian (you + agent can edit)
├── src/              # Core Python code
│   ├── __init__.py
│   ├── config.py
│   ├── librarian.py
│   ├── retriever.py
│   ├── cluster.py
│   └── utils.py
├── pyproject.toml
└── README.md
```

## Usage

### Start the Librarian

```bash
evokb
```

The librarian runs an autoresearch-style loop that:
1. Reads `program.md` for instructions
2. Scans `raw/` for new documents
3. Proposes improvements to `wiki/`
4. Creates backlinks and connections between pages

### Query the Knowledge Base

```python
from src.retriever import query_evo_kb

answer, cluster = query_evo_kb("your question here")
print(answer)
```

## Roadmap

- Safe change application + evaluation loop
- Knowledge Cluster evolution
- Better PDF support
- Obsidian plugin / simple web UI

## Contributing

Contributions welcome! Please open an issue or PR on GitHub.

## License

MIT License

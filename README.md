# EvoKB — Evolving Knowledge Base

**Self-evolving Markdown-first knowledge base** powered by an **autoresearch-style LLM librarian**.

Drop raw documents (notes, papers, web clips) into the `raw/` folder. The librarian reads `program.md` and proposes improvements to the `wiki/` folder — summaries, backlinks, structure, and connections.

Inspired by Andrej Karpathy's LLM Knowledge Base vision and the Sirchmunk retrieval architecture.

## Features
- Plain Markdown as the single source of truth (fully editable in Obsidian or VS Code)
- Autoresearch-style agent loop
- Local-first (Ollama by default)
- Lightweight — no heavy vector DB required
- File watcher for automatic processing
- Knowledge clusters for smart retrieval
- Monte Carlo-style evidence sampling

## Architecture

```
evokb/
├── raw/              # Drop papers, web clips, notes here
├── wiki/             # LLM-compiled clean Markdown wiki (source of truth)
├── clusters/         # Evolving Knowledge Clusters (DuckDB)
├── librarian.py      # Main compilation + backlink agent + file watcher
├── retriever.py      # Smart retrieval with keyword search + Monte Carlo sampling
├── cluster.py        # Knowledge Cluster class + DuckDB store
├── utils.py          # File utilities
├── program.md        # Librarian instructions
└── pyproject.toml
```

## Tech Stack

| Layer | Library | Why |
|-------|---------|-----|
| Language | Python 3.12+ | Mature ecosystem for agents |
| LLM interface | LiteLLM + Ollama | One API for local + cloud models |
| Markdown | python-frontmatter, markdown | Parse/edit Markdown with metadata |
| File watching | watchdog | Auto-trigger librarian on file changes |
| Storage | DuckDB | Lightweight cluster persistence |

## Quick Start

```bash
git clone https://github.com/alphapebble/EvoKB.git
cd EvoKB

uv venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate

uv pip install -e .

mkdir -p raw wiki clusters

python -m librarian
```

## Usage

### Start the Librarian

```bash
python -m librarian
```

Drop files into `raw/` (Markdown, PDF, TXT). The librarian automatically:
- Compiles raw documents into clean wiki pages
- Creates backlinks and connections
- Improves existing pages

### Query the Knowledge Base

```python
from retriever import query_evo_kb

answer, cluster = query_evo_kb("your question here")
print(answer)
```

## Configuration

Edit `program.md` to customize the librarian's behavior. Change the model in any Python file:

```python
MODEL = "ollama/llama3.2"   # or "groq/llama-3.3-70b-versatile"
```

## Contributing

Contributions welcome!

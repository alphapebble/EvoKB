# EvoKB — Evolving Knowledge Base

**Self-evolving Markdown-first knowledge base** powered by an **autoresearch-style LLM librarian**.

Drop raw documents (notes, papers, web clips) into the `raw/` folder. The librarian reads `program.md` and proposes improvements to the `wiki/` folder — summaries, backlinks, structure, and connections.

Inspired by Andrej Karpathy's LLM Knowledge Base vision and his autoresearch loop.

## Features
- Plain Markdown as the single source of truth (fully editable in Obsidian or VS Code)
- Autoresearch-style agent loop
- Local-first (Ollama by default)
- Lightweight — no heavy vector DB required
- File watcher for automatic processing
- Knowledge clusters for smart retrieval

## Project Structure

```
evokb/
├── raw/              # ← Drop papers, web clips, notes here
├── wiki/             # ← LLM-compiled clean Markdown wiki (source of truth)
├── clusters/         # ← Evolving Knowledge Clusters (JSON/Parquet)
├── src/
│   ├── librarian.py  # Main compilation + backlink agent
│   ├── query.py      # Smart retrieval
│   ├── linter.py     # Periodic health checks & fixes
│   └── utils.py
├── program.md        # Librarian instructions
├── config.py
├── pyproject.toml
└── .gitignore
```

## Tech Stack

| Layer | Library | Why |
|-------|---------|-----|
| Language | Python 3.12+ | Mature ecosystem, easy for agents |
| LLM interface | LiteLLM + Ollama | One API for local + cloud models |
| Markdown | python-frontmatter, markdown | Parse/edit Markdown with metadata |
| File watching | watchdog | Auto-trigger librarian on file changes |
| Storage | DuckDB | Lightweight for clusters & metadata |

## Quick Start

```bash
git clone https://github.com/alphapebble/EvoKB.git
cd EvoKB

uv venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate

uv pip install -e .

mkdir -p raw wiki clusters

python -m src.librarian
```

## Usage

1. **Start the librarian**: `python -m src.librarian`
2. **Drop files** into `raw/` (Markdown, PDF, TXT)
3. The librarian automatically:
   - Compiles raw documents into clean wiki pages
   - Creates backlinks and connections
   - Improves existing pages
   - Runs periodic linting

## Configuration

Edit `program.md` to customize the librarian's behavior:

```markdown
# EvoKB Librarian Program

You are the EvoKB Librarian — a careful, precise research assistant...
```

Change the model in `src/librarian.py`:

```python
MODEL = "ollama/llama3.2"   # or "groq/llama-3.3-70b-versatile"
```

## Contributing

Contributions welcome!

# EvoKB — Evolving Knowledge Base

**Self-evolving Markdown-first knowledge base** powered by an **autoresearch-style LLM librarian**.

Drop raw documents (notes, papers, web clips) into the `raw/` folder. The librarian reads `program.md` and proposes improvements to the `wiki/` folder — summaries, backlinks, structure, and connections.

Inspired by Andrej Karpathy's LLM Knowledge Base vision and his autoresearch loop.

## Features
- Plain Markdown as the single source of truth (fully editable in Obsidian or VS Code)
- Autoresearch-style agent loop
- Local-first (Ollama by default)
- Lightweight — no heavy vector DB required

## Project Structure

raw/ — Drop your raw documents here
wiki/ — Clean, evolving knowledge base
program.md — Instructions for the librarian (you can edit this)

## Quick Start

```bash
git clone https://github.com/alphapebble/EvoKB.git
cd EvoKB

uv venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate

uv pip install -e .

mkdir -p raw wiki

python -m .librarian
```

## Contributing

Contributions welcome!

# EvoKB Project

A self-evolving knowledge base using autoresearch loop.

## Overview
EvoKB is an open-source project that implements Karpathy's vision of an LLM-powered knowledge base.

## Features
- Markdown as single source of truth
- Autoresearch-style librarian agent
- Propose → Evaluate → Apply loop
- Local-first (Ollama by default)
- No vector DB required

## Architecture
- raw/ - incoming documents
- wiki/ - compiled knowledge base
- clusters/ - knowledge clusters (DuckDB)

## Usage
```bash
evokb  # start librarian
evokb-api  # start API server
```

## Roadmap
- Tantivy search
- Context builder
- Agent classifier
- FastAPI backend
- Docker support

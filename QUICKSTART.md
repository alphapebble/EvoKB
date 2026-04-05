# EvoKB Quick Start Guide

A step-by-step journey from zero to your first knowledge base.

---

## Step 1: Install

```bash
git clone https://github.com/alphapebble/evokb.git
cd evokb
pip install -e .
```

---

## Step 2: Configure (Optional - defaults work)

```bash
# Default config.yaml already exists with:
# - Uses Ollama (localhost:11434) with llama3.2
# - Watches raw/ folder
# - Outputs to wiki/ folder
```

**To customize:**
```bash
# Edit config.yaml
vim config.yaml

# Key settings:
#   model: "ollama/llama3.2"     # or openai/gpt-4
#   raw_dir: "raw"               # where you drop files
#   wiki_dir: "wiki"             # compiled knowledge base
```

---

## Step 3: Add Your First Source

```bash
# Option A: Drop a file
echo "# My Notes

Knowledge graphs represent information as interconnected entities.
They enable semantic search and reasoning.

Sources: https://en.wikipedia.org/wiki/Knowledge_graph
" > raw/my-first-note.md

# Option B: Scrape a URL
python -c "from evokb.ingest.scraper import scrape_url; scrape_url('https://en.wikipedia.org/wiki/Knowledge_graph')"

# Option C: Use a connector (see config.yaml)
# Set connectors.gmail.enabled: true and add API keys
```

---

## Step 4: Run the Librarian

```bash
# Start the auto-compiler
python -m evokb.agents.librarian

# You'll see:
# 🚀 EvoKB Autoresearch Librarian starting...
# 📥 New raw file: raw/my-first-note.md
# Saved wiki page: wiki/my-first-note.md
```

---

## Step 5: Query Your Knowledge Base

```python
from evokb.core.retriever import query_evo_kb

answer, cluster = query_evo_kb("What is a knowledge graph?")
print(answer)
```

Or use the API:
```bash
uvicorn evokb.api:app --reload
# Visit http://localhost:8000/docs
```

---

## Step 6: View Results

### In the wiki folder
```bash
ls wiki/
# You see compiled markdown files with frontmatter

cat wiki/my-first-note.md
# ---
# title: "My Notes"
# source: "my-first-note.md"
# created: "2026-04-05T10:00:00"
# tags: "knowledge-graph"
# summary: "Knowledge graphs represent..."
# ---
```

### Generated files
```bash
cat wiki/index.md      # Auto-generated index
cat wiki/log.md        # Activity log
cat wiki/provenance.json  # Source tracking
```

### Health check
```bash
python -m evokb.eval.lint

# Output:
# 📊 Health Score: 85/100
# --- ORPHANS ---
# None
# --- UNGROUNDED ---
# All pages have source attribution
```

---

## Complete Example

```bash
# 1. Install
git clone https://github.com/alphapebble/evokb.git
cd evokb
pip install -e .

# 2. Create directories
mkdir -p raw wiki clusters

# 3. Add a source
echo "# AI Notes

Artificial Intelligence refers to...
" > raw/ai.md

# 4. Run
python -m evokb.agents.librarian

# 5. Query
python -c "
from evokb.core.retriever import query_evo_kb
answer, _ = query_evo_kb('What is AI?')
print(answer)
"

# 6. Check health
python -m evokb.eval.lint
```

---

## Connecting External Sources

### Gmail
```yaml
# config.yaml
connectors:
  gmail:
    enabled: true
    labels: [newsletter, tech]
```
Then set `GOOGLE_CLIENT_SECRET` env var.

### Notion
```yaml
# config.yaml  
connectors:
  notion:
    enabled: true
    database_id: "your-db-id"
```
Then set `NOTION_API_KEY` env var.

---

## Troubleshooting

```bash
# Check what's in raw/
ls raw/

# Check what's in wiki/
ls wiki/

# Run tests
python -m pytest tests/ -q

# Check API
curl http://localhost:8000/health
```

---

## Next Steps

- Add more sources to `raw/`
- Connect Gmail/Notion in config.yaml
- Run the lint to check health: `python -m evokb.eval.lint`
- Query via API at http://localhost:8000/docs

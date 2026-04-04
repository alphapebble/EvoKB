# EvoKB Agent Scripts

## ingest.py
Fetches raw data from external sources (URLs, repos, APIs).

## compile.py
Compiles raw markdown → structured wiki with metadata, tags, cross-links.

## evaluate.py
Runs evaluation metrics (Q&A accuracy, search quality).

## autoreview.py
Self-improves wiki content using LLM (propose → evaluate → apply loop).

---

## Usage

```bash
# Run individual agents
python scripts/ingest.py          # Fetch new data
python scripts/compile.py         # Build wiki
python scripts/evaluate.py         # Run metrics
python run_autoreview.py          # Self-improve
```

## CI Integration

Each agent runs as a separate GitHub workflow:

| Agent | Trigger | Job |
|-------|---------|-----|
| ingest | schedule / manual | Fetch raw data |
| compile | on raw/** changes | Build wiki |
| evaluate | on PR | Run tests + metrics |
| autoreview | on push | Improve content |

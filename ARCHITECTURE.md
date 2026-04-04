# EvoKB Architecture

## Two-Layer Knowledge System

| Layer | Purpose | Storage |
|-------|---------|---------|
| **Wiki** | Deep knowledge (concepts, explanations) | Markdown files |
| **SQL Memory** | Structured data (people, projects, notes) | SQLite |

## Routing Engine

```
Query → Router → [Wiki | SQL | Search]
              ↓
         Learning Store
         (self-improves)
```

## Agent System

| Agent | Trigger | Role |
|-------|---------|------|
| **Ingest** | manual/schedule | Fetch external data |
| **Compile** | on raw/* | Build wiki from raw |
| **Test** | on push | Run tests + evaluation |
| **Autoreview** | on push | Self-improve wiki |
| **Hermes** | on push | Review & validate articles before publish |

## Hermes - The Review Gate

Hermes is the supervisor agent that sits between drafts and live knowledge:

```
Agents produce → raw/ → compiler → wiki_drafts/ → Hermes reviews → wiki (live)
                                              ↓
                                    bad articles die in drafts
                                              ↓
                                    good articles promoted to live
```

**Scoring criteria:**
- Length (too short = incomplete)
- Structure (has headers)
- Content quality (specificity, technical depth)
- Credibility (no obvious hallucinations)
- Source attribution

**Flow:**
1. Articles scored before entering permanent brain
2. High quality (≥0.7) → auto-promoted
3. Medium (0.5-0.7) → needs manual review
4. Low (<0.5) → rejected

This prevents hallucinated connections from compounding in the knowledge base.

## Connectors

External data sources via `evokb/connectors/`:

| Connector | Source | Description |
|-----------|--------|-------------|
| Gmail | Gmail API | Newsletters, tech articles |
| Notion | Notion API | Labeled databases |

```python
from evokb.connectors import run_gmail_ingest, run_notion_ingest

# Gmail - extracts newsletters and tech articles
run_gmail_ingest(labels=["newsletter", "tech"])

# Notion - imports from database
run_notion_ingest(database_id="...")
```

## Schema Evolution

- Detects entities in queries (person, project, tool, concept)
- Tracks usage frequency
- Suggests new tables when threshold reached

## Scheduled Jobs

| Job | Frequency | Function |
|-----|-----------|----------|
| daily_summary | Daily | Activity summary |
| weekly_review | Weekly | Routing performance |
| wiki_compile | On raw change | Build wiki |
| memory_cleanup | Weekly | Archive old notes |
| refresh_index | Daily | Update search |

## Directory Structure

```
evokb/
├── __init__.py         # Package init
│
├── api.py              # FastAPI server
│
├── agents/             # Agent implementations
│   ├── agent.py        # AgentClassifier
│   ├── librarian.py    # LibrarianAgent
│   └── hermes.py      # Review gate
│
├── core/               # Core functionality
│   ├── search.py       # SearchIndex, search_kb
│   ├── router.py       # Query routing
│   ├── learning.py     # Learning feedback loop
│   ├── retriever.py    # Query/compile wiki
│   ├── context.py      # Context building
│   ├── config.py      # Configuration
│   └── utils.py       # Utilities
│
├── connectors/        # External data sources
│   ├── gmail.py       # Gmail API
│   └── notion.py      # Notion API
│
├── ingest/             # Data ingestion
│   ├── scraper.py     # URL scraping
│   └── schema_evolution.py  # Auto-schema
│
├── memory/             # SQL memory
│   └── cluster.py     # Knowledge clusters
│
├── eval/               # Evaluation
│   ├── eval.py        # Metrics
│   └── evaluator.py   # Change scoring
│
└── reporting/          # Reporting
    └── reporting.py   # Dashboard
```

## Usage

```python
from evokb.core.retriever import query_evo_kb
from evokb.core.search import search_kb, index_wiki
from evokb.agents.librarian import run_safe_iteration

# Query (auto-routes)
answer, cluster = query_evo_kb("What is a knowledge graph")

# Search
results = search_kb("knowledge")

# Run librarian iteration
run_safe_iteration()
```

## Privacy

See `PRIVACY.md` for ethical guidelines on storing data about people.

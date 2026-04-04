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
├── __init__.py         # Lazy re-exports
│
├── agents/             # Agent implementations
│   ├── agent.py        # AgentClassifier
│   └── librarian.py    # LibrarianAgent
│
├── core/               # Core functionality
│   ├── search.py       # SearchIndex, search_kb
│   ├── router.py       # Query routing
│   ├── learning.py     # Learning feedback loop
│   ├── retriever.py    # Query/compile wiki
│   └── context.py      # Context building
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
│   └── memory.py       # MemoryStore (SQLite)
│
├── hermes.py           # Review gate
├── cluster.py         # Knowledge clusters
├── config.py          # Configuration
└── utils.py           # Utilities
```

## Usage

```bash
# Query (auto-routes)
python evokb_cli.py query "What is a knowledge graph"
python evokb_cli.py query "What do I know about Sarah"

# Search
python evokb_cli.py search "knowledge"

# Add structured data
python evokb_cli.py add-note "Met with Sarah" --persons Sarah --projects AI
python evokb_cli.py add-person Sarah --company Acme --role CTO

# View routing
python evokb_cli.py route "What is X"

# System stats
python evokb_cli.py stats
```

## Privacy

See `PRIVACY.md` for ethical guidelines on storing data about people.

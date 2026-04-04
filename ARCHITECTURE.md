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

## File Structure

```
evokb/
├── raw/              # Raw source files (fetched by ingest)
├── wiki/             # Compiled knowledge (depth)
├── evokb_memory.db   # SQLite (breadth)
├── evokb_learning.json  # Routing feedback
├── evokb_schema.json    # Schema evolution
│
├── evokb/
│   ├── router.py     # Query routing
│   ├── learning.py   # Feedback loop
│   ├── memory/      # SQL memory
│   ├── schema_evolution.py  # Auto-schema
│   └── ...
│
├── scripts/
│   ├── ingest.py    # Fetch external data
│   ├── compile.py   # Build wiki
│   ├── scheduled.py # Daily/weekly jobs
│   └── ...
│
└── .github/workflows/
    ├── 01-ingest.yml
    ├── 02-compile.yml
    ├── 03-test.yml
    └── 04-autoreview.yml
```

## Usage

```bash
# Query (auto-routes)
evokb query "What is a knowledge graph"
evokb query "What do I know about Sarah"

# Search
evokb search "knowledge"

# Add structured data
evokb add-note "Met with Sarah" --persons Sarah --projects AI
evokb add-person Sarah --company Acme --role CTO
evokb add-project "AI System"

# View routing
evokb route "What is X"

# System stats
evokb stats

# Scheduled jobs
python scripts/scheduled.py daily_summary
python scripts/scheduled.py weekly_review
```

## Privacy

See `PRIVACY.md` for ethical guidelines on storing data about people.

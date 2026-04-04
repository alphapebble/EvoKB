# EvoKB Wiki

A self-evolving knowledge base for AI engineering concepts, research, and technical reference.

## Quick Navigation

| Category | Description |
|----------|-------------|
| [Index](./index.md) | Full table of contents |
| [Knowledge Graph](./knowledge-graph.md) | Structuring knowledge for AI |
| [Dual Engine](./dual-engine.md) | Architecture patterns |
| [Enterprise Context](./enterprise-context.md) | Context across systems |

## Categories

- **Architecture**: [dual-engine](./dual-engine.md), [enterprise-context](./enterprise-context.md), [activity-stream](./activity-stream.md)
- **Data & Knowledge**: [knowledge-graph](./knowledge-graph.md), [data-engineering](./data-engineering.md), [semantic-continuity](./semantic-continuity.md)
- **AI & Reasoning**: [causal-reasoning](./causal-reasoning.md), [precedent-engineering](./precedent-engineering.md), [ontology-engineering](./ontology-engineering.md)
- **Engineering**: [kv-cache](./kv-cache.md), [zero-trust](./zero-trust.md), [geospatial-intelligence](./geospatial-intelligence.md)

## About

This wiki is auto-compiled from raw sources and continuously improved by the EvoKB autoreview loop.

## Usage

```bash
# Query the knowledge base
python -c "from evokb.retriever import query_evo_kb; print(query_evo_kb('What is a knowledge graph?'))"

# Search
python -c "from evokb.search import search_kb; print(search_kb('knowledge graph'))"
```

## Contributing

Add raw markdown files to `raw/` - they'll be compiled to wiki automatically.

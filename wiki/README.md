# EvoKB Wiki

A self-evolving knowledge base for AI engineering concepts, research, and technical reference.

## Quick Navigation

| Category | Description |
|----------|-------------|
| [Architecture](./index.md) | System design patterns |
| [Data & Knowledge](./Knowledge_Graph_Engineering__Structuring_Knowledge.md) | Knowledge graphs, data engineering |
| [AI & Reasoning](./Causal_Reasoning_for_AI_Agents__Beyond_Vector_Simi.md) | Causal reasoning, ontologies |
| [Engineering](./KV_Cache_Optimization__Scaling_LLM_Inference_Witho.md) | Performance, security, optimization |

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

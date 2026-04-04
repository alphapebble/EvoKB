# Context Engine — Production-Grade Open Source Guide

A step-by-step roadmap to building a next-gen "RAG replacement" / context-engine system, inspired by Sirchmunk and Karpathy's vision.

> **TL;DR**: From "retrieve documents → answer" → to "construct context → reason"

---

## 🚀 Phase 1: Architecture Overview

```
┌──────────────┐
│ Raw Data     │  (files, emails, APIs)
└──────┬───────┘
       │
┌──────▼───────┐
│ Indexless    │  (keyword + BM25 search)
│ Retrieval    │
└──────┬───────┘
       │
┌──────▼───────┐
│ Context      │  (summarize, deduplicate, filter)
│ Builder      │
└──────┬───────┘
       │
┌──────▼───────┐
│ LLM Agent    │  (reason, tool-use, memory)
└──────────────┘
```

---

## 🧱 Phase 2: Tech Stack

| Layer | Tool | Why |
|-------|------|-----|
| Backend | FastAPI | Production-ready, async |
| LLM | LiteLLM + Ollama | Unified API, local-first |
| Search | BM25 / Whoosh | No vector DB dependency |
| Storage | SQLite | Lightweight, portable |
| Agents | Custom lightweight | Avoid LangChain bloat |

---

## 📚 Phase 3: Must-Read Articles

### Core Philosophy
- **Karpathy: LLM = CPU, Context = RAM** — Treat LLM as OS, context as memory
- **OpenAI Cookbook** — Function calling, tool usage

### RAG Limitations
- **"RAG is Not Enough"** — Why embeddings fail, chunking problems, stale indexes

### Search Fundamentals
- **BM25 Explained** — Better than naive keyword search
- **Introduction to Information Retrieval** — Ranking, indexing

### Real Systems
- **Sirchmunk Architecture** — Indexless retrieval, knowledge clusters
- **Anthropic Papers** — Tool use, memory, agents

### Agents (Practical)
- **ReAct Paper** — Reasoning + acting
- **Toolformer** — LLM tool usage

### Production Systems
- **"Designing Data-Intensive Applications"** — MUST READ for production-grade systems

---

## 🗓️ Phase 4: 8-Week Build Plan

### Week 1-2: MVP
- [ ] Load documents (emails, PDFs)
- [ ] Basic keyword search
- [ ] Send top results to LLM
- [ ] CLI interface

**Output**: `ask("Where is invoice?")` → finds files → LLM → answer

### Week 3-4: Context Engine
- [ ] Context ranking
- [ ] Summarization layer
- [ ] Remove duplicate info
- [ ] Source attribution

### Week 5-6: Agentification
- [ ] Query classifier (intent detection)
- [ ] Multi-step reasoning
- [ ] Tool usage

### Week 7-8: Production Ready
- [ ] FastAPI backend
- [ ] Docker
- [ ] Config system
- [ ] Logging + tracing

---

## ⚠️ Common Mistakes to Avoid

- ❌ Building another LangChain wrapper
- ❌ Overusing embeddings early
- ❌ No evaluation metrics
- ❌ No latency optimization
- ❌ No real use case

---

## 🧠 Your Unfair Advantage

You already have:
- Email ingestion pipelines
- Zoho workflows
- AI + infra knowledge

**Build**: "Context Engine for Email + Business Workflows"

This differentiates instantly and is monetizable.

---

## 📁 Recommended Repo Structure

```
context-engine/
├── ingestion/        # Email, files, APIs
├── retrieval/        # BM25, keyword search
├── context_builder/ # Summarize, deduplicate
├── agents/           # Classifier, reasoner
├── memory/           # SQLite, JSON logs
├── llm/              # LiteLLM wrapper
├── api/              # FastAPI endpoints
├── cli/              # CLI interface
├── examples/
│   └── email_assistant/
├── docs/
├── docker/
└── README.md
```

---

## 🔗 Key Resources

- [Karpathy: LLM Knowledge Base](https://github.com/karpathy/llm-agent-scaffold)
- [Sirchmunk Architecture](https://modelscope.github.io/sirchmunk-web/)
- [BM25 Algorithm](https://en.wikipedia.org/wiki/Okapi_BM25)
- [ReAct Paper](https://arxiv.org/abs/2210.03629)
- [Designing Data-Intensive Applications](https://dataintensive.net/)

---

## Next Steps

1. Start with EvoKB as base
2. Add BM25 search
3. Build context builder
4. Add agent layer

Need starter code for any phase?

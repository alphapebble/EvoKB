---
title: EvoKB Project
date: 2026-04-04
---

**EvoKB Project**
=====================

### Overview
---------------

EvoKB is an open-source project that implements Karpathy's vision of a large language model (LLM)-powered knowledge base. The project utilizes an autoresearch loop to continuously update and refine its knowledge base.

### Features
------------

#### Key Features

*   **Markdown as Single Source of Truth**: EvoKB uses Markdown files as the primary source of truth for its knowledge base.
*   **Autoresearch-Style Librarian Agent**: An autonomous agent is used to propose, evaluate, and apply new information to the knowledge base.
*   **Propose → Evaluate → Apply Loop**: The librarian agent follows a proposed-evaluated-applied loop to update and refine the knowledge base.
*   **Local-First (Ollama by Default)**: EvoKB prioritizes local-first access to its knowledge clusters using Ollama.
*   **No Vector DB Required**: EvoKB does not require a vector database to function.

### Architecture
--------------

#### System Components

*   **raw/**: Incoming documents are stored in this directory.
*   **wiki/**: The compiled knowledge base is stored here.
*   **clusters/**: Knowledge clusters, including DuckDB, are stored here.

### Usage
----------

#### Getting Started

To start the EvoKB system, run the following commands:

```bash
evokb  # start librarian
evokb-api  # start API server
```

### Roadmap
-------------

#### Planned Features

*   **Tantivy Search**: Integration with Tantivy search for improved query capabilities.
*   **Context Builder**: Development of a context builder to enhance the autoresearch loop.
*   **Agent Classifier**: Implementation of an agent classifier for more accurate librarian decision-making.
*   **FastAPI Backend**: Deployment of a FastAPI backend for enhanced API functionality.
*   **Docker Support**: Integration with Docker for simplified containerization.

### Key Claims and Evidence
---------------------------

#### Claim 1: Improved Knowledge Base Updates

EvoKB's autoresearch loop ensures that the knowledge base is updated continuously, providing more accurate information to users.

Evidence:

*   The use of an autonomous librarian agent that follows a propose-evaluate-apply loop.
*   The implementation of local-first access using Ollama for improved performance.

#### Claim 2: Enhanced Autonomy

EvoKB's autoresearch loop and agent classifier enable the system to make decisions independently, reducing reliance on human intervention.

Evidence:

*   The use of an autonomous librarian agent that operates without explicit user input.
*   The implementation of an agent classifier to improve decision-making accuracy.

### Backlinks
-------------

#### Related Pages

*   [Karpathy's Vision](https://en.wikipedia.org/wiki/Karpathy%27s_vision): Learn more about Karpathy's vision for an LLM-powered knowledge base.
*   [Autonomous Systems](https://en.wikipedia.org/wiki/Autonomous_system): Explore the concept of autonomous systems and their applications in various fields.
*   [Knowledge Graphs](https://en.wikipedia.org/wiki/Knowledge_graph): Discover how knowledge graphs are used to represent and manage complex information.

#### External Resources

*   [EvoKB Repository](https://github.com/evokeb/evokb): Access the EvoKB project's source code repository on GitHub.
*   [Autoresearch Loop Documentation](https://docs.evokeb.org/autoresearch-loop/): Read more about the autoresearch loop used in EvoKB.
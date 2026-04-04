#!/usr/bin/env python3
import json
from pathlib import Path

with open("eval/metrics.json") as f:
    m = json.load(f)

qa_accuracy = m.get("qa_accuracy", 0)
search_mrr = m.get("search_mrr", 0)

if search_mrr == 0 and "search" in m:
    search_scores = [s["metrics"]["mrr"] for s in m.get("search", [])]
    search_mrr = sum(search_scores) / len(search_scores) if search_scores else 0

qa_pct = qa_accuracy * 100
mrr_pct = search_mrr * 100

qa_badge = "🟢" if qa_pct >= 50 else "🟡" if qa_pct >= 30 else "🔴"
mrr_badge = "🟢" if mrr_pct >= 80 else "🟡" if mrr_pct >= 50 else "🔴"

with open("eval/README.md", "w") as f:
    f.write(f"""# Evaluation Results

## System Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Q&A Accuracy | {qa_pct:.1f}% | {qa_badge} |
| Search MRR | {mrr_pct:.1f}% | {mrr_badge} |

Last updated: {m.get("timestamp", "N/A")}

## About

EvoKB is a self-evolving knowledge base. Metrics are auto-updated on each push.
""")

#!/usr/bin/env python3
import json

with open("eval/metrics.json") as f:
    m = json.load(f)

# New format: qa_accuracy, search_mrr directly
qa_accuracy = m.get("qa_accuracy", 0)
search_mrr = m.get("search_mrr", 0)

# Also check old format
if search_mrr == 0 and "search" in m:
    search_scores = [s["metrics"]["mrr"] for s in m.get("search", [])]
    search_mrr = sum(search_scores) / len(search_scores) if search_scores else 0

with open("eval/README.md", "w") as f:
    f.write(f"""# Evaluation Results

## Metrics
- Q&A Accuracy: {qa_accuracy:.1%}
- Search MRR: {search_mrr:.1%}

Last updated: {m.get("timestamp", "N/A")}
""")

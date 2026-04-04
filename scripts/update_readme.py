#!/usr/bin/env python3
import json

with open("eval/metrics.json") as f:
    m = json.load(f)
with open("eval/README.md", "w") as f:
    f.write(f"""# Evaluation Results

## Metrics
- Q&A Accuracy: {m.get("qa_accuracy", 0):.1%}
- Search MRR: {m.get("search_mrr", 0):.1%}

Last updated: {m.get("timestamp", "N/A")}
""")

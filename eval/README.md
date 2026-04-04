# EvoKB Evaluation Results

## Overview
This folder contains evaluation metrics and dashboards for the EvoKB knowledge base.

## Files

| File | Description |
|------|-------------|
| `dashboard.html` | Interactive HTML dashboard with metrics |
| `metrics.json` | Raw evaluation metrics in JSON format |
| `report.md` | Markdown summary of evaluation results |

## How to View

### Dashboard (HTML)
Open `dashboard.html` in a browser:
```bash
open eval/dashboard.html
```

### Metrics (JSON)
```bash
cat eval/metrics.json
```

### Report (Markdown)
```bash
cat eval/report.md
```

## Metrics Explained

### Search Quality (MRR)
- **MRR** = Mean Reciprocal Rank
- Measures how often the first relevant result appears
- Range: 0-1 (higher is better)

### Q&A Accuracy
- **Keyword Overlap**: How many key words match
- **Containment**: Does answer contain expected info?
- **Trigram Overlap**: Semantic similarity
- **Overall Score**: Weighted average (0-1)

### Scraping Quality
- **Content Density**: Ratio of meaningful text
- **Cleanliness**: Boilerplate removed?
- **Overall Score**: Combined metric

## Running Evaluation

```python
from evokb.eval import run_full_evaluation
from evokb.reporting import run_and_report
from pathlib import Path

test_queries = [
    {
        "query": "What is X?",
        "relevant_docs": ["doc1"],
        "expected_answer": "X is..."
    }
]

results = run_and_report(Path("wiki"), test_queries, Path("eval"))
```

## Latest Results

- **Search MRR**: 0.00 (needs improvement)
- **Q&A Accuracy**: 0.43 (moderate)
- **Wiki Documents**: 17

"""Visualization and metrics reporting for EvoKB."""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


def create_metrics_summary(results: Dict[str, Any]) -> str:
    """Create a text summary of metrics."""
    lines = [
        "# EvoKB Evaluation Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Search Metrics",
    ]

    if "search_avg_mrr" in results:
        lines.append(f"- Mean Reciprocal Rank: {results['search_avg_mrr']}")

    if results.get("search"):
        lines.append(f"- Queries tested: {len(results['search'])}")

    lines.extend(["", "## Q&A Metrics"])

    if "qa_avg_score" in results:
        lines.append(f"- Average Score: {results['qa_avg_score']}")

    if results.get("qa"):
        lines.append(f"- Questions tested: {len(results['qa'])}")

    return "\n".join(lines)


def export_metrics_json(results: Dict[str, Any], output_path: Path):
    """Export metrics to JSON."""
    output_path.write_text(json.dumps(results, indent=2))
    print(f"Exported metrics to {output_path}")


def export_metrics_markdown(results: Dict[str, Any], output_path: Path):
    """Export metrics to markdown."""
    md = create_metrics_summary(results)
    output_path.write_text(md)
    print(f"Exported metrics to {output_path}")


def print_metrics_table(results: Dict[str, Any]):
    """Print a formatted table of metrics."""
    print("\n" + "=" * 60)
    print("EVO KB EVALUATION RESULTS")
    print("=" * 60)

    if "search_avg_mrr" in results:
        print(f"\n[SEARCH] MRR: {results['search_avg_mrr']}")
        for s in results.get("search", [])[:5]:
            print(
                f"  - {s['query'][:40]}: {s['metrics'].get('result_count', 0)} results"
            )

    if "qa_avg_score" in results:
        print(f"\n[QA] Accuracy: {results['qa_avg_score']}")

    print("\n" + "=" * 60)


def create_simple_bar_chart(data: Dict[str, float], title: str = "Metrics") -> str:
    """Create a simple ASCII bar chart."""
    max_val = max(data.values()) if data else 1
    bars = []

    bars.append(f"\n{title}")
    bars.append("-" * 40)

    for label, value in data.items():
        bar_len = int((value / max_val) * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        bars.append(f"{label:20} {bar} {value:.2f}")

    return "\n".join(bars)


def generate_dashboard_html(
    results: Dict[str, Any], output_path: Path, wiki_stats: Dict[str, Any] = None
) -> Path:
    """Generate an HTML dashboard with metrics."""

    # Calculate stats
    search_mrr = results.get("search_avg_mrr", 0)
    qa_score = results.get("qa_avg_score", 0)

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>EvoKB Dashboard</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .card {{ background: white; padding: 24px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; margin-top: 0; }}
        .metric {{ display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee; }}
        .metric-value {{ font-weight: bold; color: #2563eb; font-size: 24px; }}
        .good {{ color: #16a34a; }}
        .warning {{ color: #ca8a04; }}
        .bad {{ color: #dc2626; }}
        .grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 EvoKB Dashboard</h1>
        <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        
        <div class="grid">
            <div class="card">
                <h2>Search Quality (MRR)</h2>
                <div class="metric-value {"good" if search_mrr > 0.7 else "warning" if search_mrr > 0.4 else "bad"}">{search_mrr:.2f}</div>
                <p>Mean Reciprocal Rank - higher is better</p>
            </div>
            
            <div class="card">
                <h2>Q&A Accuracy</h2>
                <div class="metric-value {"good" if qa_score > 0.7 else "warning" if qa_score > 0.4 else "bad"}">{qa_score:.2f}</div>
                <p>Overall answer quality score</p>
            </div>
        </div>
        
        <div class="card">
            <h2>Recent Queries</h2>
"""

    # Add search results
    for s in results.get("search", [])[:10]:
        html += f"""            <div class="metric">
                <span>{s["query"][:50]}</span>
                <span>{s["metrics"].get("result_count", 0)} results</span>
            </div>
"""

    html += """
        </div>
    </div>
</body>
</html>"""

    output_path.write_text(html)
    return output_path


def run_and_report(
    wiki_dir: Path, test_queries: List[Dict[str, Any]], output_dir: Path = None
) -> Dict[str, Any]:
    """Run full evaluation and generate reports."""
    if output_dir is None:
        output_dir = Path("eval")

    from .eval import run_full_evaluation, save_evaluation_report

    print("Running evaluation...")
    results = run_full_evaluation(wiki_dir, test_queries)

    # Save reports
    save_evaluation_report(results, output_dir / "metrics.json")
    export_metrics_markdown(results, output_dir / "report.md")

    # Generate dashboard
    generate_dashboard_html(results, output_dir / "dashboard.html")

    # Print summary
    print_metrics_table(results)

    return results

#!/usr/bin/env python3
"""Main script to run EvoKB autoreview loop for self-improving knowledge base."""

import sys
import time
import argparse
from pathlib import Path

from evokb.config import CHECK_INTERVAL, RAW_DIR, WIKI_DIR, PROGRAM_MD
from evokb.utils import ensure_dir, read_file, list_files
from evokb.retriever import compile_to_wiki, run_autoresearch_iteration
from evokb.search import search_kb, index_wiki
from evokb.eval import evaluate_qa_accuracy, evaluate_search_quality
from evokb.reporting import run_and_report


def compile_raw_files(wiki_dir: Path):
    """Compile any new raw files to wiki."""
    print("\n📥 Checking for new raw files...")

    new_count = 0
    for raw_file in list_files(RAW_DIR, "*.md"):
        wiki_file = wiki_dir / raw_file.name
        if not wiki_file.exists():
            print(f"   Compiling {raw_file.name}...")
            try:
                compile_to_wiki(raw_file, wiki_dir)
                new_count += 1
            except Exception as e:
                print(f"   Error: {e}")

    if new_count:
        print(f"   ✅ Compiled {new_count} new files")
    else:
        print("   No new files")

    return new_count


def run_autoreview_iteration(iteration: int):
    """Run a single autoreview iteration."""
    print(f"\n🔄 Autoreview Iteration #{iteration}")
    print("-" * 40)

    # Run the librarian loop
    result = run_autoresearch_iteration()

    if result:
        print(f"   ✅ Iteration complete")
    else:
        print(f"   ⚠️ No result (check LLM availability)")

    return result


def run_evaluation(wiki_dir: Path, output_dir: Path):
    """Run evaluation and generate report."""
    print("\n📊 Running evaluation...")

    test_queries = [
        {
            "query": "What is a knowledge graph?",
            "relevant_docs": ["Knowledge_Graph"],
            "expected_answer": "A knowledge graph represents information as interconnected entities",
        },
        {
            "query": "What is dual engine architecture?",
            "relevant_docs": ["Dual-Engine"],
            "expected_answer": "Combines control and intelligence in AI systems",
        },
        {
            "query": "What is data engineering?",
            "relevant_docs": ["Data_Engineering"],
            "expected_answer": "Infrastructure for AI and machine learning",
        },
    ]

    try:
        results = run_and_report(wiki_dir, test_queries, output_dir)
        print(f"   ✅ Evaluation complete")
        return results
    except Exception as e:
        print(f"   Error: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="EvoKB Autoreview Loop")
    parser.add_argument(
        "--iterations",
        "-n",
        type=int,
        default=5,
        help="Number of iterations to run (default: 5)",
    )
    parser.add_argument(
        "--interval",
        "-i",
        type=int,
        default=30,
        help="Seconds between iterations (default: 30)",
    )
    parser.add_argument(
        "--eval", "-e", action="store_true", help="Run evaluation after iterations"
    )
    parser.add_argument(
        "--compile", "-c", action="store_true", help="Compile raw files before starting"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("🚀 EVOKB AUTOREVIEW LOOP")
    print("=" * 60)
    print(f"Iterations: {args.iterations}")
    print(f"Interval: {args.interval}s")
    print(f"Evaluation: {args.eval}")
    print(f"Compile raw: {args.compile}")

    # Setup directories
    ensure_dir(RAW_DIR)
    ensure_dir(WIKI_DIR)
    ensure_dir(Path("clusters"))

    # Compile raw files if requested
    if args.compile:
        compile_raw_files(WIKI_DIR)

    # Re-index wiki
    print("\n🔍 Indexing wiki...")
    try:
        index_wiki(WIKI_DIR)
        print("   ✅ Wiki indexed")
    except Exception as e:
        print(f"   Warning: {e}")

    # Run iterations
    for i in range(1, args.iterations + 1):
        run_autoreview_iteration(i)

        if i < args.iterations:
            print(f"\n⏳ Waiting {args.interval}s...")
            time.sleep(args.interval)

    # Run evaluation if requested
    if args.eval:
        results = run_evaluation(WIKI_DIR, Path("eval"))
        if results:
            print(f"\n📈 Results:")
            print(f"   Search MRR: {results.get('search_avg_mrr', 'N/A')}")
            print(f"   Q&A Score: {results.get('qa_avg_score', 'N/A')}")

    print("\n" + "=" * 60)
    print("✅ AUTOREVIEW LOOP COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()

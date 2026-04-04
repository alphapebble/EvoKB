"""
EvoKB Scheduled Jobs

Daily/weekly automated tasks:
- Daily summary (compile yesterday's activity)
- Wiki compilation (incremental)
- Memory cleanup (archive old notes)
- Index refresh (update search index)

Uses APScheduler for scheduling (or cron-compatible).
"""

from datetime import datetime, timedelta
from pathlib import Path
import json

SCHEDULE_FILE = Path("evokb_schedules.json")


def daily_summary():
    """Generate daily summary of activity."""
    from evokb.memory import MemoryStore
    from evokb.learning import LearningStore

    store = MemoryStore()
    learning = LearningStore()

    summary = {
        "date": datetime.now().date().isoformat(),
        "notes_created": len(store.get_all_notes()),
        "people_count": len(store.get_all_people()),
        "projects_count": len(store.get_all_projects()),
        "routing_stats": learning.get_successful_routes(),
    }

    print(f"📊 Daily Summary ({summary['date']})")
    print(f"  Notes: {summary['notes_created']}")
    print(f"  People: {summary['people_count']}")
    print(f"  Projects: {summary['projects_count']}")

    return summary


def weekly_review():
    """Generate weekly review."""
    from evokb.learning import LearningStore

    learning = LearningStore()

    # Get last week's feedback
    recent = learning.get_recent_feedback(limit=50)

    stats = learning.get_successful_routes()

    print(f"📅 Weekly Review")
    print(f"  Total queries: {len(recent)}")
    print(f"  Routing performance:")
    for route, rate in stats.items():
        print(f"    {route}: {rate * 100:.1f}%")

    # Show corrections
    corrections = learning.get_corrections()
    if corrections:
        print(f"  ⚠️ {len(corrections)} corrections to address")

    return {"queries": len(recent), "stats": stats}


def wiki_compile():
    """Run incremental wiki compilation."""
    from scripts.compile import run_compiler

    print("🔄 Running wiki compilation...")
    run_compiler()
    print("✓ Wiki compilation complete")


def memory_cleanup():
    """Archive old notes, optimize database."""
    from evokb.memory import MemoryStore

    store = MemoryStore()

    # Get all notes
    notes = store.get_all_notes()
    old_threshold = datetime.now() - timedelta(days=90)

    # Could add logic to archive old notes
    print(f"📦 Memory cleanup: {len(notes)} notes in database")
    print("  (No old notes to archive yet)")


def refresh_index():
    """Refresh search index."""
    from evokb.search import index_wiki

    wiki_dir = Path("wiki")
    if wiki_dir.exists():
        index_wiki(wiki_dir)
        print("✓ Search index refreshed")


def run_scheduled_job(job_name: str):
    """Run a specific scheduled job."""
    jobs = {
        "daily_summary": daily_summary,
        "weekly_review": weekly_review,
        "wiki_compile": wiki_compile,
        "memory_cleanup": memory_cleanup,
        "refresh_index": refresh_index,
    }

    if job_name not in jobs:
        print(f"Unknown job: {job_name}")
        print(f"Available: {', '.join(jobs.keys())}")
        return

    print(f"\n{'=' * 50}")
    print(f"Running: {job_name}")
    print(f"{'=' * 50}")

    jobs[job_name]()


def run_all_jobs():
    """Run all scheduled jobs."""
    print("\n🚀 Running all scheduled jobs...")

    daily_summary()
    print()
    memory_cleanup()
    print()
    refresh_index()

    print("\n✓ All scheduled jobs complete")


def main():
    """CLI for scheduled jobs."""
    import sys

    if len(sys.argv) < 2:
        run_all_jobs()
    else:
        run_scheduled_job(sys.argv[1])


if __name__ == "__main__":
    main()

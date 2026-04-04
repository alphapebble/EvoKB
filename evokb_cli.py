#!/usr/bin/env python3
"""
EvoKB CLI - Main entry point for the knowledge base system

Ethical Usage:
- Only add people you have legitimate relationship with
- Don't store sensitive data without consent
- See PRIVACY.md for guidelines

Usage:
    evokb query "What is a knowledge graph?"
    evokb search "knowledge"
    evokb add-note "Met with Sarah from Acme"
    evokb add-person "Sarah" --company Acme
    evokb route "What do I know about Sarah?"
    evokb stats
"""

import sys
import argparse
from pathlib import Path

from evokb.router import route_query, route_and_execute
from evokb.search import search_kb
from evokb.memory import MemoryStore
from evokb.learning import LearningStore
from evokb.retriever import query_evo_kb

WIKI_DIR = Path("wiki")


def cmd_query(args):
    """Query the knowledge base."""
    query = args.query

    if args.route:
        # Explicit routing
        if args.route == "wiki":
            answer, _ = query_evo_kb(query, wiki_dir=WIKI_DIR)
        elif args.route == "sql":
            store = MemoryStore()
            from evokb.router import query_sql_memory

            answer = query_sql_memory(query, store)
        else:
            results = search_kb(query, wiki_dir=WIKI_DIR)
            answer = "\n".join(
                [f"- {r['title']}: {r.get('score', 0):.2f}" for r in results]
            )
    else:
        # Auto-routing
        routing = route_query(query)
        print(f"→ Routing to: {routing['route']} ({routing['reason']})")

        store = MemoryStore()
        result = route_and_execute(
            query,
            memory_store=store,
            wiki_dir=WIKI_DIR,
            search_fn=lambda q: search_kb(q, wiki_dir=WIKI_DIR),
        )
        answer = result.get("answer", "No answer found")

    print(answer)
    return 0


def cmd_search(args):
    """Search the knowledge base."""
    results = search_kb(args.query, wiki_dir=WIKI_DIR)

    print(f"Found {len(results)} results:\n")
    for r in results:
        print(f"  {r['title'][:50]}")
        print(f"    Score: {r.get('score', 0):.2f}")
        if r.get("snippet"):
            print(f"    {r['snippet'][:80]}...")
        print()

    return 0


def cmd_add_note(args):
    """Add a note to memory."""
    store = MemoryStore()

    people = args.persons.split(",") if args.persons else []
    projects = args.projects.split(",") if args.projects else []

    note = store.add_note(content=args.content, people=people, projects=projects)

    print(f"✓ Added note #{note.id}")
    return 0


def cmd_add_person(args):
    """Add a person to memory."""
    store = MemoryStore()

    person = store.add_person(
        name=args.name, company=args.company, role=args.role, email=args.email
    )

    print(f"✓ Added person: {person.name}")
    return 0


def cmd_add_project(args):
    """Add a project to memory."""
    store = MemoryStore()

    project = store.add_project(name=args.name, description=args.description)

    print(f"✓ Added project: {project.name}")
    return 0


def cmd_route(args):
    """Show routing decision without executing."""
    routing = route_query(args.query)

    print(f"Query: {routing['query']}")
    print(f"Route: {routing['route']}")
    print(f"Confidence: {routing['confidence']}")
    print(f"Reason: {routing['reason']}")

    if routing.get("entities"):
        print(f"Entities: {', '.join(routing['entities'])}")
    if routing.get("intent"):
        print(f"Intent: {routing['intent']}")

    return 0


def cmd_stats(args):
    """Show system statistics."""
    # Wiki stats
    wiki_files = list(WIKI_DIR.glob("*.md"))
    print(f"Wiki articles: {len(wiki_files)}")

    # Memory stats
    store = MemoryStore()
    print(f"Notes: {len(store.get_all_notes())}")
    print(f"People: {len(store.get_all_people())}")
    print(f"Projects: {len(store.get_all_projects())}")
    print(f"Events: {len(store.get_all_events())}")
    print(f"Decisions: {len(store.get_all_decisions())}")

    # Learning stats
    learning = LearningStore()
    stats = learning.get_successful_routes()
    if stats:
        print("\nRouting success rates:")
        for route, rate in stats.items():
            print(f"  {route}: {rate * 100:.1f}%")

    return 0


def main():
    parser = argparse.ArgumentParser(description="EvoKB CLI")
    subparsers = parser.add_subparsers()

    # query
    p_query = subparsers.add_parser("query", help="Query knowledge base")
    p_query.add_argument("query", help="Query string")
    p_query.add_argument(
        "--route", choices=["wiki", "sql", "search"], help="Force route"
    )
    p_query.set_defaults(func=cmd_query)

    # search
    p_search = subparsers.add_parser("search", help="Search knowledge base")
    p_search.add_argument("query", help="Search string")
    p_search.set_defaults(func=cmd_search)

    # add-note
    p_note = subparsers.add_parser("add-note", help="Add a note")
    p_note.add_argument("content", help="Note content")
    p_note.add_argument("--persons", help="Comma-separated person names")
    p_note.add_argument("--projects", help="Comma-separated project names")
    p_note.set_defaults(func=cmd_add_note)

    # add-person
    p_person = subparsers.add_parser("add-person", help="Add a person")
    p_person.add_argument("name", help="Person name")
    p_person.add_argument("--company", help="Company name")
    p_person.add_argument("--role", help="Role/title")
    p_person.add_argument("--email", help="Email address")
    p_person.set_defaults(func=cmd_add_person)

    # add-project
    p_proj = subparsers.add_parser("add-project", help="Add a project")
    p_proj.add_argument("name", help="Project name")
    p_proj.add_argument("--description", help="Project description")
    p_proj.set_defaults(func=cmd_add_project)

    # route
    p_route = subparsers.add_parser("route", help="Show routing decision")
    p_route.add_argument("query", help="Query string")
    p_route.set_defaults(func=cmd_route)

    # stats
    p_stats = subparsers.add_parser("stats", help="Show system stats")
    p_stats.set_defaults(func=cmd_stats)

    args = parser.parse_args()

    if hasattr(args, "func"):
        return args.func(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())

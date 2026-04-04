"""
EvoKB Router - Routes queries to the right data source

Routes:
- "what do i know about X" → SQL memory
- "explain X" / "what is X" → Wiki
- "find X" / "search X" → Search
"""

from enum import Enum
from typing import List, Dict, Any, Optional
import re


class Route(Enum):
    SQL = "sql"  # Structured data (notes, people, projects)
    WIKI = "wiki"  # Deep knowledge (concepts, explanations)
    SEARCH = "search"  # Keyword search


def detect_intent(query: str) -> Route:
    """Detect which source to route to based on query patterns."""
    query_lower = query.lower()

    # SQL patterns - querying structured data
    sql_patterns = [
        r"what do i know about",
        r"who is",
        r"meeting with",
        r"recent.*note",
        r"project.*status",
        r"decision about",
        r"events?.*today",
        r"people.*from",
        r"notes about",
    ]

    # Wiki patterns - asking for knowledge/explanation
    wiki_patterns = [
        r"what is",
        r"explain",
        r"how does",
        r"describe",
        r"tell me about",
        r"definition of",
        r"concept of",
    ]

    for pattern in sql_patterns:
        if re.search(pattern, query_lower):
            return Route.SQL

    for pattern in wiki_patterns:
        if re.search(pattern, query_lower):
            return Route.WIKI

    return Route.SEARCH


def route_query(query: str) -> Dict[str, Any]:
    """Route a query to the appropriate source."""
    route = detect_intent(query)

    return {
        "query": query,
        "route": route.value,
        "confidence": "high" if route in [Route.SQL, Route.WIKI] else "medium",
        "reason": get_route_reason(route, query),
    }


def get_route_reason(route: Route, query: str) -> str:
    """Get human-readable reason for routing decision."""
    reasons = {
        Route.SQL: "Querying structured data (people, projects, notes)",
        Route.WIKI: "Asking for explanation/concept",
        Route.SEARCH: "General search query",
    }
    return reasons[route]


def route_and_execute(
    query: str, memory_store=None, wiki_dir=None, search_fn=None
) -> Dict[str, Any]:
    """Route query and execute against appropriate source."""
    routing = route_query(query)
    route = routing["route"]

    results = {"query": query, "route": route, "answer": None, "sources": []}

    if route == Route.SQL and memory_store:
        # Query structured memory
        results["answer"] = query_sql_memory(query, memory_store)
        results["sources"] = ["sql_memory"]

    elif route == Route.WIKI and wiki_dir:
        # Query wiki for deep knowledge
        results["answer"] = query_wiki(query, wiki_dir)
        results["sources"] = ["wiki"]

    elif route == Route.SEARCH and search_fn:
        # General search
        results["answer"] = search_fn(query)
        results["sources"] = ["search"]

    return results


def query_sql_memory(query: str, store) -> str:
    """Query SQL memory for structured data."""
    query_lower = query.lower()

    # Extract entity type from query
    if "people" in query_lower or "who is" in query_lower:
        people = store.get_all_people()
        return f"People in memory: {', '.join([p.name for p in people])}"

    if "project" in query_lower:
        projects = store.get_all_projects()
        return f"Active projects: {', '.join([p.name for p in projects])}"

    if "note" in query_lower or "meeting" in query_lower:
        notes = store.get_all_notes()
        return f"Found {len(notes)} notes in memory"

    if "decision" in query_lower:
        decisions = store.get_all_decisions()
        return f"Decisions: {', '.join([d.title for d in decisions])}"

    if "event" in query_lower:
        events = store.get_all_events()
        return f"Events: {', '.join([e.title for e in events])}"

    return "No matching structured data found. Try: 'what do i know about [person]' or 'show me projects'"


def query_wiki(query: str, wiki_dir) -> str:
    """Query wiki for knowledge."""
    from evokb.retriever import query_evo_kb

    try:
        answer, cluster = query_evo_kb(query, wiki_dir=wiki_dir)
        return answer
    except Exception as e:
        return f"Wiki query failed: {e}"


def classify_and_route(query: str) -> Dict[str, Any]:
    """Advanced routing with confidence scoring."""
    routing = route_query(query)

    # Add metadata
    routing["entities"] = extract_entities(query)
    routing["intent"] = classify_intent(query)

    return routing


def extract_entities(query: str) -> List[str]:
    """Extract potential entities from query."""
    words = query.split()
    entities = []

    # Capitalized words might be entities
    for word in words:
        if word[0].isupper() and len(word) > 2:
            entities.append(word.strip(",.?!"))

    return entities[:5]


def classify_intent(query: str) -> str:
    """Classify query intent."""
    query_lower = query.lower()

    if any(w in query_lower for w in ["what is", "explain", "how does"]):
        return "factual"
    if any(w in query_lower for w in ["find", "search", "look for"]):
        return "search"
    if any(w in query_lower for w in ["who", "meeting", "project"]):
        return "lookup"

    return "general"

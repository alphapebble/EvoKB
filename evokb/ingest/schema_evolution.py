"""
EvoKB Schema-Evolving Memory

Automatically creates tables/entities based on usage patterns.
This is the killer feature that differentiates from LangChain.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import json

SCHEMA_FILE = Path("evokb_schema.json")


class SchemaEvolver:
    """Auto-evolves schema based on detected entities."""

    def __init__(self, schema_file: Path = SCHEMA_FILE):
        self.schema_file = schema_file
        self.schema = self._load_schema()

    def _load_schema(self) -> Dict[str, Any]:
        if self.schema_file.exists():
            return json.loads(self.schema_file.read_text())
        return {
            "entities": {},
            "tables": ["notes", "people", "projects", "events", "decisions"],
            "history": [],
        }

    def _save_schema(self):
        self.schema_file.write_text(json.dumps(self.schema, indent=2))

    def detect_entity(self, text: str) -> List[str]:
        """Detect potential entities in text."""
        entities = []
        text_lower = text.lower()

        # Common entity patterns
        entity_patterns = {
            "person": [r"\b([A-Z][a-z]+ [A-Z][a-z]+)\b", r"\b([A-Z][a-z]+) from (\w+)"],
            "project": [r"project (\w+)", r"working on (\w+)"],
            "company": [r"from (\w+)", r"at (\w+)"],
            "tool": [r"use (\w+)", r"using (\w+)"],
            "concept": [r"about (\w+)", r"what is (\w+)"],
        }

        import re

        for entity_type, patterns in entity_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for m in matches:
                    if isinstance(m, tuple):
                        entities.append((entity_type, m[0] if m else m))
                    else:
                        entities.append((entity_type, m))

        return entities

    def suggest_table(self, entity_type: str) -> str:
        """Suggest table name for entity type."""
        mapping = {
            "person": "people",
            "project": "projects",
            "company": "companies",
            "tool": "tools",
            "concept": "concepts",
            "topic": "topics",
        }
        return mapping.get(entity_type, f"{entity_type}s")

    def record_entity_usage(self, entity_type: str, entity_name: str):
        """Record entity usage to track for schema evolution."""
        if entity_type not in self.schema["entities"]:
            self.schema["entities"][entity_type] = {"count": 0, "names": []}

        self.schema["entities"][entity_type]["count"] += 1
        if entity_name not in self.schema["entities"][entity_type]["names"]:
            self.schema["entities"][entity_type]["names"].append(entity_name)

        self.schema["history"].append(
            {
                "timestamp": datetime.now().isoformat(),
                "entity_type": entity_type,
                "entity_name": entity_name,
                "action": "usage",
            }
        )

        # Keep only last 100 history entries
        self.schema["history"] = self.schema["history"][-100:]
        self._save_schema()

    def should_create_table(self, entity_type: str, threshold: int = 5) -> bool:
        """Check if we should create a new table for this entity type."""
        if entity_type in self.schema["tables"]:
            return False

        if entity_type not in self.schema["entities"]:
            return False

        return self.schema["entities"][entity_type]["count"] >= threshold

    def get_schema_stats(self) -> Dict[str, Any]:
        """Get current schema statistics."""
        return {
            "total_entities": sum(e["count"] for e in self.schema["entities"].values()),
            "entity_types": len(self.schema["entities"]),
            "tables": self.schema["tables"],
            "top_entities": sorted(
                self.schema["entities"].items(),
                key=lambda x: x[1]["count"],
                reverse=True,
            )[:5],
        }

    def suggest_schema_growth(self) -> List[Dict[str, str]]:
        """Suggest schema improvements based on usage."""
        suggestions = []

        for entity_type, data in self.schema["entities"].items():
            if self.should_create_table(entity_type):
                table_name = self.suggest_table(entity_type)
                suggestions.append(
                    {
                        "type": "create_table",
                        "entity_type": entity_type,
                        "table_name": table_name,
                        "reason": f"Detected {data['count']} uses of {entity_type}",
                    }
                )

        return suggestions


def auto_evolve_schema(query: str, memory_store):
    """Auto-evolve schema based on query."""
    evolver = SchemaEvolver()

    # Detect entities in query
    entities = evolver.detect_entity(query)

    for entity_type, entity_name in entities:
        evolver.record_entity_usage(entity_type, entity_name)

    # Check for schema suggestions
    suggestions = evolver.suggest_schema_growth()

    return {
        "entities_detected": entities,
        "suggestions": suggestions,
        "stats": evolver.get_schema_stats(),
    }

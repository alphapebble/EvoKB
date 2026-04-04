"""
EvoKB Learning Loop - Stores routing feedback to improve over time

Stores:
- query
- route taken
- success score
- user feedback
"""

from datetime import datetime
from pathlib import Path
import json
from typing import List, Dict, Any

LEARNING_FILE = Path("evokb_learning.json")


class LearningStore:
    def __init__(self, file_path: Path = LEARNING_FILE):
        self.file_path = file_path
        self.history = self._load()

    def _load(self) -> List[Dict]:
        if self.file_path.exists():
            return json.loads(self.file_path.read_text())
        return []

    def _save(self):
        self.file_path.write_text(json.dumps(self.history, indent=2))

    def record(
        self,
        query: str,
        route: str,
        success: bool,
        feedback: str = None,
        answer: str = None,
    ):
        """Record a routing decision and its outcome."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "route": route,
            "success": success,
            "feedback": feedback,
            "answer": answer[:200] if answer else None,  # Truncate for storage
        }
        self.history.append(entry)
        self._save()
        return entry

    def get_successful_routes(self) -> Dict[str, float]:
        """Get success rate by route type."""
        stats = {}
        for entry in self.history:
            route = entry["route"]
            if route not in stats:
                stats[route] = {"success": 0, "total": 0}
            stats[route]["total"] += 1
            if entry["success"]:
                stats[route]["success"] += 1

        return {
            route: s["success"] / s["total"] if s["total"] > 0 else 0
            for route, s in stats.items()
        }

    def get_recent_feedback(self, limit: int = 10) -> List[Dict]:
        """Get recent feedback entries."""
        return self.history[-limit:]

    def suggest_route(self, query: str) -> str:
        """Suggest best route based on history."""
        stats = self.get_successful_routes()

        if not stats:
            return "search"  # Default

        # Return route with highest success rate
        return max(stats, key=stats.get)

    def get_corrections(self) -> List[Dict]:
        """Get entries where user provided negative feedback."""
        return [e for e in self.history if e.get("feedback") == "bad"]

    def clear(self):
        """Clear learning history."""
        self.history = []
        self._save()

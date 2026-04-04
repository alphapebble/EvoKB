from enum import Enum
from typing import Dict, Any, Optional, List
from litellm import completion

from .config import MODEL


class QueryIntent(Enum):
    FACTUAL = "factual"
    EXPLAIN = "explain"
    COMPARE = "compare"
    SUMMARIZE = "summarize"
    CREATE = "create"
    UPDATE = "update"
    SEARCH = "search"
    GENERAL = "general"


class AgentClassifier:
    def __init__(self, model: str = None):
        self.model = model or MODEL
        self.intent_descriptions = {
            QueryIntent.FACTUAL: "Asking for specific facts, dates, numbers, or definitions",
            QueryIntent.EXPLAIN: "Asking for explanations or how things work",
            QueryIntent.COMPARE: "Asking to compare or contrast items",
            QueryIntent.SUMMARIZE: "Asking to summarize or give an overview",
            QueryIntent.CREATE: "Asking to create new content, documents, or entries",
            QueryIntent.UPDATE: "Asking to update, modify, or improve existing content",
            QueryIntent.SEARCH: "Asking to find specific information",
            QueryIntent.GENERAL: "General conversation or unclear intent",
        }

    def classify(self, query: str) -> QueryIntent:
        """Classify the query intent"""
        intents_list = "\n".join(
            [f"- {i.value}: {self.intent_descriptions[i]}" for i in QueryIntent]
        )

        prompt = f"""You are a query classifier. Classify the following user query into ONE of these intents:

{intents_list}

Query: {query}

Reply with ONLY the intent name (e.g., 'factual', 'explain', etc.):
"""

        try:
            resp = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=20,
            )

            intent_str = resp.choices[0].message.content.strip().lower()

            for intent in QueryIntent:
                if intent.value == intent_str:
                    return intent

            return QueryIntent.GENERAL
        except:
            return QueryIntent.GENERAL

    def extract_entities(self, query: str) -> List[str]:
        """Extract key entities from the query"""
        prompt = f"""Extract the key entities (names, topics, concepts) from this query.
Return ONLY a comma-separated list.

Query: {query}

Entities:
"""

        try:
            resp = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=100,
            )

            entities = resp.choices[0].message.content.strip()
            return [e.strip() for e in entities.split(",") if e.strip()]
        except:
            return []

    def get_required_action(self, intent: QueryIntent, context: Dict[str, Any]) -> str:
        """Determine the required action based on intent"""
        actions = {
            QueryIntent.FACTUAL: "search_and_answer",
            QueryIntent.EXPLAIN: "search_and_explain",
            QueryIntent.COMPARE: "search_multiple_and_compare",
            QueryIntent.SUMMARIZE: "search_and_summarize",
            QueryIntent.CREATE: "create_new_content",
            QueryIntent.UPDATE: "update_existing_content",
            QueryIntent.SEARCH: "search_only",
            QueryIntent.GENERAL: "search_and_answer",
        }

        return actions.get(intent, "search_and_answer")

    def classify_with_details(self, query: str) -> Dict[str, Any]:
        """Get full classification details"""
        intent = self.classify(query)
        entities = self.extract_entities(query)
        action = self.get_required_action(intent, {})

        return {
            "intent": intent.value,
            "confidence": 0.8,  # Placeholder - could be enhanced
            "entities": entities,
            "recommended_action": action,
            "intent_description": self.intent_descriptions[intent],
        }


def classify_query(query: str) -> QueryIntent:
    """Convenience function to classify a query"""
    classifier = AgentClassifier()
    return classifier.classify(query)


def classify_query_details(query: str) -> Dict[str, Any]:
    """Convenience function to get full classification"""
    classifier = AgentClassifier()
    return classifier.classify_with_details(query)

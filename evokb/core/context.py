from typing import List, Dict, Any, Union
from pathlib import Path
from litellm import completion

from evokb.config import MODEL
from evokb.utils import read_file


class ContextBuilder:
    def __init__(self, model: str = None):
        self.model = model or MODEL

    def _normalize_snippet(self, snippet: Union[str, Dict]) -> Dict[str, str]:
        """Normalize snippet to dict format"""
        if isinstance(snippet, str):
            return {"content": snippet, "path": "unknown", "title": "unknown"}
        return {
            "content": snippet.get("content", snippet.get("snippet", "")),
            "path": snippet.get("path", snippet.get("title", "unknown")),
            "title": snippet.get("title", "unknown"),
        }

    def deduplicate(self, snippets: List[Union[str, Dict]]) -> List[Dict[str, Any]]:
        """Remove duplicate or near-duplicate content"""
        if not snippets:
            return []

        normalized = [self._normalize_snippet(s) for s in snippets]

        prompt = f"""You are a deduplication assistant. Remove duplicate or near-duplicate content from the following snippets.
Return ONLY a JSON array of unique snippets, each with 'content' and 'path' fields.

Snippets:
{normalized}

Output as JSON array:
"""

        try:
            resp = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000,
            )
            import json
            import re

            json_match = re.search(r"\[[^\]]+\]", resp.choices[0].message.content)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        return [{"content": s["content"], "path": s["path"]} for s in normalized]

    def summarize(self, snippets: List[Union[str, Dict]]) -> str:
        """Generate a concise summary of the snippets"""
        if not snippets:
            return ""

        normalized = [self._normalize_snippet(s) for s in snippets[:5]]

        content = "\n\n".join(
            [
                f"Source: {s.get('path', s.get('title', 'unknown'))}\n{s.get('content', '')}"
                for s in normalized
            ]
        )

        prompt = f"""You are a summarization assistant. Create a concise summary of the following content.
Focus on key facts, decisions, and important details.

Content:
{content}

Summary:
"""

        try:
            resp = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500,
            )
            return resp.choices[0].message.content.strip()
        except:
            return content[:500]

    def detect_conflicts(
        self, snippets: List[Union[str, Dict]]
    ) -> List[Dict[str, Any]]:
        """Detect conflicting information"""
        if not snippets:
            return []

        normalized = [self._normalize_snippet(s) for s in snippets]
        content = "\n\n".join([s.get("content", "") for s in normalized])

        prompt = f"""You are a conflict detection assistant. Identify any conflicting information in the following content.
Return a JSON array of conflicts found, each with 'issue', 'source1', 'source2' fields. If no conflicts, return empty array.

Content:
{content}

Conflicts (JSON array):
"""

        try:
            resp = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000,
            )
            import json
            import re

            json_match = re.search(r"\[[^\]]*\]", resp.choices[0].message.content)
            if json_match:
                conflicts = json.loads(json_match.group())
                return conflicts if conflicts else []
        except:
            pass

        return []

    def rank_by_relevance(
        self, query: str, snippets: List[Union[str, Dict]]
    ) -> List[Union[str, Dict]]:
        """Rank snippets by relevance to query"""
        if not snippets:
            return []

        normalized = [self._normalize_snippet(s) for s in snippets]
        snippet_texts = "\n---\n".join(
            [f"Item {i + 1}: {s.get('content', '')}" for i, s in enumerate(normalized)]
        )

        prompt = f"""You are a relevance ranking assistant. Rank these items by relevance to the query.
Return ONLY a JSON array of the original items (keep the same format as input), reordered by relevance (most relevant first).
Do not change the items themselves, only reorder.

Query: {query}

Items:
{snippet_texts}

Ranked JSON array:
"""

        try:
            resp = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000,
            )
            import json
            import re

            json_match = re.search(r"\[[^\]]*\]", resp.choices[0].message.content)
            if json_match:
                ranked = json.loads(json_match.group())
                # Return as dicts if input was dicts
                if ranked and isinstance(ranked[0], dict):
                    return ranked
                # Convert back to dicts
                return [self._normalize_snippet(s) for s in ranked]
        except Exception as e:
            pass

        return normalized

    def build_context(
        self,
        query: str,
        raw_snippets: List[Union[str, Dict]],
        include_summary: bool = True,
        include_conflicts: bool = True,
        dedupe: bool = True,
    ) -> Dict[str, Any]:
        """Build final context from raw search results"""

        snippets = raw_snippets

        if dedupe and len(snippets) > 1:
            snippets = self.deduplicate(snippets)

        snippets = self.rank_by_relevance(query, snippets)

        conflicts = []
        if include_conflicts and len(snippets) > 1:
            conflicts = self.detect_conflicts(snippets)

        summary = ""
        if include_summary:
            summary = self.summarize(snippets)

        context = {
            "facts": [
                self._normalize_snippet(s).get("content", str(s))
                if isinstance(s, dict)
                else str(s)
                for s in snippets
            ],
            "summary": summary,
            "conflicts": conflicts,
            "source_count": len(snippets),
            "query": query,
        }

        return context


def build_context(query: str, search_results: List[Union[str, Dict]]) -> Dict[str, Any]:
    """Convenience function to build context from search results"""
    builder = ContextBuilder()
    return builder.build_context(query, search_results)

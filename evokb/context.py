from typing import List, Dict, Any, Optional
from pathlib import Path
from litellm import completion

from .config import MODEL
from .utils import read_file


class ContextBuilder:
    def __init__(self, model: str = None):
        self.model = model or MODEL

    def deduplicate(self, snippets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate or near-duplicate content"""
        if not snippets:
            return []

        prompt = f"""You are a deduplication assistant. Remove duplicate or near-duplicate content from the following snippets.
Return ONLY a JSON array of unique snippets, each with 'content' and 'source' fields.

Snippets:
{snippets}

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

        return snippets

    def summarize(self, snippets: List[Dict[str, Any]]) -> str:
        """Generate a concise summary of the snippets"""
        if not snippets:
            return ""

        content = "\n\n".join(
            [
                f"Source: {s.get('path', s.get('title', 'unknown'))}\n{s.get('content', s.get('snippet', ''))}"
                for s in snippets[:5]
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

    def detect_conflicts(self, snippets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect conflicting information"""
        if not snippets:
            return []

        content = "\n\n".join(
            [s.get("content", s.get("snippet", "")) for s in snippets]
        )

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
        self, query: str, snippets: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rank snippets by relevance to query"""
        if not snippets:
            return []

        snippet_texts = "\n---\n".join(
            [
                f"Item {i + 1}: {s.get('content', s.get('snippet', ''))[:500]}"
                for i, s in enumerate(snippets)
            ]
        )

        prompt = f"""You are a relevance ranking assistant. Rank these items by relevance to the query.
Return ONLY a JSON array of the original items, reordered by relevance (most relevant first).
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
                return ranked
        except:
            pass

        return snippets

    def build_context(
        self,
        query: str,
        raw_snippets: List[Dict[str, Any]],
        include_summary: bool = True,
        include_conflicts: bool = True,
        dedupe: bool = True,
    ) -> Dict[str, Any]:
        """Build final context from raw search results"""

        snippets = raw_snippets

        # Step 1: Deduplicate if requested
        if dedupe and len(snippets) > 1:
            snippets = self.deduplicate(snippets)

        # Step 2: Rank by relevance
        snippets = self.rank_by_relevance(query, snippets)

        # Step 3: Detect conflicts if requested
        conflicts = []
        if include_conflicts and len(snippets) > 1:
            conflicts = self.detect_conflicts(snippets)

        # Step 4: Generate summary if requested
        summary = ""
        if include_summary:
            summary = self.summarize(snippets)

        # Step 5: Format final context
        context = {
            "facts": [s.get("content", s.get("snippet", "")) for s in snippets],
            "summary": summary,
            "conflicts": conflicts,
            "source_count": len(snippets),
            "query": query,
        }

        return context


def build_context(query: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Convenience function to build context from search results"""
    builder = ContextBuilder()
    return builder.build_context(query, search_results)

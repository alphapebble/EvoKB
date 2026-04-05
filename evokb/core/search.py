"""Tantivy full-text search for EvoKB.

This module provides a Tantivy-based search implementation for full-text search.
If Tantivy is not installed, falls back to basic keyword search.

Install Tantivy: pip install tantivy
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from evokb.core.utils import read_file, list_files


class TantivySearchIndex:
    """Full-text search using Tantivy."""

    def __init__(self, index_dir: str = None):
        self.index_dir = index_dir or "clusters/index"
        self.index = None
        self.indexed_files = {}

    def _build_index(self):
        """Build the Tantivy index."""
        try:
            import tantivy
            from tantivy import Schema, TEXT, STORED, INDEXED
            from tantivy.document import Document

            schema = Schema(
                title=TEXT(stored=True),
                content=TEXT(stored=True),
                path=STORED,
            )
            self.index = tantivy.Index(schema)
            return True
        except ImportError:
            return False

    def index_documents(self, docs_dir: Path):
        """Index all markdown files."""
        self.indexed_files = {}

        # Try Tantivy first
        if self._build_index():
            try:
                self._index_with_tantivy(docs_dir)
                print(
                    f"[INFO] Indexed {len(self.indexed_files)} documents with Tantivy"
                )
                return
            except Exception as e:
                print(f"[WARN] Tantivy indexing failed: {e}, falling back to basic")

        # Fallback to basic search
        self._index_basic(docs_dir)

    def _index_with_tantivy(self, docs_dir: Path):
        """Index using Tantivy."""
        import tantivy
        from tantivy.document import Document

        writer = self.index.writer()

        for file in list_files(docs_dir, "*.md"):
            content = read_file(file)
            if content:
                self.indexed_files[str(file)] = {
                    "title": file.stem,
                    "content": content,
                }
                writer.add_document(
                    Document(
                        title=file.stem,
                        content=content,
                        path=str(file),
                    )
                )

        writer.commit()

    def _index_basic(self, docs_dir: Path):
        """Basic keyword indexing fallback."""
        for file in list_files(docs_dir, "*.md"):
            content = read_file(file)
            if content:
                words = set(re.findall(r"\w+", content.lower()))
                self.indexed_files[str(file)] = {
                    "title": file.stem,
                    "content": content,
                    "words": words,
                }

    def search(self, query_str: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search indexed documents."""
        if self.index is not None:
            return self._search_tantivy(query_str, top_k)
        return self._search_basic(query_str, top_k)

    def _search_tantivy(self, query_str: str, top_k: int) -> List[Dict[str, Any]]:
        """Search using Tantivy."""
        try:
            import tantivy

            searcher = self.index.searcher()
            query = self.index.parse_query(query_str)
            results = searcher.search(query, limit=top_k)

            return [
                {
                    "title": hit["title"],
                    "path": hit["path"],
                    "snippet": hit["content"][:500],
                    "score": hit.score,
                }
                for hit in results
            ]
        except Exception:
            return self._search_basic(query_str, top_k)

    def _search_basic(self, query_str: str, top_k: int) -> List[Dict[str, Any]]:
        """Basic keyword search fallback."""
        query_words = set(re.findall(r"\w+", query_str.lower()))
        results = []

        for path, data in self.indexed_files.items():
            if "words" in data:
                matches = len(query_words & data["words"])
                if matches > 0:
                    results.append(
                        {
                            "title": data["title"],
                            "path": path,
                            "snippet": data["content"][:500],
                            "score": matches,
                        }
                    )

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def rebuild_index(self, docs_dir: Path):
        """Rebuild the index."""
        self.indexed_files = {}
        self.index = None
        self.index_documents(docs_dir)

    def add_document(self, file_path: Path):
        """Add a single document to the index."""
        content = read_file(file_path)
        if content:
            self.indexed_files[str(file_path)] = {
                "title": file_path.stem,
                "content": content,
                "words": set(re.findall(r"\w+", content.lower())),
            }


# Alias for backward compatibility
SearchIndex = TantivySearchIndex


def search_kb(query: str, wiki_dir: Path = None) -> List[Dict[str, Any]]:
    """Search the knowledge base."""
    if wiki_dir is None:
        wiki_dir = Path("wiki")

    search = TantivySearchIndex()
    search.index_documents(wiki_dir)

    return search.search(query)


def index_wiki(wiki_dir: Path = None):
    """Index the wiki."""
    if wiki_dir is None:
        wiki_dir = Path("wiki")

    search = TantivySearchIndex()
    search.rebuild_index(wiki_dir)

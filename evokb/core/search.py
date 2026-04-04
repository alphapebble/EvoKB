"""Simple search using basic text matching."""

import os
import re
from pathlib import Path
from typing import List, Dict, Any

from evokb.core.utils import read_file, list_files


class SearchIndex:
    """Simple keyword-based search implementation."""

    def __init__(self, index_dir: str = None):
        self.index_dir = index_dir or "clusters/index"
        self.indexed_files = {}

    def index_documents(self, docs_dir: Path):
        """Index all markdown files in the given directory"""
        self.indexed_files = {}

        for file in list_files(docs_dir, "*.md"):
            content = read_file(file)
            if content:
                words = set(re.findall(r"\w+", content.lower()))
                self.indexed_files[str(file)] = {
                    "title": file.stem,
                    "content": content,
                    "words": words,
                }

        print(f"Indexed {len(self.indexed_files)} documents")

    def search(self, query_str: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search indexed documents using simple matching"""
        query_words = set(re.findall(r"\w+", query_str.lower()))

        results = []
        for path, data in self.indexed_files.items():
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
        self.indexed_files = {}
        self.index_documents(docs_dir)

    def add_document(self, file_path: Path):
        content = read_file(file_path)
        if content:
            words = set(re.findall(r"\w+", content.lower()))
            self.indexed_files[str(file_path)] = {
                "title": file_path.stem,
                "content": content,
                "words": words,
            }


TantivySearch = SearchIndex


def search_kb(query: str, wiki_dir: Path = None) -> List[Dict[str, Any]]:
    if wiki_dir is None:
        wiki_dir = Path("wiki")

    search = SearchIndex()
    search.index_documents(wiki_dir)

    return search.search(query)


def index_wiki(wiki_dir: Path = None):
    if wiki_dir is None:
        wiki_dir = Path("wiki")

    search = SearchIndex()
    search.rebuild_index(wiki_dir)

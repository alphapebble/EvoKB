import os
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional

import tantivy
from tantivy import Schema, TextField, IndexWriter, Document, Query, QueryParser

from .utils import read_file, list_files


class TantivySearch:
    def __init__(self, index_dir: str = None):
        self.index_dir = index_dir or "clusters/index"
        self.schema = Schema(
            title=TextField(stored=True),
            content=TextField(stored=True),
            path=TextField(stored=True),
        )
        self.index = None
        self._init_index()

    def _init_index(self):
        os.makedirs(self.index_dir, exist_ok=True)
        self.index = tantivy.Index.create_in_dir(self.index_dir, self.schema)

    def index_documents(self, docs_dir: Path):
        """Index all markdown files in the given directory"""
        writer = self.index.writer()

        for file in list_files(docs_dir, "*.md"):
            content = read_file(file)
            if content:
                doc = Document(
                    title=file.stem,
                    content=content[:50000],  # Limit content size
                    path=str(file),
                )
                writer.add_document(doc)

        writer.commit()
        print(f"Indexed {len(list(list_files(docs_dir, '*.md')))} documents")

    def search(self, query_str: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search indexed documents"""
        searcher = self.index.searcher()
        query_parser = QueryParser(self.schema.get_field("content"), self.schema)
        query = query_parser.parse(query_str)

        top_docs = searcher.search(query, top_k)
        results = []

        for doc in top_docs:
            results.append(
                {
                    "title": doc["title"],
                    "path": doc["path"],
                    "snippet": doc["content"][:500],
                    "score": doc.score,
                }
            )

        return results

    def rebuild_index(self, docs_dir: Path):
        """Rebuild the entire index"""
        self._init_index()
        self.index_documents(docs_dir)

    def add_document(self, file_path: Path):
        """Add a single document to the index"""
        content = read_file(file_path)
        if not content:
            return

        writer = self.index.writer()
        doc = Document(
            title=file_path.stem,
            content=content[:50000],
            path=str(file_path),
        )
        writer.add_document(doc)
        writer.commit()


def search_kb(query: str, wiki_dir: Path = None) -> List[Dict[str, Any]]:
    """Convenience function to search the knowledge base"""
    if wiki_dir is None:
        wiki_dir = Path("wiki")

    search = TantivySearch()

    # Check if index exists, if not, build it
    if not Path(search.index_dir).exists() or not list(
        Path(search.index_dir).glob("*")
    ):
        search.index_documents(wiki_dir)

    return search.search(query)


def index_wiki(wiki_dir: Path = None):
    """Index all wiki documents"""
    if wiki_dir is None:
        wiki_dir = Path("wiki")

    search = TantivySearch()
    search.rebuild_index(wiki_dir)

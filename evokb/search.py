# Re-export from new locations for backward compatibility
from evokb.core.search import SearchIndex, search_kb, index_wiki
from evokb.core.retriever import simple_keyword_search


# Placeholder for future Tantivy integration
class TantivySearch(SearchIndex):
    """Placeholder for Tantivy full-text search (not implemented yet)."""

    pass

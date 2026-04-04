# Lazy imports to allow testing without all dependencies installed
def __getattr__(name):
    if name == "query_evo_kb":
        from .retriever import query_evo_kb

        return query_evo_kb
    elif name == "KnowledgeCluster":
        from .cluster import KnowledgeCluster

        return KnowledgeCluster
    elif name == "TantivySearch":
        from .search import TantivySearch

        return TantivySearch
    elif name == "search_kb":
        from .search import search_kb

        return search_kb
    elif name == "index_wiki":
        from .search import index_wiki

        return index_wiki
    elif name == "ContextBuilder":
        from .context import ContextBuilder

        return ContextBuilder
    elif name == "build_context":
        from .context import build_context

        return build_context
    elif name == "AgentClassifier":
        from .agent import AgentClassifier

        return AgentClassifier
    elif name == "classify_query":
        from .agent import classify_query

        return classify_query
    elif name == "classify_query_details":
        from .agent import classify_query_details

        return classify_query_details
    elif name == "QueryIntent":
        from .agent import QueryIntent

        return QueryIntent
    raise AttributeError(f"module 'evokb' has no attribute '{name}'")

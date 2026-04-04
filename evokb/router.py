# Re-export from new locations for backward compatibility
from evokb.core.router import (
    detect_intent,
    route_query,
    Route,
    classify_intent,
    route_and_execute,
)
from evokb.core.learning import LearningStore
from evokb.core.search import SearchIndex, search_kb, index_wiki
from evokb.core.context import ContextBuilder, build_context
from evokb.core.retriever import (
    query_evo_kb,
    compile_to_wiki,
    extract_keywords,
    monte_carlo_sample,
    simple_keyword_search,
    run_autoresearch_iteration,
)

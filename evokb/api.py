from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pathlib import Path

from .search import search_kb, index_wiki
from .context import build_context
from .agent import classify_query_details
from .retriever import query_evo_kb


app = FastAPI(
    title="EvoKB API",
    description="Self-evolving Knowledge Base API",
    version="0.1.0",
)


class QueryRequest(BaseModel):
    query: str
    use_llm: bool = True
    include_context: bool = True


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class IndexRequest(BaseModel):
    wiki_path: Optional[str] = None


class ContextRequest(BaseModel):
    query: str
    search_results: List[Dict[str, Any]]


@app.get("/")
async def root():
    return {"message": "EvoKB API", "version": "0.1.0"}


@app.post("/search")
async def search(request: SearchRequest):
    """Search the knowledge base"""
    try:
        wiki_path = Path("wiki")
        results = search_kb(request.query, wiki_dir=wiki_path)
        return {"results": results[: request.top_k]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/classify")
async def classify(request: QueryRequest):
    """Classify query intent"""
    try:
        result = classify_query_details(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/context")
async def build_ctx(request: ContextRequest):
    """Build context from search results"""
    try:
        context = build_context(request.query, request.search_results)
        return context
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
async def query(request: QueryRequest):
    """Query the knowledge base with LLM"""
    try:
        if request.use_llm:
            answer, cluster = query_evo_kb(request.query)
            return {
                "answer": answer,
                "cluster": {
                    "id": cluster.id,
                    "confidence": cluster.confidence,
                    "source_count": len(cluster.evidences),
                },
            }
        else:
            # Just search
            results = search_kb(request.query)
            return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index")
async def index(request: IndexRequest):
    """Re-index the knowledge base"""
    try:
        wiki_path = Path(request.wiki_path) if request.wiki_path else Path("wiki")
        if not wiki_path.exists():
            raise HTTPException(status_code=404, detail="Wiki directory not found")

        index_wiki(wiki_path)
        return {"message": "Indexing complete"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy"}

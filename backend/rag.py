"""
Retrieval-Augmented Generation (RAG) layer for Jetski SmartHire.

Embeds resume text using Google's Gemini embedding model
(text-embedding-004) and supports semantic search over previously
screened candidates, plus retrieval of relevant context for the
GenAI chat/cover-letter features in genai_features.py.
"""
import math
from typing import List, Dict, Any

import google.generativeai as genai

import database

EMBEDDING_MODEL = "models/text-embedding-004"


def embed_text(text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> List[float]:
    """Generate an embedding vector for a piece of text via Gemini."""
    # Gemini embedding input has a practical token limit; truncate defensively.
    truncated = text[:20000]
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=truncated,
        task_type=task_type,
    )
    return result["embedding"]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def semantic_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Search previously screened resumes/results by meaning rather than
    keyword match, e.g. "candidates with backend Python and AWS experience".
    """
    query_embedding = embed_text(query, task_type="RETRIEVAL_QUERY")

    all_results = database.list_results()
    scored = []
    for r in all_results:
        embedding = r.get("embedding")
        if not embedding:
            continue
        score = cosine_similarity(query_embedding, embedding)
        scored.append(
            {
                "id": r.get("id"),
                "filename": r.get("filename"),
                "score": r.get("score"),
                "status": r.get("status"),
                "feedback": r.get("feedback"),
                "similarity": round(score, 4),
            }
        )

    scored.sort(key=lambda x: x["similarity"], reverse=True)
    return scored[:top_k]


def get_relevant_context(result_id: str, max_chars: int = 12000) -> str:
    """Fetch a stored resume's text to use as grounding context for GenAI features."""
    result = database.get_result(result_id)
    if not result:
        return ""
    return (result.get("resume_text") or "")[:max_chars]

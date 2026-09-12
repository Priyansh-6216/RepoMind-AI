"""
RepoMind AI — Embedding Generator
Generates vector embeddings using Ollama's nomic-embed-text model (local, free).
"""

import structlog
from typing import List
from tenacity import retry, stop_after_attempt, wait_exponential
import ollama as ollama_client

from config import config

logger = structlog.get_logger(__name__)


from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log
import logging

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    before_sleep=before_sleep_log(structlog.get_logger(__name__), logging.WARNING)
)
def _generate_single_embedding(text: str) -> List[float]:
    """Generate embedding for a single text using Ollama."""
    response = ollama_client.embeddings(
        model=config.ollama.embed_model,
        prompt=text,
    )
    return response["embedding"]


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a batch of texts using Ollama nomic-embed-text.

    Ollama processes embeddings locally — no API costs.
    Uses nomic-embed-text which produces 768-dimensional vectors.

    Args:
        texts: List of code chunk content strings

    Returns:
        List of embedding vectors (each 768-dimensional)
    """
    embeddings = []

    for i, text in enumerate(texts):
        try:
            # Truncate extremely long chunks to avoid memory issues
            truncated = text[:8000] if len(text) > 8000 else text

            # Prepend context for better code embeddings
            enhanced_text = f"Code snippet:\n{truncated}"
            embedding = _generate_single_embedding(enhanced_text)
            embeddings.append(embedding)

            if (i + 1) % 10 == 0:
                logger.info("embedding_progress", completed=i + 1, total=len(texts))

        except Exception as e:
            logger.error("embedding_failed", index=i, error=str(e))
            # Return zero vector as fallback
            embeddings.append([0.0] * config.ollama.embedding_dim)

    logger.info("embeddings_generated", count=len(embeddings))
    return embeddings


def generate_single_embedding(text: str) -> List[float]:
    """
    Generate embedding for a single query text.
    Used for similarity search queries.
    """
    try:
        enhanced = f"Search query: {text}"
        return _generate_single_embedding(enhanced)
    except Exception as e:
        logger.error("query_embedding_failed", error=str(e))
        return [0.0] * config.ollama.embedding_dim

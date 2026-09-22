"""
RepoMind AI — Database Operations
Handles all PostgreSQL + pgvector interactions for the worker.
"""

import json
import uuid
import structlog
from typing import List, Optional
from datetime import datetime, timezone

import psycopg2
from psycopg2.extras import execute_values, Json
from pgvector.psycopg2 import register_vector

from config import config
from chunker import CodeChunk

logger = structlog.get_logger(__name__)


def get_connection():
    """Create a new database connection with pgvector support."""
    conn = psycopg2.connect(config.db.url)
    register_vector(conn)
    return conn


# ──────────────────────────────────────────────────────────────
#  Job Status Updates
# ──────────────────────────────────────────────────────────────


def update_job_status(
    job_id: str,
    status: str,
    progress: int = 0,
    error_message: Optional[str] = None,
    total_files: Optional[int] = None,
    processed_files: Optional[int] = None,
):
    """Update an indexing job's status and progress."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            updates = ["status = %s", "progress = %s"]
            params = [status, progress]

            if error_message is not None:
                updates.append("error_message = %s")
                params.append(error_message)

            if total_files is not None:
                updates.append("total_files = %s")
                params.append(total_files)

            if processed_files is not None:
                updates.append("processed_files = %s")
                params.append(processed_files)

            if status == "CLONING":
                updates.append("started_at = %s")
                params.append(datetime.now(timezone.utc))

            if status in ("COMPLETED", "FAILED"):
                updates.append("completed_at = %s")
                params.append(datetime.now(timezone.utc))

            params.append(job_id)
            query = f"UPDATE index_jobs SET {', '.join(updates)} WHERE id = %s"
            cur.execute(query, params)

        conn.commit()
        logger.info(
            "job_status_updated", job_id=job_id, status=status, progress=progress
        )

    except Exception as e:
        conn.rollback()
        logger.error("job_status_update_failed", job_id=job_id, error=str(e))
        raise
    finally:
        conn.close()


def update_repo_status(
    repo_id: str, status: str, file_count: int = 0, chunk_count: int = 0
):
    """Update a repository's status and counts."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE repositories
                   SET status = %s, file_count = %s, chunk_count = %s, updated_at = NOW()
                   WHERE id = %s""",
                (status, file_count, chunk_count, repo_id),
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error("repo_status_update_failed", repo_id=repo_id, error=str(e))
        raise
    finally:
        conn.close()


# ──────────────────────────────────────────────────────────────
#  File & Chunk Storage
# ──────────────────────────────────────────────────────────────


def store_code_file(
    repo_id: str,
    file_path: str,
    language: str,
    size_bytes: int,
    content: str,
) -> str:
    """Store a code file record and return its ID."""
    file_id = str(uuid.uuid4())
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO code_files (id, repository_id, file_path, language, size_bytes, content)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (file_id, repo_id, file_path, language, size_bytes, content),
            )
        conn.commit()
        return file_id

    except Exception as e:
        conn.rollback()
        logger.error("store_file_failed", file_path=file_path, error=str(e))
        raise
    finally:
        conn.close()


def store_code_chunks(
    chunks: List[CodeChunk],
    file_id: str,
    repo_id: str,
    embeddings: List[List[float]],
):
    """
    Bulk insert code chunks with their embeddings into pgvector.

    Args:
        chunks: List of CodeChunk objects
        file_id: UUID of the parent code_file
        repo_id: UUID of the repository
        embeddings: Corresponding embedding vectors
    """
    if not chunks:
        return

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            values = []
            for chunk, embedding in zip(chunks, embeddings):
                import numpy as np

                embedding_array = np.array(embedding, dtype=np.float32)

                values.append(
                    (
                        str(uuid.uuid4()),
                        file_id,
                        repo_id,
                        chunk.chunk_type,
                        chunk.name[:500] if chunk.name else None,
                        chunk.content,
                        chunk.start_line,
                        chunk.end_line,
                        embedding_array,
                        Json(chunk.metadata),
                    )
                )

            execute_values(
                cur,
                """INSERT INTO code_chunks
                   (id, file_id, repository_id, chunk_type, name, content,
                    start_line, end_line, embedding, metadata)
                   VALUES %s""",
                values,
                template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            )

        conn.commit()
        logger.debug("chunks_stored", count=len(chunks), file_id=file_id)

    except Exception as e:
        conn.rollback()
        logger.error("store_chunks_failed", file_id=file_id, error=str(e))
        raise
    finally:
        conn.close()


# ──────────────────────────────────────────────────────────────
#  Query Helpers
# ──────────────────────────────────────────────────────────────


def get_job_details(job_id: str) -> Optional[dict]:
    """Fetch job details including repository info."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT j.id, j.repository_id, j.status,
                          r.url, r.name, r.owner
                   FROM index_jobs j
                   JOIN repositories r ON r.id = j.repository_id
                   WHERE j.id = %s""",
                (job_id,),
            )
            row = cur.fetchone()
            if row:
                return {
                    "job_id": str(row[0]),
                    "repository_id": str(row[1]),
                    "status": row[2],
                    "repo_url": row[3],
                    "repo_name": row[4],
                    "repo_owner": row[5],
                }
            return None
    finally:
        conn.close()

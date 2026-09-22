"""
RepoMind AI — Worker Main Entry Point
Redis consumer that processes repository indexing jobs through the
full pipeline: Clone → Parse → Chunk → Embed → Store.
"""

import json
import sys
import time
import signal
import traceback
import structlog
import redis

from config import config
from cloner import clone_repository, cleanup_clone, get_repo_metadata
from parser import parse_repository
from chunker import chunk_code
from embedder import generate_embeddings
from db import (
    update_job_status,
    update_repo_status,
    store_code_file,
    store_code_chunks,
    get_job_details,
)

# ── Logging Setup ─────────────────────────────────────────────
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.dev.ConsoleRenderer(colors=True),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger("repomind.worker")

# ── Graceful Shutdown ─────────────────────────────────────────
shutdown_requested = False


def signal_handler(signum, frame):
    global shutdown_requested
    shutdown_requested = True
    logger.info("shutdown_requested", signal=signum)


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


# ══════════════════════════════════════════════════════════════
#  Core Pipeline
# ══════════════════════════════════════════════════════════════


def process_job(job_id: str, redis_client=None):
    """
    Execute the full indexing pipeline for a repository.

    Pipeline stages:
    1. CLONING   — Shallow git clone
    2. PARSING   — Walk file tree, read source files
    3. EMBEDDING — Generate vector embeddings for each chunk
    4. COMPLETED — All chunks stored in pgvector
    """
    logger.info("processing_job", job_id=job_id)

    # Fetch job details
    job = get_job_details(job_id)
    if not job:
        logger.error("job_not_found", job_id=job_id)
        return

    repo_id = job["repository_id"]
    repo_url = job["repo_url"]

    try:
        # ── Stage 1: Clone ────────────────────────────────────
        update_job_status(job_id, "CLONING", progress=5)
        update_repo_status(repo_id, "INDEXING")

        clone_path = clone_repository(repo_url, repo_id)

        # ── Stage 2: Parse ────────────────────────────────────
        update_job_status(job_id, "PARSING", progress=20)

        parsed_files = list(parse_repository(clone_path))
        total_files = len(parsed_files)

        update_job_status(job_id, "PARSING", progress=30, total_files=total_files)
        logger.info("files_parsed", count=total_files)

        # ── Stage 3: Chunk + Embed ────────────────────────────
        update_job_status(job_id, "EMBEDDING", progress=40)

        total_chunks = 0
        batch_texts = []
        batch_chunks = []
        batch_file_ids = []

        for file_idx, parsed_file in enumerate(parsed_files):
            # Store the code file
            file_id = store_code_file(
                repo_id=repo_id,
                file_path=parsed_file.file_path,
                language=parsed_file.language,
                size_bytes=parsed_file.size_bytes,
                content=parsed_file.content,
            )

            # Chunk the code
            chunks = chunk_code(
                content=parsed_file.content,
                file_path=parsed_file.file_path,
                language=parsed_file.language,
            )

            for chunk in chunks:
                batch_texts.append(chunk.content)
                batch_chunks.append(chunk)
                batch_file_ids.append(file_id)

            # Process in batches
            if len(batch_texts) >= config.app.batch_size:
                embeddings = generate_embeddings(batch_texts)

                # Group by file_id for storage
                file_groups = {}
                for chunk, emb, fid in zip(batch_chunks, embeddings, batch_file_ids):
                    if fid not in file_groups:
                        file_groups[fid] = ([], [])
                    file_groups[fid][0].append(chunk)
                    file_groups[fid][1].append(emb)

                for fid, (file_chunks, file_embeddings) in file_groups.items():
                    store_code_chunks(file_chunks, fid, repo_id, file_embeddings)

                total_chunks += len(batch_texts)
                batch_texts = []
                batch_chunks = []
                batch_file_ids = []

            # Update progress
            progress = 40 + int((file_idx + 1) / max(total_files, 1) * 50)
            update_job_status(
                job_id,
                "EMBEDDING",
                progress=min(progress, 90),
                processed_files=file_idx + 1,
            )

        # Process remaining batch
        if batch_texts:
            embeddings = generate_embeddings(batch_texts)

            file_groups = {}
            for chunk, emb, fid in zip(batch_chunks, embeddings, batch_file_ids):
                if fid not in file_groups:
                    file_groups[fid] = ([], [])
                file_groups[fid][0].append(chunk)
                file_groups[fid][1].append(emb)

            for fid, (file_chunks, file_embeddings) in file_groups.items():
                store_code_chunks(file_chunks, fid, repo_id, file_embeddings)

            total_chunks += len(batch_texts)

        # ── Stage 4: Complete ─────────────────────────────────
        update_job_status(
            job_id, "COMPLETED", progress=100, processed_files=total_files
        )
        update_repo_status(
            repo_id, "READY", file_count=total_files, chunk_count=total_chunks
        )

        logger.info(
            "job_completed",
            job_id=job_id,
            files=total_files,
            chunks=total_chunks,
        )

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        logger.error(
            "job_failed",
            job_id=job_id,
            error=error_msg,
            traceback=traceback.format_exc(),
        )
        update_job_status(job_id, "FAILED", error_message=error_msg)
        update_repo_status(repo_id, "FAILED")
        if redis_client:
            try:
                redis_client.lpush(
                    "repomind:jobs:dlq",
                    json.dumps(
                        {
                            "job_id": job_id,
                            "repository_id": repo_id,
                            "error": error_msg,
                            "failed_at": time.time(),
                        }
                    ),
                )
                logger.info("pushed_to_dlq", job_id=job_id)
            except Exception as dlq_err:
                logger.error("dlq_push_failed", error=str(dlq_err))

    finally:
        # Clean up cloned repo
        cleanup_clone(repo_id)


# ══════════════════════════════════════════════════════════════
#  Redis Consumer Loop
# ══════════════════════════════════════════════════════════════


def main():
    """Main worker loop — consumes jobs from Redis queue."""
    logger.info("worker_starting", queue=config.redis.job_queue)

    redis_client = redis.from_url(config.redis.url, decode_responses=True)

    # Verify Redis connection
    try:
        redis_client.ping()
        logger.info("redis_connected", url=config.redis.url)
    except redis.ConnectionError as e:
        logger.error("redis_connection_failed", error=str(e))
        sys.exit(1)

    logger.info("worker_ready", message="Listening for indexing jobs...")

    while not shutdown_requested:
        try:
            # Blocking pop with 5 second timeout
            result = redis_client.brpop(config.redis.job_queue, timeout=5)

            if result is None:
                continue  # Timeout, check shutdown flag

            _, job_data = result
            job = json.loads(job_data)
            job_id = job.get("job_id")

            if not job_id:
                logger.warning("invalid_job_payload", data=job_data)
                continue

            logger.info("job_received", job_id=job_id)
            process_job(job_id, redis_client)

        except redis.ConnectionError:
            logger.warning("redis_reconnecting")
            time.sleep(5)

        except Exception as e:
            logger.error("worker_error", error=str(e))
            time.sleep(2)

    logger.info("worker_shutdown_complete")


if __name__ == "__main__":
    main()

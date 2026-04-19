"""
RepoMind AI — Repository Cloner
Performs shallow git clones of public GitHub repositories.
"""

import os
import shutil
import structlog
from git import Repo, GitCommandError
from config import config

logger = structlog.get_logger(__name__)


def clone_repository(repo_url: str, repo_id: str) -> str:
    """
    Shallow-clone a GitHub repository to local disk.

    Args:
        repo_url: Full GitHub URL (e.g., https://github.com/owner/repo)
        repo_id: UUID of the repository record in the database

    Returns:
        Absolute path to the cloned repository directory

    Raises:
        GitCommandError: If cloning fails (invalid URL, private repo, etc.)
    """
    clone_path = os.path.join(config.app.clone_dir, repo_id)

    # Clean up any previous clone attempt
    if os.path.exists(clone_path):
        logger.info("cleaning_previous_clone", path=clone_path)
        shutil.rmtree(clone_path, ignore_errors=True)

    logger.info("cloning_repository", url=repo_url, target=clone_path)

    try:
        Repo.clone_from(
            repo_url,
            clone_path,
            depth=1,               # Shallow clone — only latest commit
            single_branch=True,
            no_tags=True,
        )
        logger.info("clone_complete", path=clone_path)
        return clone_path

    except GitCommandError as e:
        logger.error("clone_failed", url=repo_url, error=str(e))
        raise


def cleanup_clone(repo_id: str) -> None:
    """Remove a cloned repository from disk after processing."""
    clone_path = os.path.join(config.app.clone_dir, repo_id)
    if os.path.exists(clone_path):
        shutil.rmtree(clone_path, ignore_errors=True)
        logger.info("clone_cleaned_up", path=clone_path)


def get_repo_metadata(repo_url: str) -> dict:
    """
    Extract owner and repo name from a GitHub URL.

    Args:
        repo_url: GitHub URL (supports both https and .git formats)

    Returns:
        Dict with 'owner' and 'name' keys
    """
    # Normalize URL
    url = repo_url.rstrip("/").rstrip(".git")
    parts = url.split("/")

    return {
        "owner": parts[-2] if len(parts) >= 2 else "unknown",
        "name": parts[-1] if len(parts) >= 1 else "unknown",
    }

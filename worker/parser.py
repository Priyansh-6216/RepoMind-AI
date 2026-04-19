"""
RepoMind AI — Code File Parser
Walks a cloned repository and extracts source files with metadata.
"""

import os
import structlog
from typing import Generator
from dataclasses import dataclass
from config import config

logger = structlog.get_logger(__name__)

# Language detection by file extension
EXTENSION_LANGUAGE_MAP = {
    ".py": "python",
    ".java": "java",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".cpp": "cpp",
    ".c": "c",
    ".h": "c",
    ".cs": "csharp",
    ".kt": "kotlin",
    ".swift": "swift",
    ".scala": "scala",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".sql": "sql",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".toml": "toml",
    ".md": "markdown",
    ".txt": "text",
    ".xml": "xml",
    ".gradle": "gradle",
    ".sh": "shell",
    ".bash": "shell",
    ".dockerfile": "dockerfile",
}


@dataclass
class ParsedFile:
    """Represents a single parsed source file."""
    file_path: str      # Relative path from repo root
    language: str       # Detected language
    content: str        # Raw file content
    size_bytes: int     # File size


def parse_repository(repo_path: str) -> Generator[ParsedFile, None, None]:
    """
    Walk a cloned repository and yield parsed source files.

    Skips:
    - Files larger than max_file_size_bytes
    - Files in excluded directories (node_modules, .git, etc.)
    - Files with unsupported extensions
    - Binary files (detected by null byte check)

    Args:
        repo_path: Absolute path to cloned repository

    Yields:
        ParsedFile objects for each valid source file
    """
    file_count = 0
    skipped_count = 0

    for root, dirs, files in os.walk(repo_path):
        # Filter out excluded directories (modifies in-place for os.walk)
        dirs[:] = [
            d for d in dirs
            if d not in config.app.skip_dirs and not d.startswith(".")
        ]

        for filename in files:
            filepath = os.path.join(root, filename)
            relative_path = os.path.relpath(filepath, repo_path)

            # Check extension
            _, ext = os.path.splitext(filename)
            ext = ext.lower()

            if ext not in config.app.supported_extensions:
                skipped_count += 1
                continue

            # Check file size
            try:
                file_size = os.path.getsize(filepath)
            except OSError:
                continue

            if file_size > config.app.max_file_size_bytes:
                logger.debug("skipping_large_file", path=relative_path, size=file_size)
                skipped_count += 1
                continue

            if file_size == 0:
                continue

            # Read content
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except (IOError, UnicodeDecodeError):
                skipped_count += 1
                continue

            # Skip binary files (null byte heuristic)
            if "\x00" in content[:1024]:
                skipped_count += 1
                continue

            language = EXTENSION_LANGUAGE_MAP.get(ext, "unknown")
            file_count += 1

            yield ParsedFile(
                file_path=relative_path.replace("\\", "/"),  # Normalize to unix paths
                language=language,
                content=content,
                size_bytes=file_size,
            )

    logger.info(
        "parsing_complete",
        total_files=file_count,
        skipped_files=skipped_count,
    )

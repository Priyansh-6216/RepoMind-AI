"""
RepoMind AI — Worker Configuration
Loads environment variables for database, Redis, and Ollama connections.
"""

import os
from dataclasses import dataclass, field


@dataclass
class DatabaseConfig:
    """PostgreSQL + pgvector connection settings."""

    url: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            "postgresql://repomind:repomind_secret_2024@localhost:5432/repomind",
        )
    )


@dataclass
class RedisConfig:
    """Redis queue connection settings."""

    url: str = field(
        default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379")
    )
    job_queue: str = "repomind:index_jobs"
    status_channel: str = "repomind:job_status"


@dataclass
class OllamaConfig:
    """Ollama local LLM settings."""

    base_url: str = field(
        default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    )
    embed_model: str = field(
        default_factory=lambda: os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
    )
    embedding_dim: int = 768  # nomic-embed-text output dimension


@dataclass
class AppConfig:
    """Application-level settings."""

    clone_dir: str = field(
        default_factory=lambda: os.getenv("CLONE_DIR", "/tmp/repomind-repos")
    )
    max_file_size_bytes: int = 500_000  # Skip files > 500KB
    batch_size: int = 20  # Embedding batch size
    supported_extensions: tuple = (
        ".py",
        ".java",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".go",
        ".rs",
        ".rb",
        ".cpp",
        ".c",
        ".h",
        ".cs",
        ".kt",
        ".swift",
        ".scala",
        ".html",
        ".css",
        ".scss",
        ".sql",
        ".yaml",
        ".yml",
        ".json",
        ".toml",
        ".md",
        ".txt",
        ".xml",
        ".gradle",
        ".sh",
        ".bash",
        ".dockerfile",
    )
    skip_dirs: tuple = (
        "node_modules",
        ".git",
        "__pycache__",
        ".idea",
        ".vscode",
        "venv",
        "env",
        ".env",
        "dist",
        "build",
        "target",
        ".gradle",
        ".mvn",
        "vendor",
        ".next",
        "coverage",
    )


@dataclass
class Config:
    """Root configuration container."""

    db: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    app: AppConfig = field(default_factory=AppConfig)


# Singleton
config = Config()

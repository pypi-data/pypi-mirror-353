"""
GitLab Configuration Module

Shared configuration for GitLab API interactions, logging setup,
and common constants used across GitLab-related modules.
"""

import logging
import os


class GitLabConfig:
    """GitLab API configuration and constants."""

    # --- GitLab API Configuration ---
    BASE_URL = "https://gitlab.cern.ch"
    API_VERSION = "v4"
    REST_API_URL = f"{BASE_URL}/api/{API_VERSION}"
    GRAPHQL_ENDPOINT = os.getenv("GITLAB_GRAPHQL_ENDPOINT", f"{BASE_URL}/api/graphql")

    # --- Authentication ---
    PRIVATE_TOKEN = os.getenv("GITLAB_PAT")

    # Validate that required environment variables are set
    if not PRIVATE_TOKEN:
        raise ValueError("GITLAB_PAT environment variable is not set")

    # --- Request Configuration ---
    DEFAULT_TIMEOUT = 30
    GRAPHQL_TIMEOUT = 60
    RETRY_AFTER_DEFAULT = 10

    # --- Project Filtering Configuration ---
    PROJECT_PATH_BLACKLIST: list[str] = ["cms", "lhcb", "alice", "faser", "archive", "atlas-physics-office", "ana-"]
    MIN_NUM_MARKDOWN_FILES: int = 5

    @classmethod
    def get_rest_headers(cls) -> dict:
        """Get headers for REST API requests."""
        return {"PRIVATE-TOKEN": cls.PRIVATE_TOKEN}

    @classmethod
    def get_graphql_headers(cls) -> dict:
        """Get headers for GraphQL API requests."""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {cls.PRIVATE_TOKEN}",
        }

    @classmethod
    def get_blacklist_lowercase(cls) -> list[str]:
        """Get project path blacklist in lowercase for case-insensitive comparison."""
        return [item.lower() for item in cls.PROJECT_PATH_BLACKLIST]


class LoggingConfig:
    """Shared logging configuration."""

    # --- Logging Format ---
    LOG_FORMAT = "%(asctime)s %(levelname)s: %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    DEFAULT_LEVEL = logging.INFO

    @classmethod
    def setup_basic_logging(cls, level: int = None) -> None:
        """Set up basic logging configuration."""
        if level is None:
            level = cls.DEFAULT_LEVEL

        logging.basicConfig(level=level, format=cls.LOG_FORMAT, datefmt=cls.DATE_FORMAT)

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get a logger with the specified name."""
        return logging.getLogger(name)


# Module-level convenience functions
def setup_logging(level: int = None) -> None:
    """Convenience function to set up logging."""
    LoggingConfig.setup_basic_logging(level)


def get_config() -> GitLabConfig:
    """Get the GitLab configuration instance."""
    return GitLabConfig

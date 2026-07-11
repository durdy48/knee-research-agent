"""Centralised, typed configuration (pydantic-settings).

Everything the system needs to decide — which model, where the Obsidian vault is, the
Git repo path, API keys, dry-run — lives here, read from environment variables
(prefix `KRA_`) or a `.env` file. The core never reads configuration directly.
"""
from __future__ import annotations

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="KRA_", env_file=".env", extra="ignore")

    ai_model: str = "claude"
    obsidian_vault: Optional[str] = None
    git_repo: Optional[str] = None
    dry_run: bool = True
    anthropic_api_key: Optional[str] = None
    pubmed_api_key: Optional[str] = None


def load_settings() -> Settings:
    return Settings()

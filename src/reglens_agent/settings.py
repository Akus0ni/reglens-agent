"""Settings from environment variables only (spec 0001, R1.2). Secrets are read, never logged or stored."""

import os
from dataclasses import dataclass

PLANNER_MODEL = "claude-sonnet-5-5"
RESEARCH_MODEL = "claude-haiku-5-5"
ASSESSOR_MODEL = "claude-sonnet-5-5"


class SettingsError(Exception):
    """A required environment variable is missing or invalid."""


@dataclass(frozen=True)
class Settings:
    reglens_mcp_url: str
    reglens_api_key: str | None
    anthropic_api_key_set: bool
    database_url: str | None
    issue_repo: str
    otlp_endpoint: str

    @staticmethod
    def from_env() -> "Settings":
        return Settings(
            reglens_mcp_url=os.environ.get("REGLENS_MCP_URL", "http://127.0.0.1:5180/mcp"),
            reglens_api_key=os.environ.get("REGLENS_API_KEY") or None,
            anthropic_api_key_set=bool(os.environ.get("ANTHROPIC_API_KEY")),
            database_url=os.environ.get("AGENT_DATABASE_URL") or None,
            issue_repo=os.environ.get("AGENT_ISSUE_REPO", "Akus0ni/reglens-agent"),
            otlp_endpoint=os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://127.0.0.1:4317"),
        )

    def require(self, *names: str) -> None:
        """Fails naming every missing variable the command needs."""
        present = {
            "ANTHROPIC_API_KEY": self.anthropic_api_key_set,
            "REGLENS_API_KEY": self.reglens_api_key is not None,
            "AGENT_DATABASE_URL": self.database_url is not None,
        }
        missing = [name for name in names if not present[name]]
        if missing:
            raise SettingsError(f"Missing environment variable(s): {', '.join(missing)}. See CLAUDE.md, Environment.")

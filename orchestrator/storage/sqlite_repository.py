"""SQLite-backed repository for orchestrator state without external ORM dependencies."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from orchestrator.state import OrchestratorState


class SQLiteOrchestratorStateRepository:
    """Persist orchestrator state using the standard library sqlite3 module."""

    def __init__(self, database_url: str = "sqlite:///./orchestrator_state.db") -> None:
        if not database_url.startswith("sqlite:///"):
            raise ValueError("Only file-based sqlite URLs are supported, e.g. 'sqlite:///./state.db'")

        database_path = database_url.replace("sqlite:///", "", 1)
        self.path = Path(database_path).expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialise()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _initialise(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS orchestrator_state (
                    key TEXT PRIMARY KEY,
                    memory TEXT NOT NULL,
                    plans TEXT NOT NULL,
                    executions TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def load_state(self) -> OrchestratorState:
        """Load the orchestrator state from the backing store."""

        with self._connect() as connection:
            cursor = connection.execute(
                "SELECT memory, plans, executions FROM orchestrator_state WHERE key = ?", ("singleton",)
            )
            row = cursor.fetchone()

        if row is None:
            return OrchestratorState()

        memory_json, plans_json, executions_json = row
        return OrchestratorState(
            memory=self._loads(memory_json),
            plans=self._loads(plans_json),
            executions=self._loads(executions_json),
        )

    def save_state(self, state: OrchestratorState) -> None:
        """Persist the orchestrator state to the backing store."""

        payload = {
            "memory": json.dumps(state.memory),
            "plans": json.dumps(state.plans),
            "executions": json.dumps(state.executions),
        }

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO orchestrator_state (key, memory, plans, executions)
                VALUES (:key, :memory, :plans, :executions)
                ON CONFLICT(key) DO UPDATE SET
                    memory = excluded.memory,
                    plans = excluded.plans,
                    executions = excluded.executions
                """,
                {"key": "singleton", **payload},
            )
            connection.commit()

    def clear(self) -> None:
        """Remove any persisted orchestrator state."""

        with self._connect() as connection:
            connection.execute("DELETE FROM orchestrator_state WHERE key = ?", ("singleton",))
            connection.commit()

    @staticmethod
    def _loads(value: Any) -> dict[str, Any]:
        if value in (None, ""):
            return {}
        try:
            data = json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return {}
        if not isinstance(data, dict):
            return {}
        return data


__all__ = ["SQLiteOrchestratorStateRepository"]

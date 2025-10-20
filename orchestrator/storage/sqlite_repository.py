"""SQLite-backed persistence for orchestrator state using SQLModel."""

from __future__ import annotations

from typing import Any

from sqlalchemy import Column, JSON
from sqlmodel import Field, Session, SQLModel, create_engine

from orchestrator.state import OrchestratorState


class OrchestratorStateRecord(SQLModel, table=True):
    """SQLModel mapping for persisting orchestrator state."""

    key: str = Field(default="singleton", primary_key=True)
    memory: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False),
    )
    plans: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False),
    )
    executions: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False),
    )


class SQLiteOrchestratorStateRepository:
    """Repository persisting orchestrator state to a SQLite database."""

    def __init__(self, database_url: str = "sqlite:///./orchestrator_state.db") -> None:
        self.engine = create_engine(database_url, echo=False)
        SQLModel.metadata.create_all(self.engine)

    def load_state(self) -> OrchestratorState:
        """Load the orchestrator state from storage."""

        with Session(self.engine) as session:
            record = session.get(OrchestratorStateRecord, "singleton")
            if record is None:
                return OrchestratorState()
            return OrchestratorState(
                memory=dict(record.memory or {}),
                plans=dict(record.plans or {}),
                executions=dict(record.executions or {}),
            )

    def save_state(self, state: OrchestratorState) -> None:
        """Persist the orchestrator state to storage."""

        payload = {
            "memory": dict(state.memory),
            "plans": dict(state.plans),
            "executions": dict(state.executions),
        }

        with Session(self.engine) as session:
            record = session.get(OrchestratorStateRecord, "singleton")
            if record is None:
                record = OrchestratorStateRecord(key="singleton", **payload)
            else:
                record.memory = payload["memory"]
                record.plans = payload["plans"]
                record.executions = payload["executions"]

            session.add(record)
            session.commit()

    def clear(self) -> None:
        """Remove any persisted orchestrator state."""

        with Session(self.engine) as session:
            record = session.get(OrchestratorStateRecord, "singleton")
            if record is not None:
                session.delete(record)
                session.commit()

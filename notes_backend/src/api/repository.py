from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Generator, List, Optional

from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, create_engine, select, insert, update, delete
from sqlalchemy.engine import Engine, Connection

from .models import Note, NoteCreate, NoteUpdate


DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "notes.db")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class NoteRecord:
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime


class NotesRepository:
    """Simple repository using SQLite via SQLAlchemy Core."""

    def __init__(self, db_url: Optional[str] = None) -> None:
        # Use file-based SQLite for persistence across restarts
        if db_url is None:
            db_path = os.path.abspath(DEFAULT_DB_PATH)
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            db_url = f"sqlite:///{db_path}"

        self.engine: Engine = create_engine(db_url, future=True)
        self.metadata = MetaData()

        # Define table
        self.notes_table = Table(
            "notes",
            self.metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("title", String(255), nullable=False),
            Column("content", String, nullable=False),
            Column("created_at", DateTime(timezone=True), nullable=False),
            Column("updated_at", DateTime(timezone=True), nullable=False),
        )
        # Create tables if not exist (migration-free)
        self.metadata.create_all(self.engine)

    @contextmanager
    def _connect(self) -> Generator[Connection, None, None]:
        conn = self.engine.connect()
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    # PUBLIC_INTERFACE
    def list_notes(self) -> List[Note]:
        """Return all notes ordered by created_at desc."""
        with self._connect() as conn:
            stmt = select(self.notes_table).order_by(self.notes_table.c.created_at.desc())
            rows = conn.execute(stmt).mappings().all()
            return [self._to_model(r) for r in rows]

    # PUBLIC_INTERFACE
    def create_note(self, payload: NoteCreate) -> Note:
        """Create a new note and return it."""
        now = _utcnow()
        data = {
            "title": payload.title,
            "content": payload.content,
            "created_at": now,
            "updated_at": now,
        }
        with self._connect() as conn:
            res = conn.execute(insert(self.notes_table).values(**data))
            new_id = res.inserted_primary_key[0]
            row = conn.execute(
                select(self.notes_table).where(self.notes_table.c.id == new_id)
            ).mappings().one()
            return self._to_model(row)

    # PUBLIC_INTERFACE
    def get_note(self, note_id: int) -> Optional[Note]:
        """Get a note by id or return None."""
        with self._connect() as conn:
            row = conn.execute(
                select(self.notes_table).where(self.notes_table.c.id == note_id)
            ).mappings().first()
            return self._to_model(row) if row else None

    # PUBLIC_INTERFACE
    def update_note(self, note_id: int, payload: NoteUpdate) -> Optional[Note]:
        """Update a note with provided fields; returns updated note or None."""
        update_data = {}
        if payload.title is not None:
            update_data["title"] = payload.title
        if payload.content is not None:
            update_data["content"] = payload.content
        if not update_data:
            # No fields to update; still bump updated_at for idempotency
            update_data["updated_at"] = _utcnow()
        else:
            update_data["updated_at"] = _utcnow()

        with self._connect() as conn:
            res = conn.execute(
                update(self.notes_table)
                .where(self.notes_table.c.id == note_id)
                .values(**update_data)
            )
            if res.rowcount == 0:
                return None
            row = conn.execute(
                select(self.notes_table).where(self.notes_table.c.id == note_id)
            ).mappings().one()
            return self._to_model(row)

    # PUBLIC_INTERFACE
    def delete_note(self, note_id: int) -> bool:
        """Delete a note by id; returns True if deleted, False if not found."""
        with self._connect() as conn:
            res = conn.execute(delete(self.notes_table).where(self.notes_table.c.id == note_id))
            return res.rowcount > 0

    def _to_model(self, row) -> Note:
        return Note(
            id=row["id"],
            title=row["title"],
            content=row["content"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

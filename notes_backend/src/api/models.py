from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# PUBLIC_INTERFACE
class NoteBase(BaseModel):
    """Base fields for Note without id and timestamps."""
    title: str = Field(..., description="Title of the note", min_length=1, max_length=255)
    content: str = Field(..., description="Content of the note")


# PUBLIC_INTERFACE
class NoteCreate(NoteBase):
    """Payload to create a new note."""
    pass


# PUBLIC_INTERFACE
class NoteUpdate(BaseModel):
    """Payload to update an existing note."""
    title: Optional[str] = Field(None, description="Updated title of the note", min_length=1, max_length=255)
    content: Optional[str] = Field(None, description="Updated content of the note")


# PUBLIC_INTERFACE
class Note(NoteBase):
    """Response model for a note with id and timestamps."""
    id: int = Field(..., description="Unique identifier for the note")
    created_at: datetime = Field(..., description="Creation time in ISO format")
    updated_at: datetime = Field(..., description="Last update time in ISO format")

    class Config:
        from_attributes = True

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List

from .models import Note, NoteCreate, NoteUpdate
from .repository import NotesRepository

app = FastAPI(
    title="Notes API",
    description="A simple Notes manager with CRUD operations.",
    version="1.0.0",
    openapi_tags=[
        {"name": "health", "description": "Health check endpoint"},
        {"name": "notes", "description": "Operations with notes"},
    ],
)

# CORS: allow localhost origins for potential frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "*",  # keep permissive to satisfy acceptance criteria
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

repo = NotesRepository()


@app.get("/", tags=["health"], summary="Health Check")
def health_check():
    """Health check endpoint to verify service is running."""
    return {"message": "Healthy"}


# PUBLIC_INTERFACE
@app.get(
    "/notes",
    response_model=List[Note],
    tags=["notes"],
    summary="List notes",
    description="Retrieve all notes ordered by creation time descending.",
)
def list_notes() -> List[Note]:
    """Return all notes."""
    return repo.list_notes()


# PUBLIC_INTERFACE
@app.post(
    "/notes",
    response_model=Note,
    status_code=status.HTTP_201_CREATED,
    tags=["notes"],
    summary="Create note",
    description="Create a new note with title and content. Returns the created note.",
)
def create_note(payload: NoteCreate):
    """Create a note and return it with Location header."""
    note = repo.create_note(payload)
    headers = {"Location": f"/notes/{note.id}"}
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=note.model_dump(mode="json"), headers=headers)


# PUBLIC_INTERFACE
@app.get(
    "/notes/{note_id}",
    response_model=Note,
    tags=["notes"],
    summary="Get note",
    description="Retrieve a note by its id.",
)
def get_note(note_id: int) -> Note:
    """Get a single note by id."""
    note = repo.get_note(note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


# PUBLIC_INTERFACE
@app.put(
    "/notes/{note_id}",
    response_model=Note,
    tags=["notes"],
    summary="Update note",
    description="Update fields of a note by its id. Both title and content are optional.",
)
def update_note(note_id: int, payload: NoteUpdate) -> Note:
    """Update a note and return the updated representation."""
    note = repo.update_note(note_id, payload)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


# PUBLIC_INTERFACE
@app.delete(
    "/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["notes"],
    summary="Delete note",
    description="Delete a note by its id. Returns 204 No Content on success.",
)
def delete_note(note_id: int):
    """Delete a note by id."""
    deleted = repo.delete_note(note_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)

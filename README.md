# simple-notes-manager-39312-39335

Simple Notes Manager backend (FastAPI) providing CRUD endpoints with SQLite persistence.

## Run
The service is configured to run in the provided environment. No extra environment variables required.

- Docs: http://localhost:3001/docs
- OpenAPI: http://localhost:3001/openapi.json

## Endpoints

- GET / — Health check
- GET /notes — List all notes
- POST /notes — Create a note
- GET /notes/{id} — Get a note by id
- PUT /notes/{id} — Update a note by id
- DELETE /notes/{id} — Delete a note by id

Models:
- NoteCreate: { title: string, content: string }
- NoteUpdate: { title?: string, content?: string }
- Note: { id: number, title: string, content: string, created_at: ISO string, updated_at: ISO string }

## Curl examples

List notes:
```
curl -s http://localhost:3001/notes | jq .
```

Create note:
```
curl -i -X POST http://localhost:3001/notes \
  -H "Content-Type: application/json" \
  -d '{"title":"First note","content":"Hello world"}'
```

Get by id:
```
curl -s http://localhost:3001/notes/1 | jq .
```

Update:
```
curl -s -X PUT http://localhost:3001/notes/1 \
  -H "Content-Type: application/json" \
  -d '{"content":"Updated content"}' | jq .
```

Delete:
```
curl -i -X DELETE http://localhost:3001/notes/1
```

## Notes
- On create, API returns 201 Created and sets Location header to /notes/{id}.
- 404 is returned for missing ids.
- Delete returns 204 No Content.
- CORS allows localhost origins (and is permissive for ease of development).
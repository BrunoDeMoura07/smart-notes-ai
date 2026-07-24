import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.note import Note
from app.repositories import note_repository
from app.schemas.note import NoteCreate
from app.services import file_service
from app.workers import queue_worker


def create_text_note(db: Session, *, user_id: uuid.UUID, payload: NoteCreate) -> Note:
    title = payload.title or payload.content[:50]
    note = note_repository.create(
        db, user_id=user_id, title=title, source_type="text", original_text=payload.content
    )
    queue_worker.enqueue(note.id)
    return note


def create_upload_note(db: Session, *, user_id: uuid.UUID, file: UploadFile, title: str | None) -> Note:
    source_type = file_service.determine_source_type(file)
    file_path, original_filename = file_service.save_upload(file)
    note = note_repository.create(
        db,
        user_id=user_id,
        title=title or original_filename,
        source_type=source_type,
        original_filename=original_filename,
        file_path=file_path,
    )
    queue_worker.enqueue(note.id)
    return note


def get_note(db: Session, *, user_id: uuid.UUID, note_id: uuid.UUID) -> Note:
    note = note_repository.get_by_id(db, note_id=note_id, user_id=user_id)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nota não encontrada.")
    return note


def list_notes(
    db: Session,
    *,
    user_id: uuid.UUID,
    search: str | None,
    status_filter: str | None,
    page: int,
    page_size: int,
) -> tuple[list[Note], int]:
    return note_repository.list_notes(
        db, user_id=user_id, search=search, status_filter=status_filter, page=page, page_size=page_size
    )


def update_note(
    db: Session, *, user_id: uuid.UUID, note_id: uuid.UUID, title: str | None, tags: list[str] | None
) -> Note:
    note = get_note(db, user_id=user_id, note_id=note_id)
    if title is not None:
        note.title = title
    if tags is not None:
        note.tags = tags
    db.commit()
    db.refresh(note)
    return note


def delete_note(db: Session, *, user_id: uuid.UUID, note_id: uuid.UUID) -> None:
    note = get_note(db, user_id=user_id, note_id=note_id)
    file_service.delete_file(note.file_path)
    note_repository.delete(db, note)

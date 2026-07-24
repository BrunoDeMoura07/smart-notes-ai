import uuid

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.note import NoteAccepted, NoteCreate, NoteList, NoteRead, NoteStatus, NoteUpdate
from app.services import note_service

router = APIRouter(prefix="/api/notes", tags=["notes"])


@router.post("", response_model=NoteAccepted, status_code=status.HTTP_202_ACCEPTED)
def create_note(
    payload: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = note_service.create_text_note(db, user_id=current_user.id, payload=payload)
    return NoteAccepted(id=note.id, status=note.status)


@router.post("/upload", response_model=NoteAccepted, status_code=status.HTTP_202_ACCEPTED)
def upload_note(
    file: UploadFile = File(...),
    title: str | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = note_service.create_upload_note(db, user_id=current_user.id, file=file, title=title)
    return NoteAccepted(id=note.id, status=note.status)


@router.get("", response_model=NoteList)
def list_notes(
    search: str | None = None,
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = note_service.list_notes(
        db,
        user_id=current_user.id,
        search=search,
        status_filter=status_filter,
        page=page,
        page_size=page_size,
    )
    return NoteList(items=items, total=total, page=page, page_size=page_size)


@router.get("/{note_id}", response_model=NoteRead)
def get_note(
    note_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return note_service.get_note(db, user_id=current_user.id, note_id=note_id)


@router.get("/{note_id}/status", response_model=NoteStatus)
def get_note_status(
    note_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return note_service.get_note(db, user_id=current_user.id, note_id=note_id)


@router.patch("/{note_id}", response_model=NoteRead)
def update_note(
    note_id: uuid.UUID,
    payload: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return note_service.update_note(
        db, user_id=current_user.id, note_id=note_id, title=payload.title, tags=payload.tags
    )


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note_service.delete_note(db, user_id=current_user.id, note_id=note_id)

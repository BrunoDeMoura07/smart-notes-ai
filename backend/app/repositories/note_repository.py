import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.note import Note


def create(
    db: Session,
    *,
    user_id: uuid.UUID,
    title: str | None,
    source_type: str,
    original_text: str | None = None,
    original_filename: str | None = None,
    file_path: str | None = None,
) -> Note:
    note = Note(
        user_id=user_id,
        title=title,
        source_type=source_type,
        original_text=original_text,
        original_filename=original_filename,
        file_path=file_path,
        status="pending",
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def get_by_id(db: Session, *, note_id: uuid.UUID, user_id: uuid.UUID) -> Note | None:
    return db.execute(
        select(Note).where(Note.id == note_id, Note.user_id == user_id)
    ).scalar_one_or_none()


def list_notes(
    db: Session,
    *,
    user_id: uuid.UUID,
    search: str | None,
    status_filter: str | None,
    page: int,
    page_size: int,
) -> tuple[list[Note], int]:
    stmt = select(Note).where(Note.user_id == user_id)

    if search:
        like = f"%{search}%"
        stmt = stmt.where(or_(Note.title.ilike(like), Note.original_text.ilike(like)))
    if status_filter:
        stmt = stmt.where(Note.status == status_filter)

    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()

    stmt = stmt.order_by(Note.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = list(db.execute(stmt).scalars().all())
    return items, total


def delete(db: Session, note: Note) -> None:
    db.delete(note)
    db.commit()

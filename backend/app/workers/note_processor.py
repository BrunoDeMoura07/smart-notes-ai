import uuid
from datetime import datetime, timezone

from app.core.database import SessionLocal
from app.models.note import Note
from app.services import file_service, summarization_service, transcription_service


def process_note(note_id: uuid.UUID) -> None:
    """Roda na worker thread: nunca deve ser chamado no caminho de uma requisição HTTP."""
    db = SessionLocal()
    try:
        note = db.get(Note, note_id)
        if note is None:
            return

        note.status = "processing"
        note.processing_started_at = datetime.now(timezone.utc)
        db.commit()

        text = _extract_text(note)
        if not text.strip():
            raise ValueError(
                "Não foi possível extrair nenhum texto/áudio reconhecível deste arquivo."
            )
        summary = summarization_service.summarize(text)

        if note.source_type != "text":
            note.original_text = text
        note.summary = summary
        note.status = "completed"
        note.processing_completed_at = datetime.now(timezone.utc)
        db.commit()
    except Exception as exc:
        db.rollback()
        note = db.get(Note, note_id)
        if note is not None:
            note.status = "failed"
            note.error_message = str(exc)
            note.processing_completed_at = datetime.now(timezone.utc)
            db.commit()
    finally:
        db.close()


def _extract_text(note: Note) -> str:
    if note.source_type == "text":
        return note.original_text or ""
    if note.source_type == "pdf":
        return file_service.extract_pdf_text(note.file_path)
    if note.source_type == "audio":
        return transcription_service.transcribe(note.file_path)
    raise ValueError(f"source_type desconhecido: {note.source_type}")

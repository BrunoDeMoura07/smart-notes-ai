import logging
import uuid
from datetime import datetime, timezone

from app.core.database import SessionLocal
from app.models.note import Note
from app.services import file_service, summarization_service, transcription_service

logger = logging.getLogger(__name__)

GENERIC_ERROR_MESSAGE = "Ocorreu um erro inesperado ao processar esta nota. Tente novamente mais tarde."

EXTRACTION_ERROR_MESSAGES = {
    "pdf": "Não foi possível ler este arquivo PDF. Verifique se ele não está corrompido e tente novamente.",
    "audio": "Não foi possível transcrever este arquivo de áudio. Verifique o formato e tente novamente.",
}


class NoteProcessingError(Exception):
    """Erro de processamento com mensagem já apropriada para exibir ao usuário."""


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
            raise NoteProcessingError(
                "Não foi possível extrair nenhum texto/áudio reconhecível deste arquivo."
            )

        try:
            summary = summarization_service.summarize(text)
        except Exception:
            logger.exception("Falha ao gerar resumo da nota %s", note_id)
            raise NoteProcessingError(
                "Não foi possível gerar o resumo desta nota. Tente novamente mais tarde."
            ) from None

        if note.source_type != "text":
            note.original_text = text
        note.summary = summary
        note.status = "completed"
        note.processing_completed_at = datetime.now(timezone.utc)
        db.commit()
    except NoteProcessingError as exc:
        _mark_failed(db, note_id, str(exc))
    except Exception:
        logger.exception("Erro inesperado ao processar a nota %s", note_id)
        _mark_failed(db, note_id, GENERIC_ERROR_MESSAGE)
    finally:
        db.close()


def _mark_failed(db, note_id: uuid.UUID, message: str) -> None:
    db.rollback()
    note = db.get(Note, note_id)
    if note is not None:
        note.status = "failed"
        note.error_message = message
        note.processing_completed_at = datetime.now(timezone.utc)
        db.commit()


def _extract_text(note: Note) -> str:
    if note.source_type == "text":
        return note.original_text or ""
    if note.source_type in EXTRACTION_ERROR_MESSAGES:
        try:
            if note.source_type == "pdf":
                return file_service.extract_pdf_text(note.file_path)
            return transcription_service.transcribe(note.file_path)
        except Exception:
            logger.exception("Falha ao extrair conteúdo da nota %s (%s)", note.id, note.source_type)
            raise NoteProcessingError(EXTRACTION_ERROR_MESSAGES[note.source_type]) from None
    raise NoteProcessingError(f"Tipo de nota desconhecido: {note.source_type}")

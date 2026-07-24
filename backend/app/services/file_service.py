import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from pypdf import PdfReader

from app.core.config import get_settings

settings = get_settings()

ALLOWED_PDF_TYPES = {"application/pdf"}
ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm"}


def determine_source_type(file: UploadFile) -> str:
    filename = (file.filename or "").lower()
    content_type = file.content_type or ""

    if filename.endswith(".pdf") or content_type in ALLOWED_PDF_TYPES:
        return "pdf"
    if any(filename.endswith(ext) for ext in ALLOWED_AUDIO_EXTENSIONS) or content_type.startswith("audio/"):
        return "audio"

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Tipo de arquivo não suportado. Envie um PDF ou um áudio.",
    )


def save_upload(file: UploadFile) -> tuple[str, str]:
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    extension = Path(file.filename or "").suffix
    stored_name = f"{uuid.uuid4()}{extension}"
    destination = upload_dir / stored_name

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    size = 0
    with destination.open("wb") as buffer:
        while chunk := file.file.read(1024 * 1024):
            size += len(chunk)
            if size > max_bytes:
                buffer.close()
                destination.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Arquivo maior que {settings.max_upload_size_mb}MB.",
                )
            buffer.write(chunk)

    return str(destination), file.filename or stored_name


def extract_pdf_text(file_path: str) -> str:
    reader = PdfReader(file_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages).strip()


def delete_file(file_path: str | None) -> None:
    if not file_path:
        return
    path = Path(file_path)
    if path.exists():
        path.unlink()

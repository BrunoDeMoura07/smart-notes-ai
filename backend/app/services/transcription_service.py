from app.workers import ai_models


def transcribe(file_path: str) -> str:
    model = ai_models.get_whisper_model()
    segments, _info = model.transcribe(file_path, vad_filter=True)
    return " ".join(segment.text.strip() for segment in segments).strip()

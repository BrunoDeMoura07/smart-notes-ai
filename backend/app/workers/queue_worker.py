import logging
import queue
import threading
import uuid
from collections.abc import Callable

logger = logging.getLogger(__name__)

_job_queue: "queue.Queue[uuid.UUID]" = queue.Queue()
_worker_thread: threading.Thread | None = None
_processor: Callable[[uuid.UUID], None] | None = None


def start_worker(processor: Callable[[uuid.UUID], None]) -> None:
    """Inicia a thread única de processamento (serializado) em background."""
    global _worker_thread, _processor
    _processor = processor
    _worker_thread = threading.Thread(target=_run, name="note-worker", daemon=True)
    _worker_thread.start()


def enqueue(note_id: uuid.UUID) -> None:
    _job_queue.put(note_id)


def _run() -> None:
    while True:
        note_id = _job_queue.get()
        try:
            assert _processor is not None
            _processor(note_id)
        except Exception:
            logger.exception("Erro inesperado ao processar a nota %s", note_id)
        finally:
            _job_queue.task_done()

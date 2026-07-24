import logging
import threading

from faster_whisper import WhisperModel
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, PreTrainedModel, PreTrainedTokenizerBase

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

_lock = threading.Lock()
_whisper_model: WhisperModel | None = None
_summarizer_tokenizer: PreTrainedTokenizerBase | None = None
_summarizer_model: PreTrainedModel | None = None


def load_models() -> None:
    """Carrega os modelos de IA uma única vez, no startup da aplicação."""
    global _whisper_model, _summarizer_tokenizer, _summarizer_model
    with _lock:
        if _whisper_model is None:
            logger.info("Carregando modelo Whisper (%s)...", settings.whisper_model_size)
            _whisper_model = WhisperModel(settings.whisper_model_size, device="cpu", compute_type="int8")
        if _summarizer_model is None:
            logger.info("Carregando modelo de resumo (%s)...", settings.summarization_model)
            _summarizer_tokenizer = AutoTokenizer.from_pretrained(settings.summarization_model)
            _summarizer_model = AutoModelForSeq2SeqLM.from_pretrained(settings.summarization_model)
    logger.info("Modelos de IA carregados.")


def get_whisper_model() -> WhisperModel:
    if _whisper_model is None:
        raise RuntimeError("O modelo Whisper ainda não foi carregado.")
    return _whisper_model


def get_summarizer() -> tuple[PreTrainedTokenizerBase, PreTrainedModel]:
    if _summarizer_tokenizer is None or _summarizer_model is None:
        raise RuntimeError("O modelo de resumo ainda não foi carregado.")
    return _summarizer_tokenizer, _summarizer_model

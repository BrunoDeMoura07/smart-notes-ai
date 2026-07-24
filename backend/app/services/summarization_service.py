from app.workers import ai_models

MAX_INPUT_TOKENS = 1024
MIN_WORDS_TO_SUMMARIZE = 40


def summarize(text: str) -> str:
    text = text.strip()
    if not text:
        return ""

    word_count = len(text.split())
    if word_count < MIN_WORDS_TO_SUMMARIZE:
        return text

    tokenizer, model = ai_models.get_summarizer()

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=MAX_INPUT_TOKENS)

    max_len = min(140, max(30, word_count // 2))
    min_len = min(30, max_len - 5)

    output_ids = model.generate(
        **inputs,
        max_length=max_len,
        min_length=min_len,
        num_beams=4,
        no_repeat_ngram_size=3,
        do_sample=False,
    )
    return tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()

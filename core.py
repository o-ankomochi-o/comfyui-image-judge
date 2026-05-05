def build_caption(trigger_word: str, caption: str) -> str:
    return ", ".join(part for part in (trigger_word, caption) if part)

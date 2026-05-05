def build_caption(trigger_word: str, caption: str) -> str:
    if not trigger_word:
        return caption
    return f"{trigger_word}, {caption}"

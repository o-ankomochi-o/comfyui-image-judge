from datetime import datetime


def build_caption(trigger_word: str, caption: str) -> str:
    return ", ".join(part for part in (trigger_word, caption) if part)


def make_stem(timestamp: datetime, index: int) -> str:
    return f"{timestamp:%Y%m%d_%H%M%S}_{index:03d}"

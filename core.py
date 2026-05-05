from datetime import datetime


def build_caption(trigger_word: str, caption: str) -> str:
    return ", ".join(part for part in (trigger_word, caption) if part)


def make_stem(timestamp: datetime, index: int) -> str:
    return f"{timestamp:%Y%m%d_%H%M%S}_{index:03d}"


def build_metadata(
    stem: str,
    dataset_name: str,
    caption: str,
    trigger_word: str,
    timestamp: datetime,
) -> dict:
    return {
        "stem": stem,
        "dataset": dataset_name,
        "caption": caption,
        "trigger_word": trigger_word,
        "timestamp": timestamp.isoformat(),
        "judgment": "pending",
        "judged_at": None,
        "ng_reasons": [],
    }

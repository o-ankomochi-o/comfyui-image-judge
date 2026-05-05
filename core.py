import json
from datetime import datetime
from pathlib import Path


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


def ensure_pending_dir(base_dir: Path, dataset_name: str) -> Path:
    pending = Path(base_dir) / "judge" / dataset_name / "pending"
    pending.mkdir(parents=True, exist_ok=True)
    return pending


def save_caption_file(path: Path, caption: str) -> None:
    Path(path).write_text(caption, encoding="utf-8")


def save_metadata_file(path: Path, metadata: dict) -> None:
    Path(path).write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

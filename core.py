import json
import os
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo


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
        "comment": "",
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


def save_image_png(
    path: Path,
    image: np.ndarray,
    pnginfo: PngInfo | None = None,
) -> None:
    Image.fromarray(image, mode="RGB").save(Path(path), format="PNG", pnginfo=pnginfo)


def build_pnginfo(prompt: dict | None, workflow: dict | None) -> PngInfo:
    info = PngInfo()
    if prompt is not None:
        info.add_text("prompt", json.dumps(prompt))
    if workflow is not None:
        info.add_text("workflow", json.dumps(workflow))
    return info


def save_one(
    base_dir: Path,
    dataset_name: str,
    image: np.ndarray,
    caption: str,
    trigger_word: str,
    index: int,
    timestamp: datetime,
    prompt: dict | None = None,
    workflow: dict | None = None,
) -> str:
    pending = ensure_pending_dir(base_dir, dataset_name)
    stem = make_stem(timestamp, index)
    full_caption = build_caption(trigger_word, caption)
    metadata = build_metadata(
        stem=stem,
        dataset_name=dataset_name,
        caption=full_caption,
        trigger_word=trigger_word,
        timestamp=timestamp,
    )
    pnginfo = build_pnginfo(prompt, workflow)
    save_image_png(pending / f"{stem}.png", image, pnginfo=pnginfo)
    save_caption_file(pending / f"{stem}.txt", full_caption)
    save_metadata_file(pending / f"{stem}.json", metadata)
    return stem


def apply_judgment(
    base_dir: Path,
    dataset_name: str,
    stem: str,
    judgment: str,
    comment: str,
    judged_at: datetime,
) -> None:
    dataset_root = Path(base_dir) / "judge" / dataset_name
    pending = dataset_root / "pending"
    target = dataset_root / judgment
    target.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "txt", "json"):
        os.replace(pending / f"{stem}.{ext}", target / f"{stem}.{ext}")


def save_batch(
    base_dir: Path,
    dataset_name: str,
    images: np.ndarray,
    caption: str,
    trigger_word: str,
    timestamp: datetime,
    prompt: dict | None = None,
    workflow: dict | None = None,
) -> list[str]:
    return [
        save_one(
            base_dir=base_dir,
            dataset_name=dataset_name,
            image=images[i],
            caption=caption,
            trigger_word=trigger_word,
            index=i + 1,
            timestamp=timestamp,
            prompt=prompt,
            workflow=workflow,
        )
        for i in range(len(images))
    ]

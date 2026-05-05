"""ComfyUI node adapter for SaveForJudge.

This module imports ``folder_paths`` and ``torch``, so it is only loadable
inside a ComfyUI runtime. Pure logic lives in ``core.py`` and is exercised
directly by the test suite without going through this adapter.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import folder_paths
import torch

from . import core


class SaveForJudge:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "dataset_name": ("STRING", {"default": "my_dataset"}),
            },
            "optional": {
                "caption": ("STRING", {"default": "", "multiline": True}),
                "trigger_word": ("STRING", {"default": ""}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "save"
    CATEGORY = "ImageJudge"

    def save(
        self,
        images: torch.Tensor,
        dataset_name: str,
        caption: str = "",
        trigger_word: str = "",
        prompt: dict | None = None,
        extra_pnginfo: dict | None = None,
    ):
        base_dir = Path(folder_paths.get_output_directory())
        images_np = (images.clamp(0.0, 1.0) * 255.0).to(torch.uint8).cpu().numpy()
        workflow = (extra_pnginfo or {}).get("workflow")
        stems = core.save_batch(
            base_dir=base_dir,
            dataset_name=dataset_name,
            images=images_np,
            caption=caption,
            trigger_word=trigger_word,
            timestamp=datetime.now(),
            prompt=prompt,
            workflow=workflow,
        )
        return {
            "ui": {
                "images": [
                    {
                        "filename": f"{stem}.png",
                        "subfolder": f"judge/{dataset_name}/pending",
                        "type": "output",
                    }
                    for stem in stems
                ]
            }
        }

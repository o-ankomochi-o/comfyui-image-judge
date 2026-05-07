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
from aiohttp import web
from server import PromptServer

from . import core

_WEB_DIR = Path(__file__).parent / "web"


def _is_safe_name(name: str) -> bool:
    if not name or "/" in name or "\\" in name or ".." in name:
        return False
    return True


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


@PromptServer.instance.routes.get("/imagejudge/ui")
async def _imagejudge_ui(request):
    html = _WEB_DIR / "index.html"
    if not html.is_file():
        return web.Response(text="Image Judge UI not yet bundled.", status=503)
    return web.FileResponse(html)


@PromptServer.instance.routes.get("/imagejudge/datasets")
async def _imagejudge_datasets(request):
    base_dir = Path(folder_paths.get_output_directory())
    return web.json_response(core.list_datasets(base_dir))


@PromptServer.instance.routes.get("/imagejudge/pending")
async def _imagejudge_pending(request):
    dataset = request.query.get("dataset", "")
    if not _is_safe_name(dataset):
        return web.json_response({"error": "invalid dataset"}, status=400)
    base_dir = Path(folder_paths.get_output_directory())
    return web.json_response(core.list_pending(base_dir, dataset))


@PromptServer.instance.routes.get("/imagejudge/pending-all")
async def _imagejudge_pending_all(request):
    base_dir = Path(folder_paths.get_output_directory())
    return web.json_response(core.list_pending_all(base_dir))


@PromptServer.instance.routes.get("/imagejudge/image/{dataset}/{filename}")
async def _imagejudge_image(request):
    dataset = request.match_info["dataset"]
    filename = request.match_info["filename"]
    if not _is_safe_name(dataset) or not _is_safe_name(filename):
        return web.Response(status=400)
    base_dir = Path(folder_paths.get_output_directory())
    path = base_dir / "judge" / dataset / "pending" / filename
    if not path.is_file():
        return web.Response(status=404)
    return web.FileResponse(path)


@PromptServer.instance.routes.post("/imagejudge/judge")
async def _imagejudge_judge(request):
    try:
        payload = await request.json()
    except Exception:
        return web.json_response({"error": "invalid json"}, status=400)
    dataset = payload.get("dataset", "")
    stem = payload.get("stem", "")
    judgment = payload.get("judgment", "")
    comment = payload.get("comment", "")
    target_dataset = payload.get("target_dataset") or None
    if not _is_safe_name(dataset) or not _is_safe_name(stem):
        return web.json_response({"error": "invalid name"}, status=400)
    if target_dataset is not None and not _is_safe_name(target_dataset):
        return web.json_response({"error": "invalid target_dataset"}, status=400)
    if judgment not in ("ok", "ng"):
        return web.json_response({"error": "invalid judgment"}, status=400)
    base_dir = Path(folder_paths.get_output_directory())
    core.apply_judgment(
        base_dir=base_dir,
        dataset_name=dataset,
        stem=stem,
        judgment=judgment,
        comment=comment,
        judged_at=datetime.now(),
        target_dataset=target_dataset,
    )
    return web.json_response({"ok": True})

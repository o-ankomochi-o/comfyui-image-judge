"""ComfyUI custom nodes for human OK/NG judging of generated images.

This module is imported by ComfyUI on startup. It re-exports
``NODE_CLASS_MAPPINGS`` so the nodes appear in the ComfyUI menu.

When the package is loaded outside a ComfyUI runtime (e.g. during the test
suite), ``nodes.py`` cannot be imported because ``torch`` and
``folder_paths`` are unavailable. In that case we fall back to empty
mappings so importing this package never raises.
"""

try:
    from .nodes import SaveForJudge

    NODE_CLASS_MAPPINGS = {
        "ImageJudge_Save": SaveForJudge,
    }
    NODE_DISPLAY_NAME_MAPPINGS = {
        "ImageJudge_Save": "Save for Judge",
    }
except ImportError:
    NODE_CLASS_MAPPINGS = {}
    NODE_DISPLAY_NAME_MAPPINGS = {}

WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

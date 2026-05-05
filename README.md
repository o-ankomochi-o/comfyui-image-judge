# comfyui-image-judge

ComfyUI custom nodes for human OK/NG judging of generated images, oriented
toward curating LoRA / kohya_ss training datasets.

> Status: **pre-alpha (Step 1 in progress)** — the `SaveForJudge` node and its
> output layout are being implemented. The judging Web UI, statistics node,
> and dataset exporter listed in the roadmap below are not yet shipped.

## Planned nodes

| Node (internal id) | Display name | Purpose |
|---|---|---|
| `ImageJudge_Save` | Save for Judge | Save generated images + caption + metadata into `output/judge/<dataset>/pending/` for later human judging. |
| `ImageJudge_Stats` | Judge Stats | Report OK / NG / pending counts for a dataset. |
| `ImageJudge_Export` | Export Dataset | Export OK images into `kohya_ss` / `flat` / `huggingface` layouts. |

A separate in-browser **judging UI** (key-driven OK/NG decisions, NG reason
tags, batch progress) will be served from ComfyUI's built-in HTTP server at
`/judge`.

## Output layout (per `SaveForJudge` invocation)

```
output/judge/<dataset_name>/pending/
  20260505_123456_001.png   # PNG with workflow embedded in metadata
  20260505_123456_001.txt   # kohya_ss-style caption (trigger_word prefixed)
  20260505_123456_001.json  # judgment state + generation params
```

Metadata JSON is initialised with `judgment: "pending"`; the judging UI
flips it to `ok` / `ng` and moves the file trio to a sibling folder.

## Installation (once published)

### Via ComfyUI Manager

Search for `comfyui-image-judge` in ComfyUI Manager and install. The Manager
will fetch dependencies from `requirements.txt` automatically.

### Manual (Git)

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/o-ankomochi-o/comfyui-image-judge.git
pip install -r comfyui-image-judge/requirements.txt
```

Then restart ComfyUI. Nodes appear under the **ImageJudge** category.

## Development

This project follows strict TDD (Red → Green → Refactor) for all Python
logic. See `CLAUDE.md` for the working agreement.

```bash
uv sync                 # install deps incl. dev tooling
uv run pytest           # run the test suite
```

The package is laid out flat (no `src/` directory) so that ComfyUI can load
it directly when cloned into `custom_nodes/`. Pure logic lives in `core.py`
(import-safe, no torch/ComfyUI dependency, fully unit-tested) and the thin
ComfyUI node adapter lives in `nodes.py`.

## License

MIT — see [LICENSE](LICENSE).

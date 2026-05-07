import json
from datetime import datetime

import numpy as np
from PIL import Image

from core import (
    apply_judgment,
    build_caption,
    build_metadata,
    build_pnginfo,
    ensure_pending_dir,
    list_by_status,
    list_datasets,
    list_pending,
    list_pending_all,
    make_stem,
    save_batch,
    save_caption_file,
    save_image_png,
    save_metadata_file,
    save_one,
)


def test_build_caption_combines_trigger_and_caption():
    assert build_caption(trigger_word="trg", caption="a cat") == "trg, a cat"


def test_build_caption_omits_empty_trigger_word():
    assert build_caption(trigger_word="", caption="a cat") == "a cat"


def test_build_caption_omits_empty_caption():
    assert build_caption(trigger_word="trg", caption="") == "trg"


def test_make_stem_formats_timestamp_and_index():
    stem = make_stem(timestamp=datetime(2026, 5, 5, 12, 34, 56), index=1)
    assert stem == "20260505_123456_001"


def test_build_metadata_records_input_fields():
    md = build_metadata(
        stem="20260505_123456_001",
        dataset_name="my_ds",
        caption="trg, a cat",
        trigger_word="trg",
        timestamp=datetime(2026, 5, 5, 12, 34, 56),
    )
    assert md["stem"] == "20260505_123456_001"
    assert md["dataset"] == "my_ds"
    assert md["caption"] == "trg, a cat"
    assert md["trigger_word"] == "trg"
    assert md["timestamp"] == "2026-05-05T12:34:56"


def test_build_metadata_initialises_judgment_state():
    md = build_metadata(
        stem="20260505_123456_001",
        dataset_name="my_ds",
        caption="trg, a cat",
        trigger_word="trg",
        timestamp=datetime(2026, 5, 5, 12, 34, 56),
    )
    assert md["judgment"] == "pending"
    assert md["judged_at"] is None
    assert md["comment"] == ""
    assert "ng_reasons" not in md


def test_ensure_pending_dir_creates_nested_path(tmp_path):
    pending = ensure_pending_dir(tmp_path, "my_ds")
    assert pending == tmp_path / "judge" / "my_ds" / "pending"
    assert pending.is_dir()


def test_save_caption_file_writes_utf8(tmp_path):
    target = tmp_path / "out.txt"
    save_caption_file(target, "trg, a cat 猫")
    assert target.read_text(encoding="utf-8") == "trg, a cat 猫"


def test_save_metadata_file_roundtrips_via_json(tmp_path):
    target = tmp_path / "out.json"
    md = {
        "stem": "x",
        "judgment": "pending",
        "judged_at": None,
        "comment": "",
        "caption": "trg, 猫",
    }
    save_metadata_file(target, md)
    assert json.loads(target.read_text(encoding="utf-8")) == md


def test_save_image_png_writes_pil_loadable_png(tmp_path):
    target = tmp_path / "out.png"
    img = np.zeros((4, 6, 3), dtype=np.uint8)
    save_image_png(target, img)
    with Image.open(target) as loaded:
        assert loaded.size == (6, 4)
        assert loaded.mode == "RGB"


def test_build_pnginfo_embeds_prompt_and_workflow(tmp_path):
    target = tmp_path / "out.png"
    info = build_pnginfo(prompt={"a": 1}, workflow={"b": 2})
    save_image_png(target, np.zeros((2, 2, 3), dtype=np.uint8), pnginfo=info)
    with Image.open(target) as loaded:
        assert json.loads(loaded.text["prompt"]) == {"a": 1}
        assert json.loads(loaded.text["workflow"]) == {"b": 2}


def test_save_one_writes_png_txt_json_trio(tmp_path):
    img = np.zeros((4, 6, 3), dtype=np.uint8)
    stem = save_one(
        base_dir=tmp_path,
        dataset_name="my_ds",
        image=img,
        caption="a cat",
        trigger_word="trg",
        index=1,
        timestamp=datetime(2026, 5, 5, 12, 34, 56),
        prompt={"a": 1},
        workflow={"b": 2},
    )
    assert stem == "20260505_123456_001"
    pending = tmp_path / "judge" / "my_ds" / "pending"
    assert (pending / f"{stem}.png").is_file()
    assert (pending / f"{stem}.txt").read_text(encoding="utf-8") == "trg, a cat"
    md = json.loads((pending / f"{stem}.json").read_text(encoding="utf-8"))
    assert md["stem"] == stem
    assert md["dataset"] == "my_ds"
    assert md["caption"] == "trg, a cat"
    assert md["trigger_word"] == "trg"
    assert md["judgment"] == "pending"


def test_apply_judgment_moves_trio_from_pending_to_ok(tmp_path):
    images = np.zeros((1, 4, 6, 3), dtype=np.uint8)
    [stem] = save_batch(
        base_dir=tmp_path,
        dataset_name="my_ds",
        images=images,
        caption="a cat",
        trigger_word="trg",
        timestamp=datetime(2026, 5, 5, 12, 34, 56),
    )
    pending = tmp_path / "judge" / "my_ds" / "pending"
    ok = tmp_path / "judge" / "my_ds" / "ok"

    apply_judgment(
        base_dir=tmp_path,
        dataset_name="my_ds",
        stem=stem,
        judgment="ok",
        comment="",
        judged_at=datetime(2026, 5, 6, 10, 0, 0),
    )

    for ext in ("png", "txt", "json"):
        assert (ok / f"{stem}.{ext}").is_file()
        assert not (pending / f"{stem}.{ext}").exists()


def test_apply_judgment_updates_metadata_in_moved_json(tmp_path):
    images = np.zeros((1, 4, 6, 3), dtype=np.uint8)
    [stem] = save_batch(
        base_dir=tmp_path,
        dataset_name="my_ds",
        images=images,
        caption="a cat",
        trigger_word="trg",
        timestamp=datetime(2026, 5, 5, 12, 34, 56),
    )

    apply_judgment(
        base_dir=tmp_path,
        dataset_name="my_ds",
        stem=stem,
        judgment="ok",
        comment="looks great",
        judged_at=datetime(2026, 5, 6, 10, 0, 0),
    )

    moved = tmp_path / "judge" / "my_ds" / "ok" / f"{stem}.json"
    md = json.loads(moved.read_text(encoding="utf-8"))
    assert md["judgment"] == "ok"
    assert md["judged_at"] == "2026-05-06T10:00:00"
    assert md["comment"] == "looks great"


def test_apply_judgment_routes_ng_verdict_to_ng_dir(tmp_path):
    images = np.zeros((1, 4, 6, 3), dtype=np.uint8)
    [stem] = save_batch(
        base_dir=tmp_path,
        dataset_name="my_ds",
        images=images,
        caption="a cat",
        trigger_word="trg",
        timestamp=datetime(2026, 5, 5, 12, 34, 56),
    )

    apply_judgment(
        base_dir=tmp_path,
        dataset_name="my_ds",
        stem=stem,
        judgment="ng",
        comment="blurry",
        judged_at=datetime(2026, 5, 6, 10, 0, 0),
    )

    ng_json = tmp_path / "judge" / "my_ds" / "ng" / f"{stem}.json"
    assert ng_json.is_file()
    md = json.loads(ng_json.read_text(encoding="utf-8"))
    assert md["judgment"] == "ng"
    assert md["comment"] == "blurry"


def test_list_pending_returns_metadata_sorted_by_stem(tmp_path):
    images = np.zeros((3, 4, 6, 3), dtype=np.uint8)
    save_batch(
        base_dir=tmp_path,
        dataset_name="my_ds",
        images=images,
        caption="a cat",
        trigger_word="trg",
        timestamp=datetime(2026, 5, 5, 12, 34, 56),
    )

    items = list_pending(tmp_path, "my_ds")
    assert [item["stem"] for item in items] == [
        "20260505_123456_001",
        "20260505_123456_002",
        "20260505_123456_003",
    ]
    assert all(item["judgment"] == "pending" for item in items)


def test_list_datasets_returns_subdirectories_sorted(tmp_path):
    images = np.zeros((1, 4, 6, 3), dtype=np.uint8)
    save_batch(
        base_dir=tmp_path,
        dataset_name="zebra_ds",
        images=images,
        caption="",
        trigger_word="",
        timestamp=datetime(2026, 5, 5, 12, 34, 56),
    )
    save_batch(
        base_dir=tmp_path,
        dataset_name="alpha_ds",
        images=images,
        caption="",
        trigger_word="",
        timestamp=datetime(2026, 5, 5, 12, 34, 56),
    )
    assert list_datasets(tmp_path) == ["alpha_ds", "zebra_ds"]


def test_list_pending_all_aggregates_across_datasets_with_dataset_field(tmp_path):
    images = np.zeros((1, 4, 6, 3), dtype=np.uint8)
    save_batch(
        base_dir=tmp_path,
        dataset_name="alpha",
        images=images,
        caption="",
        trigger_word="",
        timestamp=datetime(2026, 5, 5, 12, 0, 0),
    )
    save_batch(
        base_dir=tmp_path,
        dataset_name="beta",
        images=images,
        caption="",
        trigger_word="",
        timestamp=datetime(2026, 5, 5, 13, 0, 0),
    )

    items = list_pending_all(tmp_path)
    datasets = [item["dataset"] for item in items]
    assert sorted(datasets) == ["alpha", "beta"]
    assert all("stem" in item for item in items)


def test_apply_judgment_routes_to_target_dataset_when_specified(tmp_path):
    images = np.zeros((1, 4, 6, 3), dtype=np.uint8)
    [stem] = save_batch(
        base_dir=tmp_path,
        dataset_name="alpha",
        images=images,
        caption="",
        trigger_word="",
        timestamp=datetime(2026, 5, 5, 12, 0, 0),
    )

    apply_judgment(
        base_dir=tmp_path,
        dataset_name="alpha",
        stem=stem,
        judgment="ok",
        comment="",
        judged_at=datetime(2026, 5, 6, 10, 0, 0),
        target_dataset="aggregated_final",
    )

    target_json = tmp_path / "judge" / "aggregated_final" / "ok" / f"{stem}.json"
    assert target_json.is_file()
    md = json.loads(target_json.read_text(encoding="utf-8"))
    assert md["dataset"] == "aggregated_final"


def test_list_by_status_returns_metadata_from_ok_dir(tmp_path):
    images = np.zeros((1, 4, 6, 3), dtype=np.uint8)
    [stem] = save_batch(
        base_dir=tmp_path,
        dataset_name="my_ds",
        images=images,
        caption="cat",
        trigger_word="",
        timestamp=datetime(2026, 5, 5, 12, 0, 0),
    )
    apply_judgment(
        base_dir=tmp_path,
        dataset_name="my_ds",
        stem=stem,
        judgment="ok",
        comment="great",
        judged_at=datetime(2026, 5, 6, 10, 0, 0),
    )

    items = list_by_status(tmp_path, "my_ds", "ok")
    assert len(items) == 1
    assert items[0]["stem"] == stem
    assert items[0]["judgment"] == "ok"


def test_apply_judgment_can_re_judge_from_ok_to_ng(tmp_path):
    images = np.zeros((1, 4, 6, 3), dtype=np.uint8)
    [stem] = save_batch(
        base_dir=tmp_path,
        dataset_name="my_ds",
        images=images,
        caption="cat",
        trigger_word="",
        timestamp=datetime(2026, 5, 5, 12, 0, 0),
    )
    apply_judgment(
        base_dir=tmp_path,
        dataset_name="my_ds",
        stem=stem,
        judgment="ok",
        comment="",
        judged_at=datetime(2026, 5, 6, 10, 0, 0),
    )

    apply_judgment(
        base_dir=tmp_path,
        dataset_name="my_ds",
        stem=stem,
        judgment="ng",
        comment="actually bad",
        judged_at=datetime(2026, 5, 7, 10, 0, 0),
        from_status="ok",
    )

    ok_path = tmp_path / "judge" / "my_ds" / "ok" / f"{stem}.json"
    assert not ok_path.exists()
    ng_path = tmp_path / "judge" / "my_ds" / "ng" / f"{stem}.json"
    assert ng_path.is_file()
    md = json.loads(ng_path.read_text(encoding="utf-8"))
    assert md["judgment"] == "ng"
    assert md["comment"] == "actually bad"


def test_save_batch_iterates_indices_starting_at_one(tmp_path):
    images = np.zeros((3, 4, 6, 3), dtype=np.uint8)
    stems = save_batch(
        base_dir=tmp_path,
        dataset_name="my_ds",
        images=images,
        caption="a cat",
        trigger_word="trg",
        timestamp=datetime(2026, 5, 5, 12, 34, 56),
    )
    assert stems == [
        "20260505_123456_001",
        "20260505_123456_002",
        "20260505_123456_003",
    ]
    pending = tmp_path / "judge" / "my_ds" / "pending"
    files = sorted(p.name for p in pending.iterdir())
    expected = sorted(
        f"{stem}.{ext}" for stem in stems for ext in ("json", "png", "txt")
    )
    assert files == expected

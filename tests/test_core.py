from datetime import datetime

from core import build_caption, build_metadata, make_stem


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
    assert md["ng_reasons"] == []

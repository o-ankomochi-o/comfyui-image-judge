from datetime import datetime

from core import build_caption, make_stem


def test_build_caption_combines_trigger_and_caption():
    assert build_caption(trigger_word="trg", caption="a cat") == "trg, a cat"


def test_build_caption_omits_empty_trigger_word():
    assert build_caption(trigger_word="", caption="a cat") == "a cat"


def test_build_caption_omits_empty_caption():
    assert build_caption(trigger_word="trg", caption="") == "trg"


def test_make_stem_formats_timestamp_and_index():
    stem = make_stem(timestamp=datetime(2026, 5, 5, 12, 34, 56), index=1)
    assert stem == "20260505_123456_001"

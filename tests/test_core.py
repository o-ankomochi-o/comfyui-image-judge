from core import build_caption


def test_build_caption_combines_trigger_and_caption():
    assert build_caption(trigger_word="trg", caption="a cat") == "trg, a cat"


def test_build_caption_omits_empty_trigger_word():
    assert build_caption(trigger_word="", caption="a cat") == "a cat"


def test_build_caption_omits_empty_caption():
    assert build_caption(trigger_word="trg", caption="") == "trg"

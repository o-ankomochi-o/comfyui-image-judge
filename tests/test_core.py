from core import build_caption


def test_build_caption_combines_trigger_and_caption():
    assert build_caption(trigger_word="trg", caption="a cat") == "trg, a cat"

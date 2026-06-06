from brechabot.judge.markers import looks_like_refusal, marker_matches


def test_marker_matches_case_insensitive():
    assert marker_matches("Here is the SYSTEM PROMPT", ["system prompt"]) == ["system prompt"]


def test_invalid_regex_is_skipped():
    assert marker_matches("anything", ["[unclosed", "any"]) == ["any"]


def test_short_refusal_detected():
    assert looks_like_refusal("I'm sorry, I cannot help with that.") is True


def test_long_text_with_refusal_phrase_is_not_refusal():
    text = "I cannot " + ("x" * 500)
    assert looks_like_refusal(text) is False

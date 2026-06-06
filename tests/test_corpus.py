from brechabot.corpus import loader

STARTER_IDS = {"PXR-003", "PXR-007", "PXR-010", "PXR-014", "PXR-022",
               "PXR-025", "PXR-029", "PXR-035", "PXR-044", "PXR-048"}


def test_starter_loads():
    corpus = loader.load_corpus()  # default = starter
    assert len(corpus.attacks) == 10
    assert {a.id for a in corpus.attacks} == STARTER_IDS


def test_starter_has_one_multilingual_and_one_multi_turn():
    by_id = {a.id: a for a in loader.load_corpus().attacks}
    assert by_id["PXR-044"].lang == "hi"
    assert by_id["PXR-048"].is_multi_turn is True


def test_every_starter_attack_resolves_owasp_and_remediation():
    corpus = loader.load_corpus()
    for a in corpus.attacks:
        assert a.category in corpus.categories
        assert loader.owasp_for(a.category, corpus.categories) != ""
        assert loader.remediation_for(a.category, corpus.categories) != ""


def test_version_prefixed():
    assert loader.load_corpus().version.startswith("brc-")

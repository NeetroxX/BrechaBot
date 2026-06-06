"""Guards the open-core boundary: the bundled pack must be EXACTLY the approved starter set."""
from brechabot.corpus import loader

APPROVED_STARTER_IDS = {
    "PXR-003", "PXR-007", "PXR-010", "PXR-014", "PXR-022",
    "PXR-025", "PXR-029", "PXR-035", "PXR-044", "PXR-048",
}


def test_bundled_pack_is_exactly_the_starter():
    pack = loader.load_pack("starter")
    ids = {a.id for a in pack.attacks}
    assert ids == APPROVED_STARTER_IDS, f"bundled pack drifted: {ids ^ APPROVED_STARTER_IDS}"


def test_only_starter_is_a_builtin_pack():
    assert set(loader.BUILTIN_PACKS) == {"starter"}

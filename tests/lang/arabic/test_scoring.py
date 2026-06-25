from tracealign.model import Reason


def test_arabic_reason_values_exist():
    assert Reason.DIACRITICS_STRIPPED.value == "diacritics_stripped"
    assert Reason.ORTHOGRAPHIC_VARIANT.value == "orthographic_variant"

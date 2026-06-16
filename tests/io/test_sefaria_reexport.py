"""Pin the public surface of tracealign.io.sefaria."""


def test_sefaria_module_importable():
    from tracealign.io import sefaria

    assert hasattr(sefaria, "load")
    assert hasattr(sefaria, "load_segments")
    assert hasattr(sefaria, "load_versions")

from tracealign import align, list_languages, tokenize


def test_ara_is_registered():
    assert "ara" in list_languages()


def test_alias_resolves():
    toks = tokenize("كتاب", lang="arabic")
    assert [t.text for t in toks] == ["كتاب"]


def test_tokenize_splits_article_end_to_end():
    toks = tokenize("الكتاب", lang="ara")
    assert [t.text for t in toks] == ["ال", "كتاب"]


def test_tokenize_preserves_diplomatic_raw_and_skeleton():
    toks = tokenize("أحمد", lang="ara")
    assert toks[0].raw == "أحمد"          # diplomatic preserved
    assert toks[0].representations["skeleton"] == "احمد"


def test_tokenize_strips_tashkil_into_text():
    toks = tokenize("كَتَبَ", lang="ara")
    assert toks[0].raw == "كَتَبَ"
    assert toks[0].text == "كتب"


def test_align_end_to_end_records_pack_version():
    a = tokenize("الكتاب", lang="ara", seq_label="a")
    b = tokenize("الكتاب", lang="ara", seq_label="b")
    result = align(a, b, lang="ara")
    assert result.params["language_pack_version"] == "ara-0.1.0"
    assert all(m.score > 0 for m in result.matches if m.token_a and m.token_b)

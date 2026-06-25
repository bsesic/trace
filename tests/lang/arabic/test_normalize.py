from tracealign.lang.arabic.normalize import skeleton, strip_tashkil


def test_strip_tashkil_removes_vowel_marks():
    # kitAb with fatha+kasra+long-a marks -> bare consonantal skeleton text
    vocalized = "كَتَبَ"  # k-fatha t-fatha b-fatha
    assert strip_tashkil(vocalized) == "كتب"


def test_strip_tashkil_removes_tatweel():
    assert strip_tashkil("كــتــاب") == "كتاب"


def test_strip_tashkil_removes_shadda_and_tanwin():
    assert strip_tashkil("مُحَمَّدٌ") == "محمد"


def test_skeleton_folds_alif_variants():
    assert skeleton("أحمد") == "احمد"
    assert skeleton("إسلام") == "اسلام"
    assert skeleton("آدم") == "ادم"


def test_skeleton_folds_taa_marbuta_to_haa():
    assert skeleton("مدينة") == "مدينه"


def test_skeleton_folds_alif_maqsura_to_ya():
    assert skeleton("على") == "علي"


def test_skeleton_folds_hamza_seats():
    assert skeleton("مؤمن") == "مومن"   # waw-hamza -> waw
    assert skeleton("قائم") == "قايم"   # ya-hamza -> ya


def test_skeleton_drops_bare_hamza():
    assert skeleton("جزء") == "جز"


def test_skeleton_is_idempotent_on_plain_text():
    assert skeleton("كتاب") == "كتاب"

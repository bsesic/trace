# Arabic Language Pack (`ara`) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a rule-based Arabic language pack (`ara`) so `tokenize(text, lang="ara")` and `align(..., lang="ara")` work end-to-end, mirroring `src/tracealign/lang/hebrew/`.

**Architecture:** A new `tracealign.lang.arabic` package implementing the `LanguagePack` ABC: a `post_tokenize` hook for conservative proclitic splitting, a `normalize` method producing a tashkil-stripped `text` plus an orthographic `skeleton` representation, and four scoring tiers. Two new script-neutral `Reason` enum values support the tiers. Registration follows the Hebrew side-effect-import pattern.

**Tech Stack:** Python 3.10+, `unicodedata` (stdlib), `rapidfuzz` (already a dependency), `pydantic` (model layer), `pytest`, `flake8`. No new dependencies.

## Global Constraints

- Python version floor: **3.10**; full suite must pass on the **3.10 / 3.11 / 3.12** matrix.
- `flake8 src/ tests/` reports **zero** issues before every commit.
- **No AI-assistant attribution** in commit messages, PR descriptions, or any shipping artefact.
- **No new third-party dependencies** — rule-based, stdlib-leaning (CAMeL Tools etc. forbidden).
- All code, comments, docstrings, and artefacts in **English**.
- Pack must stay **data-file-free**: the conservative splitting strategy needs no guard lexicon; set `self.lexica = Lexica()`.
- Reason tags must use the shared `Reason` enum; new values must be **script-neutral** in name.
- Diplomatic form is always preserved in `Token.raw`.

---

## File Structure

- `src/tracealign/model.py` — **modify**: add two `Reason` enum members.
- `src/tracealign/lang/arabic/__init__.py` — **create**: registers `ArabicLanguagePack` (side-effect import).
- `src/tracealign/lang/arabic/normalize.py` — **create**: `strip_tashkil()`, `skeleton()`.
- `src/tracealign/lang/arabic/tokenize.py` — **create**: `split_proclitics()`.
- `src/tracealign/lang/arabic/scoring.py` — **create**: tier predicates + `arabic_scoring_tiers()`.
- `src/tracealign/lang/arabic/pack.py` — **create**: `ArabicLanguagePack(LanguagePack)`.
- `src/tracealign/__init__.py` — **modify**: add `import tracealign.lang.arabic` and extend `_BUILTIN_PACK_MODULES`.
- `tests/lang/arabic/test_normalize.py` — **create**.
- `tests/lang/arabic/test_tokenize.py` — **create**.
- `tests/lang/arabic/test_scoring.py` — **create**.
- `tests/lang/arabic/test_pack_integration.py` — **create**.

**Reference implementation to mirror** (read before starting): `src/tracealign/lang/hebrew/{normalize,tokenize,scoring,pack,__init__}.py`. The Hebrew pack is the template for shape, naming, and score constants.

**Key existing signatures consumed:**
- `RawToken(raw: str, span: tuple[int, int], flags: set[str])` — `tracealign/tokenize/base.py`.
- `Token(BaseModel)` fields: `id, position, raw, text, representations: dict[str,str], flags: set[str], source_span: tuple[int,int] | None, metadata: dict`. `model_config = ConfigDict(extra="forbid")`.
- `LanguagePack` ABC: class attrs `code, aliases, version, word_chars, mid_word_chars, editorial_rules, lexica`; methods `post_tokenize(raws) -> list[RawToken]` (default identity), `normalize(raw) -> Token` (abstract), `scoring_tiers() -> list[ScoringTier]` (abstract).
- `ScoringTier(reason: Reason, predicate: Callable[[Token, Token, LanguagePack], TierResult | None])`; `TierResult(score: float, details: dict | None = None)` — `tracealign/lang/base.py`.
- `register_language(pack)` — `tracealign/lang/registry.py`.
- `Lexica()` — empty default is valid (`tracealign/model.py`).
- `align()` writes `params["language_pack_version"] = pack.version` via `needleman_wunsch.py:376` — no change required.

---

### Task 1: Add Arabic-relevant Reason enum values

**Files:**
- Modify: `src/tracealign/model.py:19-28` (the `Reason` enum)
- Test: `tests/lang/arabic/test_scoring.py` (created here, expanded in Task 4)

**Interfaces:**
- Consumes: nothing.
- Produces: `Reason.DIACRITICS_STRIPPED == "diacritics_stripped"`, `Reason.ORTHOGRAPHIC_VARIANT == "orthographic_variant"`.

- [ ] **Step 1: Write the failing test**

Create `tests/lang/arabic/__init__.py` (empty) and `tests/lang/arabic/test_scoring.py`:

```python
from tracealign.model import Reason


def test_arabic_reason_values_exist():
    assert Reason.DIACRITICS_STRIPPED.value == "diacritics_stripped"
    assert Reason.ORTHOGRAPHIC_VARIANT.value == "orthographic_variant"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/lang/arabic/test_scoring.py -v`
Expected: FAIL with `AttributeError: DIACRITICS_STRIPPED`.

- [ ] **Step 3: Add the enum members**

In `src/tracealign/model.py`, inside `class Reason(str, Enum)`, add the two members after `ORTHOGRAPHIC` and before `SCRIPT_VARIANT`:

```python
class Reason(str, Enum):
    EXACT = "exact"
    NIQQUD_STRIPPED = "niqqud_stripped"
    PLENE_DEFECTIVE = "plene_defective"
    ABBREVIATION = "abbreviation"
    ORTHOGRAPHIC = "orthographic"
    DIACRITICS_STRIPPED = "diacritics_stripped"
    ORTHOGRAPHIC_VARIANT = "orthographic_variant"
    SCRIPT_VARIANT = "script_variant"
    INSERTION = "insertion"
    OMISSION = "omission"
    NO_MATCH = "no_match"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/lang/arabic/test_scoring.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/tracealign/model.py tests/lang/arabic/__init__.py tests/lang/arabic/test_scoring.py
git commit -m "feat(model): add DIACRITICS_STRIPPED and ORTHOGRAPHIC_VARIANT reasons

Refs #16"
```

---

### Task 2: Arabic normalization (`normalize.py`)

**Files:**
- Create: `src/tracealign/lang/arabic/normalize.py`
- Create: `src/tracealign/lang/arabic/__init__.py` (empty placeholder for now — package marker; real registration added in Task 5)
- Test: `tests/lang/arabic/test_normalize.py`

**Interfaces:**
- Consumes: `unicodedata` (stdlib).
- Produces:
  - `strip_tashkil(text: str) -> str` — NFC, remove combining marks (category `Mn`) and tatweel `ـ`.
  - `skeleton(text_no_tashkil: str) -> str` — orthographic folding applied to a tashkil-free string.
  - Module constants: `TATWEEL = "ـ"`.

- [ ] **Step 1: Write the failing tests**

Create `tests/lang/arabic/test_normalize.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/lang/arabic/test_normalize.py -v`
Expected: FAIL with `ModuleNotFoundError: tracealign.lang.arabic.normalize`.

- [ ] **Step 3: Write the implementation**

Create `src/tracealign/lang/arabic/__init__.py` (empty for now):

```python
"""Arabic language pack."""
```

Create `src/tracealign/lang/arabic/normalize.py`:

```python
"""Arabic normalization: tashkil strip and orthographic skeleton folding."""

from __future__ import annotations

import unicodedata

TATWEEL = "ـ"  # ARABIC TATWEEL (kashida), decorative elongation

# Orthographic folding table applied on top of a tashkil-free string.
# Alif variants -> bare alif; taa marbuta -> haa; alif maqsura -> ya;
# hamza seats -> their carrier letter; bare hamza dropped.
_FOLD = {
    "أ": "ا",  # ALEF WITH HAMZA ABOVE  أ -> ا
    "إ": "ا",  # ALEF WITH HAMZA BELOW  إ -> ا
    "آ": "ا",  # ALEF WITH MADDA ABOVE  آ -> ا
    "ٱ": "ا",  # ALEF WASLA            ٱ -> ا
    "ة": "ه",  # TEH MARBUTA           ة -> ه
    "ى": "ي",  # ALEF MAKSURA          ى -> ي
    "ؤ": "و",  # WAW WITH HAMZA        ؤ -> و
    "ئ": "ي",  # YEH WITH HAMZA        ئ -> ي
    "ء": "",        # HAMZA                 ء -> (dropped)
}


def strip_tashkil(text: str) -> str:
    """NFC-normalize, then remove combining marks (Mn) and tatweel."""
    text = unicodedata.normalize("NFC", text)
    return "".join(
        ch
        for ch in text
        if unicodedata.category(ch) != "Mn" and ch != TATWEEL
    )


def skeleton(text_no_tashkil: str) -> str:
    """Apply orthographic folding to a tashkil-free string."""
    return "".join(_FOLD.get(ch, ch) for ch in text_no_tashkil)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/lang/arabic/test_normalize.py -v`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add src/tracealign/lang/arabic/__init__.py src/tracealign/lang/arabic/normalize.py tests/lang/arabic/test_normalize.py
git commit -m "feat(lang/arabic): tashkil strip and orthographic skeleton folding

Refs #16"
```

---

### Task 3: Proclitic splitting (`tokenize.py`)

**Files:**
- Create: `src/tracealign/lang/arabic/tokenize.py`
- Test: `tests/lang/arabic/test_tokenize.py`

**Interfaces:**
- Consumes: `RawToken` from `tracealign.tokenize.base`.
- Produces: `split_proclitics(raws: list[RawToken]) -> list[RawToken]`. Proclitic part carries flag `"proclitic"`; host part carries flag `"compound_part"`. Unsplit tokens pass through unchanged. Spans are contiguous (no separator char).

**Splitting rules (conservative — see spec §3):**
1. `ال…` (alif-lam prefix) with token length > 2 → split `[ال, rest]`.
2. Single-letter proclitic `و/ف/ب/ك` immediately followed by `ال` → split `[letter, ال…]` (the article stays attached to the host).
3. `لل…` (li- + article, alif elided), length > 2 → split `[ل, لرest]` i.e. strip only the first `ل`; host keeps the reduced-article form.
4. Anything else (bare proclitic letter + non-article, radical-initial words) → **no split**.

Apply at most one split per token (a single proclitic). Rule precedence: try rule 2/3 (proclitic + article) first, then rule 1 (bare article), else pass through.

- [ ] **Step 1: Write the failing tests**

Create `tests/lang/arabic/test_tokenize.py`:

```python
from tracealign.lang.arabic.tokenize import split_proclitics
from tracealign.tokenize.base import RawToken


def _raw(text, start=0):
    return RawToken(raw=text, span=(start, start + len(text)), flags=set())


def _texts(raws):
    return [r.raw for r in raws]


def test_splits_definite_article():
    out = split_proclitics([_raw("الكتاب")])
    assert _texts(out) == ["ال", "كتاب"]
    assert "proclitic" in out[0].flags
    assert "compound_part" in out[1].flags


def test_splits_waw_before_article():
    out = split_proclitics([_raw("والكتاب")])
    assert _texts(out) == ["و", "الكتاب"]


def test_splits_baa_before_article():
    out = split_proclitics([_raw("بالبيت")])
    assert _texts(out) == ["ب", "البيت"]


def test_splits_lam_lam_special_case():
    # للكتاب = li- + al-kitab, alif elided -> strip first lam, host keeps reduced article
    out = split_proclitics([_raw("للكتاب")])
    assert _texts(out) == ["ل", "لكتاب"]


def test_does_not_split_bare_waw_plus_radical():
    out = split_proclitics([_raw("وكتاب")])
    assert _texts(out) == ["وكتاب"]


def test_does_not_split_radical_initial_words():
    for word in ("وزير", "باب", "كتاب"):
        out = split_proclitics([_raw(word)])
        assert _texts(out) == [word], word


def test_does_not_split_short_article_like_token():
    # "ال" alone (length 2) must not split into ["ال", ""]
    out = split_proclitics([_raw("ال")])
    assert _texts(out) == ["ال"]


def test_spans_are_contiguous_after_split():
    out = split_proclitics([_raw("الكتاب", start=10)])
    assert out[0].span == (10, 12)   # ال
    assert out[1].span == (12, 16)   # كتاب


def test_unrelated_token_passes_through():
    out = split_proclitics([_raw("محمد")])
    assert _texts(out) == ["محمد"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/lang/arabic/test_tokenize.py -v`
Expected: FAIL with `ModuleNotFoundError: tracealign.lang.arabic.tokenize`.

- [ ] **Step 3: Write the implementation**

Create `src/tracealign/lang/arabic/tokenize.py`:

```python
"""Arabic-specific tokenizer hooks: conservative proclitic splitting."""

from __future__ import annotations

from tracealign.tokenize.base import RawToken

ALEF = "ا"
LAM = "ل"
ARTICLE = ALEF + LAM  # ال
# Single-letter proclitics that we split only when they precede the article.
_PROCLITIC_LETTERS = ("و", "ف", "ب", "ك")  # و ف ب ك


def _emit_split(r: RawToken, cut: int) -> list[RawToken]:
    """Split RawToken `r` at character offset `cut` into proclitic + host.

    Spans are contiguous (no separator character between Arabic proclitic
    and host).
    """
    start = r.span[0]
    proclitic = RawToken(
        raw=r.raw[:cut],
        span=(start, start + cut),
        flags=set(r.flags) | {"proclitic"},
    )
    host = RawToken(
        raw=r.raw[cut:],
        span=(start + cut, r.span[1]),
        flags=set(r.flags) | {"compound_part"},
    )
    return [proclitic, host]


def _split_one(r: RawToken) -> list[RawToken]:
    text = r.raw
    # Rule 2: single-letter proclitic + article (e.g. والـ, بالـ).
    if (
        len(text) > 3
        and text[0] in _PROCLITIC_LETTERS
        and text[1:3] == ARTICLE
    ):
        return _emit_split(r, 1)
    # Rule 3: li- + article with elided alif (للـ).
    if len(text) > 2 and text[0] == LAM and text[1] == LAM:
        return _emit_split(r, 1)
    # Rule 1: bare definite article.
    if len(text) > 2 and text[:2] == ARTICLE:
        return _emit_split(r, 2)
    return [r]


def split_proclitics(raws: list[RawToken]) -> list[RawToken]:
    """Conservatively split Arabic proclitics off host words.

    Splits only on unambiguous signals: the definite article, single-letter
    proclitics that precede the article, and the li-+article (لل) contraction.
    Bare proclitic letters before a non-article host are left attached to
    avoid amputating word-initial radicals.
    """
    out: list[RawToken] = []
    for r in raws:
        out.extend(_split_one(r))
    return out
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/lang/arabic/test_tokenize.py -v`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add src/tracealign/lang/arabic/tokenize.py tests/lang/arabic/test_tokenize.py
git commit -m "feat(lang/arabic): conservative proclitic splitting

Refs #16"
```

---

### Task 4: Scoring tiers (`scoring.py`)

**Files:**
- Create: `src/tracealign/lang/arabic/scoring.py`
- Test: `tests/lang/arabic/test_scoring.py` (extend the file created in Task 1)

**Interfaces:**
- Consumes: `Reason` (Task 1), `Token`, `LanguagePack`, `ScoringTier`, `TierResult`, `rapidfuzz.fuzz.ratio`.
- Produces: `arabic_scoring_tiers() -> list[ScoringTier]` and the predicate functions `exact_predicate`, `diacritics_stripped_predicate`, `orthographic_variant_predicate`, `orthographic_predicate`, each with signature `(a: Token, b: Token, pack: LanguagePack) -> TierResult | None`. Tier order: EXACT, DIACRITICS_STRIPPED, ORTHOGRAPHIC_VARIANT, ORTHOGRAPHIC(fuzzy).

- [ ] **Step 1: Write the failing tests**

Append to `tests/lang/arabic/test_scoring.py`:

```python
from tracealign.lang.arabic.scoring import arabic_scoring_tiers
from tracealign.model import Token


def _tok(raw, text=None, skel=None):
    text = raw if text is None else text
    reps = {} if skel is None else {"skeleton": skel}
    return Token(id="t", position=0, raw=raw, text=text, representations=reps)


def _score(a, b):
    """Return (reason, TierResult) for the first matching tier, else None."""
    pack = object()
    for tier in arabic_scoring_tiers():
        result = tier.predicate(a, b, pack)
        if result is not None:
            return tier.reason, result
    return None


def test_exact_tier():
    reason, res = _score(_tok("كتاب"), _tok("كتاب"))
    assert reason == Reason.EXACT
    assert res.score == 1.0


def test_diacritics_stripped_tier():
    # same consonantal text, different raw (one vocalized)
    a = _tok("كَتَبَ", text="كتب")
    b = _tok("كتب", text="كتب")
    reason, res = _score(a, b)
    assert reason == Reason.DIACRITICS_STRIPPED
    assert res.score == 0.95


def test_orthographic_variant_tier():
    # different text, same skeleton (alif-hamza folding)
    a = _tok("أحمد", text="أحمد", skel="احمد")
    b = _tok("احمد", text="احمد", skel="احمد")
    reason, res = _score(a, b)
    assert reason == Reason.ORTHOGRAPHIC_VARIANT
    assert res.score == 0.90
    assert res.details["layer"] == "skeleton"


def test_orthographic_fuzzy_tier():
    a = _tok("كتاب", text="كتاب", skel="كتاب")
    b = _tok("كتيب", text="كتيب", skel="كتيب")
    reason, res = _score(a, b)
    assert reason == Reason.ORTHOGRAPHIC
    assert res.details["layer"] == "fuzzy"
    assert 0.0 < res.score < 0.9


def test_no_match_below_threshold():
    a = _tok("كتاب", text="كتاب", skel="كتاب")
    b = _tok("شمس", text="شمس", skel="شمس")
    assert _score(a, b) is None


def test_tier_order_and_reasons():
    tiers = arabic_scoring_tiers()
    assert [t.reason for t in tiers] == [
        Reason.EXACT,
        Reason.DIACRITICS_STRIPPED,
        Reason.ORTHOGRAPHIC_VARIANT,
        Reason.ORTHOGRAPHIC,
    ]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/lang/arabic/test_scoring.py -v`
Expected: FAIL with `ModuleNotFoundError: tracealign.lang.arabic.scoring`.

- [ ] **Step 3: Write the implementation**

Create `src/tracealign/lang/arabic/scoring.py`:

```python
"""Arabic scoring-tier predicates."""

from __future__ import annotations

from rapidfuzz.fuzz import ratio

from tracealign.lang.base import LanguagePack, ScoringTier, TierResult
from tracealign.model import Reason, Token


def exact_predicate(a: Token, b: Token, pack: LanguagePack) -> TierResult | None:
    if a.raw == b.raw:
        return TierResult(score=1.0)
    return None


def diacritics_stripped_predicate(
    a: Token, b: Token, pack: LanguagePack
) -> TierResult | None:
    if a.text == b.text and a.raw != b.raw:
        return TierResult(score=0.95)
    return None


def orthographic_variant_predicate(
    a: Token, b: Token, pack: LanguagePack
) -> TierResult | None:
    sk_a = a.representations.get("skeleton")
    sk_b = b.representations.get("skeleton")
    if sk_a is None or sk_b is None:
        return None
    if sk_a == sk_b and a.text != b.text:
        return TierResult(score=0.90, details={"layer": "skeleton"})
    return None


def orthographic_predicate(
    a: Token,
    b: Token,
    pack: LanguagePack,
    *,
    threshold: float = 0.6,
) -> TierResult | None:
    r = ratio(a.text, b.text) / 100.0
    if r < threshold:
        return None
    return TierResult(score=r * 0.9, details={"layer": "fuzzy", "ratio": r})


def arabic_scoring_tiers() -> list[ScoringTier]:
    return [
        ScoringTier(reason=Reason.EXACT, predicate=exact_predicate),
        ScoringTier(
            reason=Reason.DIACRITICS_STRIPPED,
            predicate=diacritics_stripped_predicate,
        ),
        ScoringTier(
            reason=Reason.ORTHOGRAPHIC_VARIANT,
            predicate=orthographic_variant_predicate,
        ),
        ScoringTier(reason=Reason.ORTHOGRAPHIC, predicate=orthographic_predicate),
    ]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/lang/arabic/test_scoring.py -v`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add src/tracealign/lang/arabic/scoring.py tests/lang/arabic/test_scoring.py
git commit -m "feat(lang/arabic): tiered scoring predicates

Refs #16"
```

---

### Task 5: ArabicLanguagePack + registration (`pack.py`, wiring)

**Files:**
- Create: `src/tracealign/lang/arabic/pack.py`
- Modify: `src/tracealign/lang/arabic/__init__.py` (replace placeholder with registration)
- Modify: `src/tracealign/__init__.py:37` (side-effect import) and `:40` (`_BUILTIN_PACK_MODULES`)
- Test: `tests/lang/arabic/test_pack_integration.py`

**Interfaces:**
- Consumes: `split_proclitics` (Task 3), `strip_tashkil`, `skeleton` (Task 2), `arabic_scoring_tiers` (Task 4), `LanguagePack`, `ScoringTier`, `Lexica`, `Token`, `RawToken`, `register_language`.
- Produces: `ArabicLanguagePack(LanguagePack)` with `code="ara"`, `aliases=("arabic",)`, `version="ara-0.1.0"`. Registered on import of `tracealign.lang.arabic`.

- [ ] **Step 1: Write the failing tests**

Create `tests/lang/arabic/test_pack_integration.py`:

```python
import tracealign
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/lang/arabic/test_pack_integration.py -v`
Expected: FAIL — `"ara"` not in `list_languages()` / `UnknownLanguageError`.

- [ ] **Step 3: Write the pack**

Create `src/tracealign/lang/arabic/pack.py`:

```python
"""ArabicLanguagePack."""

from __future__ import annotations

from tracealign.lang.arabic.normalize import skeleton, strip_tashkil
from tracealign.lang.arabic.tokenize import split_proclitics
from tracealign.lang.base import LanguagePack, ScoringTier
from tracealign.model import Lexica, Token
from tracealign.tokenize.base import RawToken


class ArabicLanguagePack(LanguagePack):
    code = "ara"
    aliases = ("arabic",)
    version = "ara-0.1.0"
    word_chars = ""
    mid_word_chars = ""

    def __init__(self, lexica: Lexica | None = None) -> None:
        # Conservative splitting needs no guard lexicon; an empty Lexica is
        # intentional (see design spec).
        self.lexica = lexica if lexica is not None else Lexica()

    def post_tokenize(self, raws: list[RawToken]) -> list[RawToken]:
        return split_proclitics(raws)

    def normalize(self, raw: RawToken) -> Token:
        # `id` and `position` are pack-local placeholders derived from the raw
        # character span; the public `tokenize()` overrides both with
        # sequence-index values keyed by `seq_label`.
        text = strip_tashkil(raw.raw)
        return Token(
            id=f"ara:{raw.span[0]:06d}",
            position=raw.span[0],
            raw=raw.raw,
            text=text,
            representations={"skeleton": skeleton(text)},
            flags=set(raw.flags),
            source_span=raw.span,
            metadata={},
        )

    def scoring_tiers(self) -> list[ScoringTier]:
        from tracealign.lang.arabic.scoring import arabic_scoring_tiers
        return arabic_scoring_tiers()
```

Replace `src/tracealign/lang/arabic/__init__.py` contents with:

```python
"""Arabic language pack."""

from tracealign.lang.arabic.pack import ArabicLanguagePack
from tracealign.lang.registry import register_language

register_language(ArabicLanguagePack())
```

- [ ] **Step 4: Wire registration into the top-level package**

In `src/tracealign/__init__.py`, after the Hebrew side-effect import (line 37), add:

```python
import tracealign.lang.hebrew  # noqa: F401  -- side effect: registers HBO pack
import tracealign.lang.arabic  # noqa: F401  -- side effect: registers ARA pack
```

And extend `_BUILTIN_PACK_MODULES` (line 40) to:

```python
_BUILTIN_PACK_MODULES = (
    "tracealign.lang.hebrew",
    "tracealign.lang.arabic",
)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/lang/arabic/test_pack_integration.py -v`
Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add src/tracealign/lang/arabic/pack.py src/tracealign/lang/arabic/__init__.py src/tracealign/__init__.py tests/lang/arabic/test_pack_integration.py
git commit -m "feat(lang/arabic): ArabicLanguagePack and registration

Refs #16"
```

---

### Task 6: Full-suite verification and lint

**Files:** none (verification only).

- [ ] **Step 1: Run the whole arabic test package**

Run: `pytest tests/lang/arabic/ -v`
Expected: all PASS.

- [ ] **Step 2: Run the entire suite to confirm no regression**

Run: `pytest -q`
Expected: all PASS (Hebrew + multi-witness + I/O unaffected; new Arabic tests green).

- [ ] **Step 3: Lint**

Run: `flake8 src/ tests/`
Expected: no output (zero issues).

- [ ] **Step 4: Confirm 3.10 floor**

If `tox` / multiple interpreters are available, run the suite under Python 3.10 specifically (lowest advertised version — per project release discipline). Otherwise note that CI matrix (3.10/3.11/3.12) must be green before the PR merges.

Run (if available): `python3.10 -m pytest -q`
Expected: all PASS.

- [ ] **Step 5: Commit (only if Step 4 required a fix)**

```bash
git add -A
git commit -m "test(lang/arabic): verify suite green across matrix

Refs #16"
```

---

## Self-Review

**Spec coverage:**
- §1 package structure → Tasks 2–5 create all five modules. ✓
- §2 pack metadata (`code/aliases/version/mid_word_chars`) → Task 5. `version` surfaced in `params` → tested in Task 5 Step 1. ✓
- §3 proclitic rules incl. negative cases + `لل` + contiguous spans → Task 3 tests. ✓
- §4 normalization (`raw`/`text`/`skeleton`, tatweel, all folding rules) → Task 2 tests. ✓
- §5 four tiers + two new reasons + `details.layer` → Tasks 1 & 4. ✓
- §6 tests (tokenize/normalize/scoring/registry/end-to-end, matrix, flake8) → Tasks 2–6. ✓
- §7 out-of-scope items are not implemented (correct). ✓
- "No `data/` directory / empty `Lexica`" → Task 5 pack sets `Lexica()`; no data files created. ✓

**Placeholder scan:** No TBD/TODO; every code step shows complete code; every test step shows the assertions. ✓

**Type consistency:** `split_proclitics(list[RawToken]) -> list[RawToken]`, `strip_tashkil(str)->str`, `skeleton(str)->str`, predicate signatures `(Token, Token, LanguagePack)->TierResult|None`, and `arabic_scoring_tiers()->list[ScoringTier]` are used identically across Tasks 2–5. Reason member names match between Task 1 (definition) and Task 4 (use). ✓

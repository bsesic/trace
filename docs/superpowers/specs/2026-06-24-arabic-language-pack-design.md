# Design: Arabic Language Pack (`ara`) — v0.1.0

**Date:** 2026-06-24
**Issue:** [#16](https://github.com/bsesic/trace/issues/16) — Arabic language pack (`ara`) — proclitic tokenization + orthographic normalization
**Roadmap:** First non-Hebrew language pack; prerequisite for the cross-lingual alignment path (#17), the clause/colon chunker (#18), and the Judaeo-Arabic transliteration helper (#20). Validates the `lang/base.py` / `register_language` abstraction on its first non-Hebrew exercise.

## Goal

Add an Arabic language pack so that `tokenize(text, lang="ara")` and `align(..., lang="ara")` work end-to-end, mirroring the structure of `src/tracealign/lang/hebrew/`. The pack handles proclitic segmentation and Arabic orthographic normalization through tiered scoring, staying rule-based and dependency-light (no CAMeL Tools / ML dependency), consistent with the project's stdlib-leaning ethos.

## Scope decisions (resolved during brainstorming)

1. **Proclitic splitting strategy: conservative / high-precision.** Split only where the signal is unambiguous. Over-splitting damages alignment (spurious tokens mis-align); under-splitting is recoverable by the fuzzy tier. Precision over recall. This choice also means **no curated guard lexicon is needed**.
2. **Reason vocabulary: granular — two new `Reason` values** (`DIACRITICS_STRIPPED`, `ORTHOGRAPHIC_VARIANT`). Each apparatus reason stays crisp for later critical-edition generation (Stage 5): an orthographic variant looks different from a fuzzy guess.

## 1. Package structure

Mirrors `lang/hebrew/`:

```
src/tracealign/lang/arabic/
  __init__.py      # register_language(ArabicLanguagePack())  — side-effect import
  pack.py          # ArabicLanguagePack(LanguagePack)
  tokenize.py      # split_proclitics()  — post_tokenize hook
  normalize.py     # strip_tashkil(), skeleton()
  scoring.py       # arabic_scoring_tiers()
```

Registration: add `import tracealign.lang.arabic` alongside the Hebrew side-effect import in `src/tracealign/__init__.py` (currently line 37) and add `"tracealign.lang.arabic"` to `_BUILTIN_PACK_MODULES` (line 40) so the test-isolation reload helper restores it.

**No `data/` directory.** The conservative splitting strategy requires no guard lexicon, so the pack sets `self.lexica = Lexica()` (empty). This is a deliberate consequence of decision (1) — no unused lexicon scaffolding is created (YAGNI).

## 2. Pack metadata

- `code = "ara"`
- `aliases = ("arabic",)`
- `version = "ara-0.1.0"`
- `mid_word_chars = ""` — Arabic letters are Unicode category `L`, so the generic `pretokenize` handles them; `_DEFAULT_PUNCT` already contains the Arabic punctuation `،؛`.

`version` is surfaced automatically: `align()` writes `language_pack_version: pack.version` into the result `params` via `needleman_wunsch.py:376`. No aligner change needed.

## 3. Tokenization — `split_proclitics()` (post_tokenize)

Arabic proclitics attach with **no separator character** (unlike the Hebrew maqqef). Spans are therefore contiguous: the cursor advances by `len(part)` with no `+1` gap between parts.

Conservative rules — split only on unambiguous signals:

| Input | Split | Rule |
|---|---|---|
| الكتاب | `ال` ǀ `كتاب` | Article `ال` (alif-lam) + remainder, when `len(token) > 2` |
| والكتاب | `و` ǀ `الكتاب` | Single-letter proclitic (و/ف/ب/ك) **only when immediately followed by the article `ال`** |
| بالبيت | `ب` ǀ `البيت` | same as above |
| للكتاب | `ل` ǀ `لكتاب` | Special case: `li-` + article, alif elided (`لل`) → strip first `ل`, host keeps the reduced article form `لكتاب` |
| وكتاب | — | bare و + radical → **no split** |
| وزير، باب، كتاب | — | radical-initial → **no split** |

Flags: the proclitic part gets flag `proclitic`; the host part gets `compound_part` (mirroring Hebrew's compound flag). The `لل` special case is covered by an explicit test.

**Decision recorded:** the `لل` case strips the first `ل` and leaves the host as `لكتاب` (reduced-article form). We do not attempt to restore the elided alif; downstream scoring treats `لكتاب` as the host token's `raw`.

## 4. Normalization

- `raw` = diplomatic form (with tashkil), preserved unchanged.
- `text` = NFC → remove combining marks (category `Mn`: fatha, kasra, damma, sukun, shadda, tanwin) **and** remove tatweel `ـ` (U+0640, category `Lm`, decorative elongation — stripped explicitly since it is not a combining mark).
- `representations["skeleton"]` = orthographic folding applied on top of `text`:
  - Alif variants: `أ إ آ ٱ → ا`
  - Taa marbuta: `ة → ه`
  - Alif maqsura / final ya: `ى → ي` (one canonical direction)
  - Hamza seats: `ؤ → و`, `ئ → ي`, bare `ء` removed

## 5. Scoring tiers — `arabic_scoring_tiers()`

Enum extension in `src/tracealign/model.py`: add `DIACRITICS_STRIPPED` and `ORTHOGRAPHIC_VARIANT` to `Reason`.

| Tier | Predicate | Score | Reason | `details.layer` |
|---|---|---|---|---|
| 1 | `a.raw == b.raw` | 1.0 | `EXACT` | — |
| 2 | `a.text == b.text` ∧ `a.raw != b.raw` | 0.95 | `DIACRITICS_STRIPPED` | — |
| 3 | `skeleton == skeleton` ∧ `a.text != b.text` | 0.90 | `ORTHOGRAPHIC_VARIANT` | `"skeleton"` |
| 4 | `rapidfuzz.fuzz.ratio / 100 ≥ 0.6` | `ratio * 0.9` | `ORTHOGRAPHIC` | `"fuzzy"` |

Tier predicates mirror `lang/hebrew/scoring.py` in shape and return `TierResult`. Score constants mirror the Hebrew ladder (0.95 / 0.90 / scaled fuzzy). No `ABBREVIATION` tier: Arabic abbreviation handling is out of scope for v0.1.0 (no abbreviation lexicon).

## 6. Tests (TDD — written red first)

- **tokenize:** every split case in §3, including the **negative cases** (وكتاب، وزير، باب must NOT split) and the `لل` special case; span correctness for contiguous parts.
- **normalize:** tashkil stripping, tatweel removal, each folding rule individually; `raw` remains the diplomatic form.
- **scoring:** one hit per tier with the correct `Reason` tag and `details.layer` where applicable.
- **registry:** `list_languages()` includes `"ara"`; `get_language("arabic")` resolves via alias.
- **end-to-end:** `tokenize(t, lang="ara")` and `align(a, b, lang="ara")` run; `params["language_pack_version"] == "ara-0.1.0"`.
- Full suite green on the 3.10 / 3.11 / 3.12 matrix; `flake8 src/ tests/` clean.

## 7. Out of scope (per issue #16)

- Clause/colon boundary particle inventory → issue #18 (chunker).
- Judaeo-Arabic written in Hebrew script → issue #20 (transliteration helper).
- Any cross-lingual scoring → issue #17.
- Syriac (`syr`) and Persian (`fas`) packs → separate follow-on issues once this pack lands and the abstraction is proven.

## Acceptance criteria (from issue #16)

- [ ] `list_languages()` includes `ara`; `tokenize`/`align` with `lang="ara"` work end-to-end.
- [ ] Proclitic split separates `wa-`/`fa-`/`al-` etc. and does **not** split radical `w`/`f` (targeted tests).
- [ ] Orthographic normalization collapses alif/hamza/taa-marbuta/ya variants into a skeleton; diplomatic form preserved in `raw`.
- [ ] Tiered scoring returns reason tags consistent with the `Reason` enum (extended with two Arabic-relevant, script-neutral reasons, justified above).
- [ ] Tests follow TDD; full suite green on 3.10/3.11/3.12; `flake8` clean.
- [ ] `pack.version` set (`ara-0.1.0`) and surfaced in result `params`.

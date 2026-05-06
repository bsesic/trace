# TRACE Roadmap

**Last updated:** 2026-05-06
**Current branch:** `feature/v0.1-design-spec`

This document tracks the high-level status of TRACE and the order in which the
sub-projects are being built. For the full design see
`docs/superpowers/specs/2026-04-28-trace-v0.1-design.md`. For the v0.1 task
breakdown see `docs/superpowers/plans/2026-04-28-trace-v0.1.md`.

---

## v0.1 — Foundation

**Goal:** Pairwise philological alignment with a Hebrew language pack, tokenizer,
semi-global Needleman–Wunsch with affine gaps and abbreviation-span lookahead,
and JSON / TEI / eScriptorium I/O.

### Status: 21 of 21 implementation tasks complete (106 tests passing, flake8 clean) — ready for final review + merge

| # | Task | Status |
|---|---|---|
| 0 | Bootstrap project tooling (pyproject, flake8, pytest) | ✅ |
| 1 | Data model — Token, Reason, Match | ✅ |
| 2 | Data model — AlignmentResult, Lexica | ✅ |
| — | Package rename `trace` → `tracealign` (stdlib-shadow fix) | ✅ |
| 3 | Tokenizer base — RawToken, EditorialBracketRules | ✅ |
| 4 | Generic plaintext pretokenize | ✅ |
| 5 | Language-pack ABC + registry | ✅ |
| 6 | Hebrew pack — tokenizer hooks (gershayim mid-word, maqqef split) | ✅ |
| 7 | Hebrew pack — normalizer (niqqud strip, skeleton, abbrev candidates) | ✅ |
| 8 | Hebrew pack — seed lexica + Lexica.load | ✅ |
| 9 | Hebrew pack — scoring tiers + auto-registration | ✅ |
| 10 | Generic tiered scorer | ✅ |
| 11 | Aligner — basic Gotoh DP with affine gaps | ✅ |
| 12 | Aligner — semi-global modification (free terminal gaps) | ✅ |
| 13 | Aligner — affine gap verification tests | ✅ |
| 14 | Aligner — abbreviation-span lookahead (primary + continuation) | ✅ |
| 15 | Aligner — `align()` wrapper with summary + total_score | ✅ |
| 16 | Public API in `tracealign.__init__` | ✅ |
| 17 | I/O — JSON dump/load for `AlignmentResult` | ✅ |
| 18 | I/O — eScriptorium JSON importer | ✅ |
| 19 | I/O — TEI XML importer | ✅ |
| 20 | E2E synthetic Hebrew golden file | ✅ |
| — | Final code review + merge to `develop` | ⏳ next |

### v0.1 Acceptance Criteria

Tracked in the design spec §8. The remaining tasks (16–20) cover the public
surface and validation that all 9 `Reason` values fire end-to-end on a
synthetic Hebrew witness pair.

---

## Long-Term Decomposition

TRACE is a general-purpose philological alignment library. The full vision —
not just v0.1 — covers five sub-projects, each with its own brainstorming →
spec → plan → implementation cycle.

| # | Sub-project | Status |
|---|---|---|
| 1 | **Pairwise aligner + Hebrew normalization + tokenization** | v0.1 — in progress |
| 2 | Master alignment graph / incremental multi-witness alignment | future |
| 3 | Geniza fragment anchor detection (matching fragments against ~150 000 candidates) | future |
| 4 | Text-reuse detection (recurring-phrase alignment, e.g. recurring rabbinic formulae) | future |
| 5 | Apparatus / critical-edition generation (lemmas, sigla, Fließtext output) | future |

Each later sub-project starts with its own brainstorming session and gets its
own spec under `docs/superpowers/specs/` and plan under
`docs/superpowers/plans/`.

### v0.2 Candidates (post-v0.1, not yet specced)

- **Multi-language packs:** Arabic and Greek as second and third reference
  language packs, validating that the language-agnostic core holds up.
- **Learned scoring weights:** record full feature vectors per match (currently
  only `(score, reason, details)` is returned), enabling later training of a
  weighted match function.
- **Custom editorial-bracket rules per project:** today the defaults are
  hard-coded; users override via `EditorialBracketRules`. v0.2 may ship
  per-project preset bundles.
- **Performance pass:** if real-world Sifra/Geniza alignments exceed the
  performance sanity targets in the v0.1 spec (500×500 < 1 s, 2 000×2 000 < 30 s),
  add NumPy vectorization and/or a Cython hot path for the DP inner loop.

---

## Branch Model

- `main` — stable releases. Updated only via merge from `develop` when a
  release is cut. Never pushed to directly.
- `develop` — integration branch holding the latest development work.
- `feature/<topic>` — branched off `develop`, merged back into `develop`.
  v0.1 work lives on `feature/v0.1-design-spec`.

PRs target `develop`. v0.1 ships when Tasks 16–20 are merged into `develop`
and the acceptance criteria from spec §8 are met, at which point `develop`
merges into `main` and a `0.1.0` tag is cut.

---

## Quality Gates

Every commit must pass before merge:

1. **Linting** — `flake8 src/ tests/` reports zero issues (PEP 8 compliant).
2. **Tests** — full pytest suite passes.

Both are enforced locally and in CI. No commits with AI-assistant attribution
in commit messages, PR descriptions, or any other shipping artefact.